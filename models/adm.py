from datetime import datetime

import bcrypt
import mysql.connector
from sqlalchemy import Column, Integer, String, DateTime, Date  # Importando Date para 'data_ativacao'
from models.conexao_adm import * #esse script fornece conexao com o banco da tabela adm
import json
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError, IntegrityError
import os
import platform
from sqlalchemy import update


class Adm(Base):
    __tablename__ = 'adm'

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(255), nullable=False)
    nome_academia = Column(String(255), nullable=False)
    cnpj_cpf = Column(String(50), nullable=False)
    telefone = Column(String(50), nullable=True)
    data_cadastro = Column(DateTime)
    status = Column(String(1))
    banco_de_dados = Column(String(255))
    email = Column(String(255))
    usuario = Column(String(255))
    senha = Column(String(255))
    api_link = Column(String(255))
    plano_id = Column(Integer)  # Plano_id está correto como Integer
    data_ativacao = Column(Date)  # data_ativacao deve ser do tipo Date
    status_assinatura = Column(String(20))  # Novo campo para controlar o status da assinatura (ativa, suspensa, etc.)

def busca_dados_login_cliente_json(cpf_cnpj: str):
    db = SessionLocal()
    try:
        resultado = db.query(Adm).filter(Adm.cnpj_cpf == cpf_cnpj).first()
        if resultado:
            data = {
                "id": resultado.id,
                "nome_completo": resultado.nome_completo,
                "nome_academia": resultado.nome_academia,
                "cnpj_cpf": resultado.cnpj_cpf,
                "data_cadastro": resultado.data_cadastro.isoformat() if resultado.data_cadastro else None,
                "status": resultado.status,
                "banco_de_dados": resultado.banco_de_dados,
                "usuario": resultado.usuario,
                "senha": resultado.senha,
                "api_link": resultado.api_link,
                "plano_id": resultado.plano_id,  # Novo campo
                "data_ativacao": resultado.data_ativacao.isoformat() if resultado.data_ativacao else None,  # Novo campo
                "status_assinatura": resultado.status_assinatura  # Novo campo
            }
            return json.dumps(data, indent=4)  # Retorna JSON formatado
        return json.dumps(None)
    finally:
        db.close()

def criar_banco_e_restaurar_dump(
        cnpj_cpf: str,
        dump_file_path: str,
        mysql_user: str,
        mysql_password: str,
        mysql_host: str = MYSQL_HOST,
        mysql_port: int = 3306
):
    """
    Cria um novo banco de dados 'sysfit_cli_<cpf_cnpj>' com a collation utf8_general_ci e restaura a estrutura e dados
    de um arquivo de dump fornecido no novo banco de dados.

    Parâmetros:
    - cnpj_cpf: CPF ou CNPJ para nomear o novo banco.
    - dump_file_path: Caminho do arquivo de dump SQL gerado.
    - mysql_user: Usuário MySQL.
    - mysql_password: Senha do MySQL.
    - mysql_host: Host MySQL.
    - mysql_port: Porta MySQL.
    """

    # Nome do novo banco de dados
    novo_banco = f"sysfit_cli_{cnpj_cpf}"

    # Conectar ao servidor MySQL (sem especificar um banco de dados)
    conn = mysql.connector.connect(
        user=mysql_user,
        password=mysql_password,
        host=mysql_host,
        port=mysql_port
    )

    cursor = conn.cursor()

    # 1. Criar o banco de dados com utf8_general_ci
    try:
        cursor.execute(f"""
            CREATE DATABASE IF NOT EXISTS {novo_banco}
            CHARACTER SET utf8
            COLLATE utf8_general_ci;
        """)
        print(f"Banco {novo_banco} criado com sucesso com utf8_general_ci.")
    except mysql.connector.Error as err:
        print(f"Erro ao criar banco de dados: {err}")
        return

    # Fechar a conexão de criação do banco
    cursor.close()
    conn.close()

    # Conectar novamente, agora com o novo banco
    conn = mysql.connector.connect(
        user=mysql_user,
        password=mysql_password,
        host=mysql_host,
        port=mysql_port,
        database=novo_banco
    )
    cursor = conn.cursor()

    # 2. Restaurar o dump no novo banco
    if not os.path.exists(dump_file_path):
        raise FileNotFoundError(f"O arquivo de dump não foi encontrado: {dump_file_path}")

    try:
        # Tentar abrir o arquivo de dump com codificação 'latin1' (ou cp1252)
        with open(dump_file_path, 'r', encoding='latin1') as dump_file:
            dump_data = dump_file.read()

        # Executar o SQL de dump diretamente no banco
        for statement in dump_data.split(';'):
            if statement.strip():
                cursor.execute(statement)
        conn.commit()
        print(f"Dump restaurado com sucesso no banco {novo_banco}.")
    except mysql.connector.Error as err:
        print(f"Erro ao restaurar o dump: {err}")
        conn.rollback()

    # Fechar a conexão
    cursor.close()
    conn.close()


