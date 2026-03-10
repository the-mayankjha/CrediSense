from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ──────────────────────────────────────────────
# Enums (fixed choices — like dropdowns)
# ──────────────────────────────────────────────

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    INGESTING = "ingesting"
    RESEARCHING = "researching"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class RiskSeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertCategory(str, Enum):
    LITIGATION = "litigation"
    REGULATORY = "regulatory"
    PROMOTER = "promoter"
    SECTOR = "sector"
    FINANCIAL = "financial"


class DocumentType(str, Enum):
    ANNUAL_REPORT = "annual_report"
    BANK_STATEMENT = "bank_statement"
    GST_FILING = "gst_filing"
    SANCTION_LETTER = "sanction_letter"
    RATING_REPORT = "rating_report"
    LEGAL_NOTICE = "legal_notice"
    OTHER = "other"


class InsightCategory(str, Enum):
    SITE_VISIT = "site_visit"
    MANAGEMENT_INTERVIEW = "management_interview"
    MARKET_FEEDBACK = "market_feedback"
    OTHER = "other"


class InsightImpact(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class Decision(str, Enum):
    APPROVE = "APPROVE"
    APPROVE_WITH_CONDITIONS = "APPROVE_WITH_CONDITIONS"
    REJECT = "REJECT"


# ──────────────────────────────────────────────
# Model 1: Company Application
# ──────────────────────────────────────────────

class CompanyApplicationCreate(BaseModel):
    company_name: str = Field(..., example="Zenith Metals Ltd")
    pan: str = Field(..., example="AABCZ1234F")
    gstin: str = Field(..., example="27AABCZ1234F1Z5")
    sector: str = Field(..., example="Industrials")
    requested_loan_amount: Optional[float] = Field(None, example=500000000.0, description="In INR")


class CompanyApplication(BaseModel):
    id: str = Field(..., example="APP-001")
    company_name: str
    pan: str
    gstin: str
    sector: str
    requested_loan_amount: Optional[float] = None
    status: ApplicationStatus = ApplicationStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ──────────────────────────────────────────────
# Model 2: Extracted Financials + Ingested Document
# ──────────────────────────────────────────────

class ExtractedFinancials(BaseModel):
    revenue: Optional[float] = Field(None, description="Annual revenue in INR")
    net_profit: Optional[float] = Field(None, description="Net profit in INR")
    total_debt: Optional[float] = Field(None, description="Total debt in INR")
    total_equity: Optional[float] = Field(None, description="Total equity in INR")
    debt_to_equity: Optional[float] = Field(None, description="Debt-to-equity ratio")
    current_ratio: Optional[float] = Field(None, description="Current assets / current liabilities")
    interest_coverage_ratio: Optional[float] = Field(None, description="EBIT / Interest expense")
    covenants: list[str] = Field(default_factory=list, description="Financial covenants found in docs")
    related_party_transactions: list[str] = Field(default_factory=list)
    contingent_liabilities: list[str] = Field(default_factory=list)


class StructuredDataAnomaly(BaseModel):
    anomaly_type: str = Field(..., example="gstr_mismatch")
    description: str = Field(..., example="GSTR-3B shows ₹4Cr more revenue than bank deposits confirm")
    severity: RiskSeverity = RiskSeverity.MEDIUM
    data_points: dict = Field(default_factory=dict, description="Supporting numbers")


class IngestedDocument(BaseModel):
    id: str
    application_id: str
    file_name: str
    file_type: DocumentType
    extracted_text_preview: str = Field("", description="First ~500 chars of extracted text")
    financials: Optional[ExtractedFinancials] = None
    anomalies: list[StructuredDataAnomaly] = Field(default_factory=list)
    processing_status: str = Field("completed", example="completed")
    processed_at: datetime = Field(default_factory=datetime.now)


# ──────────────────────────────────────────────
# Model 3: Risk Alert (from Research Agent)
# ──────────────────────────────────────────────

class RiskAlert(BaseModel):
    severity: RiskSeverity
    source: str = Field(..., example="Economic Times")
    category: AlertCategory
    title: str = Field(..., example="Promoter under ED investigation")
    summary: str = Field(..., example="The ED has initiated a probe into...")
    url: Optional[str] = None
    discovered_at: datetime = Field(default_factory=datetime.now)


class ResearchResult(BaseModel):
    application_id: str
    company_name: str
    alerts: list[RiskAlert] = Field(default_factory=list)
    sector_outlook: str = Field("", description="LLM summary of sector conditions")
    promoter_background: str = Field("", description="LLM summary of promoter history")
    researched_at: datetime = Field(default_factory=datetime.now)


# ──────────────────────────────────────────────
# Model 4: Primary Insight (Credit Officer's input)
# ──────────────────────────────────────────────

class PrimaryInsightCreate(BaseModel):
    application_id: str
    category: InsightCategory
    note: str = Field(..., example="Factory found operating at 40% capacity with outdated machinery")
    impact: InsightImpact


class PrimaryInsight(BaseModel):
    id: str
    application_id: str
    category: InsightCategory
    note: str
    impact: InsightImpact
    created_at: datetime = Field(default_factory=datetime.now)


# ──────────────────────────────────────────────
# Model 5: Credit Score (Five Cs Breakdown)
# ──────────────────────────────────────────────

class FiveCsScore(BaseModel):
    character: int = Field(..., ge=0, le=100, description="Promoter integrity & track record")
    capacity: int = Field(..., ge=0, le=100, description="Ability to repay from cash flows")
    capital: int = Field(..., ge=0, le=100, description="Net worth & financial strength")
    collateral: int = Field(..., ge=0, le=100, description="Security available against the loan")
    conditions: int = Field(..., ge=0, le=100, description="Industry & economic conditions")
    overall: int = Field(..., ge=0, le=100, description="Weighted average score")


class FiveCsNarrative(BaseModel):
    character: str = Field(..., description="Narrative on promoter integrity")
    capacity: str = Field(..., description="Narrative on repayment ability")
    capital: str = Field(..., description="Narrative on financial strength")
    collateral: str = Field(..., description="Narrative on security/assets")
    conditions: str = Field(..., description="Narrative on industry outlook")


# ──────────────────────────────────────────────
# Model 6: Credit Decision
# ──────────────────────────────────────────────

class CreditDecision(BaseModel):
    decision: Decision
    suggested_limit: Optional[float] = Field(None, description="Suggested loan limit in INR")
    interest_rate_premium: Optional[float] = Field(None, description="% above base rate")
    reasoning: str = Field(..., description="Explainable justification for the decision")
    key_risk_factors: list[str] = Field(default_factory=list)
    key_strengths: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────
# Model 7: CAM Report (the final output)
# ──────────────────────────────────────────────

class CAMReport(BaseModel):
    id: str
    application: CompanyApplication
    financials: Optional[ExtractedFinancials] = None
    anomalies: list[StructuredDataAnomaly] = Field(default_factory=list)
    risk_alerts: list[RiskAlert] = Field(default_factory=list)
    primary_insights: list[PrimaryInsight] = Field(default_factory=list)
    sector_outlook: str = ""
    promoter_background: str = ""
    five_cs_scores: Optional[FiveCsScore] = None
    five_cs_narrative: Optional[FiveCsNarrative] = None
    decision: Optional[CreditDecision] = None
    generated_at: datetime = Field(default_factory=datetime.now)


# ──────────────────────────────────────────────
# API Request Models
# ──────────────────────────────────────────────

class DocumentUploadRequest(BaseModel):
    application_id: str = Field(..., example="APP-001")
    file_type: DocumentType = Field(..., example="annual_report")


class ExportFormat(str, Enum):
    DOCX = "docx"
    PDF = "pdf"


class CAMExportRequest(BaseModel):
    application_id: str = Field(..., example="APP-001")
    format: ExportFormat = ExportFormat.DOCX


# ──────────────────────────────────────────────
# API Response Wrappers
# ──────────────────────────────────────────────

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class DocumentUploadResponse(BaseModel):
    success: bool
    document: IngestedDocument
    message: str = "Document processed successfully"
