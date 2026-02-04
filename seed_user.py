from app import create_app
import app as app_module
from app.models.user import User

app = create_app()

def seed_admin():
    with app.app_context():
        # Acessa db do módulo app para pegar o valor atualizado após create_app()
        db = app_module.db
        
        if db.users.find_one({"username": "admin"}):
            print("Usuário 'admin' já existe.")
            return

        admin_user = User(username="admin", password_hash="", role="admin")
        admin_user.set_password("123")
        
        db.users.insert_one(admin_user.model_dump())
        print("Usuário 'admin' criado com sucesso!")

if __name__ == "__main__":
    seed_admin()
