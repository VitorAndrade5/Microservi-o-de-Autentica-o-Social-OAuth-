import logging
from fastapi import FastAPI

from routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("microservico-oauth")

app = FastAPI(title="Microserviço de Autenticação Social OAuth - Observabilidade")
app.include_router(router)
