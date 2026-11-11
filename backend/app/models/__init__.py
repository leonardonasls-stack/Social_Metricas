import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Float, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Niche(Base):
    __tablename__ = "niches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    analyses = relationship("Analysis", back_populates="niche", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    niche_id = Column(UUID(as_uuid=True), ForeignKey("niches.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword = Column(String(255), nullable=False, index=True)
    mode = Column(String(50), default="mock", nullable=False)
    sources_selected = Column(JSON, default=list, nullable=False)
    sample_size = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    niche = relationship("Niche", back_populates="analyses")
    pain_points = relationship("PainPoint", back_populates="analysis", cascade="all, delete-orphan")
    recommended_features = relationship("RecommendedFeature", back_populates="analysis", cascade="all, delete-orphan")
    hook_copies = relationship("HookCopy", back_populates="analysis", cascade="all, delete-orphan")
    faq_items = relationship("FaqItem", back_populates="analysis", cascade="all, delete-orphan")
    dossier_report = relationship("DossierReport", back_populates="analysis", uselist=False, cascade="all, delete-orphan")


class PainPoint(Base):
    __tablename__ = "pain_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    frequency_percentage = Column(Float, default=0.0, nullable=False)
    severity = Column(String(50), default="medium", nullable=False)

    analysis = relationship("Analysis", back_populates="pain_points")


class RecommendedFeature(Base):
    __tablename__ = "recommended_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    rationale = Column(Text, nullable=False)
    reach = Column(Integer, default=5, nullable=False)
    impact = Column(Integer, default=5, nullable=False)
    confidence = Column(Integer, default=5, nullable=False)
    effort = Column(Integer, default=5, nullable=False)
    rice_score = Column(Float, default=0.0, nullable=False)

    analysis = relationship("Analysis", back_populates="recommended_features")


class HookCopy(Base):
    __tablename__ = "hook_copies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    placement = Column(String(100), nullable=False)
    hook_text = Column(Text, nullable=False)
    intent = Column(String(100), default="social_proof", nullable=False)

    analysis = relationship("Analysis", back_populates="hook_copies")


class FaqItem(Base):
    __tablename__ = "faq_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer_suggestion = Column(Text, nullable=False)
    friction_level = Column(Integer, default=3, nullable=False)

    analysis = relationship("Analysis", back_populates="faq_items")


class DossierReport(Base):
    __tablename__ = "dossier_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), unique=True, nullable=False)
    markdown_content = Column(Text, nullable=False)
    metadata_info = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    analysis = relationship("Analysis", back_populates="dossier_report")
