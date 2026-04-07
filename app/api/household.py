import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.household import Household, HouseholdMember, HouseholdRole
from app.models.user import User
from app.schemas.household import (
    HouseholdCreate, HouseholdUpdate, HouseholdResponse,
    HouseholdWithMembers, HouseholdJoin, InviteCodeResponse,
    HouseholdMemberResponse
)
from app.core.security import get_current_user


router = APIRouter()


def generate_invite_code():
    """Generate 8-character alphanumeric invite code"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def get_user_household(db: Session, user_id: int):
    """Get user's household if they belong to one"""
    member = db.query(HouseholdMember).filter(
        HouseholdMember.user_id == user_id
    ).first()
    if member:
        return db.query(Household).filter(Household.id == member.household_id).first()
    return None


def get_member_role(db: Session, user_id: int, household_id: int) -> HouseholdRole:
    """Get user's role in a household"""
    member = db.query(HouseholdMember).filter(
        HouseholdMember.user_id == user_id,
        HouseholdMember.household_id == household_id
    ).first()
    return member.role if member else None


@router.post("/", response_model=HouseholdWithMembers)
def create_household(
    household: HouseholdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new household"""
    # Check if user already belongs to a household
    existing = get_user_household(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already belong to a household"
        )

    # Create household
    db_household = Household(
        name=household.name,
        invite_code=generate_invite_code()
    )
    db.add(db_household)
    db.commit()
    db.refresh(db_household)

    # Add creator as owner
    db_member = HouseholdMember(
        user_id=current_user.id,
        household_id=db_household.id,
        role=HouseholdRole.OWNER
    )
    db.add(db_member)
    db.commit()

    return db_household


@router.get("/", response_model=HouseholdWithMembers)
def get_my_household(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's household"""
    household = get_user_household(db, current_user.id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any household"
        )
    return household


@router.put("/{household_id}", response_model=HouseholdResponse)
def update_household(
    household_id: int,
    household: HouseholdUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update household name"""
    role = get_member_role(db, current_user.id, household_id)
    if role not in [HouseholdRole.OWNER, HouseholdRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update household"
        )

    db_household = db.query(Household).filter(Household.id == household_id).first()
    if not db_household:
        raise HTTPException(status_code=404, detail="Household not found")

    if household.name:
        db_household.name = household.name
    db.commit()
    db.refresh(db_household)
    return db_household


@router.post("/join", response_model=HouseholdWithMembers)
def join_household(
    join_data: HouseholdJoin,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a household via invite code"""
    # Check if user already belongs to a household
    existing = get_user_household(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already belong to a household. Leave first to join another."
        )

    # Find household by invite code
    household = db.query(Household).filter(
        Household.invite_code == join_data.invite_code
    ).first()
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code"
        )

    # Add user as member
    db_member = HouseholdMember(
        user_id=current_user.id,
        household_id=household.id,
        role=HouseholdRole.MEMBER
    )
    db.add(db_member)
    db.commit()

    return household


@router.post("/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_household(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Leave current household"""
    household = get_user_household(db, current_user.id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any household"
        )

    member = db.query(HouseholdMember).filter(
        HouseholdMember.user_id == current_user.id,
        HouseholdMember.household_id == household.id
    ).first()

    if member.role == HouseholdRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner cannot leave. Transfer ownership or delete household."
        )

    db.delete(member)
    db.commit()


@router.get("/members", response_model=list[HouseholdMemberResponse])
def list_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List household members"""
    household = get_user_household(db, current_user.id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any household"
        )

    members = db.query(HouseholdMember).filter(
        HouseholdMember.household_id == household.id
    ).all()

    result = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        result.append(HouseholdMemberResponse(
            id=m.id,
            user_id=m.user_id,
            household_id=m.household_id,
            role=m.role,
            joined_at=m.joined_at,
            user={"id": user.id, "username": user.username, "display_name": user.display_name} if user else None
        ))
    return result


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a member from household"""
    household = get_user_household(db, current_user.id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any household"
        )

    # Check role
    role = get_member_role(db, current_user.id, household.id)
    if role not in [HouseholdRole.OWNER, HouseholdRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to remove members"
        )

    # Find member
    member = db.query(HouseholdMember).filter(
        HouseholdMember.id == member_id,
        HouseholdMember.household_id == household.id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    # Cannot remove owner
    if member.role == HouseholdRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove owner"
        )

    db.delete(member)
    db.commit()


@router.post("/regenerate-code", response_model=InviteCodeResponse)
def regenerate_invite_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Regenerate invite code"""
    household = get_user_household(db, current_user.id)
    if not household:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any household"
        )

    role = get_member_role(db, current_user.id, household.id)
    if role not in [HouseholdRole.OWNER, HouseholdRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to regenerate code"
        )

    household.invite_code = generate_invite_code()
    db.commit()
    db.refresh(household)
    return InviteCodeResponse(invite_code=household.invite_code)


@router.delete("/{household_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_household(
    household_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete household (owner only)"""
    household = db.query(Household).filter(Household.id == household_id).first()
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")

    role = get_member_role(db, current_user.id, household.id)
    if role != HouseholdRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owner can delete household"
        )

    # Delete all members first
    db.query(HouseholdMember).filter(
        HouseholdMember.household_id == household_id
    ).delete()
    
    # Delete household
    db.delete(household)
    db.commit()
