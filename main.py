import logging
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict
import httpx

# Configuração de Logs Estruturados Básicos
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("microservico-oauth")

app = FastAPI(title="Microserviço de Autenticação Social OAuth - Observabilidade")

fake_users_db: Dict[str, dict] = {}

# Alinhado com o test_main.py (espera callbacks_sucesso)
METRICAS = {
    "requisicoes_login_total": 0,
    "callbacks_sucesso": 0,
    "callbacks_falha": 0
}

class UserSchema(BaseModel):
    email: str
    name: str
    provider: str

SUPPORTED_PROVIDERS = ["google", "github"]

# --- ENDPOINT /health (Alinhado com CONNECTED) ---
@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    logger.info("Health check executado com sucesso.")
    return {
        "status": "CONNECTED", # Mudado de 'UP' para 'CONNECTED' como o teste 8 exige
        "database": "CONNECTED" if isinstance(fake_users_db, dict) else "DOWN",
        "metrics": METRICAS  
    }

@app.get("/")
def read_root():
    return {"message": "Microserviço de Autenticação Social Ativo"}

@app.get("/auth/login/{provider}")
def login(provider: str):
    METRICAS["requisicoes_login_total"] += 1
    logger.info(f"Tentativa de login iniciada para o provedor: {provider}")

    if provider not in SUPPORTED_PROVIDERS:
        logger.warning(f"Tentativa de login rejeitada: Provedor {provider} não suportado.")
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
        METRICAS["callbacks_falha"] += 1
        logger.error(f"Callback falhou: Provedor {provider} inválido.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provedor não suportado"
        )

    if not code:
        METRICAS["callbacks_falha"] += 1
        logger.error("Callback chamado sem código de autenticação.")
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
        METRICAS["callbacks_falha"] += 1
        logger.critical("Serviço externo OAuth indisponível (Erro de Conexão).")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço externo indisponível"
        )

    if response.status_code != 200:
        METRICAS["callbacks_falha"] += 1
        logger.warning(f"Erro na validação do token externo. Status: {response.status_code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token/Código expirado ou inválido"
        )

    user_info = response.json()
    fake_users_db[user_info["email"]] = user_info

    METRICAS["callbacks_sucesso"] += 1 # Alinhado com o teste E2E
    logger.info(f"Usuário {user_info['email']} autenticado e salvo com sucesso.")

    return {
        "status": "authenticated", # Adicionado para corrigir o KeyError do Teste 4 e E2E
        "message": "Autenticação realizada com sucesso!",
        "access_token": "mocked_jwt_token_xyz123",
        "user": user_info
    }