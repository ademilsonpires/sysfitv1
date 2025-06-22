import jwt
import bcrypt
import json
from models.adm import busca_dados_login_cliente_json
from models.conexao_cli import get_engine_cliente, get_session_cliente
from models.usuarios.usuario import Usuario
import mysql.connector


SECRET_KEY = "0aA38Lfb5u8AzqNa0btUx0j1"
ALGORITHM = "HS256"

def gerar_token(usuario_login: str) -> str:
    """
    Gera um JWT com base no login do usuário.

    Parâmetros:
    - usuario_login: string representando o campo USR_LOGIN.

    Retorna:
    - token JWT como string.
    """
    payload = {
        "sub": usuario_login
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token



def autenticar_usuario(cnpj_cpf, login, senha, host="localhost"):
    dados_cliente = json.loads(busca_dados_login_cliente_json(cnpj_cpf))
    if not dados_cliente:
        return {"erro": "Cliente não encontrado"}

    db_name = dados_cliente.get("banco_de_dados")
    user = dados_cliente.get("usuario")
    password = dados_cliente.get("senha")

    session = get_session_cliente(get_engine_cliente(db_name, user, password, host))
    try:
        usuario = session.query(Usuario).filter(Usuario.USR_LOGIN == login).first()
        if not usuario or not bcrypt.checkpw(senha.encode('utf-8'), usuario.USR_SENHA.encode('utf-8')):
            return {"erro": "Usuário ou senha inválida"}

        # Gera token caso não exista
        if not usuario.USR_TOKEN:
            token = gerar_token(usuario.USR_LOGIN)
            usuario.USR_TOKEN = token
            session.commit()
        else:
            token = usuario.USR_TOKEN

        return {
            "USR_ID": usuario.USR_ID,
            "USR_NOME": usuario.USR_NOME.strip(),
            "USR_DTA_NASCIMENTO": usuario.USR_DTA_NASCIMENTO.isoformat(),
            "USR_DTA_CADASTRO": usuario.USR_DTA_CADASTRO.isoformat() if usuario.USR_DTA_CADASTRO else None,
            "USR_TIPO": usuario.USR_TIPO.strip(),
            "USR_LOGIN": usuario.USR_LOGIN.strip(),
            "USR_TOKEN": token,
            "USR_USR_CADASTRO_ID": usuario.USR_USR_CADASTRO_ID,
            "USR_CPF": usuario.USR_CPF.strip(),
            "USR_TELEFONE": usuario.USR_TELEFONE.strip(),
            "USR_EMAIL": usuario.USR_EMAIL.strip(),
            "USR_STATUS": usuario.USR_STATUS.strip()
        }
    finally:
        session.close()

#####################teste

#print(autenticar_usuario('02885690329', 'denisfit@gmail.com', '123', host="localhost"))
# print(json.loads(busca_dados_login_cliente_json('02885690329')))