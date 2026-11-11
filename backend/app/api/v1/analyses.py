from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.database import get_db
from app.models import Niche, Analysis, PainPoint, RecommendedFeature, HookCopy, FaqItem, DossierReport
from app.schemas import AnalysisCreateRequest, AnalysisResponse, DossierResponse
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.dossier_compiler import DossierCompiler

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
            resp = AnalysisResponse.model_validate(cached_analysis)
            resp.is_cached = True
            return resp

    # 3. Cache Miss / Force Refresh -> Executa Orquestrador Multi-LLM com Failover
    raw_data = await LLMOrchestrator.synthesize(
        keyword=keyword_clean,
        niche_name=niche.name
    )

    # 4. Grava Nova Análise no PostgreSQL
    new_analysis = Analysis(
        niche_id=payload.niche_id,
        keyword=keyword_clean,
        mode=payload.mode or "mock",
        sources_selected=payload.sources,
        sample_size=raw_data["sample_size"]
    )
    db.add(new_analysis)
    await db.flush()  # Obtém ID da análise

    # Adiciona itens relacionais
    for p in raw_data["pain_points"]:
        db.add(PainPoint(analysis_id=new_analysis.id, **p))

    for f in raw_data["recommended_features"]:
        db.add(RecommendedFeature(analysis_id=new_analysis.id, **f))

    for h in raw_data["hook_copies"]:
        db.add(HookCopy(analysis_id=new_analysis.id, **h))

    for faq in raw_data["faq_items"]:
        db.add(FaqItem(analysis_id=new_analysis.id, **faq))

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
