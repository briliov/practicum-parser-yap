from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Pep(Base):
    __tablename__ = 'pep'
    id = Column(Integer, primary_key=True)
    pep_number = Column(Integer, unique=True)
    name = Column(String(200))
    status = Column(String(20))


if __name__ == '__main__':
    engine = create_engine('sqlite:///sqlite.db', echo=True)
    Base.metadata.create_all(engine)
