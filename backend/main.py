import os
import tempfile
import uuid
import logging
from datetime import datetime, date
from typing import Dict, Any, List
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.database import get_db_repository, get_default_user_profile
from backend.agents.orchestrator import get_orchestrator

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chillar_seedhi.main")

# Initialize FastAPI App
app = FastAPI(title="ChillarSeedhi Backend API")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For prototype flexibility; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas for Request Validation
class OnboardingRequest(BaseModel):
    userId: str
    name: str
    language: str
    primaryIncome: str
    incomeFrequency: str
    monthlyIncome: int
    urgentExpenses: int
    savingsHabit: str
    hasEmergencyFund: str
    hasDebt: str
    primaryGoal: str
    selfRating: int

class ChatRequest(BaseModel):
    userId: str
    message: str

class TransactionRequest(BaseModel):
    userId: str
    amount: int
    type: str  # "in" or "out"
    category: str
    description: str = ""

class GoalRequest(BaseModel):
    userId: str
    type: str  # e.g., "education", "emergency", "home"
    target: int
    current: int

class StreakRequest(BaseModel):
    userId: str
    amountSavedToday: int

# Endpoints

@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    """Retrieves user profile data or creates a default one if new."""
    db = get_db_repository()
    profile = db.get_user(user_id)
    if not profile:
        profile = get_default_user_profile(user_id)
        db.save_user(user_id, profile)
    return profile

@app.post("/api/onboard")
async def onboard_user(request: OnboardingRequest):
    """Processes onboarding input and computes initial level and scores."""
    try:
        orch = get_orchestrator()
        # Convert Pydantic request to dict representation for Profile Agent ingestion
        form_data = request.dict()
        profile = orch.process_onboarding(request.userId, form_data)
        return {"status": "success", "profile": profile}
    except Exception as e:
        logger.error(f"Error in onboarding endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_message(request: ChatRequest):
    """Processes a user message and returns agent response and updated profile."""
    try:
        orch = get_orchestrator()
        result = orch.process_message(request.userId, request.message)
        return result
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice-upload")
async def voice_upload(
    userId: str = Form(...),
    file: UploadFile = File(...)
):
    """Receives audio file binary, transcribes using Groq Whisper, and routes to Chat Orchestrator."""
    temp_file_path = ""
    try:
        # Create a unique random file name to prevent Path Traversal/Collision
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".webm"
        # Security: strictly sanitize extension to web audio types
        if file_ext.lower() not in [".webm", ".wav", ".mp3", ".m4a", ".ogg"]:
            file_ext = ".webm"
            
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        # Store in system temporary directory
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, unique_filename)
        
        # Write binary file chunks to disk safely
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        logger.info(f"Saved uploaded audio file to temporary path: {temp_file_path}")
        
        # Initialize Groq client to transcribe
        from groq import Groq
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
        
        with open(temp_file_path, "rb") as audio_file:
            translation = groq_client.audio.transcriptions.create(
                file=(unique_filename, audio_file.read()),
                model="whisper-large-v3",
                prompt="Audio contains Indian regional accents or dialect. Hindi, Tamil, Kannada, Marathi, English or Hinglish.",
                response_format="json"
            )
            
        transcription_text = translation.text
        logger.info(f"Groq Whisper transcription success: '{transcription_text}'")
        
        # Route the transcribed text to Chat Orchestrator
        orch = get_orchestrator()
        result = orch.process_message(userId, transcription_text)
        
        # Return transcription along with response
        return {
            "transcription": transcription_text,
            "response": result["response"],
            "profile": result["profile"],
            "intent": result["intent"]
        }
        
    except Exception as e:
        logger.error(f"Error processing voice upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temporary audio file from disk
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"Cleaned up temporary audio file: {temp_file_path}")
            except Exception as ce:
                logger.warning(f"Failed to delete temp file {temp_file_path}: {ce}")

@app.post("/api/tracker")
async def add_transaction(request: TransactionRequest):
    """Logs money tracking transactions for Level 0-1 daily trackers."""
    db = get_db_repository()
    profile = db.get_user(request.userId)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    today_str = date.today().strftime("%Y-%m-%d")
    transaction = {
        "id": str(uuid.uuid4())[:8],
        "date": today_str,
        "type": request.type,
        "amount": request.amount,
        "category": request.category,
        "description": request.description
    }
    
    if "dailyTrackerLogs" not in profile:
        profile["dailyTrackerLogs"] = []
        
    profile["dailyTrackerLogs"].append(transaction)
    profile["lastActive"] = datetime.utcnow().isoformat() + "Z"
    
    db.save_user(request.userId, profile)
    return {"status": "success", "profile": profile}

@app.post("/api/goals")
async def update_goal(request: GoalRequest):
    """Sets or updates targets/current savings inside visual goal pockets."""
    db = get_db_repository()
    profile = db.get_user(request.userId)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    if "goals" not in profile:
        profile["goals"] = []
        
    # Check if goal of same type already exists
    found = False
    for g in profile["goals"]:
        if g["type"] == request.type:
            g["target"] = request.target
            g["current"] = request.current
            found = True
            break
            
    if not found:
        profile["goals"].append({
            "type": request.type,
            "target": request.target,
            "current": request.current
        })
        
    profile["lastActive"] = datetime.utcnow().isoformat() + "Z"
    db.save_user(request.userId, profile)
    return {"status": "success", "profile": profile}

@app.post("/api/streaks")
async def update_streak(request: StreakRequest):
    """Increments savings check-in streak and updates daily streak records."""
    db = get_db_repository()
    profile = db.get_user(request.userId)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    streaks = profile.get("streaks", {"streakCount": 0, "lastSavedDate": "", "calendar": []})
    today_str = date.today().strftime("%Y-%m-%d")
    
    # Check if already saved today
    if streaks.get("lastSavedDate") == today_str:
        return {"status": "success", "message": "Already checked in today", "profile": profile}
        
    # Check if streak is consecutive (yesterday or fresh)
    last_date_str = streaks.get("lastSavedDate", "")
    is_consecutive = False
    
    if last_date_str:
        try:
            last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
            days_diff = (date.today() - last_date).days
            if days_diff == 1:
                is_consecutive = True
        except ValueError:
            pass
            
    if is_consecutive:
        streaks["streakCount"] += 1
    else:
        streaks["streakCount"] = 1  # Reset or start new streak
        
    streaks["lastSavedDate"] = today_str
    if today_str not in streaks["calendar"]:
        streaks["calendar"].append(today_str)
        
    profile["streaks"] = streaks
    profile["lastActive"] = datetime.utcnow().isoformat() + "Z"
    
    db.save_user(request.userId, profile)
    return {"status": "success", "profile": profile}

# Run Server check
if __name__ == "__main__":
    import uvicorn
    # Security: Server binds to 127.0.0.1 for local/testing. Do NOT bind to 0.0.0.0
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
