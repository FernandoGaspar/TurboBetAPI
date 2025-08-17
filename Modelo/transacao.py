# -*- coding: utf-8 -*-
from Auxiliar import conectorSQL 
import pandas as pd


def getTransacoesUsuario (idUsuario):
    conexao = conectorSQL.conn
    query = "pr_s_transacoes '"+idUsuario+"'"
    retorno = pd.read_sql(query, conexao)      
    conexao.commit()
    return retorno

def setTransacao (idUsuario, direcao, valor, tipoOrigem):
    cursor = conectorSQL.conn.cursor()
    query = "pr_i_transacoes '"+idUsuario+"', '"+direcao+"', '"+valor+"', '"+tipoOrigem+"'"
    print (query)
    cursor.execute(query)
    conectorSQL.conn.commit()

def getSaldo (idUsuario):
    conexao = conectorSQL.conn
    query = "pr_s_Saldo '"+idUsuario+"'"
    retorno = pd.read_sql(query, conexao)      
    conexao.commit()
    return retorno