import io
from app import create_app

app = create_app()
client = app.test_client()

# Login
login_resp = client.post('/login', json={"username": "admin", "password": "123"})
token = login_resp.json['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Upload
data = {
    'file': (io.BytesIO(b"sale_date,product_id,quantity,total_value\n2023-01-01,PROD123,2,100.50"), 'vendas.csv')
}
rv = client.post('/sales/upload', headers=headers, data=data, content_type='multipart/form-data')

print(f"Status Code: {rv.status_code}")
print(f"Response Body: {rv.json}")
