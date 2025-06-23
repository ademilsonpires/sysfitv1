from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel, Field
from models.login.login import autenticar_usuario  # ajuste import conforme projeto
from models.usuarios.crud_usuario import *
from models.adm import criar_banco_e_restaurar_dump
from models.config_adm import *


app = FastAPI(
    title="API SysFitness Gestão de Academias",
    description="API para integração do sistema SysFitness.",
    version="0.1.0",
    openapi_url="/openapi.json"
)


origins = [
    "http://127.0.0.1",
    "http://localhost",
    # Se quiser liberar todos, pode usar "*"
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Domínios liberados para requisição
    allow_credentials=True,
    allow_methods=["*"],            # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"],            # Permite todos os headers
)
#define a classe basemodel para login
class LoginRequest(BaseModel):
    cnpj_cpf: str
    login: str
    senha: str
#endpoint login
@app.post(
    "/login-painel",
    tags=["Autenticação"],
    summary="Autenticação de usuário",
    description="Endpoint para autenticar usuários usando CNPJ/CPF, login e senha."
)
def login(request: LoginRequest):
    resultado = autenticar_usuario(request.cnpj_cpf, request.login, request.senha)
    if "erro" in resultado:
        raise HTTPException(status_code=401, detail=resultado["erro"])
    return resultado

#define a classe basemodel usuario
class UsuarioCreateRequest(BaseModel):
    cnpj_cpf: str = Field(..., description="CNPJ ou CPF do cliente")
    USR_NOME: str
    USR_DTA_NASCIMENTO: str  # string no formato 'YYYY-MM-DD'
    USR_TIPO: str
    USR_LOGIN: str
    USR_SENHA: str
    USR_USR_CADASTRO_ID: int
    USR_CPF: str
    USR_TELEFONE: str
    USR_EMAIL: str
    USR_STATUS: str

#endpoint criar usuario

@app.post("/cadastrar-usuarios", tags=["Pessoas"], summary="Cria um novo usuário")
def criar_usuario(request: UsuarioCreateRequest, token: str = Header(...)):
    if not token:
        raise HTTPException(status_code=401, detail="Token não informado no header")

    # Obter dados do cliente (conexão)
    dados_cliente_json = busca_dados_login_cliente_json(request.cnpj_cpf)
    if not dados_cliente_json:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    dados_cliente = json.loads(dados_cliente_json)
    db_name = dados_cliente.get("banco_de_dados")
    user = dados_cliente.get("usuario")
    password = dados_cliente.get("senha")
    host = "localhost"  # ajustar se necessário

    # Validar token direto
    usuario_autenticado = get_usuario_por_token(db_name, user, password, token, host)
    if not usuario_autenticado or "erro" in usuario_autenticado:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Verificar se é ADM ou MASTER
    if usuario_autenticado["USR_TIPO"] not in ("ADM", "MASTER"):
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    usuario_data = request.dict()
    del usuario_data["cnpj_cpf"]  # remove cnpj_cpf para passar só os dados do usuário

    try:
        novo_usuario = create_usuario(db_name, user, password, usuario_data, host)
        return novo_usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar usuário: {str(e)}")


############### Listagem de Usuarios ######################

@app.get("/lista-todos-usuarios", tags=["Pessoas"], summary="Lista todos os usuários")
def lista_usuarios(cpf_cnpj: str, token: str = Header(...)):
    # Verificar se o token foi fornecido
    if not token:
        raise HTTPException(status_code=401, detail="Token não informado no header")

    # Obter dados do cliente (conexão)
    dados_cliente_json = busca_dados_login_cliente_json(cpf_cnpj)
    if not dados_cliente_json:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    dados_cliente = json.loads(dados_cliente_json)
    db_name = dados_cliente.get("banco_de_dados")
    user = dados_cliente.get("usuario")
    password = dados_cliente.get("senha")
    host = "localhost"  # ajustar se necessário

    # Validar token direto
    usuario_autenticado = get_usuario_por_token(db_name, user, password, token, host)
    if not usuario_autenticado or "erro" in usuario_autenticado:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Verificar se é ADM ou MASTER
    if usuario_autenticado["USR_TIPO"] not in ("ADM", "MASTER"):
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Chamar a função que retorna a lista de usuários
    try:
        usuarios = get_usuarios(db_name, user, password)
        return {"usuarios": usuarios}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")

@app.get("/lista-usuario-id", tags=["Pessoas"], summary="Lista usuário por id")
def lista_usuario_id(cpf_cnpj: str,usr_id: int, token: str = Header(...)):
    # Verificar se o token foi fornecido
    if not token:
        raise HTTPException(status_code=401, detail="Token não informado no header")

    # Obter dados do cliente (conexão)
    dados_cliente_json = busca_dados_login_cliente_json(cpf_cnpj)
    if not dados_cliente_json:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    dados_cliente = json.loads(dados_cliente_json)
    db_name = dados_cliente.get("banco_de_dados")
    user = dados_cliente.get("usuario")
    password = dados_cliente.get("senha")
    host = "localhost"  # ajustar se necessário

    # Validar token direto
    usuario_autenticado = get_usuario_por_token(db_name, user, password, token, host)
    if not usuario_autenticado or "erro" in usuario_autenticado:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Verificar se é ADM ou MASTER
    if usuario_autenticado["USR_TIPO"] not in ("ADM", "MASTER"):
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Chamar a função que retorna a lista de usuários
    try:
        usuarios = get_usuario(db_name, user, password, usr_id)
        return {"usuarios": usuarios}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar usuários: {str(e)}")


############### /Listagem de Usuarios #####################
############### update de Usuarios #####################
# Definir o schema para receber os dados no corpo da requisição
class UpdateUsuarioRequest(BaseModel):
    campo: str  # Campo que será atualizado
    valor: str  # Novo valor para o campo

