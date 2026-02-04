from functools import wraps
from flask import request, jsonify, current_app
import jwt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Verifica se o token veio no cabeçalho (Ex: "Authorization: Bearer <token>")
        if 'Authorization' in request.headers:
            try:
                # O split separa "Bearer" do código do token
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token malformado'}), 401
        
        if not token:
            return jsonify({'message': 'Token não encontrado'}), 401
        
        try:
            # Tenta decodificar o token usando a nossa SECRET_KEY
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            # O token é válido! Passamos os dados dele (ex: user_id) para a função
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(data, *args, **kwargs)
    
    return decorated
