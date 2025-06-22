from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_engine_cliente(db_name: str, user: str, password: str, host: str = "localhost"):
    """
    Cria e retorna uma engine SQLAlchemy para a base de dados do cliente.
    """
    DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}/{db_name}"
    engine = create_engine(DATABASE_URL, echo=False)
    return engine

def get_session_cliente(engine):
    """
    Cria e retorna uma sessão SQLAlchemy usando a engine fornecida.
    """
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
