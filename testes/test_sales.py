import pytest
import sys
import os
import io

# Adiciona o diretório raiz ao path para importar 'app' corretamente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def get_auth_header(client):
    rv = client.post('/login', json={"username": "admin", "password": "123"})
    token = rv.json['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_upload_sales_no_file(client):
    headers = get_auth_header(client)
    rv = client.post('/sales/upload', headers=headers)
    assert rv.status_code == 400
    assert rv.json['error'] == "Nenhum arquivo foi enviado"

def test_upload_sales_success(client):
    headers = get_auth_header(client)
    data = {
        'file': (io.BytesIO(b"sale_date,product_id,quantity,total_value\n2023-01-01,PROD123,2,100.50"), 'vendas.csv')
    }
    rv = client.post('/sales/upload', headers=headers, data=data, content_type='multipart/form-data')
    assert rv.status_code == 200
    assert rv.json['message'] == "Upload processado com sucesso."
    assert rv.json['vendas_importadas'] == 1
    assert rv.json['erros_encontrados'] == []

def test_upload_sales_partial_error(client):
    headers = get_auth_header(client)
    # Segunda linha tem data inválida
    csv_content = b"sale_date,product_id,quantity,total_value\n2023-01-01,PROD123,2,100.50\nINVALID-DATE,PROD456,1,50.00"
    data = {
        'file': (io.BytesIO(csv_content), 'vendas_erro.csv')
    }
    rv = client.post('/sales/upload', headers=headers, data=data, content_type='multipart/form-data')
    assert rv.status_code == 200
    assert rv.json['vendas_importadas'] == 1
    assert len(rv.json['erros_encontrados']) == 1
