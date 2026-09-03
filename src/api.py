from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from src.agent import WaterIntakeAgent
from src.database import log_intake, get_intake_history
from src.logger import log_message
app = FastAPI(title="AI Water Tracker API")
agent = WaterIntakeAgent()
class IntakeRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    intake_ml: int = Field(gt=0, le=10000)


@app.post("/log_intake")
async def log_water_intake(request: IntakeRequest):
    user_id = request.user_id.strip()
    if not user_id:
        raise HTTPException(status_code=422, detail="user_id must not be blank")
    log_intake(user_id, request.intake_ml)
    analysis = agent.analyze_intake(request.intake_ml)
    log_message(f"user {user_id} logged {request.intake_ml} ml")
    return {"message": "Water intake logged successfully","analysis":analysis}
@app.get("/history/{user_id}")
async def get_history(user_id: str):
    user_id = user_id.strip()
    if not user_id:
        raise HTTPException(status_code=422, detail="user_id must not be blank")
    history = get_intake_history(user_id)
    return {"user_id": user_id, "history": history}