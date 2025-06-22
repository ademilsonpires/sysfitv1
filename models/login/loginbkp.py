import json
from sqlalchemy import text
from models.adm import busca_dados_login_cliente_json
from models.conexao_cli import get_engine_cliente, get_session_cliente

# Chamar a função que retorna JSON string
json_str = busca_dados_login_cliente_json(36366290000139)
print(busca_dados_login_cliente_json(36366290000139))# teste para exibir dados
# Converter JSON string para dicionário Python
dados_cliente = json.loads(json_str)

if dados_cliente:
    db_name = dados_cliente.get("banco_de_dados")
    user = dados_cliente.get("usuario")
    password = dados_cliente.get("senha")
    host = "localhost"  # Pode alterar se precisar

    # Criar engine e sessão para base do cliente
    engine_cliente = get_engine_cliente(db_name, user, password, host)
    sessao_cliente = get_session_cliente(engine_cliente)

    # Agora pode usar sessao_cliente para consultas na base específica do cliente

else:
    print("Cliente não encontrado.")

def executar_sql_teste(db_name, user, password, host="localhost", sql="SELECT * FROM planos"):
    # Criar engine e sessão com os parâmetros fornecidos
    engine = get_engine_cliente(db_name, user, password, host)
    session = get_session_cliente(engine)

    try:
        resultado = session.execute(text(sql))
        colunas = resultado.keys()
        linhas = resultado.fetchall()
        # Formata o resultado como lista de dicionários
        resultados_formatados = [dict(zip(colunas, linha)) for linha in linhas]
        return resultados_formatados
    except Exception as e:
        print(f"Erro ao executar SQL: {e}")
        return None
    finally:
        session.close()


resultado1 = executar_sql_teste(db_name, user, password, host)
print(resultado1)
