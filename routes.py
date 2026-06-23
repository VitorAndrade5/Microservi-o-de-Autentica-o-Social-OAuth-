import logging
from fastapi import APIRouter, HTTPException, status

from schemas import CredentialSchema
from services import (
    METRICS,
    SUPPORTED_PROVIDERS,
    build_credential_user,
    exchange_code_for_user,
    get_auth_url,
    save_user,
    validate_credential_login,
)

logger = logging.getLogger("microservico-oauth.routes")
router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    logger.info("Health check executado com sucesso.")
    return {
        "status": "CONNECTED",
        "database": "CONNECTED",
        "metrics": METRICS,
    }


@router.get("/")
def read_root():
    return {"message": "Microserviço de Autenticação Social Ativo"}


@router.get("/auth/login/{provider}")
def login(provider: str):
    METRICS["requisicoes_login_total"] += 1
    logger.info(f"Tentativa de login iniciada para o provedor: {provider}")

    auth_url = get_auth_url(provider)
    return {
        "message": f"Redirecionando para o fluxo do {provider}",
        "auth_url": auth_url,
        "status": "simulated_redirect"
    }


@router.post("/auth/login")
def login_with_credentials(credentials: CredentialSchema):
    METRICS["requisicoes_login_total"] += 1
    METRICS["credentials_logins_total"] += 1
    validate_credential_login(credentials.email, credentials.password)

    user_info = build_credential_user(credentials.email, credentials.name)
    save_user(user_info)

    logger.info(f"Usuário {credentials.email} autenticado por credenciais.")
    return {
        "status": "authenticated",
        "message": "Login por credenciais realizado com sucesso.",
        "access_token": "mocked_jwt_credentials_token",
        "user": user_info
    }


@router.get("/auth/callback")
async def callback(code: str | None = None, provider: str = "google"):
    user_info = await exchange_code_for_user(code, provider)
    save_user(user_info)

    METRICS["callbacks_sucesso"] += 1
    logger.info(f"Usuário {user_info['email']} autenticado e salvo com sucesso.")

    return {
        "status": "authenticated",
        "message": "Autenticação realizada com sucesso!",
        "access_token": "mocked_jwt_token_xyz123",
        "user": user_info
    }
