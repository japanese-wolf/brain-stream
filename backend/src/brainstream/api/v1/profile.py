"""User profile API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from brainstream.core.database import get_db
from brainstream.models.article import UserProfile

router = APIRouter(prefix="/profile", tags=["profile"])


# Request/Response models
class TechStackItem(BaseModel):
    """A single tech stack item."""

    name: str = Field(..., description="Technology name (e.g., 'lambda', 'kubernetes')")
    category: Optional[str] = Field(
        None, description="Category (e.g., 'compute', 'database', 'ai')"
    )


class ProfileResponse(BaseModel):
    """User profile response."""

    id: str
    tech_stack: list[str]
    preferred_vendors: list[str]
    llm_provider: str
    created_at: str
    updated_at: str


class ProfileUpdateRequest(BaseModel):
    """Request to update user profile."""

    tech_stack: Optional[list[str]] = Field(
        None, description="List of technologies to track"
    )
    preferred_vendors: Optional[list[str]] = Field(
        None, description="List of preferred vendors (e.g., ['AWS', 'GCP'])"
    )
    llm_provider: Optional[str] = Field(
        None, description="LLM provider to use ('claude', 'copilot')"
    )


class TechStackSuggestion(BaseModel):
    """Suggested tech stack items."""

    name: str
    category: str
    description: str


# Predefined tech stack suggestions
TECH_STACK_SUGGESTIONS = {
    "compute": [
        TechStackSuggestion(name="lambda", category="compute", description="AWS Lambda serverless functions"),
        TechStackSuggestion(name="ec2", category="compute", description="AWS EC2 virtual machines"),
        TechStackSuggestion(name="ecs", category="compute", description="AWS ECS container service"),
        TechStackSuggestion(name="eks", category="compute", description="AWS EKS Kubernetes service"),
        TechStackSuggestion(name="fargate", category="compute", description="AWS Fargate serverless containers"),
        TechStackSuggestion(name="cloud-run", category="compute", description="GCP Cloud Run serverless containers"),
        TechStackSuggestion(name="cloud-functions", category="compute", description="GCP Cloud Functions"),
        TechStackSuggestion(name="gke", category="compute", description="GCP Google Kubernetes Engine"),
        TechStackSuggestion(name="kubernetes", category="compute", description="Kubernetes container orchestration"),
    ],
    "database": [
        TechStackSuggestion(name="rds", category="database", description="AWS RDS relational database"),
        TechStackSuggestion(name="dynamodb", category="database", description="AWS DynamoDB NoSQL database"),
        TechStackSuggestion(name="aurora", category="database", description="AWS Aurora database"),
        TechStackSuggestion(name="redshift", category="database", description="AWS Redshift data warehouse"),
        TechStackSuggestion(name="cloud-sql", category="database", description="GCP Cloud SQL"),
        TechStackSuggestion(name="firestore", category="database", description="GCP Firestore NoSQL"),
        TechStackSuggestion(name="bigquery", category="database", description="GCP BigQuery analytics"),
        TechStackSuggestion(name="spanner", category="database", description="GCP Cloud Spanner"),
    ],
    "ai": [
        TechStackSuggestion(name="openai", category="ai", description="OpenAI GPT models"),
        TechStackSuggestion(name="anthropic", category="ai", description="Anthropic Claude models"),
        TechStackSuggestion(name="bedrock", category="ai", description="AWS Bedrock AI service"),
        TechStackSuggestion(name="sagemaker", category="ai", description="AWS SageMaker ML platform"),
        TechStackSuggestion(name="vertex-ai", category="ai", description="GCP Vertex AI platform"),
        TechStackSuggestion(name="langchain", category="ai", description="LangChain framework"),
        TechStackSuggestion(name="gemini", category="ai", description="Google Gemini models"),
    ],
    "storage": [
        TechStackSuggestion(name="s3", category="storage", description="AWS S3 object storage"),
        TechStackSuggestion(name="efs", category="storage", description="AWS EFS file system"),
        TechStackSuggestion(name="cloud-storage", category="storage", description="GCP Cloud Storage"),
    ],
    "networking": [
        TechStackSuggestion(name="cloudfront", category="networking", description="AWS CloudFront CDN"),
        TechStackSuggestion(name="api-gateway", category="networking", description="AWS API Gateway"),
        TechStackSuggestion(name="route53", category="networking", description="AWS Route 53 DNS"),
        TechStackSuggestion(name="cloud-cdn", category="networking", description="GCP Cloud CDN"),
    ],
}


async def get_or_create_profile(session: AsyncSession) -> UserProfile:
    """Get the user profile or create a default one.

    Since this is a local app, we use a single profile per installation.
    """
    result = await session.execute(select(UserProfile).limit(1))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(
            tech_stack=[],
            preferred_vendors=[],
            llm_provider="claude",
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

    return profile


@router.get("", response_model=ProfileResponse)
async def get_profile(session: AsyncSession = Depends(get_db)) -> ProfileResponse:
    """Get the current user profile."""
    profile = await get_or_create_profile(session)

    return ProfileResponse(
        id=profile.id,
        tech_stack=profile.tech_stack,
        preferred_vendors=profile.preferred_vendors,
        llm_provider=profile.llm_provider,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


@router.put("", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    session: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Update the user profile."""
    profile = await get_or_create_profile(session)

    if request.tech_stack is not None:
        profile.tech_stack = request.tech_stack

    if request.preferred_vendors is not None:
        profile.preferred_vendors = request.preferred_vendors

    if request.llm_provider is not None:
        if request.llm_provider not in ["claude", "copilot", "none"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid LLM provider. Must be 'claude', 'copilot', or 'none'",
            )
        profile.llm_provider = request.llm_provider

    await session.commit()
    await session.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        tech_stack=profile.tech_stack,
        preferred_vendors=profile.preferred_vendors,
        llm_provider=profile.llm_provider,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


@router.post("/tech-stack", response_model=ProfileResponse)
async def add_tech_stack(
    items: list[str],
    session: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Add items to the tech stack."""
    profile = await get_or_create_profile(session)

    # Add new items, avoiding duplicates
    current_stack = set(profile.tech_stack)
    for item in items:
        current_stack.add(item.lower())

    profile.tech_stack = list(current_stack)
    await session.commit()
    await session.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        tech_stack=profile.tech_stack,
        preferred_vendors=profile.preferred_vendors,
        llm_provider=profile.llm_provider,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


@router.delete("/tech-stack/{item}", response_model=ProfileResponse)
async def remove_tech_stack_item(
    item: str,
    session: AsyncSession = Depends(get_db),
) -> ProfileResponse:
    """Remove an item from the tech stack."""
    profile = await get_or_create_profile(session)

    current_stack = [t for t in profile.tech_stack if t.lower() != item.lower()]
    profile.tech_stack = current_stack

    await session.commit()
    await session.refresh(profile)

    return ProfileResponse(
        id=profile.id,
        tech_stack=profile.tech_stack,
        preferred_vendors=profile.preferred_vendors,
        llm_provider=profile.llm_provider,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat(),
    )


@router.get("/suggestions", response_model=dict[str, list[TechStackSuggestion]])
async def get_tech_stack_suggestions() -> dict[str, list[TechStackSuggestion]]:
    """Get suggested tech stack items organized by category."""
    return TECH_STACK_SUGGESTIONS


@router.get("/vendors", response_model=list[str])
async def get_available_vendors() -> list[str]:
    """Get list of available vendors."""
    return ["AWS", "GCP", "OpenAI", "Anthropic", "GitHub", "GitHub OSS"]
