from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict

app = FastAPI(title="Microserviço de Autenticação Social (OAuth)")

fake_users_db: Dict[str, dict] = {}

class UserSchema(BaseModel):
    email: str
    name: str
    provider: str

@app.get("/")
def read_root():
    return {"message": "Microserviço de Autenticação Social Ativo"}

@app.get("/auth/login/{provider}")
def login(provider: str):
    if provider not in ["google", "github"]:
        raise HTTPException(status_code=400, detail="Provedor não suportado")
    
    target_url = f"https://accounts.{provider}.com/o/oauth2/v2/auth"
    return {
        "message": f"Redirecionando para o fluxo do {provider}",
        "auth_url": target_url,
        "status": "simulated_redirect"
    }

@app.get("/auth/callback")
def callback(code: str = None, error: str = None):
    if error or not code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Falha na autenticação com o provedor externo"
        )
    
    if code == "codigo_invalido_fake":
        raise HTTPException(status_code=400, detail="Token/Código expirado ou inválido")

    user_info = {
        "email": "vito@exemplo.com",
        "name": "Vito Andrade",
        "provider": "google"
    }
    
    fake_users_db[user_info["email"]] = user_info

    return {
        "message": "Autenticação realizada com sucesso!",
        "access_token": "mocked_jwt_token_xyz123",
        "user": user_info
    }   