@app.put("/atualizar-usuario/{usr_id}", tags=["Pessoas"], summary="Atualiza um campo específico de um usuário")
def update_usuario_dinam(cpf_cnpj: str, token: str, usr_id: int, request: UpdateUsuarioRequest):
    # Verificar se o token foi fornecido
    if not token:
        raise HTTPException(status_code=401, detail="Token não informado no header")

    # Obter dados do cliente (conexão)
    dados_cliente_json = busca_dados_login_cliente_json(cpf_cnpj)
    if not dados_cliente_json:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    dados_cliente = json.loads(dados_cliente_json)
    db_name = dados_cliente.get("banco_de_dados")
    user = dados_cliente.get("usuario")
    password = dados_cliente.get("senha")
    host = "localhost"  # ajustar se necessário

    # Validar token direto
    usuario_autenticado = get_usuario_por_token(db_name, user, password, token, host)
    if not usuario_autenticado or "erro" in usuario_autenticado:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Verificar se é ADM ou MASTER
    if usuario_autenticado["USR_TIPO"] not in ("ADM", "MASTER"):
        raise HTTPException(status_code=403, detail="Usuário não autorizado")
    if usuario_autenticado["USR_STATUS"] =="D":
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Verificar se o campo a ser atualizado é válido
    valid_fields = ["USR_NOME", "USR_TIPO", "USR_EMAIL", "USR_TELEFONE", "USR_CPF", "USR_STATUS"]
    if request.campo not in valid_fields:
        raise HTTPException(status_code=400, detail="Campo inválido para atualização")

    # Atualizar o usuário com o campo e valor fornecido
    try:
        campo_valor = {request.campo: request.valor}  # Passa como um dicionário
        updated_usuario = update_usuario_dinamico(db_name, user, password, usr_id, campo_valor, host)

        if updated_usuario:
            return {"mensagem": "Usuário atualizado com sucesso", "dados": updated_usuario}
        else:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")


class UpdateUsuarioRequestCadastroCompleto(BaseModel):
    USR_NOME: str
    USR_DTA_NASCIMENTO: str
    USR_TIPO: str
    USR_LOGIN: str
    USR_SENHA: str
    USR_CPF: str
    USR_TELEFONE: str
    USR_EMAIL: str
    USR_STATUS: str

@app.put("/atualizar-usuario-completo/{usr_id}", tags=["Pessoas"], summary="Atualiza todos os dados de um usuário")
async def update_usuario_cadastro_completo(cpf_cnpj: str, usr_id: int, usuario_data: UpdateUsuarioRequestCadastroCompleto,token: str = Header(...)):
    # Verificar se o token foi fornecido
    if not token:
        raise HTTPException(status_code=401, detail="Token não informado no header")

    # Obter dados do cliente (conexão)
    dados_cliente_json = busca_dados_login_cliente_json(cpf_cnpj)
    if not dados_cliente_json:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    dados_cliente = json.loads(dados_cliente_json)
    db_name = dados_cliente.get("banco_de_dados")
    user = dados_cliente.get("usuario")
    password = dados_cliente.get("senha")
    host = "localhost"  # ajustar se necessário

    # Validar token direto
    usuario_autenticado = get_usuario_por_token(db_name, user, password, token, host)
    if not usuario_autenticado or "erro" in usuario_autenticado:
        raise HTTPException(status_code=401, detail="Token inválido")

    # Verificar se é ADM ou MASTER
    if usuario_autenticado["USR_TIPO"] not in ("ADM", "MASTER"):
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Atualizar os dados do usuário com a função update_usuario
    try:
        # Passa os dados do formulário para a função de update
        updated_usuario = update_usuario(db_name, user, password, usr_id, usuario_data.dict(), host)

        if updated_usuario:
            return {"mensagem": "Usuário atualizado com sucesso", "dados": updated_usuario}
        else:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")
############### /update de Usuarios #####################

@app.post("/criar_banco/", tags=["Credenciamento"], summary="Cria um novo banco de dados", include_in_schema=False)
async def criar_banco(cpf_cnpj: str):
    try:
        criar_banco_e_restaurar_dump(
            cnpj_cpf=cpf_cnpj,
            dump_file_path=DUMP_FILE_PATH,
            mysql_user=MYSQL_USER,
            mysql_password=MYSQL_PASSWORD,
            mysql_host=MYSQL_HOST,
            mysql_port=MYSQL_PORT
        )
        return JSONResponse(content={"mensagem": f"Banco para {cpf_cnpj} criado com sucesso."})
    except Exception as e:
        # Pode ser melhorado para erros específicos
        raise HTTPException(status_code=500, detail=str(e))

#####Inserir Registro Cadastre-se#####################

# Classe BaseModel para receber os dados do administrador
class AdmCreateRequest(BaseModel):
    nome_completo: str
    nome_academia: str
    cnpj_cpf: str = Field(..., description="CNPJ ou CPF do cliente (sem máscara)")
    email: str
    telefone: str
    senha: str


# Endpoint para cadastro de administrador
@app.post("/cadastrar-administrador", tags=["Cadastre-se"], summary="Cria novo cadastro de cliente", include_in_schema=False)
async def cadastrar_administrador(request: AdmCreateRequest):
    try:
        # Preparar os dados para inserção
        usuario_data = request.dict()

        # Chama a função que insere o novo administrador
        resultado = inserir_adm(usuario_data)

        if "erro" in resultado:
            raise HTTPException(status_code=400, detail=resultado["erro"])

        return JSONResponse(content={"mensagem": "Administrador cadastrado com sucesso", "dados": resultado}, status_code=201)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar administrador: {str(e)}")