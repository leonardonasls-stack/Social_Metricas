from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from slugify import slugify

from app.core.database import get_db
from app.models import Niche, Analysis, PainPoint, RecommendedFeature, HookCopy, FaqItem, DossierReport
from app.schemas import AnalysisCreateRequest, AnalysisResponse, DossierResponse
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.scrapecreators.real_miner import ScrapeCreatorsClient
from app.services.dossier_compiler import DossierCompiler
from app.services.typst_service import TypstPdfService

router = APIRouter(prefix="/analyses", tags=["Analyses"])


@router.post("", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def create_or_get_analysis(
    payload: AnalysisCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Executa ou recupera uma análise do banco de dados (Cache Hit).
    Se force_refresh=False e já houver análise prévia, responde em < 100ms.
    """
    # 1. Verifica existência do nicho
    niche = await db.get(Niche, payload.niche_id)
    if not niche:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nicho especificado não foi encontrado."
        )

    keyword_clean = payload.keyword.strip()

    # 2. Verifica Cache no PostgreSQL
    if not payload.force_refresh:
        query = (
            select(Analysis)
            .where(Analysis.niche_id == payload.niche_id, Analysis.keyword.ilike(keyword_clean))
            .options(
                selectinload(Analysis.pain_points),
                selectinload(Analysis.recommended_features),
                selectinload(Analysis.hook_copies),
                selectinload(Analysis.faq_items),
                selectinload(Analysis.dossier_report)
            )
            .order_by(Analysis.created_at.desc())
        )
        result = await db.execute(query)
        cached_analysis = result.scalars().first()
        
        if cached_analysis:
            # Se for um dossiê antigo que não tinha a Seção 3.1, recompila na hora
            if cached_analysis.dossier_report and "3.1 Especificação de Engenharia" not in cached_analysis.dossier_report.markdown_content:
                recompiled_md = DossierCompiler.compile_from_models(
                    niche_name=niche.name,
                    keyword=cached_analysis.keyword,
                    sample_size=cached_analysis.sample_size,
                    pain_points=cached_analysis.pain_points,
                    features=cached_analysis.recommended_features,
                    hooks=cached_analysis.hook_copies,
                    faqs=cached_analysis.faq_items
                )
                cached_analysis.dossier_report.markdown_content = recompiled_md
                await db.commit()

            resp = AnalysisResponse.model_validate(cached_analysis)
            resp.is_cached = True
            return resp

    # 3. Cache Miss / Force Refresh -> Minera dados reais se modo="live"
    mined_comments = []
    if payload.mode == "live":
        miner = ScrapeCreatorsClient()
        if miner.is_configured():
            mined_comments = await miner.mine_social_discussions(
                keyword=keyword_clean,
                niche_name=niche.name,
                max_interactions=50
            )

    # 4. Executa Orquestrador Multi-LLM com Failover enriquecido com dados minerados
    raw_data = await LLMOrchestrator.synthesize(
        keyword=keyword_clean,
        niche_name=niche.name,
        mined_comments=mined_comments
    )

    sample_size = raw_data.get("sample_size", 100)
    if mined_comments:
        sample_size = max(sample_size, len(mined_comments) * 3)

    # 5. Grava Nova Análise no PostgreSQL
    new_analysis = Analysis(
        niche_id=payload.niche_id,
        keyword=keyword_clean,
        mode=payload.mode or "mock",
        sources_selected=payload.sources,
        sample_size=sample_size
    )
    db.add(new_analysis)
    await db.flush()  # Obtém ID da análise

    # Adiciona itens relacionais com extração resiliente de chaves
    pain_points_data = raw_data.get("pain_points") or raw_data.get("pains") or []
    for p in pain_points_data:
        db.add(PainPoint(
            analysis_id=new_analysis.id,
            category=p.get("category", "Geral"),
            title=p.get("title", ""),
            description=p.get("description", ""),
            frequency_percentage=float(p.get("frequency_percentage", 0.0)),
            severity=p.get("severity", "medium"),
            sample_comments=p.get("sample_comments", []),
            financial_impact=p.get("financial_impact"),
            competitors_affected=p.get("competitors_affected", [])
        ))

    features_data = raw_data.get("recommended_features") or raw_data.get("features") or []
    for f in features_data:
        db.add(RecommendedFeature(
            analysis_id=new_analysis.id,
            title=f.get("title", ""),
            rationale=f.get("rationale", ""),
            reach=int(f.get("reach", 5)),
            impact=int(f.get("impact", 5)),
            confidence=int(f.get("confidence", 5)),
            effort=int(f.get("effort", 5)),
            rice_score=float(f.get("rice_score", 0.0)),
            user_story=f.get("user_story"),
            acceptance_criteria=f.get("acceptance_criteria", []),
            effort_breakdown=f.get("effort_breakdown"),
            technical_notes=f.get("technical_notes")
        ))

    hooks_data = raw_data.get("hook_copies") or raw_data.get("hooks") or []
    for h in hooks_data:
        db.add(HookCopy(
            analysis_id=new_analysis.id,
            placement=h.get("placement", "hero_headline"),
            hook_text=h.get("hook_text", ""),
            intent=h.get("intent", "social_proof"),
            variations=h.get("variations", []),
            page_position=h.get("page_position")
        ))

    faqs_data = raw_data.get("faq_items") or raw_data.get("faqs") or []
    for faq in faqs_data:
        db.add(FaqItem(
            analysis_id=new_analysis.id,
            question=faq.get("question", ""),
            answer_suggestion=faq.get("answer_suggestion", ""),
            friction_level=int(faq.get("friction_level", 3)),
            placement_tip=faq.get("placement_tip")
        ))

    # Gera e compila Dossiê em Markdown
    markdown_doc = DossierCompiler.compile_markdown(
        niche_name=niche.name,
        keyword=keyword_clean,
        data=raw_data
    )
    
    db.add(DossierReport(
        analysis_id=new_analysis.id,
        markdown_content=markdown_doc,
        metadata_info={"sources": payload.sources, "mode": payload.mode}
    ))

    await db.commit()

    # Recarrega análise com relacionamentos populados
    query = (
        select(Analysis)
        .where(Analysis.id == new_analysis.id)
        .options(
            selectinload(Analysis.pain_points),
            selectinload(Analysis.recommended_features),
            selectinload(Analysis.hook_copies),
            selectinload(Analysis.faq_items),
            selectinload(Analysis.dossier_report)
        )
    )
    result = await db.execute(query)
    saved_analysis = result.scalar_one()

    resp = AnalysisResponse.model_validate(saved_analysis)
    resp.is_cached = False
    return resp


@router.get("/{analysis_id}/dossier", response_model=DossierResponse)
async def get_analysis_dossier(analysis_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retorna o Dossiê Técnico em Markdown estruturado para visualização e impressão A4."""
    query = (
        select(DossierReport, Analysis.keyword)
        .join(Analysis, DossierReport.analysis_id == Analysis.id)
        .where(DossierReport.analysis_id == analysis_id)
    )
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dossiê para esta análise não foi encontrado."
        )
        
    dossier, keyword = row
    return DossierResponse(
        analysis_id=dossier.analysis_id,
        keyword=keyword,
        markdown_content=dossier.markdown_content,
        metadata_info=dossier.metadata_info,
        created_at=dossier.created_at
    )


@router.get("/{analysis_id}/pdf")
async def download_analysis_pdf(analysis_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Gera nativamente o PDF ultrarrápido com Typst (< 20ms) a partir dos dados do PostgreSQL.
    Garante A4 Portrait, margens exatas e blocos inquebráveis (#block(breakable: false)).
    """
    query = (
        select(Analysis)
        .where(Analysis.id == analysis_id)
        .options(
            selectinload(Analysis.niche),
            selectinload(Analysis.pain_points),
            selectinload(Analysis.recommended_features),
            selectinload(Analysis.hook_copies),
            selectinload(Analysis.faq_items)
        )
    )
    result = await db.execute(query)
    analysis = result.scalars().first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada para exportação em PDF."
        )

    # Compila o PDF usando o motor nativo em Rust do Typst
    try:
        pdf_bytes = TypstPdfService.generate_pdf(
            niche_name=analysis.niche.name if analysis.niche else "Geral",
            keyword=analysis.keyword,
            sample_size=analysis.sample_size,
            pain_points=analysis.pain_points,
            features=analysis.recommended_features,
            hooks=analysis.hook_copies,
            faqs=analysis.faq_items
        )
    except Exception as e:
        import logging
        logging.error(f"Erro na compilacao Typst: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao compilar PDF: {str(e)}"
        )

    safe_filename = f"Dossie_{slugify(analysis.keyword)}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"'
        }
    )

