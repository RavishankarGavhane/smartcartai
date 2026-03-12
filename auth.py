from fastapi import Request, Depends
from sqlalchemy.orm import Session
from typing import Optional
from auth_utils import verify_token
from database import get_db
from models import User
from crud import SessionCRUD, UserCRUD

async def get_current_user_from_cookie(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user from cookie"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    # Verify token
    payload = verify_token(token)
    if not payload:
        return None
    
    # Check session in database
    session = SessionCRUD.get_by_token(db, token)
    if not session:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    return UserCRUD.get_by_id(db, user_id)