# -*- coding: utf-8 -*-
import os
import sys 
import logging

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.abspath(os.path.join(ROOT_DIR, '.'))
sys.path.append(ROOT_DIR)

import json
from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
from flask_cors import CORS
from Modelo import usuario, transacao


PORTA = 8090

app = Flask(__name__)
CORS(app)
api = Api(app)

class Login(Resource):
    def post(self): 
        dispositivo = request.headers.get('User-Agent')
        macaddress = request.remote_addr
        origin = request.headers.get('Origin')
        logging.info(f"[LOGIN] request from {macaddress} | UA={dispositivo} | Origin={origin}")

        payload = request.get_json(silent=True)
        if payload is None:
            raw = request.get_data(cache=False, as_text=True)
            logging.info(f"[LOGIN] raw body (len={len(raw) if raw else 0}): {raw}")
            try:
                payload = json.loads(raw) if raw else {}
            except Exception as e:
                logging.error(f"[LOGIN] JSON parse error: {e}")
                return jsonify({"error": "invalid_json"}), 400

        email = payload.get("email", "")
        senha = payload.get("senha", "")
        masked_senha = f"{senha[:1]}{'*'*(max(len(senha)-2,0))}{senha[-1:] if len(senha)>1 else ''}"
        logging.info(f"[LOGIN] email={email} senha={masked_senha}")

        df = usuario.Login(email, senha, macaddress, dispositivo)
        logging.info(f"[LOGIN] df.shape={getattr(df,'shape',None)}")

        data = df.to_dict(orient='records') if hasattr(df, 'to_dict') else []
        # normalize keys expected by the frontend
        normalized = []
        for row in data:
            r = dict(row)
            if 'token' not in r:
                if 'Token' in r:
                    r['token'] = r.get('Token')
                elif 'TokenCode' in r:
                    r['token'] = r.get('TokenCode')
            if 'nome' not in r and 'Nome' in r:
                r['nome'] = r.get('Nome')
            if 'email' not in r and 'Email' in r:
                r['email'] = r.get('Email')
            normalized.append(r)

        # Decide sucesso/erro
        def is_truthy(v):
            if v is None:
                return False
            s = str(v).strip()
            return s != "" and s != "0" and s.lower() != "false" and s.lower() != "null"

        valid = None
        for r in normalized:
            tok = r.get('token')
            uid = r.get('idUsuario') or r.get('IdUsuario') or r.get('UserId')
            if is_truthy(tok) and is_truthy(uid):
                valid = dict(r)
                # padroniza idUsuario
                if 'idUsuario' not in valid and uid is not None:
                    valid['idUsuario'] = uid
                break

        # Enriquecimento rápido: se a consulta não trouxe nome/email, usa o email do payload
        if valid:
            if 'email' not in valid or not str(valid.get('email') or '').strip():
                valid['email'] = email
            if 'nome' not in valid or not str(valid.get('nome') or '').strip():
                # tenta aproveitar 'Nome' se existir, senão usa prefixo do email
                raw_nome = valid.get('Nome') or payload.get('nome') or ''
                if isinstance(raw_nome, str) and raw_nome.strip():
                    valid['nome'] = raw_nome.strip()
                elif isinstance(email, str) and '@' in email:
                    valid['nome'] = email.split('@')[0]

        if not valid:
            logging.info(f"[LOGIN] invalid credentials for email={email}")
            return jsonify({"error": "invalid_credentials"}), 401

        logging.info(f"[LOGIN] success response: {valid}")
        return jsonify(valid)

class Cadastro(Resource):
    def post(self): 
        dispositivo = request.headers.get('User-Agent')
        macaddress = request.remote_addr
        origin = request.headers.get('Origin')
        logging.info(f"[CADASTRO] request from {macaddress} | UA={dispositivo} | Origin={origin}")

        payload = request.get_json(silent=True)
        if payload is None:
            raw = request.get_data(cache=False, as_text=True)
            logging.info(f"[CADASTRO] raw body (len={len(raw) if raw else 0}): {raw}")
            try:
                payload = json.loads(raw) if raw else {}
            except Exception as e:
                logging.error(f"[CADASTRO] JSON parse error: {e}")
                return jsonify({"error": "invalid_json"}), 400

        email = payload.get("email", "")
        nome = payload.get("nome", "")
        senha = payload.get("senha", "")
        masked_senha = f"{senha[:1]}{'*'*(max(len(senha)-2,0))}{senha[-1:] if len(senha)>1 else ''}"
        logging.info(f"[CADASTRO] email={email} nome={nome} senha={masked_senha}")

        df = usuario.RealizaCadastro(email, nome, senha)
        success = bool(df is not None and (not getattr(df, 'empty', False)))
        logging.info(f"[CADASTRO] success={success}")
        return jsonify({"success": success})

class getTransacoes(Resource):
    def post(self): 
        x = request.stream.read()
        y = json.loads(x)
        idUsuario = y["idUsuario"]
        dispositivo = request.headers.get('User-Agent')
        macaddress = request.remote_addr
        
        df = transacao.getTransacoesUsuario(idUsuario)
        result = df.to_json(orient='records')
        print (result)
        return jsonify(result)   

class setTransacoes(Resource):
    def post(self): 
        x = request.stream.read()
        y = json.loads(x)
        idUsuario = y["idUsuario"]
        direcao = y["direcao"]
        valor = y["valor"]
        tipoOrigem = y["tipoOrigem"]

        dispositivo = request.headers.get('User-Agent')
        macaddress = request.remote_addr
        
        try:
            transacao.setTransacao(idUsuario, direcao, valor, tipoOrigem)
            return jsonify({"success": True})
        except Exception as e:
            # log opcional
            # import logging; logging.exception("[setTransacoes] erro")
            return jsonify({"success": False, "error": "db_error"}), 500

class getSaldo(Resource):
    def post(self): 
        x = request.stream.read()
        y = json.loads(x)
        idUsuario = y["idUsuario"]
        dispositivo = request.headers.get('User-Agent')
        macaddress = request.remote_addr
        
        df = transacao.getSaldo(idUsuario)
        result = df.to_json(orient='records')
        print (result)
        return jsonify(result)   


#Main
api.add_resource(Login, '/login')
api.add_resource(Cadastro, '/cadastro')

#Transacoes
api.add_resource(getTransacoes, '/getTransacoes')
api.add_resource(setTransacoes, '/setTransacoes')
api.add_resource(getSaldo, '/getSaldo')

@app.route('/health')
def health():
    return jsonify({"status": "ok"})
 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORTA, threaded=False)