import pytest
import sys
import os

# Ajuste do path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.category import Category

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Teste do Modelo Pydantic
def test_category_model_valid():
    cat = Category(name="Eletrônicos", description="Gadgets e computadores")
    assert cat.name == "Eletrônicos"

def test_category_routes(client):
    # Teste GET
    rv = client.get('/categories')
    assert rv.status_code == 200
    assert rv.json == {"message": "Listagem de categorias"}
    
    # Teste POST
    rv = client.post('/categories')
    assert rv.status_code == 200
    assert rv.json == {"message": "Categoria criada com sucesso"}
