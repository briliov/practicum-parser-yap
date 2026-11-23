from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, declared_attr

Base = declarative_base()


class AbstractBase(Base):
    """Abstract base model."""

    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


class Pep(Base):
    __tablename__ = 'pep'
    id = Column(Integer, primary_key=True)
    pep_number = Column(Integer, unique=True)
    name = Column(String(200))
    status = Column(String(20))


if __name__ == '__main__':
    engine = create_engine('sqlite:///sqlite.db', echo=True)
    session = Session(engine)
    Base.metadata.create_all(engine)
