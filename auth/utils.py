from fastapi import HTTPException, status

from auth.jwt import verify_access_token
from crud.users import UserCrudManager
from schemas.auth import oauth2_token_scheme

UserCrud = UserCrudManager()

async def get_current_user(token = oauth2_token_scheme):
    payload = await verify_access_token(token)
    user_id = int(payload.get("id"))
    user = await UserCrud.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
            headers={"WWW-Authenticate": "Bearer"}
            )
    return user