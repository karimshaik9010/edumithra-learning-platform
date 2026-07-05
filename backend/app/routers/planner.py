from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from app.database import get_db
from app.models import User, StudySession, Topic, Milestone, Roadmap
from app.schemas import StudySessionResponse, StudySessionUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/planner", tags=["Weekly Study Planner"])

@router.get("/sessions", response_model=List[StudySessionResponse])
def get_study_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(StudySession).filter(
        StudySession.user_id == current_user.id
    ).order_by(StudySession.session_date.asc()).all()
    
    response = []
    for s in sessions:
        # Resolve topic title
        topic_title = s.topic.title if s.topic else "Self Study"
        response.append(
            StudySessionResponse(
                id=s.id,
                session_date=s.session_date,
                topic_id=s.topic_id,
                topic_title=topic_title,
                hours_scheduled=s.hours_scheduled,
                hours_completed=s.hours_completed,
                status=s.status
            )
        )
    return response

@router.put("/sessions/{session_id}", response_model=StudySessionResponse)
def update_study_session(session_id: int, data: StudySessionUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study session not found or access denied"
        )
        
    session.hours_completed = data.hours_completed
    session.status = data.status
    
    # If the user completed the session, check if we should complete the topic
    if data.status == "Completed" and session.topic_id:
        topic = db.query(Topic).filter(Topic.id == session.topic_id).first()
        if topic and not topic.is_completed:
            topic.is_completed = True
            topic.completed_at = datetime.utcnow()
            
            # Boost job readiness on topic completion
            roadmap = topic.milestone.roadmap
            total_topics = db.query(Topic).join(Milestone).filter(Milestone.roadmap_id == roadmap.id).count()
            completed_topics = db.query(Topic).join(Milestone).filter(
                Milestone.roadmap_id == roadmap.id,
                Topic.is_completed == True
            ).count()
            if total_topics > 0:
                base_readiness = int((completed_topics / total_topics) * 80)
                roadmap.job_readiness_score = min(base_readiness + 10, 100)
                
    db.commit()
    
    # Return response
    return StudySessionResponse(
        id=session.id,
        session_date=session.session_date,
        topic_id=session.topic_id,
        topic_title=session.topic.title if session.topic else "Self Study",
        hours_scheduled=session.hours_scheduled,
        hours_completed=session.hours_completed,
        status=session.status
    )

@router.post("/regenerate")
def regenerate_plan(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(
        Roadmap.user_id == current_user.id,
        Roadmap.is_active == True
    ).first()
    
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active roadmap found to generate schedule for"
        )
        
    # Clear existing pending/missed study sessions
    db.query(StudySession).filter(
        StudySession.user_id == current_user.id,
        StudySession.status != "Completed"
    ).delete()
    db.commit()
    
    # Get all uncompleted topics
    uncompleted_topics = db.query(Topic).join(Milestone).filter(
        Milestone.roadmap_id == roadmap.id,
        Topic.is_completed == False
    ).order_by(Milestone.sort_order.asc(), Topic.sort_order.asc()).all()
    
    # Create study sessions for uncompleted topics
    today = datetime.utcnow().date()
    hours_per_day = current_user.profile.daily_study_hours if current_user.profile else 2.0
    
    for idx, tp in enumerate(uncompleted_topics):
        session_date = today + timedelta(days=idx * 2)
        session = StudySession(
            user_id=current_user.id,
            session_date=session_date,
            topic_id=tp.id,
            hours_scheduled=hours_per_day,
            hours_completed=0.0,
            status="Pending"
        )
        db.add(session)
        

    
    return {"message": f"Successfully scheduled {len(uncompleted_topics)} topics"}
