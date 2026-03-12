from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
from database import get_db
from models import Address, User
from schemas import AddressCreate, AddressResponse
from auth import get_current_user_from_cookie

router = APIRouter()

@router.get("/addresses", response_model=List[AddressResponse])
async def get_user_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Get all addresses for current user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    addresses = db.query(Address).filter(Address.user_id == current_user.id).all()
    return addresses

@router.post("/addresses", response_model=AddressResponse)
async def create_address(
    address: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Create a new address for current user"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # If this is set as default, remove default from other addresses
    if address.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True
        ).update({"is_default": False})
    
    # Create new address
    db_address = Address(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        type=address.type,
        recipient_name=address.recipient_name,
        phone=address.phone,
        address_line1=address.address_line1,
        address_line2=address.address_line2 or "",
        city=address.city,
        state=address.state,
        zip_code=address.zip_code,
        is_default=address.is_default,
        created_at=datetime.utcnow()
    )
    
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    
    return db_address

@router.put("/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: str,
    address: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Update an existing address"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # If setting as default, remove default from others
    if address.is_default and not db_address.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True
        ).update({"is_default": False})
    
    # Update fields
    for key, value in address.dict().items():
        setattr(db_address, key, value)
    
    db_address.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_address)
    
    return db_address

@router.delete("/addresses/{address_id}")
async def delete_address(
    address_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Delete an address"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    db_address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db.delete(db_address)
    db.commit()
    
    return {"success": True, "message": "Address deleted successfully"}

@router.post("/addresses/{address_id}/default")
async def set_default_address(
    address_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """Set an address as default"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Remove default from all addresses
    db.query(Address).filter(
        Address.user_id == current_user.id,
        Address.is_default == True
    ).update({"is_default": False})
    
    # Set new default
    db_address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db_address.is_default = True
    db.commit()
    
    return {"success": True, "message": "Default address updated"}