import uuid
from datetime import date
from sqlalchemy.exc import IntegrityError

import bcrypt
from sqlalchemy.orm import Session
from models.usuarios.usuario import Usuario
from models.conexao_cli import get_engine_cliente, get_session_cliente
from models.adm import *


def get_session(db_name, user, password, host=MYSQL_HOST) -> Session:
    """
    Cria e retorna uma sessão SQLAlchemy para o banco de dados especificado.

    Parâmetros:
    - db_name: nome do banco de dados do cliente.
    - user: usuário do banco.
    - password: senha do usuário.
    - host: servidor do banco (default 'localhost').

    Retorna:
    - sessão SQLAlchemy pronta para uso.
    """
    engine = get_engine_cliente(db_name, user, password, host)
    session = get_session_cliente(engine)
    return session


def get_usuario(db_name, user, password, usr_id, host=MYSQL_HOST):
    """
    Busca um usuário pelo ID na base do cliente.

    Parâmetros:
    - db_name, user, password, host: dados para conexão com o banco do cliente.
    - usr_id: ID do usuário a ser buscado.

    Retorna:
    - dicionário com os dados do usuário, ou None se não encontrado.
    """
    session = get_session(db_name, user, password, host)
    try:
        usuario = session.query(Usuario).filter(Usuario.USR_ID == usr_id).first()
        if usuario:
            return {
                "USR_ID": usuario.USR_ID,
                "USR_NOME": usuario.USR_NOME.strip(),
                "USR_DTA_NASCIMENTO": usuario.USR_DTA_NASCIMENTO.isoformat(),
                "USR_DTA_CADASTRO": usuario.USR_DTA_CADASTRO.isoformat() if usuario.USR_DTA_CADASTRO else None,
                "USR_TIPO": usuario.USR_TIPO.strip(),
                "USR_LOGIN": usuario.USR_LOGIN.strip(),
                "USR_SENHA": usuario.USR_SENHA.strip(),
                "USR_USR_CADASTRO_ID": usuario.USR_USR_CADASTRO_ID,
                "USR_CPF": usuario.USR_CPF.strip(),
                "USR_TELEFONE": usuario.USR_TELEFONE.strip(),
                "USR_EMAIL": usuario.USR_EMAIL.strip(),
                "USR_STATUS": usuario.USR_STATUS.strip(),
            }
        return None
    finally:
        session.close()


def get_usuarios(db_name, user, password, skip=0, limit=100, host=MYSQL_HOST):
    """
    Retorna uma lista de usuários paginada da base do cliente.

    Parâmetros:
    - db_name, user, password, host: dados para conexão.
    - skip: quantos registros pular (offset).
    - limit: limite máximo de registros a retornar.

    Retorna:
    - lista de dicionários com dados dos usuários.
    """
    session = get_session(db_name, user, password, host)
    try:
        usuarios = session.query(Usuario).offset(skip).limit(limit).all()
        return [
            {
                "USR_ID": u.USR_ID,
                "USR_NOME": u.USR_NOME.strip(),
                "USR_DTA_NASCIMENTO": u.USR_DTA_NASCIMENTO.isoformat(),
                "USR_DTA_CADASTRO": u.USR_DTA_CADASTRO.isoformat() if u.USR_DTA_CADASTRO else None,
                "USR_TIPO": u.USR_TIPO.strip(),
                "USR_LOGIN": u.USR_LOGIN.strip(),
                # "USR_SENHA": u.USR_SENHA.strip(),
                "USR_USR_CADASTRO_ID": u.USR_USR_CADASTRO_ID,
                "USR_CPF": u.USR_CPF.strip(),
                "USR_TELEFONE": u.USR_TELEFONE.strip(),
                "USR_EMAIL": u.USR_EMAIL.strip(),
                "USR_STATUS": u.USR_STATUS.strip(),
            }
            for u in usuarios
        ]
    finally:
        session.close()

