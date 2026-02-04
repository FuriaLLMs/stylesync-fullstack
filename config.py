import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Adicionamos um fallback padrão que inclui o nome do banco (/stylesync)
    # Isso impede que get_default_database() falhe se a ENV estiver vazia
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/stylesync")
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-secreta-bem-dificil'
