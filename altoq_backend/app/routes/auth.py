from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from google.oauth2 import id_token
from google.auth.transport import requests
from ..database import get_db
from ..models.user import User as UserModel
from ..schemas.user import UserCreate, UserLogin, Token, User, ForgotPasswordRequest, VerifyCodeRequest, ResetPasswordRequest
from ..utils.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, login_rate_limiter, recovery_rate_limiter, hash_recovery_code
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
def register(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario"""
    # Rate limit check
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not login_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de registro. Por favor, intente de nuevo más tarde."
        )

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
def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Iniciar sesión"""
    # Rate limit check
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not login_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de inicio de sesión. Por favor, intente de nuevo en un minuto."
        )

    print(f"DEBUG LOGIN: email={credentials.email}, password={credentials.password}")
    # Buscar usuario por email
    db_user = db.query(UserModel).filter(UserModel.email == credentials.email).first()
    if not db_user:
        print("DEBUG LOGIN: User not found in DB")
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # Verificar password
    is_valid = verify_password(credentials.password, db_user.password)
    print(f"DEBUG LOGIN: db_user found, hash={db_user.password}, matches={is_valid}")
    if not is_valid:
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


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """Solicitar recuperación de contraseña (envía un código de 6 dígitos)"""
    # Rate limit check
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not recovery_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiadas solicitudes de recuperación. Por favor, intente de nuevo más tarde."
        )

    # 1. Verificar si el usuario existe
    db_user = db.query(UserModel).filter(UserModel.email == req.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="El correo electrónico no está registrado")

    # 2. Generar código de 6 dígitos
    import random
    code = f"{random.randint(100000, 999999)}"
    hashed_code = hash_recovery_code(code)

    # 3. Invalidar códigos anteriores no usados para este email
    from datetime import datetime, timedelta
    from ..models.password_reset import PasswordResetCode

    db.query(PasswordResetCode).filter(
        PasswordResetCode.email == req.email,
        PasswordResetCode.is_used == False
    ).update({"is_used": True})

    # 4. Guardar en BD con expiración de 15 minutos
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    reset_entry = PasswordResetCode(
        email=req.email,
        code=hashed_code,
        expires_at=expires_at
    )
    db.add(reset_entry)
    db.commit()

    # 5. Enviar correo (o simular en desarrollo) con el código original (sin hashear)
    from ..utils.email import send_recovery_email
    send_recovery_email(req.email, code)

    return {"message": "Código de verificación enviado correctamente"}


@router.post("/verify-code")
def verify_code(req: VerifyCodeRequest, request: Request, db: Session = Depends(get_db)):
    """Verificar si el código es correcto y no ha expirado"""
    # Rate limit check
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not recovery_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de verificación. Por favor, intente de nuevo más tarde."
        )

    from datetime import datetime
    from ..models.password_reset import PasswordResetCode

    hashed_input_code = hash_recovery_code(req.code)

    # Buscar código válido
    db_code = db.query(PasswordResetCode).filter(
        PasswordResetCode.email == req.email,
        PasswordResetCode.code == hashed_input_code,
        PasswordResetCode.is_used == False,
        PasswordResetCode.expires_at > datetime.utcnow()
    ).order_by(PasswordResetCode.id.desc()).first()

    if not db_code:
        raise HTTPException(status_code=400, detail="Código inválido o expirado")

    return {"message": "Código verificado correctamente"}


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """Cambiar la contraseña usando el código verificado"""
    # Rate limit check
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not recovery_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de cambio de contraseña. Por favor, intente de nuevo más tarde."
        )

    from datetime import datetime
    from ..models.password_reset import PasswordResetCode

    hashed_input_code = hash_recovery_code(req.code)

    # 1. Validar el código de nuevo
    db_code = db.query(PasswordResetCode).filter(
        PasswordResetCode.email == req.email,
        PasswordResetCode.code == hashed_input_code,
        PasswordResetCode.is_used == False,
        PasswordResetCode.expires_at > datetime.utcnow()
    ).order_by(PasswordResetCode.id.desc()).first()

    if not db_code:
        raise HTTPException(status_code=400, detail="Código inválido o expirado")

    # 2. Obtener el usuario y cambiar password
    db_user = db.query(UserModel).filter(UserModel.email == req.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Hashear nueva contraseña
    db_user.password = get_password_hash(req.new_password)
    
    # Marcar código como usado
    db_code.is_used = True

    db.commit()

    return {"message": "Contraseña actualizada correctamente"}

