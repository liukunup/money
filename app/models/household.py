from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class HouseholdRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Household(Base):
    __tablename__ = "households"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    invite_code = Column(String(8), unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    members = relationship("HouseholdMember", back_populates="household")


class HouseholdMember(Base):
    __tablename__ = "household_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    household_id = Column(Integer, ForeignKey("households.id"), nullable=False)
    role = Column(Enum(HouseholdRole), default=HouseholdRole.MEMBER)
    joined_at = Column(DateTime, server_default=func.now())

    # Relationships
    household = relationship("Household", back_populates="members")
    user = relationship("User", back_populates="household_memberships")


# Add reverse relationship to User model
from app.models.user import User
User.household_memberships = relationship("HouseholdMember", back_populates="user")
