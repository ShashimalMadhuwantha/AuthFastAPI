from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import  verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings
from app.core.logger import logger

class AuthService:
    @staticmethod
    def create_user(db: Session, user: UserCreate):
        """
        Create a new user
        """
        logger.info(f"Attempting to create new user: {user.username}")
        
        # Check if username already exists
        db_user = db.query(User).filter(User.username == user.username).first()
        if db_user:
            logger.warning(f"User creation failed: Username '{user.username}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            logger.warning(f"User creation failed: Email '{user.email}' already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        try:
            db_user = User(
                username=user.username,
                email=user.email,
                password=user.password  
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"User created successfully: {user.username} (ID: {db_user.id})")
            return db_user
        except Exception as e:
            logger.error(f"Database error during user creation for '{user.username}': {str(e)}", exc_info=True)
            db.rollback()
            raise
    
    @staticmethod
    def authenticate_user(db: Session, user_login: UserLogin):
        """
        Authenticate user and return access token
        """
        logger.info(f"Authentication attempt for user: {user_login.username}")
        
        # Find user by username
        db_user = db.query(User).filter(User.username == user_login.username).first()
        if not db_user:
            logger.warning(f"Authentication failed: User '{user_login.username}' not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(user_login.password, db_user.password):
            logger.warning(f"Authentication failed: Invalid password for user '{user_login.username}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        try:
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": db_user.username}, expires_delta=access_token_expires
            )
            logger.info(f"Authentication successful for user: {user_login.username}")
            return {"access_token": access_token, "token_type": "bearer"}
        except Exception as e:
            logger.error(f"Token creation failed for user '{user_login.username}': {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def get_user_by_username(db: Session, username: str):
        """
        Get user by username
        """
        logger.debug(f"Fetching user by username: {username}")
        user = db.query(User).filter(User.username == username).first()
        if user:
            logger.debug(f"User found: {username}")
        else:
            logger.debug(f"User not found: {username}")
        return user
    
    @staticmethod
    def get_current_user_from_token(token: str) -> str:
        """
        Verify JWT token and extract username
        Used for authentication in protected routes
        """
        from app.core.security import verify_token
        
        logger.debug("Verifying JWT token")
        payload = verify_token(token)
        if payload is None:
            logger.warning("Token verification failed: Invalid or expired token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Token verification failed: Missing username in token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"Token verified successfully for user: {username}")
        return username