def create_usuario(db_name, user, password, usuario_data: dict, host=MYSQL_HOST):
    """
    Cria um novo usuário na base do cliente, criptografando a senha e gerando token.

    Parâmetros:
    - db_name, user, password, host: dados para conexão.
    - usuario_data: dicionário com os dados do usuário a criar.

    Retorna:
    - dicionário com os dados do usuário criado, incluindo o token.
    - dicionário com chave 'erro' e 'campo' em caso de duplicidade.
    """
    session = get_session(db_name, user, password, host)
    try:
        senha_plain = usuario_data.get("USR_SENHA")
        if not senha_plain:
            raise ValueError("Senha é obrigatória")

        # Criptografar senha
        senha_hash = bcrypt.hashpw(senha_plain.encode('utf-8'), bcrypt.gensalt())
        usuario_data["USR_SENHA"] = senha_hash.decode('utf-8')

        # Gerar token de autenticação simples (UUID4)
        token = str(uuid.uuid4())

        # Adicionar o token ao dicionário (campo extra, pode adaptar)
        usuario_data["USR_TOKEN"] = token

        usuario = Usuario(**usuario_data)
        session.add(usuario)
        session.commit()
        session.refresh(usuario)

        return {
            "USR_ID": usuario.USR_ID,
            "USR_NOME": usuario.USR_NOME.strip(),
            "USR_DTA_NASCIMENTO": usuario.USR_DTA_NASCIMENTO.isoformat(),
            "USR_DTA_CADASTRO": usuario.USR_DTA_CADASTRO.isoformat() if usuario.USR_DTA_CADASTRO else None,
            "USR_TIPO": usuario.USR_TIPO.strip(),
            "USR_LOGIN": usuario.USR_LOGIN.strip(),
            "USR_SENHA": usuario.USR_SENHA.strip(),
            "USR_TOKEN": token,
            "USR_USR_CADASTRO_ID": usuario.USR_USR_CADASTRO_ID,
            "USR_CPF": usuario.USR_CPF.strip(),
            "USR_TELEFONE": usuario.USR_TELEFONE.strip(),
            "USR_EMAIL": usuario.USR_EMAIL.strip(),
            "USR_STATUS": usuario.USR_STATUS.strip(),
        }

    except IntegrityError as e:
        session.rollback()
        msg = str(e.orig).lower()  # mensagem do banco em minúsculas

        if "usr_login" in msg or "login" in msg:
            campo_erro = "USR_LOGIN"
            mensagem = "Login já em uso."
        elif "usr_cpf" in msg or "cpf" in msg:
            campo_erro = "USR_CPF"
            mensagem = "CPF já em uso."
        elif "usr_email" in msg or "email" in msg:
            campo_erro = "USR_EMAIL"
            mensagem = "Email já em uso."
        else:
            campo_erro = "desconhecido"
            mensagem = "Erro de integridade no banco de dados."

        return {
            "erro": mensagem,
            "campo": campo_erro
        }

    finally:
        session.close()


