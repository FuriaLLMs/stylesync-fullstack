from flask import Blueprint, jsonify, request, current_app
from pydantic import ValidationError
from app.models.user import LoginPayload
from app.models.product import Product, ProductDBModel
from app import db
from bson import ObjectId
import jwt # Importação nova
from datetime import datetime, timedelta, timezone # Importação nova
from app.decorators import token_required # Importação nova

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return jsonify({"message": "Bem-vindo à API da StyleSync!"})

# --- ROTA DE LOGIN (Gera o Token) ---
@main_bp.route('/login', methods=['POST'])
def login():
    try:
        raw_data = request.get_json()
        user_data = LoginPayload(**raw_data)

        # Autenticação simulada (admin / 123)
        if user_data.username == 'admin' and user_data.password == '123':
            # Cria o Token JWT
            token = jwt.encode({
                "user_id": user_data.username,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=30) # Expira em 30 min
            }, current_app.config['SECRET_KEY'], algorithm="HS256")

            return jsonify({'access_token': token})
        else:
            return jsonify({"message": "Credenciais invalidas!"}), 401

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": f"Erro no login: {e}"}), 500

# --- ROTA DE LISTAGEM (Pública) ---
@main_bp.route('/products', methods=['GET'])
def get_products():
    if db is None: return jsonify({"error": "Database not connected"}), 500
    products_cursor = db.products.find()
    products_list = [ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True) for product in products_cursor]
    return jsonify(products_list)

# --- ROTA DE CRIAÇÃO (Protegida) ---
@main_bp.route('/products', methods=['POST'])
@token_required # <--- O Guarda entra em ação aqui
def create_product(token_data): # <--- Recebe os dados do token
    if db is None: return jsonify({"error": "Database not connected"}), 500

    try:
        raw_data = request.get_json()
        product = Product(**raw_data)
        product_dict = product.model_dump()
        
        result = db.products.insert_one(product_dict)
        
        return jsonify({
            "message": "Produto criado com sucesso!",
            "_id": str(result.inserted_id),
            "created_by": token_data['user_id'] # Mostra quem criou
        }), 201
        
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": f"Erro ao criar produto: {e}"}), 500

# (Mantenha as outras rotas GET id, PUT, DELETE, Upload iguais...)
@main_bp.route('/product/<product_id>', methods=['GET'])
def get_product_by_id(product_id):
    if db is None:
         return jsonify({"error": "Database not connected"}), 500

    try:
        oid = ObjectId(product_id)
        product = db.products.find_one({"_id": oid})
        
        if product:
             # Usa o modelo para serializar corretamente
            product_model = ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True)
            return jsonify(product_model)
        else:
            return jsonify({"error": f"Produto com o id: {product_id} - Não encontrado"}), 404
            
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar o produto: {e}"}), 400

@main_bp.route('/product/<product_id>', methods=['PUT'])
def update_product(product_id):
    return jsonify({"message": f"Esta é a rota de atualizacao do produto com o id {product_id}"})

@main_bp.route('/product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    return jsonify({"message": f"Esta é a rota de deleção do produto com o id {product_id}"})

@main_bp.route('/sales/upload', methods=['POST'])
def upload_sales():
    return jsonify({"message": "Esta é a rota de upload do arquivo de vendas"})
