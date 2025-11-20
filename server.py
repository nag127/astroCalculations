from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from astrology_full import astrology_full


class AstroRequest(BaseModel):
    dob: str = Field(..., example="1977-08-04")
    tob: str = Field(..., example="01:30")
    tz: str = Field(..., description="IANA timezone string", example="Asia/Kolkata")
    latitude: float = Field(..., example=16.1817369)
    longitude: float = Field(..., example=81.1348181)


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
    except Exception as exc:  # pragma: no cover - just defensive
        raise HTTPException(status_code=500, detail=str(exc)) from exc

