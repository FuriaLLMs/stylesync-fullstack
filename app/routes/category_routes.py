from flask import Blueprint, jsonify

# Note que o nome do blueprint é diferente: category_bp
category_bp = Blueprint('category_bp', __name__)

# RF: O sistema deve permitir listar todas as categorias
@category_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify({"message": "Listagem de categorias"})

# RF: O sistema deve permitir criar uma nova categoria
@category_bp.route('/categories', methods=['POST'])
def create_category():
    return jsonify({"message": "Categoria criada com sucesso"})

# RF: O sistema deve permitir visualizar uma categoria específica
@category_bp.route('/category/<int:category_id>', methods=['GET'])
def get_category_by_id(category_id):
    return jsonify({"message": f"Detalhes da categoria {category_id}"})

# RF: O sistema deve permitir atualizar uma categoria
@category_bp.route('/category/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    return jsonify({"message": f"Categoria {category_id} atualizada"})

# RF: O sistema deve permitir deletar uma categoria
@category_bp.route('/category/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    return jsonify({"message": f"Categoria {category_id} deletada"})
