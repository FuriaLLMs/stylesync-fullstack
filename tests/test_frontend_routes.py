import pytest
import sys
import os

# Adiciona o diretório raiz ao path para importar 'app' corretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_page(client):
    response = client.get('/login_page')
    assert response.status_code == 200
    assert b'Entrar no Sistema' in response.data

def test_dashboard_page(client):
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Estoque de Produtos' in response.data

def test_upload_csv_page(client):
    response = client.get('/upload_csv_page')
    assert response.status_code == 200
    assert b'Importar Vendas (CSV)' in response.data
