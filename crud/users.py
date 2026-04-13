from sqlalchemy import select , update , delete
from sqlalchemy.ext.asyncio import AsyncSession

from auth.passwd import get_password_hash
from database.generic import crud_class_decorator
from database.redis_cache import generic_cache_get, generic_cache_update, generic_cache_delete, generic_pagenation_cache_get
from models.users import User as UserModel 
from schemas import users as UserSchema

@crud_class_decorator
class UserCrudManager:

    @generic_pagenation_cache_get(prefix="user", cls=UserSchema.UserRead)
    async def get_users(self, keyword:str = None, last:int = 0, limit:int = 50, db_session: AsyncSession = None):
        stmt = select(UserModel.name, UserModel.id, UserModel.email, UserModel.avatar)

        if keyword:
            stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
        stmt = stmt.offset(last).limit(limit)

        result = await db_session.execute(stmt)
        users = result.all()

        return users

    @generic_cache_get(prefix="user", key="email", cls=UserSchema.UserRead)
    async def get_user_by_email(self, email: str, db_session: AsyncSession = None) -> UserSchema.UserRead:
        stmt = select(UserModel.name, UserModel.id, UserModel.email, UserModel.avatar).where(UserModel.email == email)
        user = (await db_session.execute(stmt)).first()
        if user:
            return UserSchema.UserRead(**user._asdict())
        return None
    
    @generic_cache_get(prefix="user", key="user_id", cls=UserSchema.UserInfor)
    async def get_user_infor_by_id(self,user_id: int,db_session:AsyncSession) -> UserSchema.UserInfor:
        stmt = select(UserModel.name, UserModel.id, UserModel.birthday, UserModel.age, UserModel.avatar).where(UserModel.id == user_id)
        user = (await db_session.execute(stmt)).first()
        if user:
            return UserSchema.UserInfor(**user._asdict())
            
        return None
    
    @generic_cache_get(prefix="user", key="user_id", cls=UserSchema.UserRead)
    async def get_user_by_id(self, user_id:str, db_session: AsyncSession = None) -> UserSchema.UserRead:
        stmt = select(UserModel.name, UserModel.id, UserModel.email, UserModel.avatar).where(UserModel.id == user_id)
        user = (await db_session.execute(stmt)).first()
        if user:
            return UserSchema.UserRead(**user._asdict())
        return None

    @generic_cache_get(prefix="user", key="email", cls=UserSchema.UserId)
    async def get_user_id_by_email(self, email: str, db_session: AsyncSession = None) -> UserSchema.UserId:
        stmt = select(UserModel.id).where(UserModel.email == email)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return UserSchema.UserId(id=user.id)
        return None
    
    @generic_cache_get(prefix="user", key="user_id", cls=UserSchema.UserId)
    async def get_user_id_by_id(self, user_id: int, db_session: AsyncSession = None) -> UserSchema.UserId:
        stmt = select(UserModel.id).where(UserModel.id == user_id)
        result = await db_session.execute(stmt)
        return result.scalar()

    async def create_user(self, newUser: UserSchema.UserCreate, db_session: AsyncSession = None):
        user = UserModel(
            name=newUser.name,
            password=get_password_hash(newUser.password),
            age=newUser.age,
            birthday=newUser.birthday,
            email=newUser.email,
            avatar=newUser.avatar,
        )
        db_session.add(user)
        await db_session.commit()

        return user
    
    @generic_cache_update(prefix="user", key="user_id", update_with_page=True, pagenation_key="id")
    async def update_user(self, user_id: int, newUser: UserSchema.UserUpdate, db_session: AsyncSession = None):
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            name = newUser.name,
            age = newUser.age,
            birthday = newUser.birthday,
            avatar = newUser.avatar
        )
        await db_session.execute(stmt)
        await db_session.commit()

        return newUser

    @generic_cache_update(prefix="user", key="user_id")
    async def update_user_password(self, user_id: int, newUser: UserSchema.UserUpdatePassword, db_session: AsyncSession = None):
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            password = get_password_hash(newUser.password)
        )
        await db_session.execute(stmt)
        await db_session.commit()

        return

    async def delete_users(self, user_id: int, db_session: AsyncSession = None):
        stmt = delete(UserModel).where(UserModel.id == user_id)
        await db_session.execute(stmt)
        await db_session.commit()

        return
    
    @generic_cache_get(prefix="user", key="email", cls=UserSchema.UserInDB)
    async def get_user_in_db(self, email: str, db_session: AsyncSession = None) -> UserSchema.UserInDB:
        stmt = select(UserModel.id, UserModel.name, UserModel.password).where(UserModel.email == email)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return UserSchema.UserInDB(**user._asdict())
        return None
