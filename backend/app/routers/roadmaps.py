from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.database import get_db
from app.models import User, Roadmap, Milestone, Topic, StudySession, QuizResult
from app.schemas import RoadmapCreate, RoadmapResponse
from app.auth import get_current_user
from app.ai import generate_roadmap_ai

# Include Router Modules
router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])

@router.post("/generate", response_model=RoadmapResponse)
async def generate_roadmap(data: RoadmapCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Set all other user roadmaps to inactive
    db.query(Roadmap).filter(Roadmap.user_id == current_user.id).update({"is_active": False})
    
    # Generate profile updates
    profile = current_user.profile
    if profile:
        profile.career_goal = data.career_goal
        profile.skill_level = data.skill_level
        profile.daily_study_hours = data.daily_study_hours
        profile.study_duration = data.study_duration
    db.commit()
    
    # Generate Roadmap via AI or Fallback
    roadmap_data = await generate_roadmap_ai(
        career_goal=data.career_goal,
        skill_level=data.skill_level,
        daily_hours=data.daily_study_hours,
        study_duration=data.study_duration
    )
    
    # Save Roadmap to DB
    new_roadmap = Roadmap(
        user_id=current_user.id,
        title=roadmap_data.get("title", f"Roadmap for {data.career_goal}"),
        target_goal=data.career_goal,
        is_active=True,
        job_readiness_score=10  # Base level
    )
    db.add(new_roadmap)
    db.commit()
    db.refresh(new_roadmap)
    
    # Add Milestones & Topics
    milestones_in = roadmap_data.get("milestones", [])
    for m_idx, m_data in enumerate(milestones_in):
        milestone = Milestone(
            roadmap_id=new_roadmap.id,
            phase_number=m_data.get("phase_number", m_idx + 1),
            title=m_data.get("title", f"Phase {m_idx + 1}"),
            description=m_data.get("description", ""),
            estimated_weeks=m_data.get("estimated_weeks", 2),
            sort_order=m_idx
        )
        db.add(milestone)
        db.commit()
        db.refresh(milestone)
        
        topics_in = m_data.get("topics", [])
        for t_idx, t_data in enumerate(topics_in):
            topic = Topic(
                milestone_id=milestone.id,
                title=t_data.get("title", f"Topic {t_idx + 1}"),
                description=t_data.get("description", ""),
                resource_url=None,
                is_completed=False,
                sort_order=t_idx
            )
            db.add(topic)
            
    db.commit()
    

    
    # Autogenerate Planner study sessions based on topics
    db_roadmap = db.query(Roadmap).filter(Roadmap.id == new_roadmap.id).first()
    
    # Create study sessions for first milestone topics
    topics_list = []
    for ms in db_roadmap.milestones:
        for tp in ms.topics:
            topics_list.append(tp)
            
    today = datetime.utcnow().date()
    for idx, tp in enumerate(topics_list):
        session_date = today + timedelta(days=idx * 2)  # spread study sessions out every 2 days
        session = StudySession(
            user_id=current_user.id,
            session_date=session_date,
            topic_id=tp.id,
            hours_scheduled=data.daily_study_hours,
            hours_completed=0.0,
            status="Pending"
        )
        db.add(session)
    db.commit()
    
    # Refresh to return full roadmap with milestones and topics
    db.refresh(new_roadmap)
    return new_roadmap

@router.get("/active", response_model=Optional[RoadmapResponse])
def get_active_roadmap(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(
        Roadmap.user_id == current_user.id, 
        Roadmap.is_active == True
    ).first()
    return roadmap

@router.post("/topics/{topic_id}/complete")
def complete_topic(topic_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = db.query(Topic).join(Milestone).join(Roadmap).filter(
        Topic.id == topic_id,
        Roadmap.user_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
        
    topic.is_completed = True
    topic.completed_at = datetime.utcnow()
    
    # Update associated study sessions
    sessions = db.query(StudySession).filter(
        StudySession.topic_id == topic_id,
        StudySession.user_id == current_user.id
    ).all()
    for sess in sessions:
        sess.status = "Completed"
        sess.hours_completed = sess.hours_scheduled
        
    # Recalculate Job Readiness (increases proportional to topic completion)
    roadmap = topic.milestone.roadmap
    total_topics = db.query(Topic).join(Milestone).filter(Milestone.roadmap_id == roadmap.id).count()
    completed_topics = db.query(Topic).join(Milestone).filter(
        Milestone.roadmap_id == roadmap.id,
        Topic.is_completed == True
    ).count()
    
    # Map progress to job readiness
    if total_topics > 0:
        base_readiness = int((completed_topics / total_topics) * 80)  # Topics master up to 80%
        # Add a little boost for user profile strong areas
        boost = min(len(current_user.profile.strong_areas) * 4, 15) if current_user.profile else 0
        roadmap.job_readiness_score = min(base_readiness + 10 + boost, 100) # baseline 10%
        
    db.commit()
    return {"message": "Topic completed successfully", "job_readiness": roadmap.job_readiness_score}

@router.get("/topics/{topic_id}/resources")
async def get_topic_resources(topic_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    topic = db.query(Topic).join(Milestone).join(Roadmap).filter(
        Topic.id == topic_id,
        Roadmap.user_id == current_user.id
    ).first()
    
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found or access denied"
        )
        
    roadmap = topic.milestone.roadmap
    total_topics = db.query(Topic).join(Milestone).filter(Milestone.roadmap_id == roadmap.id).count()
    completed_topics = db.query(Topic).join(Milestone).filter(
        Milestone.roadmap_id == roadmap.id,
        Topic.is_completed == True
    ).count()
    progress_percent = (completed_topics / total_topics * 100.0) if total_topics > 0 else 0.0
    
    quiz = db.query(QuizResult).filter(
        QuizResult.topic_id == topic_id,
        QuizResult.user_id == current_user.id
    ).order_by(QuizResult.created_at.desc()).first()
    quiz_score = quiz.score if quiz else None
    
    profile = current_user.profile
    career_goal = profile.career_goal if profile else "Full-Stack Web Developer"
    skill_level = profile.skill_level if profile else "Beginner"
    
    from app.ai import generate_topic_resources_ai
    
    resources = await generate_topic_resources_ai(
        career_goal=career_goal,
        skill_level=skill_level,
        topic_title=topic.title,
        topic_desc=topic.description,
        progress_percent=progress_percent,
        quiz_score=quiz_score
    )
    return resources

from datetime import timedelta
