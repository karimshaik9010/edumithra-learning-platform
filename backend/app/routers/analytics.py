from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from app.database import get_db
from app.models import User, Roadmap, Milestone, Topic, StudySession, QuizResult
from app.schemas import DashboardAnalytics
from app.auth import get_current_user
router = APIRouter(prefix="/analytics", tags=["Progress & Analytics"])

@router.get("/", response_model=DashboardAnalytics)
def get_analytics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(
        Roadmap.user_id == current_user.id,
        Roadmap.is_active == True
    ).first()
    
    if not roadmap:
        # Return default values if no active roadmap
        return DashboardAnalytics(
            learning_progress=0.0,
            weekly_study_time=0.0,
            learning_streak=current_user.streak,
            completed_topics_count=0,
            total_topics_count=0,
            job_readiness=10,
            recent_quiz_score=0.0,
            skills_progress={},
            ai_insights="Initialize your roadmap to unlock progress analytics."
        )
        
    # 1. Topic counts
    total_topics = db.query(Topic).join(Milestone).filter(Milestone.roadmap_id == roadmap.id).count()
    completed_topics = db.query(Topic).join(Milestone).filter(
        Milestone.roadmap_id == roadmap.id,
        Topic.is_completed == True
    ).count()
    
    learning_progress = float(completed_topics / total_topics) if total_topics > 0 else 0.0
    
    # 2. Weekly study time (hours completed in last 7 days)
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=7)
    weekly_hours = db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.session_date >= seven_days_ago,
        StudySession.session_date <= today,
        StudySession.status == "Completed"
    ).all()
    weekly_study_time = sum(s.hours_completed for s in weekly_hours)
    
    # 3. Recent quiz score
    recent_quizzes = db.query(QuizResult).filter(
        QuizResult.user_id == current_user.id
    ).order_by(QuizResult.created_at.desc()).limit(5).all()
    
    recent_quiz_score = 0.0
    if recent_quizzes:
        recent_quiz_score = sum(q.score for q in recent_quizzes) / len(recent_quizzes)
        
    # 4. Skills progress (Milestone level completion)
    skills_progress = {}
    for m in roadmap.milestones:
        m_total = len(m.topics)
        m_completed = sum(1 for t in m.topics if t.is_completed)
        skills_progress[m.title] = float(m_completed / m_total * 100) if m_total > 0 else 0.0
        
    # 5. AI Insights generator
    ai_insights = ""
    profile = current_user.profile
    
    if learning_progress == 0.0:
        ai_insights = f"Welcome aboard, {current_user.name}! Your syllabus for '{roadmap.target_goal}' is ready. Get started by completing your first study session today."
    elif recent_quiz_score > 0 and recent_quiz_score < 70:
        ai_insights = "Mentor Insight: We noticed some difficulties in recent quizzes. Focus on review sessions and look through the newly inserted prerequisite items."
    elif weekly_study_time > 10:
        ai_insights = "Excellent dedication! You have logged over 10 hours of study this week. Keep up this momentum, but remember to take breaks to avoid burnout."
    else:
        ai_insights = f"You are making steady progress in your roadmap. Completing 2 more topics will boost your estimated job readiness to {min(roadmap.job_readiness_score + 8, 100)}%!"
        
    return DashboardAnalytics(
        learning_progress=learning_progress,
        weekly_study_time=float(weekly_study_time),
        learning_streak=current_user.streak,
        completed_topics_count=completed_topics,
        total_topics_count=total_topics,
        job_readiness=roadmap.job_readiness_score,
        recent_quiz_score=float(recent_quiz_score),
        skills_progress=skills_progress,
        ai_insights=ai_insights
    )
