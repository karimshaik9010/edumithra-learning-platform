from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models import User, Roadmap, Topic, Milestone, QuizResult
from app.auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/readiness", tags=["Job Readiness Coach"])

class JobReadinessReport(BaseModel):
    score: int

@router.get("/", response_model=JobReadinessReport)
def get_job_readiness(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(
        Roadmap.user_id == current_user.id,
        Roadmap.is_active == True
    ).first()
    
    if not roadmap:
        return JobReadinessReport(
            score=10
        )
        
    # Analyze topic details
    total_topics = db.query(Topic).join(Milestone).filter(Milestone.roadmap_id == roadmap.id).count()
    completed_topics = db.query(Topic).join(Milestone).filter(
        Milestone.roadmap_id == roadmap.id,
        Topic.is_completed == True
    ).count()
    
    # Calculate base score from roadmap completion
    completion_rate = completed_topics / total_topics if total_topics > 0 else 0.0
    
    # Quizzes influence
    quiz_results = db.query(QuizResult).filter(QuizResult.user_id == current_user.id).all()
    avg_quiz_score = sum(q.score for q in quiz_results) / len(quiz_results) if quiz_results else 70.0
    
    # Combined score weights:
    # 60% roadmap completion, 40% quiz score performance
    comp_weight = completion_rate * 60
    quiz_weight = (avg_quiz_score / 100) * 40
    
    calculated_score = int(comp_weight + quiz_weight)
    calculated_score = max(min(calculated_score, 100), 10)  # Bound between 10% and 100%
    
    # Save the updated readiness score on the roadmap
    roadmap.job_readiness_score = calculated_score
    db.commit()
    
    return JobReadinessReport(
        score=calculated_score
    )
