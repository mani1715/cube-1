"""
Phase 8.1A - AI-Assisted Admin Tools Router
Endpoints for AI blog assistance, notifications, and workflow automation
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from .permissions import get_current_admin, require_admin_or_above
from .phase8_ai import ai_assistant
from .phase8_notifications import notification_engine
from .utils import log_admin_action
import os
from pymongo import MongoClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client[os.environ.get('DB_NAME', 'test_database')]

router = APIRouter(prefix="/api/admin/phase8", tags=["Phase 8 - Intelligence & Automation"])

# ==========================================
# PYDANTIC MODELS
# ==========================================

class BlogDraftRequest(BaseModel):
    topic: str = Field(..., description="Main topic for the blog")
    keywords: Optional[List[str]] = Field(None, description="Keywords to include")
    tone: str = Field("professional", description="Tone: professional, casual, friendly")
    length: str = Field("medium", description="Length: short, medium, long")

class ContentImprovementRequest(BaseModel):
    content: str = Field(..., description="Content to improve")
    improvement_type: str = Field("general", description="Type: general, clarity, engagement, tone")

class TagSuggestionRequest(BaseModel):
    title: str = Field(..., description="Blog title")
    content: str = Field(..., description="Blog content")

class TitleSuggestionRequest(BaseModel):
    content: str = Field(..., description="Blog content")
    count: int = Field(5, ge=1, le=10, description="Number of title suggestions")

class SummaryRequest(BaseModel):
    content: str = Field(..., description="Content to summarize")
    max_length: int = Field(150, ge=50, le=300, description="Maximum summary length in words")

class QualityCheckRequest(BaseModel):
    title: str = Field(..., description="Blog title")
    content: str = Field(..., description="Blog content")


# ==========================================
# AI BLOG ASSISTANT ENDPOINTS
# ==========================================

@router.post("/ai/blog/draft")
async def generate_blog_draft(
    request: BlogDraftRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Generate a complete blog draft from topic and keywords (AI-assisted)
    
    - **topic**: Main topic for the blog
    - **keywords**: Optional keywords to include
    - **tone**: Writing tone (professional, casual, friendly)
    - **length**: Content length (short, medium, long)
    
    Returns AI-generated title, content, and suggested tags
    """
    try:
        result = await ai_assistant.generate_draft(
            topic=request.topic,
            keywords=request.keywords,
            tone=request.tone,
            length=request.length
        )
        
        # Log AI usage
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_blog_draft_generated",
            entity="blog",
            entity_id=None,
            details={
                "topic": request.topic,
                "tone": request.tone,
                "length": request.length
            }
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Blog draft generated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/ai/blog/improve")
async def improve_blog_content(
    request: ContentImprovementRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Improve existing blog content with AI suggestions
    
    - **content**: Content to improve
    - **improvement_type**: Focus area (general, clarity, engagement, tone)
    
    Returns improved version of the content
    """
    try:
        result = await ai_assistant.improve_content(
            content=request.content,
            improvement_type=request.improvement_type
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_content_improved",
            entity="blog",
            entity_id=None,
            details={"improvement_type": request.improvement_type}
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Content improved successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI improvement failed: {str(e)}")


@router.post("/ai/blog/suggest-tags")
async def suggest_blog_tags(
    request: TagSuggestionRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get AI-suggested tags for a blog post
    
    - **title**: Blog title
    - **content**: Blog content
    
    Returns list of relevant tags
    """
    try:
        tags = await ai_assistant.suggest_tags(
            title=request.title,
            content=request.content
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_tags_suggested",
            entity="blog",
            entity_id=None,
            details={"tag_count": len(tags)}
        )
        
        return {
            "success": True,
            "data": {"tags": tags},
            "message": f"Generated {len(tags)} tag suggestions"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tag suggestion failed: {str(e)}")


@router.post("/ai/blog/suggest-titles")
async def suggest_blog_titles(
    request: TitleSuggestionRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Get AI-suggested titles for blog content
    
    - **content**: Blog content
    - **count**: Number of title suggestions (1-10)
    
    Returns list of suggested titles
    """
    try:
        titles = await ai_assistant.suggest_titles(
            content=request.content,
            count=request.count
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_titles_suggested",
            entity="blog",
            entity_id=None,
            details={"title_count": len(titles)}
        )
        
        return {
            "success": True,
            "data": {"titles": titles},
            "message": f"Generated {len(titles)} title suggestions"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Title suggestion failed: {str(e)}")


@router.post("/ai/blog/generate-summary")
async def generate_blog_summary(
    request: SummaryRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Generate a concise summary of blog content
    
    - **content**: Content to summarize
    - **max_length**: Maximum length in words (50-300)
    
    Returns AI-generated summary
    """
    try:
        summary = await ai_assistant.generate_summary(
            content=request.content,
            max_length=request.max_length
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_summary_generated",
            entity="blog",
            entity_id=None,
            details={"max_length": request.max_length}
        )
        
        return {
            "success": True,
            "data": {"summary": summary},
            "message": "Summary generated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@router.post("/ai/blog/quality-check")
async def check_blog_quality(
    request: QualityCheckRequest,
    admin: dict = Depends(require_admin_or_above)
):
    """
    Analyze blog content quality with AI
    
    - **title**: Blog title
    - **content**: Blog content
    
    Returns quality analysis with scores and suggestions
    """
    try:
        result = await ai_assistant.quality_check(
            title=request.title,
            content=request.content
        )
        
        await log_admin_action(
            admin_id=admin["id"],
            admin_email=admin["email"],
            action="ai_quality_check",
            entity="blog",
            entity_id=None,
            details={"word_count": result["word_count"]}
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Quality check completed"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality check failed: {str(e)}")


# ==========================================
# AI FEATURE STATUS
# ==========================================

@router.get("/ai/status")
async def get_ai_status(admin: dict = Depends(get_current_admin)):
    """
    Get AI feature status and availability
    
    Returns information about AI capabilities and configuration
    """
    try:
        # Check if AI key is configured
        ai_key = os.getenv("EMERGENT_LLM_KEY")
        is_configured = bool(ai_key)
        
        # Get AI feature toggle status from database
        feature_toggle = db.feature_toggles.find_one({"name": "ai_assistance"})
        is_enabled = feature_toggle["enabled"] if feature_toggle else True
        
        return {
            "success": True,
            "data": {
                "configured": is_configured,
                "enabled": is_enabled,
                "provider": "OpenAI",
                "model": "gpt-4o-mini",
                "features": [
                    "blog_draft_generation",
                    "content_improvement",
                    "tag_suggestion",
                    "title_suggestion",
                    "summary_generation",
                    "quality_check"
                ]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