def criar_banco_e_restaurar_dump_2(
        cnpj_cpf: str,
        dump_file_path: str,
        mysql_user: str,
        mysql_password: str,
        mysql_host: str = MYSQL_HOST,
        mysql_port: int = 3306,
        novo_email: str = None,  # Novo parâmetro para o email
        nova_senha: str = None   # Novo parâmetro para a senha
):
    """
    Cria um novo banco de dados 'sysfit_cli_<cpf_cnpj>' com a collation utf8_general_ci e restaura a estrutura e dados
    de um arquivo de dump fornecido no novo banco de dados.
    A função também substitui o email e a senha no arquivo de dump.

    Parâmetros:
    - cnpj_cpf: CPF ou CNPJ para nomear o novo banco.
    - dump_file_path: Caminho do arquivo de dump SQL gerado.
    - mysql_user: Usuário MySQL.
    - mysql_password: Senha do MySQL.
    - mysql_host: Host MySQL.
    - mysql_port: Porta MySQL.
    - novo_email: Novo email para ser substituído no dump.
    - nova_senha: Nova senha para ser substituída no dump.
    """

    # Nome do novo banco de dados
    novo_banco = f"sysfit_cli_{cnpj_cpf}"

    # Conectar ao servidor MySQL (sem especificar um banco de dados)
    conn = mysql.connector.connect(
        user=mysql_user,
        password=mysql_password,
        host=mysql_host,
        port=mysql_port
    )

    cursor = conn.cursor()

    # 1. Criar o banco de dados com utf8_general_ci
    try:
        cursor.execute(f"""
            CREATE DATABASE IF NOT EXISTS {novo_banco}
            CHARACTER SET utf8
            COLLATE utf8_general_ci;
        """)
        print(f"Banco {novo_banco} criado com sucesso com utf8_general_ci.")
    except mysql.connector.Error as err:
        print(f"Erro ao criar banco de dados: {err}")
        return

    # Fechar a conexão de criação do banco
    cursor.close()
    conn.close()

    # Conectar novamente, agora com o novo banco
    conn = mysql.connector.connect(
        user=mysql_user,
        password=mysql_password,
        host=mysql_host,
        port=mysql_port,
        database=novo_banco
    )
    cursor = conn.cursor()

    # 2. Restaurar o dump no novo banco
    if not os.path.exists(dump_file_path):
        raise FileNotFoundError(f"O arquivo de dump não foi encontrado: {dump_file_path}")

    try:
        # Tentar abrir o arquivo de dump com codificação 'latin1' (ou cp1252)
        with open(dump_file_path, 'r', encoding='latin1') as dump_file:
            dump_data = dump_file.read()

        # Substituir valores no arquivo de dump, se fornecido
        if novo_email:
            dump_data = dump_data.replace("admin@example.com", novo_email)
        if nova_senha:
            dump_data = dump_data.replace("$2b$12$ZR6YSX.aaa", nova_senha)

        # Executar o SQL de dump diretamente no banco
        for statement in dump_data.split(';'):
            if statement.strip():
                cursor.execute(statement)
        conn.commit()
        print(f"Dump restaurado com sucesso no banco {novo_banco}.")
    except mysql.connector.Error as err:
        print(f"Erro ao restaurar o dump: {err}")
        conn.rollback()

    # Fechar a conexão
    cursor.close()
    conn.close()

