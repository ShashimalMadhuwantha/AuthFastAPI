from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.user import UserResponse, UserUpdate, UserCreate
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.core.logger import logger

router = APIRouter()

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> str:
    return AuthService.get_current_user_from_token(token)

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Get all users
    """
    logger.info(f"[API] Get all users request by {current_user}")
    try:
        users = UserService.get_all_users(db)
        logger.info(f"[API] Retrieved {len(users)} users for {current_user}")
        return users
    except HTTPException as e:
        logger.warning(f"[API] Get all users failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[API] Unexpected error getting all users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Create a new user 
    """
    logger.info(f"[API] Create user request by {current_user} for username: {user.username}")
    try:
        # Use AuthService to create user 
        db_user = AuthService.create_user(db, user)
        logger.info(f"[API] User {user.username} created successfully by {current_user}")
        return db_user
    except HTTPException as e:
        logger.warning(f"[API] Create user failed for {user.username}: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[API] Unexpected error creating user {user.username}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Get a specific user by ID
    """
    logger.info(f"[API] Get user {user_id} request by {current_user}")
    try:
        user = UserService.get_user_by_id(db, user_id)
        logger.info(f"[API] User {user_id} retrieved successfully by {current_user}")
        return user
    except HTTPException as e:
        logger.warning(f"[API] Get user {user_id} failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[API] Unexpected error getting user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Update a user's information
    """
    logger.info(f"[API] Update user {user_id} request by {current_user}")
    try:
        updated_user = UserService.update_user(db, user_id, user_update)
        logger.info(f"[API] User {user_id} updated successfully by {current_user}")
        return updated_user
    except HTTPException as e:
        logger.warning(f"[API] Update user {user_id} failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[API] Unexpected error updating user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Delete a user
    """
    logger.info(f"[API] Delete user {user_id} request by {current_user}")
    try:
        result = UserService.delete_user(db, user_id)
        logger.info(f"[API] User {user_id} deleted successfully by {current_user}")
        return result
    except HTTPException as e:
        logger.warning(f"[API] Delete user {user_id} failed: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[API] Unexpected error deleting user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
