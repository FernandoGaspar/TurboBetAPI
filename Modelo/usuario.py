# -*- coding: utf-8 -*-
from Auxiliar import conectorSQL 
import pandas as pd
import datetime
import secrets
from Mensageria import EmailHelpMe

def Login(email, senha, macaddress, dispositivo):
    conexao = conectorSQL.conn

    # 1) Executa o procedimento de login (mantém seu fluxo atual)
    #    Observação: se o seu proc já insere/gera token, ele deve retornar pelo menos idUsuario e Token
    query_proc = "pr_realizaLogin '" + email + "', '" + senha + "', '" + macaddress + "', '" + dispositivo + "'"
    df_proc = pd.read_sql(query_proc, conexao)
    conexao.commit()

    # Se o proc não autenticou, devolve exatamente o que ele retornou (compatibilidade com a API)
    if df_proc is None or df_proc.empty:
        return pd.DataFrame([{"idUsuario": "", "Token": "0"}])

    # 2) Extrai idUsuario e token do retorno do proc
    #    (pelos logs anteriores, ele retorna colunas 'idUsuario' e 'Token')
    id_usuario = None
    token_proc = None
    try:
        id_usuario = int(df_proc.iloc[0]["idUsuario"]) if "idUsuario" in df_proc.columns else None
    except Exception:
        id_usuario = df_proc.iloc[0].get("idUsuario")

    token_proc = df_proc.iloc[0].get("Token") if "Token" in df_proc.columns else None

    # Se não temos idUsuario válido, devolve falha padrão
    if not id_usuario:
        return pd.DataFrame([{"idUsuario": "", "Token": "0"}])

    # 3) Busca nome e email do usuário
    query_user = """
        SELECT TOP 1 idUsuario, nome, email
        FROM dbo.tbUsuario
        WHERE idUsuario = ?
    """
    df_user = pd.read_sql(query_user, conexao, params=[id_usuario])

    # 4) Garante um token: usa o do proc; se vier vazio/zero, pega o mais recente na tbToken
    token_final = str(token_proc or "").strip()
    if token_final in ("", "0", None):
        query_token = """
            SELECT TOP 1 TokenCode AS Token
            FROM dbo.tbToken
            WHERE idUsuario = ?
            ORDER BY DataLogin DESC
        """
        df_token = pd.read_sql(query_token, conexao, params=[id_usuario])
        if not df_token.empty:
            token_final = df_token.iloc[0]["Token"]
        else:
            token_final = "0"

    # 5) Monta saída consolidada com as colunas esperadas pelo frontend/API
    if df_user is None or df_user.empty:
        # Se por algum motivo não achou o usuário (não deveria acontecer), devolve estrutura mínima
        return pd.DataFrame([{ "idUsuario": id_usuario, "nome": "", "email": email, "Token": token_final }])

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



    