# Exemplo de uso da função
# criar_banco_e_restaurar_dump(
#     cnpj_cpf="12345678904",
#     dump_file_path="sysfit_cli_template.sql",  # Caminho do arquivo de dump
#     mysql_user="root",
#     mysql_password="",
#     mysql_host="localhost",
#     mysql_port=3306
# )
####################################MANIPULAÇÃO TABELA ADM
def update_adm(cnpj_cpf, campo, valor):
    """
    Atualiza um campo específico de um administrador na tabela `adm`
    baseado no CPF/CNPJ (cnpj_cpf), campo e valor passados.
    """
    db = SessionLocal()
    try:
        campos_validos = ['nome_completo', 'nome_academia', 'cnpj_cpf', 'status', 'banco_de_dados', 'usuario', 'senha', 'api_link', 'plano_id', 'data_ativacao', 'status_assinatura']
        if campo not in campos_validos:
            return {"erro": f"Campo '{campo}' não encontrado na tabela."}

        if campo == 'senha':
            senha_hash = bcrypt.hashpw(valor.encode('utf-8'), bcrypt.gensalt())
            valor = senha_hash.decode('utf-8')

        stmt = update(Adm).where(Adm.cnpj_cpf == cnpj_cpf).values({campo: valor})
        db.execute(stmt)
        db.commit()

        return {"sucesso": f"{campo} atualizado com sucesso."}
    except Exception as e:
        db.rollback()
        return {"erro": str(e)}
    finally:
        db.close()


def busca_dados_adm(cnpj_cpf: str):
    """
    Busca os dados de um administrador na tabela 'adm' baseado no CPF/CNPJ informado.
    """
    db = SessionLocal()
    try:
        resultado = db.query(Adm).filter(Adm.cnpj_cpf == cnpj_cpf).first()
        if resultado:
            dados = {
                "id": resultado.id,
                "nome_completo": resultado.nome_completo,
                "nome_academia": resultado.nome_academia,
                "cnpj_cpf": resultado.cnpj_cpf,
                "data_cadastro": resultado.data_cadastro.isoformat() if resultado.data_cadastro else None,
                "status": resultado.status,
                "banco_de_dados": resultado.banco_de_dados,
                "usuario": resultado.usuario,
                "senha": resultado.senha,
                "api_link": resultado.api_link,
                "plano_id": resultado.plano_id,
                "data_ativacao": resultado.data_ativacao.isoformat() if resultado.data_ativacao else None,
                "status_assinatura": resultado.status_assinatura
            }
            return json.dumps(dados, indent=4)
        return json.dumps(None)
    finally:
        db.close()


def deletar_adm(cnpj_cpf: str):
    """
    Deleta um administrador da tabela 'adm' baseado no CPF/CNPJ informado.
    """
    db = SessionLocal()
    try:
        resultado = db.query(Adm).filter(Adm.cnpj_cpf == cnpj_cpf).first()
        if resultado:
            db.delete(resultado)
            db.commit()
            return {"sucesso": f"Administrador com CPF/CNPJ {cnpj_cpf} deletado com sucesso."}
        return {"erro": "Administrador não encontrado."}
    except Exception as e:
        db.rollback()
        return {"erro": str(e)}
    finally:
        db.close()


def atualizar_status_assinatura(cnpj_cpf: str, novo_status: str):
    """
    Atualiza o status da assinatura de um administrador.
    """
    return update_adm(cnpj_cpf, 'status_assinatura', novo_status)


def verificar_cpf_cnpj(cnpj_cpf: str):
    """
    Verifica se o CPF/CNPJ já está cadastrado na tabela 'adm'.
    """
    db = SessionLocal()
    try:
        resultado = db.query(Adm).filter(Adm.cnpj_cpf == cnpj_cpf).first()
        return resultado is not None
    finally:
        db.close()
