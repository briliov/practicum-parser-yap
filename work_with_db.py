from typing import Any

from sqlalchemy import (
    Integer,
    String,
    create_engine,
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    declared_attr,
    mapped_column,
)


class Base(DeclarativeBase):
    """Abstract base model with common fields."""

    @declared_attr.directive
    def __tablename__(cls: Any) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Pep(Base):
    """Model for PEP documents."""

    pep_number: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20))

    def __repr__(self) -> str:
        return f'PEP {self.pep_number} {self.name}'


if __name__ == '__main__':
    engine = create_engine('sqlite:///sqlite.db', echo=False)
    session = Session(engine)

    # 1. CREATE (Вставка)
    stmt = insert(Pep).values(pep_number=42, name='New PEP', status='Draft')
    session.execute(stmt)
    session.commit()

    # 2. READ (Чтение)
    stmt = select(Pep).where(Pep.status == 'Active')
    # .scalars() разворачивает кортежи Row в чистые объекты Pep
    peps = session.execute(stmt).scalars().all()

    # 3. UPDATE (Обновление)
    stmt = update(Pep).where(Pep.pep_number == 42).values(status='Active')
    session.execute(stmt)
    session.commit()

    # 4. DELETE (Удаление)
    stmt = delete(Pep).where(Pep.pep_number == 42)
    session.execute(stmt)
    session.commit()
