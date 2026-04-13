from fastapi import APIRouter, HTTPException, status
from backend.auth.jwt import create_refresh_token, create_token_pair, verify_refresh_token
from backend.auth.passwd import verify_password, get_password_hash
from backend.crud.users import UserCrudManager
from backend.schemas.auth import RefreshRequest, Token, login_form_schema, oauth2_token_scheme
from backend.schemas.users import UserInDB

router = APIRouter(
    tags = ["auth"],
    prefix = "/api/auth"
)

UserCrud = UserCrudManager()

exception_invalid_token = HTTPException(
    status_code=401,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"}
)

exception_invalid_login = HTTPException(
    status_code=401,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"}
)

@router.post("/login", response_model=Token)
async def login(form_data: login_form_schema):
    """
    Login with the following information:

    - **username**
    - **password**

    """
    user_in_db: UserInDB = await UserCrud.get_user_in_db(email=form_data.username)

    if not user_in_db or \
        not verify_password(form_data.password, user_in_db.password):
        raise exception_invalid_login

    return await create_token_pair(
        {"username": user_in_db.name, "id": user_in_db.id},
        {"username": user_in_db.name, "id": user_in_db.id}
    )

@router.post("/refresh", response_model=Token)
async def refresh(refresh_data: RefreshRequest):
    """
    Refresh token with the following information:

    - **token** in `Authorization` header

    """
    payload: dict = await verify_refresh_token(refresh_data.refresh_token)
    
    username: str = payload.get("username")
    u_id: int = payload.get("id")
    if not username or not u_id:
        raise exception_invalid_token

    return await create_token_pair(
        {"username": username, "id": u_id},
        {"username": username, "id": u_id}
    )