def update_usuario(db_name, user, password, usr_id, usuario_data: dict, host=MYSQL_HOST):
    """
    Atualiza os dados de um usuário existente na base do cliente.

    Parâmetros:
    - db_name, user, password, host: dados para conexão.
    - usr_id: ID do usuário a ser atualizado.
    - usuario_data: dicionário com os campos a atualizar.

    Retorna:
    - dicionário com os dados atualizados do usuário, ou None se usuário não existir.
    """
    session = get_session(db_name, user, password, host)
    try:
        usuario = session.query(Usuario).filter(Usuario.USR_ID == usr_id).first()
        if not usuario:
            return {"erro": "Usuário não encontrado", "campo": "USR_ID"}

        # Verifica se a senha foi alterada e criptografa
        if 'USR_SENHA' in usuario_data and usuario_data['USR_SENHA']:
            senha_plain = usuario_data['USR_SENHA']
            usuario_data['USR_SENHA'] = bcrypt.hashpw(senha_plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Atualiza os campos do usuário
        for key, value in usuario_data.items():
            if hasattr(usuario, key):
                setattr(usuario, key, value)

        session.commit()
        session.refresh(usuario)

        return {
            "USR_ID": usuario.USR_ID,
            "USR_NOME": usuario.USR_NOME.strip(),
            "USR_DTA_NASCIMENTO": usuario.USR_DTA_NASCIMENTO.isoformat(),
            "USR_DTA_CADASTRO": usuario.USR_DTA_CADASTRO.isoformat() if usuario.USR_DTA_CADASTRO else None,
            "USR_TIPO": usuario.USR_TIPO.strip(),
            "USR_LOGIN": usuario.USR_LOGIN.strip(),
            "USR_SENHA": usuario.USR_SENHA.strip(),  # Se a senha foi alterada, ela estará criptografada
            "USR_USR_CADASTRO_ID": usuario.USR_USR_CADASTRO_ID,
            "USR_CPF": usuario.USR_CPF.strip(),
            "USR_TELEFONE": usuario.USR_TELEFONE.strip(),
            "USR_EMAIL": usuario.USR_EMAIL.strip(),
            "USR_STATUS": usuario.USR_STATUS.strip(),
        }

    except IntegrityError as e:
        session.rollback()
        msg = str(e.orig).lower()  # mensagem do banco em minúsculas

        if "usr_login" in msg or "login" in msg:
            campo_erro = "USR_LOGIN"
            mensagem = "Login já em uso."
        elif "usr_cpf" in msg or "cpf" in msg:
            campo_erro = "USR_CPF"
            mensagem = "CPF já em uso."
        elif "usr_email" in msg or "email" in msg:
            campo_erro = "USR_EMAIL"
            mensagem = "Email já em uso."
        else:
            campo_erro = "desconhecido"
            mensagem = "Erro de integridade no banco de dados."

        return {
            "erro": mensagem,
            "campo": campo_erro
        }

    except Exception as e:
        session.rollback()
        return {
            "erro": "Erro desconhecido ao atualizar o usuário.",
            "detalhes": str(e)
        }

    finally:
        session.close()

def update_usuario_dinamico(db_name, user, password, usr_id, campo_valor: dict, host=MYSQL_HOST):
    """
    Atualiza um campo específico de um usuário existente na base do cliente.

    Parâmetros:
    - db_name, user, password, host: dados para conexão.
    - usr_id: ID do usuário a ser atualizado.
    - campo_valor: dicionário com o campo a ser atualizado e o novo valor.

    Retorna:
    - dicionário com os dados atualizados do usuário, ou None se usuário não existir.
    """
    session = get_session(db_name, user, password, host)
    try:
        # Buscar o usuário pelo ID
        usuario = session.query(Usuario).filter(Usuario.USR_ID == usr_id).first()

        if not usuario:
            return None  # Usuário não encontrado

        # Atualizar o campo e valor fornecido
        for campo, valor in campo_valor.items():
            if hasattr(usuario, campo):  # Verifica se o campo existe na tabela
                setattr(usuario, campo, valor)  # Atribui o novo valor ao campo

        # Commit das alterações no banco de dados
        session.commit()
        session.refresh(usuario)

        # Retornar os dados do usuário atualizado
        return {
            "USR_ID": usuario.USR_ID,
            "USR_NOME": usuario.USR_NOME.strip(),
            "USR_DTA_NASCIMENTO": usuario.USR_DTA_NASCIMENTO.isoformat(),
            "USR_DTA_CADASTRO": usuario.USR_DTA_CADASTRO.isoformat() if usuario.USR_DTA_CADASTRO else None,
            "USR_TIPO": usuario.USR_TIPO.strip(),
            "USR_LOGIN": usuario.USR_LOGIN.strip(),
            "USR_SENHA": usuario.USR_SENHA.strip(),
            "USR_USR_CADASTRO_ID": usuario.USR_USR_CADASTRO_ID,
            "USR_CPF": usuario.USR_CPF.strip(),
            "USR_TELEFONE": usuario.USR_TELEFONE.strip(),
            "USR_EMAIL": usuario.USR_EMAIL.strip(),
            "USR_STATUS": usuario.USR_STATUS.strip(),
        }

    finally:
        session.close()


def delete_usuario(db_name, user, password, usr_id, host=MYSQL_HOST):
    """
    Remove um usuário da base do cliente.

    Parâmetros:
    - db_name, user, password, host: dados para conexão.
    - usr_id: ID do usuário a ser deletado.

    Retorna:
    - True se deletado com sucesso, None se usuário não existir.
    """
    session = get_session(db_name, user, password, host)
    try:
        usuario = session.query(Usuario).filter(Usuario.USR_ID == usr_id).first()
        if not usuario:
            return None
        session.delete(usuario)
        session.commit()
        return True
    finally:
        session.close()

def update_usuario_dinamico(db_name, user, password, usr_id, campos_valores: dict, host=MYSQL_HOST):
    """
    Atualiza campos dinâmicos de um usuário existente na base do cliente.

    Parâmetros:
    - db_name, user, password, host: dados para conexão.
    - usr_id: ID do usuário a ser atualizado.
    - campos_valores: dicionário com pares campo: valor a atualizar.

    Retorna:
    - dicionário com os dados atualizados do usuário, ou None se usuário não existir.
    """
    session = get_session(db_name, user, password, host)
    try:
        usuario = session.query(Usuario).filter(Usuario.USR_ID == usr_id).first()
        if not usuario:
            return None

        for campo, valor in campos_valores.items():
            if hasattr(usuario, campo):
                setattr(usuario, campo, valor)

        session.commit()
        session.refresh(usuario)

        return {
            "USR_ID": usuario.USR_ID,
            "USR_NOME": usuario.USR_NOME.strip(),
            "USR_DTA_NASCIMENTO": usuario.USR_DTA_NASCIMENTO.isoformat(),
            "USR_DTA_CADASTRO": usuario.USR_DTA_CADASTRO.isoformat() if usuario.USR_DTA_CADASTRO else None,
            "USR_TIPO": usuario.USR_TIPO.strip(),
            "USR_LOGIN": usuario.USR_LOGIN.strip(),
            "USR_SENHA": usuario.USR_SENHA.strip(),
            "USR_USR_CADASTRO_ID": usuario.USR_USR_CADASTRO_ID,
            "USR_CPF": usuario.USR_CPF.strip(),
            "USR_TELEFONE": usuario.USR_TELEFONE.strip(),
            "USR_EMAIL": usuario.USR_EMAIL.strip(),
            "USR_STATUS": usuario.USR_STATUS.strip(),
        }
    finally:
        session.close()

def get_usuario_por_token(db_name, user, password, token, host=MYSQL_HOST):
    """
    Busca um usuário pelo token na base do cliente.

    Parâmetros:
    - db_name, user, password, host: dados para conexão com o banco do cliente.
    - token: token do usuário a ser buscado.

    Retorna:
    - dicionário com os dados do usuário se encontrado.
    - dicionário com chave 'erro' caso token inválido.
    """
    session = get_session(db_name, user, password, host)
    try:
        usuario = session.query(Usuario).filter(Usuario.USR_TOKEN == token).first()
        if usuario:
            return {
                "USR_ID": usuario.USR_ID,
                "USR_NOME": usuario.USR_NOME.strip(),
                "USR_DTA_NASCIMENTO": usuario.USR_DTA_NASCIMENTO.isoformat(),
                "USR_DTA_CADASTRO": usuario.USR_DTA_CADASTRO.isoformat() if usuario.USR_DTA_CADASTRO else None,
                "USR_TIPO": usuario.USR_TIPO.strip(),
                "USR_LOGIN": usuario.USR_LOGIN.strip(),
                "USR_USR_CADASTRO_ID": usuario.USR_USR_CADASTRO_ID,
                "USR_TELEFONE": usuario.USR_TELEFONE.strip(),
                "USR_EMAIL": usuario.USR_EMAIL.strip(),
                "USR_STATUS": usuario.USR_STATUS.strip(),
            }
        else:
            return {"erro": "Token inválido"}
    finally:
        session.close()

#####################teste
#
# # # CNPJ do cliente
# cnpj_cpf = "02885690321"
# #
# # # Obtém dados de conexão com o banco do cliente
# dados_cliente_json = busca_dados_login_cliente_json(cnpj_cpf)
# dados_cliente = json.loads(dados_cliente_json)
#
# if dados_cliente:
#     db_name = dados_cliente.get("banco_de_dados")
#     user = dados_cliente.get("usuario")
#     password = dados_cliente.get("senha")
#     host = "localhost"  # ou outro, se aplicável
#
#     # Dados do novo usuário
#     novo_usuario = {
#         "USR_NOME": "Administrador",
#         "USR_DTA_NASCIMENTO": date(1990, 5, 20),  # ou string: "1990-05-20"
#         "USR_TIPO": "ADM",
#         "USR_LOGIN": "Admin",
#         "USR_SENHA": "123",  # será criptografada internamente
#         "USR_USR_CADASTRO_ID": 1,
#         "USR_CPF": "000.000.000-00",
#         "USR_TELEFONE": "(00) 0000000-0000",
#         "USR_EMAIL": "admin@example.com",
#         "USR_STATUS": "A"
#     }
#
#     try:
#         resultado = create_usuario(db_name, user, password, novo_usuario, host)
#         print("Usuário criado com sucesso:")
#         print(json.dumps(resultado, indent=4, ensure_ascii=False))
#     except Exception as e:
#         print(f"Erro ao criar usuário: {e}")
# else:
#     print("Erro: Cliente não encontrado.")