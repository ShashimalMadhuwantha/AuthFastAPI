from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.logger import logger
from typing import List, Optional

class UserService:
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 1000) -> List[User]:
        """
        Get all users 
        """
        logger.info(f"Fetching users with skip={skip}, limit={limit}")
        try:
            users = db.query(User).offset(skip).limit(limit).all()
            logger.info(f"Retrieved {len(users)} users")
            return users
        except Exception as e:
            logger.error(f"Error fetching users: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching users: {str(e)}"
            )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get a specific user by ID
        """
        logger.info(f"Fetching user with ID: {user_id}")
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"User with ID {user_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with ID {user_id} not found"
                )
            logger.info(f"User found: {user.username}")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching user {user_id}: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching user: {str(e)}"
            )
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
        """
        Update a user's information
        """
        logger.info(f"Attempting to update user with ID: {user_id}")
        
        # Get the user
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            logger.warning(f"User with ID {user_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Check if username is being updated and if it's already taken
        if user_update.username and user_update.username != db_user.username:
            existing_user = db.query(User).filter(User.username == user_update.username).first()
            if existing_user:
                logger.warning(f"Username '{user_update.username}' already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Check if email is being updated and if it's already taken
        if user_update.email and user_update.email != db_user.email:
            existing_user = db.query(User).filter(User.email == user_update.email).first()
            if existing_user:
                logger.warning(f"Email '{user_update.email}' already exists")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
        
        # Update fields
        try:
            update_data = user_update.model_dump(exclude_unset=True)
            
            if 'password' in update_data:
                update_data['password'] = update_data['password']  
                logger.info(f"Password updated for user {user_id}")
            
            for field, value in update_data.items():
                setattr(db_user, field, value)
            
            db.commit()
            db.refresh(db_user)
            logger.info(f"User {user_id} updated successfully")
            return db_user
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {str(e)}", exc_info=True)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating user: {str(e)}"
            )
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> dict:
        """
        Delete a user
        """
        logger.info(f"Attempting to delete user with ID: {user_id}")
        
        # Get the user
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            logger.warning(f"User with ID {user_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        try:
            username = db_user.username
            db.delete(db_user)
            db.commit()
            logger.info(f"User {user_id} ({username}) deleted successfully")
            return {"message": f"User {username} deleted successfully", "id": user_id}
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}", exc_info=True)
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting user: {str(e)}"
            )
