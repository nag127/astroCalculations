import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from astrology_full import astrology_full, AstrologyComputationError
from crewai_answer import generate_answer_with_crewai


class AstroRequest(BaseModel):
    dob: str = Field(..., example="1977-08-04")
    tob: str = Field(..., example="01:30")
    tz: str = Field(..., description="IANA timezone string", example="Asia/Kolkata")
    latitude: float = Field(..., example=16.1817369)
    longitude: float = Field(..., example=81.1348181)


class AnswerRequest(BaseModel):
    """Request model for CrewAI-based answer generation."""
    question: str = Field(..., description="User's astrology question")
    chart_data: Dict[str, Any] = Field(..., description="Full astrology chart JSON data")
    needed_sections: List[str] = Field(default_factory=list, description="Chart sections needed for answer")
    current_date: str = Field(..., description="Current date in YYYY-MM-DD format")
    dasha_info: Optional[Dict[str, Any]] = Field(None, description="Dasha information if needed")
    planner_response: Optional[str] = Field(None, description="Planner's analysis if available")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("astrology_api")


app = FastAPI(title="Astrology API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Astrology API is running"}


@app.post("/astrology")
def compute_astrology(payload: AstroRequest):
    try:
        return astrology_full(
            dob=payload.dob,
            tob=payload.tob,
            tz_str=payload.tz,
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
    except AstrologyComputationError as exc:
        logger.error("Computation error: %s", exc, exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - just defensive
        logger.exception("Unexpected error while processing request")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@app.post("/answer")
def generate_answer(payload: AnswerRequest):
    """
    Generate astrology answers using CrewAI multi-agent system.
    This endpoint replaces direct OpenAI calls with a more sophisticated agent-based approach.
    """
    try:
        answer = generate_answer_with_crewai(
            question=payload.question,
            chart_data=payload.chart_data,
            needed_sections=payload.needed_sections,
            current_date=payload.current_date,
            dasha_info=payload.dasha_info,
            planner_response=payload.planner_response
        )
        return {
            "answer": answer,
            "success": True
        }
    except Exception as exc:
        logger.exception("Error generating answer with CrewAI")
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(exc)}") from exc


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Fallback handler so clients always get JSON instead of plain text.
    """
    if isinstance(exc, HTTPException):
        # Let FastAPI handle its own HTTPException responses.
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    logger.exception("Unhandled exception for %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

