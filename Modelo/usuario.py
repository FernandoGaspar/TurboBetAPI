# -*- coding: utf-8 -*-
from Auxiliar import conectorSQL 
import pandas as pd
import datetime
import secrets
from Mensageria import EmailHelpMe

def Login(email, senha, macaddress, dispositivo):
    conexao = conectorSQL.conn
    query = "pr_realizaLogin '"+email+"', '"+senha+"', '"+macaddress+"', '"+dispositivo+"'"
    Usuario = pd.read_sql(query, conexao)      
    conexao.commit()
    
    return Usuario

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



    