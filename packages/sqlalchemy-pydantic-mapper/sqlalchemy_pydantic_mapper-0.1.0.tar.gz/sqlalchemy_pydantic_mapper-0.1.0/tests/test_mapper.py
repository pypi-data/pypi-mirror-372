import pytest
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src import ObjectMapper  # импортируем твой класс

engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)


class Base(DeclarativeBase):
    pass


class UserDB(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)


class StudentDB(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class StudSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class BadSchema(BaseModel):
    id: int
    name: str


def test_register_direct():
    def mapper(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name)

    ObjectMapper.register(UserDB, UserSchema, func=mapper)
    assert ObjectMapper._mappers[UserDB][UserSchema] is mapper


def test_register_decorator():
    @ObjectMapper.register(UserDB, UserSchema)
    def mapper2(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name)

    assert ObjectMapper._mappers[UserDB][UserSchema] is mapper2


async def test_register_async():
    async def async_mapper(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name.upper())

    ObjectMapper.register(UserDB, UserSchema, func=async_mapper)

    user = UserDB()
    user.id = 1
    user.name = "alice"

    result = await ObjectMapper.map(user, UserSchema)
    assert result.name == "ALICE"


async def test_register_async_decorator():
    @ObjectMapper.register(UserDB, UserSchema)
    async def mapper3(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name)

    assert ObjectMapper._mappers[UserDB][UserSchema] is mapper3


async def test_auto_mapping():
    stud = StudentDB()
    stud.id = 2
    stud.name = "Bob"

    result = await ObjectMapper.map(stud, UserSchema)
    assert result.id == 2
    assert result.name == "Bob"


async def test_manual_mapping():
    def stud_to_user(db: UserDB) -> StudSchema:
        return StudSchema(id=db.id, name=db.name)

    stud = StudentDB()
    stud.id = 2
    stud.name = "Bob"
    ObjectMapper.register(StudentDB, StudSchema, func=stud_to_user)
    result = await ObjectMapper.map(stud, StudSchema)
    assert result.id == 2
    assert result.name == "Bob"


def test_missing_from_attributes():
    with pytest.raises(ValueError):
        ObjectMapper.register(UserDB, BadSchema)


def test_wrong_types():
    class NotABase:
        pass

    with pytest.raises(TypeError):
        ObjectMapper.register(NotABase, UserSchema)

    with pytest.raises(TypeError):
        ObjectMapper.register(UserDB, NotABase)
