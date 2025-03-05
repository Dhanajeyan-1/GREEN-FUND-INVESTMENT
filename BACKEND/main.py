from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from auth import create_jwt_token, get_current_user
from models import User, Project
from database import SessionLocal, engine
from sqlalchemy.orm import Session

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Mock AI function (replace later)
def calculate_risk(esg_score: float) -> str:
    if esg_score > 75:
        return "Low"
    elif esg_score > 50:
        return "Medium"
    else:
        return "High"

# Login route
@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": create_jwt_token({"sub": email})}

# Submit project route
@app.post("/submit-project")
def submit_project(name: str, esg_score: float, user=Depends(get_current_user), db: Session = Depends(get_db)):
    risk = calculate_risk(esg_score)
    project = Project(name=name, esg_score=esg_score, risk_category=risk, user_id=user["sub"])
    db.add(project)
    db.commit()
    return {"status": "success", "risk": risk}

# Root route
@app.get("/")
def read_root():
    return {"message": "API is running!"}