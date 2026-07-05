from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from app.database import get_db
from app.models import User, Profile
from app.schemas import UserRegister, UserLogin, Token, UserResponse, ProfileResponse
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/users", tags=["Users & Authentication"])

@router.post("/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_pwd = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pwd,
        name=user_data.name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create default profile
    new_profile = Profile(
        user_id=new_user.id,
        career_goal="Full-Stack Web Developer",
        skill_level="Beginner",
        daily_study_hours=2.0
    )
    db.add(new_profile)
    db.commit()
    
    # Return JWT token
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update active date for streak checking
    today = datetime.utcnow().date()
    if user.last_active_date is None:
        user.streak = 1
    elif user.last_active_date == today:
        pass  # already logged in today
    elif user.last_active_date == today - timedelta(days=1):
        user.streak += 1
    else:
        user.streak = 1
        
    user.last_active_date = today
    db.commit()

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=ProfileResponse)
def update_profile(profile_data: ProfileResponse, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = current_user.profile
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.add(profile)
        
    profile.career_goal = profile_data.career_goal
    profile.skill_level = profile_data.skill_level
    profile.daily_study_hours = profile_data.daily_study_hours
    profile.study_duration = profile_data.study_duration
    profile.weak_areas = profile_data.weak_areas
    profile.strong_areas = profile_data.strong_areas
    
    db.commit()
    db.refresh(profile)
    return profile
from datetime import timedelta # added import helper just in case
