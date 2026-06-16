import pytest
import httpx
import respx  

from fastapi.testclient import TestClient
from main import app, fake_users_db


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_test_database():
    fake_users_db.clear()

#teste de integração para o endpoint 
def test_read_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Microserviço de Autenticação Social Ativo"
    }

#teste de integração para o endpoint de login com um provedor válido
def test_login_with_valid_provider():
    response = client.get("/auth/login/google")

    assert response.status_code == 200
    assert "google" in response.json()["auth_url"]
    assert response.json()["status"] == "simulated_redirect"

#teste de integração para o endpoint de login com um provedor inválido
def test_login_with_invalid_provider():
    response = client.get("/auth/login/facebook")

    assert response.status_code == 400
    assert response.json()["detail"] == "Provedor não suportado"

#teste de integração para o endpoint de callback com um código válido e criação do usuário
@respx.mock
def test_callback_success_and_user_creation():
    respx.post("https://oauth.fake/google/token").mock(
        return_value=httpx.Response(
            200,
            json={
                "email": "vito@exemplo.com",
                "name": "Vito Andrade",
                "provider": "google"
            }   
        )
    )

    response = client.get("/auth/callback?code=valid_code_123&provider=google")

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["user"]["email"] == "vito@exemplo.com"
    assert "vito@exemplo.com" in fake_users_db

#teste de integração para o endpoint de callback com um código expirado ou inválido
@respx.mock
def test_callback_with_expired_code():
    respx.post("https://oauth.fake/google/token").mock(
        return_value=httpx.Response(
            400,
            json={"detail": "Código expirado"}
        )
    )

    response = client.get("/auth/callback?code=expired_code&provider=google")

    assert response.status_code == 400
    assert response.json()["detail"] == "Token/Código expirado ou inválido"

#teste de integração para o endpoint de callback com um serviço externo indisponível
@respx.mock
def test_callback_external_service_unavailable():
    respx.post("https://oauth.fake/google/token").mock(
        side_effect=httpx.ConnectError("Erro de conexão")
    )

    response = client.get("/auth/callback?code=valid_code_123&provider=google")

    assert response.status_code == 503
    assert response.json()["detail"] == "Serviço externo indisponível"

#teste de integração para o endpoint de callback sem informar o código de autenticação
def test_callback_without_code():
    response = client.get("/auth/callback?provider=google")

    assert response.status_code == 401
    assert response.json()["detail"] == "Código de autenticação não informado"
    
    def test_health_check_endpoint():
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"
    assert "metrics" in response.json()