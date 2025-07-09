"""
User service layer for authentication and user management
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from ..models.user import User, UserRole
from ..schemas.auth import UserCreate, UserUpdate
from ..auth.security import get_password_hash, verify_password

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user operations with business logic"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user with validation"""
        try:
            # Business logic: validate user data
            if self.get_user_by_username(db, user_data.username):
                raise ValueError("Username already exists")
            
            if self.get_user_by_email(db, user_data.email):
                raise ValueError("Email already exists")
            
            # Validate password strength
            if len(user_data.password) < 8:
                raise ValueError("Password must be at least 8 characters long")
            
            # Create user
            hashed_password = get_password_hash(user_data.password)
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                role=UserRole.USER,  # Default role
                is_active=True,
                is_verified=False
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            self.logger.info(f"Created new user: {db_user.username}")
            return db_user
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating user: {e}")
            raise
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        try:
            user = self.get_user_by_username(db, username)
            if not user:
                return None
            
            if not verify_password(password, user.hashed_password):
                return None
            
            if not user.is_active:
                return None
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
            
            self.logger.info(f"User authenticated: {username}")
            return user
            
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return None
    
    def update_user(
        self, 
        db: Session, 
        user_id: int, 
        user_data: UserUpdate,
        current_user: User
    ) -> Optional[User]:
        """Update user with access control"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                return None
            
            # Access control: users can only update themselves, admins can update anyone
            if current_user.role != UserRole.ADMIN and current_user.id != user_id:
                raise PermissionError("Not authorized to update this user")
            
            # Validate unique constraints
            update_data = user_data.dict(exclude_unset=True)
            
            if 'username' in update_data and update_data['username'] != user.username:
                if self.get_user_by_username(db, update_data['username']):
                    raise ValueError("Username already exists")
            
            if 'email' in update_data and update_data['email'] != user.email:
                if self.get_user_by_email(db, update_data['email']):
                    raise ValueError("Email already exists")
            
            # Role changes require admin privileges
            if 'role' in update_data and current_user.role != UserRole.ADMIN:
                raise PermissionError("Only admins can change user roles")
            
            # Apply updates
            for field, value in update_data.items():
                setattr(user, field, value)
            
            user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(user)
            
            self.logger.info(f"User {current_user.username} updated user: {user.username}")
            return user
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error updating user: {e}")
            raise
    
    def deactivate_user(self, db: Session, user_id: int, current_user: User) -> bool:
        """Deactivate a user (admin only)"""
        try:
            if current_user.role != UserRole.ADMIN:
                raise PermissionError("Only admins can deactivate users")
            
            user = self.get_user_by_id(db, user_id)
            if not user:
                return False
            
            # Prevent self-deactivation
            if user.id == current_user.id:
                raise ValueError("Cannot deactivate your own account")
            
            user.is_active = False
            user.updated_at = datetime.utcnow()
            db.commit()
            
            self.logger.info(f"Admin {current_user.username} deactivated user: {user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error deactivating user: {e}")
            raise
    
    def get_users(
        self, 
        db: Session, 
        current_user: User,
        skip: int = 0, 
        limit: int = 100,
        role_filter: Optional[UserRole] = None,
        active_only: bool = True
    ) -> List[User]:
        """Get users with filtering (admin only)"""
        try:
            if current_user.role != UserRole.ADMIN:
                raise PermissionError("Only admins can list users")
            
            query = db.query(User)
            
            if active_only:
                query = query.filter(User.is_active == True)
            
            if role_filter:
                query = query.filter(User.role == role_filter)
            
            users = query.offset(skip).limit(limit).all()
            
            self.logger.info(f"Admin {current_user.username} retrieved {len(users)} users")
            return users
            
        except Exception as e:
            self.logger.error(f"Error retrieving users: {e}")
            raise
    
    def get_user_statistics(self, db: Session, current_user: User) -> Dict[str, Any]:
        """Get user statistics (admin only)"""
        try:
            if current_user.role != UserRole.ADMIN:
                raise PermissionError("Only admins can access user statistics")
            
            # Total users
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            
            # Role distribution
            role_stats = db.query(
                User.role,
                db.func.count(User.id).label('count')
            ).group_by(User.role).all()
            
            # Recent registrations (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_registrations = db.query(User).filter(
                User.created_at >= thirty_days_ago
            ).count()
            
            # Recent logins (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            recent_logins = db.query(User).filter(
                User.last_login >= seven_days_ago
            ).count()
            
            stats = {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "recent_registrations": recent_registrations,
                "recent_logins": recent_logins,
                "roles": [
                    {"role": role.value, "count": count} 
                    for role, count in role_stats
                ]
            }
            
            self.logger.info(f"Admin {current_user.username} accessed user statistics")
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting user statistics: {e}")
            raise
    
    def change_password(
        self, 
        db: Session, 
        user_id: int, 
        old_password: str, 
        new_password: str,
        current_user: User
    ) -> bool:
        """Change user password with validation"""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                return False
            
            # Access control
            if current_user.role != UserRole.ADMIN and current_user.id != user_id:
                raise PermissionError("Not authorized to change this password")
            
            # Verify old password (unless admin)
            if current_user.role != UserRole.ADMIN:
                if not verify_password(old_password, user.hashed_password):
                    raise ValueError("Current password is incorrect")
            
            # Validate new password
            if len(new_password) < 8:
                raise ValueError("New password must be at least 8 characters long")
            
            # Update password
            user.hashed_password = get_password_hash(new_password)
            user.updated_at = datetime.utcnow()
            db.commit()
            
            self.logger.info(f"Password changed for user: {user.username}")
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error changing password: {e}")
            raise

# Create singleton instance
user_service = UserService()
