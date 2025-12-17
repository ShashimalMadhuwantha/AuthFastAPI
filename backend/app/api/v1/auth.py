from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService
from app.core.logger import logger

router = APIRouter()

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin")

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account
    
    """
    logger.info(f"[API] Signup request received for username: {user.username}, email: {user.email}")
    try:
        db_user = AuthService.create_user(db, user)
        logger.info(f"[API] Signup successful for user: {user.username}")
        return db_user
    except HTTPException as e:
        logger.warning(f"[API] Signup failed for {user.username}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[API] Unexpected error during signup for {user.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signup: {str(e)}"
        )

@router.post("/signin", response_model=Token)
async def signin(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and get access token
    Returns JWT access token for authenticated requests
    """
    logger.info(f"[API] Signin request received for username: {user_login.username}")
    try:
        token = AuthService.authenticate_user(db, user_login)
        logger.info(f"[API] Signin successful for user: {user_login.username}")
        return token
    except HTTPException as e:
        logger.warning(f"[API] Signin failed for {user_login.username}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[API] Unexpected error during signin for {user_login.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during signin: {str(e)}"
        )

@router.get("/users/me", response_model=UserResponse)
async def get_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get current user's information based on JWT token
    """
    current_user = AuthService.get_current_user_from_token(token)
    logger.info(f"[API] Get user request for authenticated user: {current_user}")
    db_user = AuthService.get_user_by_username(db, current_user)
    if not db_user:
        logger.warning(f"[API] User not found: {current_user}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    logger.info(f"[API] User retrieved successfully: {current_user}")
    return db_user
