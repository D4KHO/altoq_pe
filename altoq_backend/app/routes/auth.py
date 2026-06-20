from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from google.oauth2 import id_token
from google.auth.transport import requests
from ..database import get_db
from ..models.user import User as UserModel
from ..schemas.user import UserCreate, UserLogin, Token, User
from ..utils.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import os

router = APIRouter(prefix="/api/auth", tags=["auth"])

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class GoogleToken(UserLogin):
    token: str
    email: str | None = None
    password: str | None = None

@router.post("/google", response_model=Token)
def google_login(token_data: dict, db: Session = Depends(get_db)):
    token = token_data.get("token")
    if not token:
         raise HTTPException(status_code=400, detail="Token requerido")
         
    try:
        # Verify token
        # If GOOGLE_CLIENT_ID is not set, we cannot verify properly, but we can decode for testing if we skip verification
        # For production, GOOGLE_CLIENT_ID is mandatory.
        
        id_info = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )

        email = id_info['email']
        name = id_info.get('name', '')
        
        # Check if user exists
        db_user = db.query(UserModel).filter(UserModel.email == email).first()
        
        if not db_user:
            # Register new user
            # Create a random password or handle passwordless
            # Here we just set a dummy password that cannot be used for normal login easily
            import secrets
            random_password = secrets.token_urlsafe(16)
            hashed_password = get_password_hash(random_password)
            
            db_user = UserModel(
                email=email,
                name=name,
                password=hashed_password
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.email}, expires_delta=access_token_expires
        )
        
        return {
            "token": access_token,
            "user": User.model_validate(db_user)
        }

    except ValueError as e:
        # Invalid token
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")


@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario"""
    # Verificar si el email ya existe
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    # Crear usuario con password hasheada
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        name=user.name,
        password=hashed_password,
        address=user.address,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "token": access_token,
        "user": User.model_validate(db_user)
    }

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Iniciar sesión"""
    # Buscar usuario por email
    db_user = db.query(UserModel).filter(UserModel.email == credentials.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # Verificar password
    if not verify_password(credentials.password, db_user.password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    return {
        "token": access_token,
        "user": User.model_validate(db_user)
    }
