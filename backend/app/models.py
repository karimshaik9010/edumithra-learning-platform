from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    streak = Column(Integer, default=0)
    last_active_date = Column(Date, nullable=True)

    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="user", cascade="all, delete-orphan")
    weekly_plans = relationship("WeeklyPlan", back_populates="user", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="user", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    career_goal = Column(String, nullable=False)
    skill_level = Column(String, default="Beginner")  # Beginner, Intermediate, Advanced
    daily_study_hours = Column(Float, default=2.0)
    study_duration = Column(String, nullable=True)
    weak_areas = Column(JSON, default=list)  # List of strings
    strong_areas = Column(JSON, default=list)  # List of strings

    user = relationship("User", back_populates="profile")

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    target_goal = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    job_readiness_score = Column(Integer, default=10)  # Starts at 10%

    user = relationship("User", back_populates="roadmaps")
    milestones = relationship("Milestone", back_populates="roadmap", cascade="all, delete-orphan")

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    phase_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    estimated_weeks = Column(Integer, default=2)
    sort_order = Column(Integer, default=0)

    roadmap = relationship("Roadmap", back_populates="milestones")
    topics = relationship("Topic", back_populates="milestone", cascade="all, delete-orphan")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    resource_url = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    sort_order = Column(Integer, default=0)

    milestone = relationship("Milestone", back_populates="topics")
    study_sessions = relationship("StudySession", back_populates="topic", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="topic", cascade="all, delete-orphan")

class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    plan_schema = Column(JSON, nullable=False)  # JSON representation of weekly schedule

    user = relationship("User", back_populates="weekly_plans")

class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_date = Column(Date, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    hours_scheduled = Column(Float, default=1.0)
    hours_completed = Column(Float, default=0.0)
    status = Column(String, default="Pending")  # Pending, Completed, Missed

    user = relationship("User", back_populates="study_sessions")
    topic = relationship("Topic", back_populates="study_sessions")

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    score = Column(Integer, nullable=False)  # Percentage, e.g., 85
    total_questions = Column(Integer, default=5)
    recommendations = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="quiz_results")
    topic = relationship("Topic", back_populates="quiz_results")





