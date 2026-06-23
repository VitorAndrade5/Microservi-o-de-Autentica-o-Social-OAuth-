import logging
import os
from typing import Dict

import httpx
from fastapi import HTTPException, status

from storage import fake_users_db

SUPPORTED_PROVIDERS = ["google", "github"]
METRICS = {
    "requisicoes_login_total": 0,
    "callbacks_sucesso": 0,
    "callbacks_falha": 0,
    "credentials_logins_total": 0,
}

logger = logging.getLogger("microservico-oauth.services")


def get_auth_url(provider: str) -> str:
    if provider not in SUPPORTED_PROVIDERS:
        logger.warning(f"Provedor de login inválido: {provider}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provedor não suportado"
        )

    return f"https://accounts.{provider}.com/o/oauth2/v2/auth"


async def exchange_code_for_user(code: str, provider: str) -> dict:
    if provider not in SUPPORTED_PROVIDERS:
        logger.error(f"Callback falhou por provedor inválido: {provider}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provedor não suportado"
        )

    if not code:
        logger.error("Callback chamado sem código de autenticação.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de autenticação não informado"
        )

    if "SSLKEYLOGFILE" in os.environ:
        os.environ.pop("SSLKEYLOGFILE", None)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://oauth.fake/{provider}/token",
                json={"code": code, "provider": provider},
                timeout=5
            )
    except httpx.RequestError:
        logger.critical("Serviço externo OAuth indisponível (Erro de Conexão).")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço externo indisponível"
        )

    if response.status_code != 200:
        logger.warning(f"Erro na validação do token externo. Status: {response.status_code}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token/Código expirado ou inválido"
        )

    return response.json()


def save_user(user_info: dict) -> None:
    fake_users_db[user_info["email"]] = user_info


def validate_credential_login(email: str, password: str) -> None:
    if not password or len(password.strip()) < 6:
        logger.warning(f"Tentativa de login por credenciais com senha inválida para {email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha deve ter ao menos 6 caracteres"
        )


def build_credential_user(email: str, name: str | None = None) -> dict:
    return {
        "email": email,
        "name": name or email.split("@")[0],
        "provider": "credentials"
    }


def reset_metrics() -> None:
    for key in METRICS:
        METRICS[key] = 0
