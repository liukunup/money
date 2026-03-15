from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.household import HouseholdRole


# Household Schemas
class HouseholdBase(BaseModel):
    name: str


class HouseholdCreate(HouseholdBase):
    pass


class HouseholdUpdate(BaseModel):
    name: Optional[str] = None


class HouseholdResponse(HouseholdBase):
    id: int
    invite_code: str
    created_at: datetime

    class Config:
        from_attributes = True


# HouseholdMember Schemas
class HouseholdMemberBase(BaseModel):
    role: HouseholdRole = HouseholdRole.MEMBER


class HouseholdMemberResponse(BaseModel):
    id: int
    user_id: int
    household_id: int
    role: HouseholdRole
    joined_at: datetime
    user: Optional[dict] = None  # Will include user info

    class Config:
        from_attributes = True


# Full household with members
class HouseholdWithMembers(HouseholdResponse):
    members: List[HouseholdMemberResponse] = []

    class Config:
        from_attributes = True


# Join household
class HouseholdJoin(BaseModel):
    invite_code: str


# Invite code response
class InviteCodeResponse(BaseModel):
    invite_code: str
