import base64
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.config import settings

# Configuration loaded from Central Settings (Strictly validated)
JWT_SECRET = settings.SUPABASE_JWT_SECRET

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Decodes and validates a Supabase JWT. 
    Returns the user data if valid, otherwise raises a 401.
    """
    token = credentials.credentials
    try:
        # Diagnostic Logging for USER context (reveals alg used by Supabase)
        unverified_header = jwt.get_unverified_header(token)
        print(f"JWT HEADER: {unverified_header}")
        
        # Supabase JWTs are signed with HS256 and your project's JWT Secret
        # verify_aud=False because Supabase uses project-specific audiences (e.g. 'authenticated')
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=["HS256"], 
            options={"verify_aud": False}
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials: No sub found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError as e:
        # Detailed error log for diagnosis
        print(f"ERROR: JWT Validation failed. Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
