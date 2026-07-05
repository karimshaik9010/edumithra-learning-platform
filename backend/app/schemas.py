from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# Auth & User Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProfileResponse(BaseModel):
    career_goal: str
    skill_level: str
    daily_study_hours: float
    study_duration: Optional[str] = None
    weak_areas: List[str] = []
    strong_areas: List[str] = []

    @field_validator("skill_level")
    @classmethod
    def check_skill_level(cls, v: str) -> str:
        if v not in ["Beginner", "Intermediate", "Advanced"]:
            raise ValueError("Skill level must be 'Beginner', 'Intermediate', or 'Advanced'")
        return v

    @field_validator("study_duration")
    @classmethod
    def check_study_duration(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_strip = v.strip()
        if not v_strip:
            raise ValueError("Study duration cannot be empty")
        import re
        match = re.search(r'([+-]?\d+(?:\.\d+)?)', v_strip)
        if not match:
            raise ValueError("Study duration must contain a numeric value (e.g., '2 months', '90 days')")
        try:
            num = float(match.group(1))
            if num <= 0:
                raise ValueError("Study duration must be a positive value")
        except ValueError:
            raise ValueError("Invalid number in study duration")
        v_lower = v_strip.lower()
        if not any(unit in v_lower for unit in ["day", "week", "month", "year"]):
            raise ValueError("Study duration must specify a unit (e.g., 'days', 'weeks', 'months', 'years')")
        return v_strip

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    streak: int
    created_at: datetime
    profile: Optional[ProfileResponse] = None

    class Config:
        from_attributes = True

# Roadmap & Syllabus Schemas
class RoadmapCreate(BaseModel):
    career_goal: str
    skill_level: str = "Beginner"
    daily_study_hours: float = 2.0
    study_duration: str

    @field_validator("skill_level")
    @classmethod
    def check_skill_level(cls, v: str) -> str:
        if v not in ["Beginner", "Intermediate", "Advanced"]:
            raise ValueError("Skill level must be 'Beginner', 'Intermediate', or 'Advanced'")
        return v

    @field_validator("study_duration")
    @classmethod
    def check_study_duration(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Study duration cannot be empty")
        v_strip = v.strip()
        import re
        match = re.search(r'([+-]?\d+(?:\.\d+)?)', v_strip)
        if not match:
            raise ValueError("Study duration must contain a numeric value (e.g., '2 months', '90 days')")
        try:
            num = float(match.group(1))
            if num <= 0:
                raise ValueError("Study duration must be a positive value")
        except ValueError:
            raise ValueError("Invalid number in study duration")
        v_lower = v_strip.lower()
        if not any(unit in v_lower for unit in ["day", "week", "month", "year"]):
            raise ValueError("Study duration must specify a unit (e.g., 'days', 'weeks', 'months', 'years')")
        return v_strip

class TopicResponse(BaseModel):
    id: int
    milestone_id: int
    title: str
    description: Optional[str] = None
    resource_url: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime] = None
    sort_order: int

    class Config:
        from_attributes = True

class MilestoneResponse(BaseModel):
    id: int
    roadmap_id: int
    phase_number: int
    title: str
    description: Optional[str] = None
    estimated_weeks: int
    sort_order: int
    topics: List[TopicResponse] = []

    class Config:
        from_attributes = True

class RoadmapResponse(BaseModel):
    id: int
    user_id: int
    title: str
    target_goal: str
    created_at: datetime
    is_active: bool
    job_readiness_score: int
    milestones: List[MilestoneResponse] = []

    class Config:
        from_attributes = True

# Planner & Calendar Schemas
class StudySessionResponse(BaseModel):
    id: int
    session_date: date
    topic_id: int
    topic_title: Optional[str] = None
    hours_scheduled: float
    hours_completed: float
    status: str

    class Config:
        from_attributes = True

class WeeklyPlanResponse(BaseModel):
    id: int
    start_date: date
    end_date: date
    plan_schema: Any  # JSON object containing layout

    class Config:
        from_attributes = True

class StudySessionUpdate(BaseModel):
    hours_completed: float
    status: str  # Pending, Completed, Missed

# Quiz & Assessment Schemas
class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_option_index: int
    explanation: str

class QuizGenerationResponse(BaseModel):
    topic_id: int
    topic_title: str
    questions: List[QuizQuestion]

class QuizSubmit(BaseModel):
    topic_id: int
    score: int  # frontend graded for ease, backend logs it
    total_questions: int = 5
    recommendations: Optional[str] = None

class QuizResultResponse(BaseModel):
    id: int
    topic_id: int
    score: int
    total_questions: int
    recommendations: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True





# Dashboard Analytics
class DashboardAnalytics(BaseModel):
    learning_progress: float  # completed topics / total topics
    weekly_study_time: float   # total hours completed this week
    learning_streak: int
    completed_topics_count: int
    total_topics_count: int
    job_readiness: int
    recent_quiz_score: float
    skills_progress: Dict[str, float]  # category -> progress percentage
    ai_insights: str
