import enum
import bcrypt
from sqlalchemy import Column, Integer, String, Enum
from database import Base

class UserRole(enum.Enum):
    """
    Defines the roles a user can have.
    """
    USER = "user"
    ADMIN = "admin"

class User(Base):
    """
    User model for storing login credentials and roles.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)

    def set_password(self, password: str):
        """
        Hashes the password and stores it.
        """
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.password_hash = pw_hash.decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Checks a provided password against the stored hash.
        """
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role.value}')>"