def inserir_adm(usuario_data: dict):
    """
    Insere um novo administrador na tabela 'adm' com os dados fornecidos.
    A senha será criptografada antes de ser salva no banco.

    Parâmetros:
    - usuario_data: dicionário contendo os dados do administrador.

    Retorna:
    - Um dicionário com os dados do administrador inserido, incluindo seu ID e outros campos.
    """
    db = SessionLocal()
    try:
        senha_plain = usuario_data.get("senha")
        if not senha_plain:
            raise ValueError("Senha é obrigatória")

        # Criptografar a senha (para o banco de dados do cliente)
        senha_hash = bcrypt.hashpw(senha_plain.encode('utf-8'), bcrypt.gensalt())
        senha_criptografada = senha_hash.decode('utf-8')

        # Definir valores padrão para campos não informados
        usuario_data.setdefault("status", "A")  # Ativo por padrão
        usuario_data.setdefault("status_assinatura", "A")  # Ativo por padrão
        usuario_data.setdefault("plano_id", 0)  # Plano_id pode ser 0 por padrão
        usuario_data.setdefault("data_ativacao", datetime.now().date())  # Data de ativação é a data atual, se não fornecido
        usuario_data.setdefault("banco_de_dados", f"sysfit_cli_{usuario_data['cnpj_cpf']}")  # Banco de dados nomeado com prefixo

        # Preencher o campo 'data_cadastro' com a data e hora atual
        usuario_data["data_cadastro"] = datetime.now()

        # **Aqui fazemos as alterações necessárias para o banco principal:**
        # - Define o 'usuario' como 'root'
        # - Define a 'senha' como uma string vazia para a tabela 'adm' (no ambiente de desenvolvimento)
        usuario_data["usuario"] = MYSQL_USER  # Valor fixo para o campo 'usuario'
        usuario_data["senha"] = MYSQL_PASSWORD  # Senha vazia para o banco principal 'adm'

        # Criar o objeto Adm
        novo_adm = Adm(**usuario_data)

        # Inserir no banco
        db.add(novo_adm)
        db.commit()
        db.refresh(novo_adm)  # Confirma a inserção do novo administrador no banco

        ####### CRIAÇÃO DA BASE DE DADOS DO CLIENTE ###############
        try:
            # Passar a senha criptografada para a criação do banco de dados
            criar_banco_e_restaurar_dump_2(
                cnpj_cpf=usuario_data['cnpj_cpf'],
                dump_file_path=DUMP_FILE_PATH,
                mysql_user=MYSQL_USER,
                mysql_password=MYSQL_PASSWORD,
                mysql_host=MYSQL_HOST,
                mysql_port=MYSQL_PORT,
                novo_email=usuario_data['email'],  # Substituindo o email
                nova_senha=senha_criptografada  # Senha criptografada para o banco do cliente
            )
        except Exception as e:
            db.rollback()  # Caso o banco de dados não seja criado, fazer rollback
            return {"erro": f"Erro ao criar a base de dados: {str(e)}"}
        ####### CRIAÇÃO DA BASE DE DADOS DO CLIENTE ###############

        # Retornar os dados do novo administrador
        return {
            "id": novo_adm.id,
            "nome_completo": novo_adm.nome_completo,
            "nome_academia": novo_adm.nome_academia,
            "cnpj_cpf": novo_adm.cnpj_cpf,
            "status": novo_adm.status,
            "banco_de_dados": novo_adm.banco_de_dados,
            "email": novo_adm.email,
            "usuario": novo_adm.usuario,
            "api_link": novo_adm.api_link,
            "plano_id": novo_adm.plano_id,
            "data_ativacao": novo_adm.data_ativacao.isoformat() if novo_adm.data_ativacao else None,
            "status_assinatura": novo_adm.status_assinatura
        }
    except IntegrityError as e:
        db.rollback()
        msg = str(e.orig).lower()
        # Adiciona logs mais detalhados para o erro de integridade
        print(f"IntegrityError: {e.orig}")
        if "cnpj_cpf" in msg:
            return {"erro": "CNPJ/CPF já em uso.", "campo": "cnpj_cpf"}
        elif "email" in msg:
            return {"erro": "Email já em uso.", "campo": "email"}
        return {"erro": "Erro de integridade no banco de dados.", "campo": "desconhecido"}
    except Exception as e:
        db.rollback()
        print(f"Erro inesperado: {str(e)}")  # Log de erro inesperado
        return {"erro": str(e)}
    finally:
        db.close()

