from fastapi import APIRouter, HTTPException, status
from auth.jwt import create_refresh_token, create_token_pair, verify_refresh_token
from schemas.auth import RefreshRequest, Token, login_form_schema, oauth2_token_scheme

router = APIRouter(
    tags = ["auth"],
    prefix="/auth"
)

@router.post("/login", response_model=Token)
async def login(form_data: login_form_schema):
    """
    Login with the following information:

    - **username**
    - **password**

    """
    return await create_token_pair({
        "username": form_data.username,
        "username": form_data.username
    })

@router.post("/refresh", response_model=Token)
async def refresh(refresh_data: RefreshRequest):
    """
    Refresh token with the following information:

    - **token** in `Authorization` header

    """
    payload: dict = await verify_refresh_token(refresh_data.refresh_token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    username: str = payload.get["user"]
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token ( No `username` in payload )",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return await create_token_pair({
        "username": username,
        "username": username
    })