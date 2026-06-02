from fastapi.testclient import TestClient
from main import app, fake_users_db

client = TestClient(app)

# Teste 1: Validar se a rota inicial responde corretamente
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Microserviço de Autenticação Social Ativo"}

# Teste 2: Validar o redirecionamento de provedor válido e erro para inválido
def test_login_providers():
    response = client.get("/auth/login/google")
    assert response.status_code == 200
    assert "google" in response.json()["auth_url"]
    
    response_invalid = client.get("/auth/login/facebook")
    assert response_invalid.status_code == 400
    assert response_invalid.json()["detail"] == "Provedor não suportado"

# Teste 3: Validar fluxo de sucesso no Callback e criação do usuário
def test_callback_success_and_user_creation():
    fake_users_db.clear()
    response = client.get("/auth/callback?code=valid_code_123")
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["user"]["email"] == "vito@exemplo.com"
    assert "vito@exemplo.com" in fake_users_db