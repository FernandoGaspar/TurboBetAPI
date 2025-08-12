# -*- coding: utf-8 -*-
from Auxiliar import conectorSQL 
import pandas as pd
import datetime
import secrets
from Mensageria import EmailHelpMe
import logging
import pyodbc
logger = logging.getLogger(__name__)


def _ensure_conn():
    """Garante que conectorSQL.conn está ativo; tenta reconectar uma vez se necessário."""
    conn = getattr(conectorSQL, 'conn', None)
    try:
        # Teste barato: SELECT 1
        if conn is None:
            raise RuntimeError("conn is None")
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return conn
    except Exception:
        # tenta reconectar se o módulo expuser um método adequado
        try:
            if hasattr(conectorSQL, 'reconnect'):
                conn = conectorSQL.reconnect()
            elif hasattr(conectorSQL, 'connect'):
                conn = conectorSQL.connect()
            elif hasattr(conectorSQL, 'get_connection'):
                conn = conectorSQL.get_connection()
            else:
                # Recarrega o módulo para refazer o conn
                import importlib
                conn = importlib.reload(conectorSQL).conn
        except Exception as e:
            logger.exception("[DB] Falha ao reconectar: %s", e)
            raise
        # Testa de novo
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return conn

def Login(email, senha, macaddress, dispositivo):
    # 0) Garante conexão viva
    conexao = _ensure_conn()

    # Helper para executar SQL com retry em 08S01
    def _read_sql_retry(sql: str, params=None):
        try:
            return pd.read_sql(sql, conexao, params=params)
        except Exception as e:
            # Se for falha de link (08S01), tenta reconectar 1x e repetir
            msg = str(e)
            if isinstance(e, (pyodbc.Error, pyodbc.OperationalError)) or '08S01' in msg:
                logger.warning("[DB] 1/1 retry após erro: %s", msg)
                nonlocal_conn = _ensure_conn()
                return pd.read_sql(sql, nonlocal_conn, params=params)
            raise

    # 1) Executa o procedimento de login de forma segura (parametrizada)
    # Observação importante: usar EXEC com parâmetros evita concatenação e problemas de aspas
    sql_proc = "SET NOCOUNT ON; EXEC pr_realizaLogin ?, ?, ?, ?"
    try:
        df_proc = _read_sql_retry(sql_proc, params=[email, senha, macaddress, dispositivo])
    except Exception as e:
        logger.exception("[LOGIN] Falha ao executar pr_realizaLogin: %s", e)
        # Retorna estrutura padrão de falha para a API traduzir em 401/500 conforme regra
        return pd.DataFrame([{"idUsuario": "", "Token": "0", "_err": str(e)}])

    try:
        conexao.commit()
    except Exception:
        pass

    # Se não autenticou
    if df_proc is None or df_proc.empty:
        return pd.DataFrame([{"idUsuario": "", "Token": "0"}])

    # 2) Extrai idUsuario e token
    id_usuario = None
    token_proc = None
    try:
        if "idUsuario" in df_proc.columns:
            try:
                id_usuario = int(df_proc.iloc[0]["idUsuario"])  # tenta converter
            except Exception:
                id_usuario = df_proc.iloc[0]["idUsuario"]
        if "Token" in df_proc.columns:
            token_proc = df_proc.iloc[0]["Token"]
    except Exception as e:
        logger.warning("[LOGIN] Não foi possível extrair id/token do retorno: %s", e)

    if not id_usuario:
        return pd.DataFrame([{"idUsuario": "", "Token": "0"}])

    # 3) Busca nome/email
    sql_user = "SELECT TOP 1 idUsuario, nome, email FROM dbo.tbUsuario WHERE idUsuario = ?"
    df_user = _read_sql_retry(sql_user, params=[id_usuario])

    # 4) Token final: prioriza o do proc; se vazio, tenta o mais recente na tbToken
    token_final = str(token_proc or "").strip()
    if token_final in ("", "0", None):
        sql_token = (
            "SELECT TOP 1 TokenCode AS Token FROM dbo.tbToken WHERE idUsuario = ? ORDER BY DataLogin DESC"
        )
        df_token = _read_sql_retry(sql_token, params=[id_usuario])
        if df_token is not None and not df_token.empty:
            token_final = df_token.iloc[0]["Token"]
        else:
            token_final = "0"

    # 5) Saída consolidada
    if df_user is None or df_user.empty:
        return pd.DataFrame([
            {"idUsuario": id_usuario, "nome": "", "email": email, "Token": token_final}
        ])

    out = df_user[["idUsuario", "nome", "email"]].copy()
    out["Token"] = token_final
    return out

def ValidaToken(idUsuario, token, dispositivo):
    conexao = conectorSQL.conn
    query = "pr_s_ValidaToken '"+token+"', '"+str(idUsuario)+"', '"+dispositivo+"'"
    Retorno = pd.read_sql(query, conexao)      
    conexao.commit()
    isValid = Retorno.iloc[0, 0]
    if isValid == 1:
        isValid = True
    else:
        isValid = False

    return isValid

def RealizaCadastro (email, nome, senha):
    cursor = conectorSQL.conn.cursor()
    query = "pr_i_realizaCadastroUsuario '"+email+"', '"+nome+"', '"+senha+"'"
    # Usuario = pd.read_sql(query, conexao)      
    # conexao.commit()
    cursor.execute(query)
    conectorSQL.conn.commit()

# def ResetDeSenha (login):
#     token = ''.join(secrets.choice('0123456789') for _ in range(6))
    
#     conexao = conectorSQL.conn
#     query = "pr_i_Token_ResetSenha '"+login+"', '"+token+"'"
#     EmailEnvio = pd.read_sql(query, conexao)      
#     conexao.commit()
#     EmailEnvio = EmailEnvio.iloc[0, 0]
    
#     if (EmailEnvio != "NULL"):
#         EmailHelpMe.enviar_email (EmailEnvio, "Reset de Senha HelpMe", "Token para reset: "+token)
    
#     return EmailEnvio

# def ValidaTokenResetSenha (login, token):
#     conexao = conectorSQL.conn
#     query = "pr_s_ValidaToken_ResetSenha '"+login+"', '"+token+"'"
#     TokenValido = pd.read_sql(query, conexao)      
#     conexao.commit()

#     TokenValido = TokenValido.iloc[0, 0]
    
#     return TokenValido

# def alteraSenha (login, senha):
#     conexao = conectorSQL.conn
#     cursor = conexao.cursor()
#     query = f"EXEC pr_u_senhaUsuario '{login}', '{senha}'"

#     try:
#         cursor.execute(query)
#         conexao.commit() 
#         return {"status": "Sucesso", "mensagem": "Senha alterada com sucesso"}
#     except Exception as e:
#         conexao.rollback()
#         return {"status": "Erro", "mensagem": str(e)}
#     finally:
#         cursor.close()



    