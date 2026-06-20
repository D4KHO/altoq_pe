from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models.admin import Admin
from ..schemas.admin import AdminLogin, AdminToken, AdminResponse
from ..utils.security import verify_password, create_access_token, verify_token

router = APIRouter(prefix="/api/admin", tags=["admin-auth"])
security = HTTPBearer()

@router.post("/login", response_model=AdminToken)
def admin_login(credentials: AdminLogin, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    # Find admin by username
    admin = db.query(Admin).filter(Admin.username == credentials.username).first()
    
    if not admin or not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Update last login
    admin.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": admin.username, "type": "admin"})
    
    return AdminToken(
        access_token=access_token,
        admin=AdminResponse.model_validate(admin)
    )

@router.get("/me", response_model=AdminResponse)
def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current admin info"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload or payload.get("type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    username = payload.get("sub")
    admin = db.query(Admin).filter(Admin.username == username).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    return AdminResponse.model_validate(admin)
