from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID
from slugify import slugify

from app.core.database import get_db
from app.models import Niche, Analysis
from app.schemas import NicheCreate, NicheResponse

router = APIRouter(prefix="/niches", tags=["Niches"])


@router.get("", response_model=List[NicheResponse])
async def list_niches(db: AsyncSession = Depends(get_db)):
    """Lista todos os nichos cadastrados com a contagem de análises executadas."""
    query = (
        select(Niche, func.count(Analysis.id).label("total_analyses"))
        .outerjoin(Analysis, Niche.id == Analysis.niche_id)
        .group_by(Niche.id)
        .order_by(Niche.name.asc())
    )
    result = await db.execute(query)
    rows = result.all()
    
    response = []
    for niche, count in rows:
        niche_dict = {
            "id": niche.id,
            "name": niche.name,
            "slug": niche.slug,
            "description": niche.description,
            "created_at": niche.created_at,
            "updated_at": niche.updated_at,
            "total_analyses": count
        }
        response.append(niche_dict)
    return response


@router.post("", response_model=NicheResponse, status_code=status.HTTP_201_CREATED)
async def create_niche(payload: NicheCreate, db: AsyncSession = Depends(get_db)):
    """Cria um novo nicho temático."""
    slug = payload.slug or slugify(payload.name)
    
    # Verifica duplicidade de slug
    existing = await db.execute(select(Niche).where(Niche.slug == slug))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um nicho com o identificador '{slug}'."
        )
        
    niche = Niche(
        name=payload.name,
        slug=slug,
        description=payload.description
    )
    db.add(niche)
    await db.commit()
    await db.refresh(niche)
    
    return {
        "id": niche.id,
        "name": niche.name,
        "slug": niche.slug,
        "description": niche.description,
        "created_at": niche.created_at,
        "updated_at": niche.updated_at,
        "total_analyses": 0
    }
