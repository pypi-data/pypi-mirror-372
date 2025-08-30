import pytest
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.sqlalchemy_pydantic_mapper import ObjectMapper  # импортируем твой класс

engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False, future=True)


class Base(DeclarativeBase):
    pass


class BadDB(Base):
    __tablename__ = "BAD"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)


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

    ObjectMapper.register(UserDB, UserSchema, func=mapper, override_existing=True)
    assert ObjectMapper._mappers[UserDB][UserSchema] is mapper


def test_register_decorator():
    @ObjectMapper.register(UserDB, UserSchema, override_existing=True)
    def mapper2(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name)

    assert ObjectMapper._mappers[UserDB][UserSchema] is mapper2


async def test_register_async():
    async def async_mapper(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name.upper())

    ObjectMapper.register(UserDB, UserSchema, func=async_mapper, override_existing=True)

    user = UserDB()
    user.id = 1
    user.name = "alice"

    result = await ObjectMapper.map(user, UserSchema)
    assert result.name == "ALICE"


async def test_register_async_decorator():
    @ObjectMapper.register(UserDB, UserSchema, override_existing=True)
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
        return StudSchema(id=db.id, name=db.name.upper())

    stud = StudentDB()
    stud.id = 2
    stud.name = "Bob"
    ObjectMapper.register(
        StudentDB, StudSchema, func=stud_to_user, override_existing=True
    )
    result = await ObjectMapper.map(stud, StudSchema)
    assert result.id == 2
    assert result.name == "BOB"


async def test_map_many_fallback():
    users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]
    results = await ObjectMapper.map_many(users, UserSchema)
    assert len(results) == 2
    assert results[0].name == "Alice"
    assert results[1].name == "Bob"


async def test_map_many_no_func():
    ObjectMapper.clear()
    ObjectMapper.register(UserDB, UserSchema, override_existing=True)
    users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]
    results = await ObjectMapper.map_many(users, UserSchema)
    assert len(results) == 2
    assert results[0].name == "Alice"
    assert results[1].name == "Bob"


async def test_map_many_with_sync_mapper():
    def mapper(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name.upper())

    ObjectMapper.register(UserDB, UserSchema, func=mapper, override_existing=True)

    users = [UserDB(id=1, name="alice"), UserDB(id=2, name="bob")]
    results = await ObjectMapper.map_many(users, UserSchema)
    assert results[0].name == "ALICE"
    assert results[1].name == "BOB"


async def test_map_many_with_async_mapper():
    async def async_mapper(db: UserDB) -> UserSchema:
        return UserSchema(id=db.id, name=db.name.lower())

    ObjectMapper.register(UserDB, UserSchema, func=async_mapper, override_existing=True)

    users = [UserDB(id=1, name="ALICE"), UserDB(id=2, name="BOB")]
    results = await ObjectMapper.map_many(users, UserSchema)
    assert results[0].name == "alice"
    assert results[1].name == "bob"


async def test_map_many_with_func_kwargs():
    async def mapper_with_session(user: UserDB, session: str) -> UserSchema:
        return UserSchema(id=user.id, name=f"{user.name}-{session}")

    ObjectMapper.register(
        UserDB, UserSchema, func=mapper_with_session, override_existing=True
    )

    users = [UserDB(id=1, name="Alice"), UserDB(id=2, name="Bob")]
    results = await ObjectMapper.map_many(users, UserSchema, session="X")
    assert results[0].name == "Alice-X"
    assert results[1].name == "Bob-X"


async def test_map_many_empty_sequence():
    results = await ObjectMapper.map_many([], UserSchema)
    assert results == []


async def test_unregister():
    ObjectMapper.clear()
    ObjectMapper.register(UserDB, UserSchema, override_existing=True)
    print(ObjectMapper._mappers)
    assert UserSchema in ObjectMapper._mappers[UserDB]
    ObjectMapper.unregister(UserDB, UserSchema)
    assert ObjectMapper._mappers.get(UserDB) is None


async def test_unregister_bad_to_class():
    ObjectMapper.register(UserDB, UserSchema, override_existing=True)
    print(ObjectMapper._mappers)
    assert UserSchema in ObjectMapper._mappers[UserDB]
    with pytest.raises(KeyError):
        ObjectMapper.unregister(UserDB, BadSchema)


async def test_unregister_bad_from_class():
    ObjectMapper.register(UserDB, UserSchema, override_existing=True)
    print(ObjectMapper._mappers)
    assert UserSchema in ObjectMapper._mappers[UserDB]
    with pytest.raises(KeyError):
        ObjectMapper.unregister(BadDB, UserSchema)


async def test_unregister_not_removes_from_class_when_empty():
    ObjectMapper.clear()
    ObjectMapper.register(UserDB, UserSchema)
    ObjectMapper.register(UserDB, StudSchema)
    assert UserDB in ObjectMapper._mappers
    assert UserSchema in ObjectMapper._mappers[UserDB]

    ObjectMapper.unregister(UserDB, UserSchema)

    assert UserDB in ObjectMapper._mappers


async def test_clear():
    ObjectMapper.clear()
    ObjectMapper.register(
        UserDB,
        UserSchema,
        func=lambda x: UserSchema(id=1, name="1"),
        override_existing=True,
    )
    assert UserDB in ObjectMapper._mappers
    assert UserSchema in ObjectMapper._mappers[UserDB]
    ObjectMapper.clear()
    assert ObjectMapper._mappers == {}


def test_missing_from_attributes():
    with pytest.raises(ValueError):
        ObjectMapper.register(UserDB, BadSchema, override_existing=True)


def test_already_registered():
    ObjectMapper.register(
        UserDB,
        UserSchema,
        func=lambda x: UserSchema(id=1, name="1"),
        override_existing=True,
    )
    with pytest.raises(KeyError):
        ObjectMapper.register(UserDB, UserSchema)


def test_list_mappers_empty():
    ObjectMapper._mappers = {}
    result = ObjectMapper.list_mappers()
    assert result == []


def test_list_mappers_with_data():
    class FromA: ...

    class FromB: ...

    class ToX: ...

    class ToY: ...

    ObjectMapper._mappers = {
        FromA: {ToX: None},
        FromB: {ToY: None},
    }

    assert sorted(
        ObjectMapper.list_mappers(), key=lambda x: (x[0].__name__, x[1].__name__)
    ) == sorted(
        [(FromA, ToX), (FromB, ToY)], key=lambda x: (x[0].__name__, x[1].__name__)
    )


def test_wrong_types():
    class NotABase:
        pass

    with pytest.raises(TypeError):
        ObjectMapper.register(NotABase, UserSchema)

    with pytest.raises(TypeError):
        ObjectMapper.register(UserDB, NotABase)


def test_create_instance_from_mapper():
    with pytest.raises(TypeError):
        ObjectMapper()