# def inserir_adm(usuario_data: dict):
#     """
#     Insere um novo administrador na tabela 'adm' com os dados fornecidos.
#     A senha será criptografada antes de ser salva no banco.
#
#     Parâmetros:
#     - usuario_data: dicionário contendo os dados do administrador.
#
#     Retorna:
#     - Um dicionário com os dados do administrador inserido, incluindo seu ID e outros campos.
#     """
#     db = SessionLocal()
#     try:
#         senha_plain = usuario_data.get("senha")
#         if not senha_plain:
#             raise ValueError("Senha é obrigatória")
#
#         # Criptografar a senha
#         senha_hash = bcrypt.hashpw(senha_plain.encode('utf-8'), bcrypt.gensalt())
#         senha_criptografada = senha_hash.decode('utf-8')
#
#
#         # Definir valores padrão para campos não informados
#         usuario_data.setdefault("status", "A")  # Ativo por padrão
#         usuario_data.setdefault("status_assinatura", "A")  # Ativo por padrão
#         usuario_data.setdefault("plano_id", 0)  # Plano_id pode ser 0 por padrão
#         usuario_data.setdefault("data_ativacao", datetime.now().date())  # Data de ativação é a data atual, se não fornecido
#         usuario_data.setdefault("banco_de_dados", f"sysfit_cli_{usuario_data['cnpj_cpf']}")  # Banco de dados nomeado com prefixo
#
#         # Preencher o campo 'data_cadastro' com a data e hora atual
#         usuario_data["data_cadastro"] = datetime.now()
#         usuario_data["usuario"] = 'root'
#         usuario_data["senha"] = ''
#
#         # Criar o objeto Adm
#         novo_adm = Adm(**usuario_data)
#
#         # Inserir no banco
#         db.add(novo_adm)
#         db.commit()
#         db.refresh(novo_adm)  # Confirma a inserção do novo administrador no banco
#
#         ####### CRIAÇÃO DA BASE DE DADOS DO CLIENTE ###############
#         try:
#             # Criar o banco de dados usando a função existente
#             criar_banco_e_restaurar_dump_2(
#                 cnpj_cpf=usuario_data['cnpj_cpf'],
#                 dump_file_path=DUMP_FILE_PATH,
#                 mysql_user=MYSQL_USER,
#                 mysql_password=MYSQL_PASSWORD,
#                 mysql_host=MYSQL_HOST,
#                 mysql_port=MYSQL_PORT,
#                 novo_email=usuario_data['email'],  # Substituindo o email
#                 nova_senha=senha_criptografada  # Substituindo a senha (será criptografada)
#             )
#
#         except Exception as e:
#             db.rollback()  # Caso o banco de dados não seja criado, fazer rollback
#             return {"erro": f"Erro ao criar a base de dados: {str(e)}"}
#         ####### CRIAÇÃO DA BASE DE DADOS DO CLIENTE ###############
#
#         # Retornar os dados do novo administrador
#         return {
#             "id": novo_adm.id,
#             "nome_completo": novo_adm.nome_completo,
#             "nome_academia": novo_adm.nome_academia,
#             "cnpj_cpf": novo_adm.cnpj_cpf,
#             "status": novo_adm.status,
#             "banco_de_dados": novo_adm.banco_de_dados,
#             "email": novo_adm.email,
#             "usuario": novo_adm.usuario,
#             "api_link": novo_adm.api_link,
#             "plano_id": novo_adm.plano_id,
#             "data_ativacao": novo_adm.data_ativacao.isoformat() if novo_adm.data_ativacao else None,
#             "status_assinatura": novo_adm.status_assinatura
#         }
#     except IntegrityError as e:
#         db.rollback()
#         msg = str(e.orig).lower()
#         # Adiciona logs mais detalhados para o erro de integridade
#         print(f"IntegrityError: {e.orig}")
#         if "cnpj_cpf" in msg:
#             return {"erro": "CNPJ/CPF já em uso.", "campo": "cnpj_cpf"}
#         elif "email" in msg:
#             return {"erro": "Email já em uso.", "campo": "email"}
#         return {"erro": "Erro de integridade no banco de dados.", "campo": "desconhecido"}
#     except Exception as e:
#         db.rollback()
#         print(f"Erro inesperado: {str(e)}")  # Log de erro inesperado
#         return {"erro": str(e)}
#     finally:
#         db.close()

def update_adm_dinamico(cnpj_cpf: str, campo: str, valor: str):
    """
    Atualiza um campo específico da tabela 'adm' para o CPF/CNPJ informado.

    Parâmetros:
    - cnpj_cpf: CPF ou CNPJ do administrador a ser atualizado.
    - campo: Nome do campo a ser atualizado.
    - valor: Novo valor a ser atribuído ao campo.

    Retorna:
    - Dicionário com o resultado da operação (sucesso ou erro).
    """
    db = SessionLocal()
    try:
        # Verificar se o campo existe na tabela
        campos_validos = ['nome_completo', 'nome_academia', 'cnpj_cpf', 'status', 'banco_de_dados', 'usuario', 'senha', 'api_link', 'plano_id', 'data_ativacao', 'status_assinatura']
        if campo not in campos_validos:
            return {"erro": f"Campo '{campo}' não encontrado na tabela."}

        # Se o campo for senha, criptografá-la
        if campo == 'senha':
            senha_hash = bcrypt.hashpw(valor.encode('utf-8'), bcrypt.gensalt())
            valor = senha_hash.decode('utf-8')

        # Realizar o update no campo específico
        stmt = update(Adm).where(Adm.cnpj_cpf == cnpj_cpf).values({campo: valor})
        db.execute(stmt)
        db.commit()

        return {"sucesso": f"{campo} atualizado com sucesso."}
    except Exception as e:
        db.rollback()
        return {"erro": str(e)}
    finally:
        db.close()
