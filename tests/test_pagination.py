import pytest
import sys
import os

# Adiciona o diretório raiz ao path para importar 'app' corretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
import app as app_module
from app.models.product import ProductDBModel

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db = app_module.db
            # Limpa e popula produtos para teste
            db.products.delete_many({})
            products = [
                {"name": f"Prod {i}", "sku": f"SKU-{i}", "price": 10.0, "stock": 10}
                for i in range(1, 26)
            ]
            db.products.insert_many(products)
        yield client
        # Limpeza opcional após testes
        with app.app_context():
            db = app_module.db
            db.products.delete_many({})

def test_pagination_default(client):
    rv = client.get('/products')
    assert rv.status_code == 200
    data = rv.json
    assert len(data['data']) == 20 # Default limit
    assert data['meta']['page'] == 1
    assert data['meta']['total'] == 25
    assert data['meta']['pages'] == 2

def test_pagination_custom(client):
    rv = client.get('/products?page=2&limit=5')
    assert rv.status_code == 200
    data = rv.json
    assert len(data['data']) == 5
    assert data['data'][0]['name'] == "Prod 6" # 1-5 na pag 1, 6-10 na pag 2
    assert data['meta']['page'] == 2
    assert data['meta']['limit'] == 5
