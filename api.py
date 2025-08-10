# -*- coding: utf-8 -*-
import os
import sys 
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.abspath(os.path.join(ROOT_DIR, '.'))
sys.path.append(ROOT_DIR)

import json
from flask import Flask, request, jsonify, Response
from flask_restful import Resource, Api
from flask_cors import CORS
from Modelo import usuario

PORTA = 8090

app = Flask(__name__)
CORS(app)
api = Api(app)

class Login(Resource):
    def post(self): 
        x = request.stream.read()
        y = json.loads(x)
        email = y["email"]
        senha = y["senha"]
        dispositivo = request.headers.get('User-Agent')
        macaddress = request.remote_addr
        
        df = usuario.Login(email, senha, macaddress, dispositivo)
        result = df.to_json(orient='records')
        print (result)
        return jsonify(result)   

class Cadastro(Resource):
    def post(self): 
        x = request.stream.read()
        y = json.loads(x)
        email = y["email"]
        nome = y["nome"]
        senha = y["senha"]
        dispositivo = request.headers.get('User-Agent')
        macaddress = request.remote_addr
        
        df = usuario.RealizaCadastro(email, nome, senha)
        # result = df.to_json(orient='records')
        # print (result)
        return True   

#Main
api.add_resource(Login, '/login')

api.add_resource(Cadastro, '/cadastro')
 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORTA, threaded=False)