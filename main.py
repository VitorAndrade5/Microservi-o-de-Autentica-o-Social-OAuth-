from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict
import httpx


app = FastAPI(title="Microserviço de Autenticação Social OAuth")

fake_users_db: Dict[str, dict] = {}


class UserSchema(BaseModel):
    email: str
    name: str
    provider: str


SUPPORTED_PROVIDERS = ["google", "github"]


@app.get("/")
def read_root():
    return {"message": "Microserviço de Autenticação Social Ativo"}


@app.get("/auth/login/{provider}")
def login(provider: str):
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provedor não suportado"
        )

    auth_url = f"https://accounts.{provider}.com/o/oauth2/v2/auth"

    return {
        "message": f"Redirecionando para o fluxo do {provider}",
        "auth_url": auth_url,
        "status": "simulated_redirect"
    }


@app.get("/auth/callback")
async def callback(code: str = None, provider: str = "google"):
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provedor não suportado"
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de autenticação não informado"
        )

    external_api_url = f"https://oauth.fake/{provider}/token"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                external_api_url,
                json={"code": code, "provider": provider},
                timeout=5
            )

    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço externo indisponível"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token/Código expirado ou inválido"
        )

    user_info = response.json()

    fake_users_db[user_info["email"]] = user_info

    return {
        "message": "Autenticação realizada com sucesso!",
        "access_token": "mocked_jwt_token_xyz123",
        "user": user_info
    }