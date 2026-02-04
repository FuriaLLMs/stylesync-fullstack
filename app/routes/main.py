import csv
import io
from flask import Blueprint, jsonify, request, current_app, render_template
from pydantic import ValidationError
from app.models.user import LoginPayload, UserDBModel
from app.models.product import Product, ProductDBModel, UpdateProduct
from app.models.sale import Sale # Importe o modelo de Venda
import app as app_module # Alterado para acesso dinâmico ao db
from bson import ObjectId
import jwt # Importação nova
from datetime import datetime, timedelta, timezone # Importação nova
from app.decorators import token_required # Importação nova

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return jsonify({"message": "Bem-vindo à API da StyleSync!"})

@main_bp.route('/login_page')
def login_page():
    return render_template('login.html')

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/upload_csv_page')
def upload_csv_page():
    return render_template('upload_csv.html')

# --- ROTA DE LOGIN (Gera o Token) ---
@main_bp.route('/login', methods=['POST'])
def login():
    try:
        raw_data = request.get_json()
        user_data = LoginPayload(**raw_data)

        # Busca o usuário no banco
        db = app_module.db
        user_dict = db.users.find_one({"username": user_data.username})
        
        if user_dict:
            user = UserDBModel(**user_dict)
            if user.check_password(user_data.password):
                # Cria o Token JWT
                token = jwt.encode({
                    "user_id": user.username,
                    "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
                }, current_app.config['SECRET_KEY'], algorithm="HS256")

                return jsonify({'access_token': token})

        return jsonify({"message": "Credenciais invalidas!"}), 401

    except ValidationError as e:
        # include_input=False remove o valor original (ObjectId) do erro,
        # permitindo que o jsonify serialize o resto sem crashar.
        return jsonify({"error": e.errors(include_input=False)}), 400
    except Exception as e:
        return jsonify({"error": f"Erro no login: {str(e)}"}), 500

# --- ROTA DE LISTAGEM (Pública) ---
@main_bp.route('/products', methods=['GET'])
def get_products():
    db = app_module.db
    if db is None: return jsonify({"error": "Database not connected"}), 500
    
    # Parâmetros de paginação
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    limit = min(limit, 100) # Limite máximo de 100
    skip = (page - 1) * limit

    total_products = db.products.count_documents({})
    products_cursor = db.products.find().skip(skip).limit(limit)
    
    products_list = [ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True) for product in products_cursor]
    
    return jsonify({
        "data": products_list,
        "meta": {
            "page": page,
            "limit": limit,
            "total": total_products,
            "pages": (total_products + limit - 1) // limit
        }
    })

# --- ROTA DE CRIAÇÃO (Protegida) ---
@main_bp.route('/products', methods=['POST'])
@token_required # <--- O Guarda entra em ação aqui
def create_product(token_data): # <--- Recebe os dados do token
    db = app_module.db
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
    db = app_module.db
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

# RF: O sistema deve permitir a atualizacao de um unico produto e produto existente
@main_bp.route('/product/<product_id>', methods=['PUT'])
@token_required # <--- Protegido com Token
def update_product(token_data, product_id):
    db = app_module.db
    if db is None: return jsonify({"error": "Database not connected"}), 500

    try:
        # 1. Converte ID e valida dados parciais
        oid = ObjectId(product_id)
        raw_data = request.get_json()
        update_data = UpdateProduct(**raw_data)
        
        # 2. Atualiza no MongoDB usando $set
        # exclude_unset=True garante que só campos enviados sejam atualizados
        update_result = db.products.update_one(
            {"_id": oid},
            {"$set": update_data.model_dump(exclude_unset=True)}
        )
        
        # 3. Verifica se achou o produto
        if update_result.matched_count == 0:
            return jsonify({"error": "Produto não encontrado"}), 404
            
        # 4. Retorna o produto atualizado
        updated_product = db.products.find_one({"_id": oid})
        # Serializa com ProductDBModel para garantir formato correto do ID
        product_model = ProductDBModel(**updated_product).model_dump(by_alias=True, exclude_none=True)
        
        return jsonify(product_model)

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar: {e}"}), 400

# RF: O sistema deve permitir a delecao de um unico produto e produto existente
@main_bp.route('/product/<product_id>', methods=['DELETE'])
@token_required # <--- Protegido com Token
def delete_product(token_data, product_id):
    db = app_module.db
    if db is None: return jsonify({"error": "Database not connected"}), 500

    try:
        oid = ObjectId(product_id)
        
        # Deleta o documento
        delete_result = db.products.delete_one({"_id": oid})
        
        if delete_result.deleted_count == 0:
            return jsonify({"error": "Produto não encontrado"}), 404
            
        # Retorna 204 No Content (sucesso sem corpo de resposta)
        return "", 204
        
    except Exception as e:
        return jsonify({"error": f"Erro ao deletar: {e}"}), 400

# RF: O sistema deve permitir a importacao de vendas através de um arquivo
@main_bp.route('/sales/upload', methods=['POST'])
@token_required # Somente usuários logados podem importar vendas
def upload_sales(token_data):
    db = app_module.db
    if db is None: return jsonify({"error": "Database not connected"}), 500

    # 1. Verifica se o arquivo foi enviado
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo foi enviado"}), 400
    
    file = request.files['file']

    # 2. Verifica se o nome do arquivo não está vazio
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    
    # 3. Verifica a extensão e processa
    if file and file.filename.endswith('.csv'):
        try:
            # Lê o arquivo da memória e decodifica para texto
            csv_stream = io.StringIO(file.stream.read().decode('UTF-8'), newline=None)
            csv_reader = csv.DictReader(csv_stream)
            
            sales_to_insert = []
            errors = []
            
            # 4. Itera sobre as linhas do CSV
            for row_num, row in enumerate(csv_reader, 1):
                try:
                    # Valida cada linha com o Pydantic
                    # O Pydantic é inteligente para converter strings do CSV ("2023-01-01") em objetos (date)
                    sale_data = Sale(**row)
                    
                    # Prepara para inserir (exclui o id para o Mongo gerar)
                    sales_to_insert.append(sale_data.model_dump(exclude={'id'}))
                    
                except ValidationError as e:
                    errors.append(f"Linha {row_num}: Dados inválidos - {e.errors()}")
                except Exception as e:
                    errors.append(f"Linha {row_num}: Erro inesperado - {str(e)}")
            
            # 5. Insere os dados válidos no Banco (Bulk Insert)
            if sales_to_insert:
                try:
                    db.sales.insert_many(sales_to_insert)
                except Exception as e:
                    return jsonify({"error": f"Erro ao inserir dados no banco: {str(e)}"}), 500
            
            # 6. Retorna o relatório do processamento
            return jsonify({
                "message": "Upload processado com sucesso.",
                "vendas_importadas": len(sales_to_insert),
                "erros_encontrados": errors
            }), 200

        except Exception as e:
             return jsonify({"error": f"Erro ao processar arquivo: {str(e)}"}), 500
    
    return jsonify({"error": "Formato de arquivo inválido. Apenas .csv é permitido"}), 400
