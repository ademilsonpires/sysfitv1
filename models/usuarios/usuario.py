from sqlalchemy import Column, Integer, String, Date, DateTime, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'

    USR_ID = Column(Integer, primary_key=True, index=True)
    USR_NOME = Column(CHAR(50), nullable=False)
    USR_DTA_NASCIMENTO = Column(Date, nullable=False)
    USR_DTA_CADASTRO = Column(DateTime, server_default=func.current_timestamp())
    USR_TIPO = Column(CHAR(20), nullable=False)
    USR_LOGIN = Column(CHAR(20), nullable=False)
    USR_SENHA = Column(CHAR(255), nullable=False)
    USR_TOKEN = Column(CHAR(255), nullable=False)
    USR_USR_CADASTRO_ID = Column(Integer, nullable=False)
    USR_CPF = Column(CHAR(50), nullable=False)
    USR_TELEFONE = Column(CHAR(50), nullable=False)
    USR_EMAIL = Column(CHAR(255), nullable=False)
    USR_STATUS = Column(CHAR(1), nullable=False)
