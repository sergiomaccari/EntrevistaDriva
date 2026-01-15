from fastapi import FastAPI, HTTPException, Header, Query
from typing import Optional, List
from pydantic import BaseModel
from faker import Faker
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

# --- CONFIGURAÇÃO INICIAL ---
app = FastAPI()
fake = Faker('pt_BR')
API_TOKEN = "driva_test_key_abc123xyz789"

# --- CONEXÃO COM BANCO (PARA ANALYTICS) ---
# Tenta conectar internamente (Docker) ou externamente (Localhost)
try:
    # URL interna do Docker
    DB_URL = "postgresql://driva_user:driva_password@postgres:5432/driva_db"
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        pass
    print("Conectado ao banco via Docker (interno)!")
except:
    # Fallback para localhost
    DB_URL = "postgresql://driva_user:driva_password@localhost:5432/driva_db"
    engine = create_engine(DB_URL)
    print("Conectado ao banco via Localhost (externo)!")

# --- MODELOS DE DADOS ---
class EnrichmentData(BaseModel):
    id: str
    id_workspace: str
    workspace_name: str
    total_contacts: int
    contact_type: str
    status: str
    created_at: datetime
    updated_at: datetime

# --- GERADOR DE DADOS FAKES (Simulação da Fonte) ---
print("Gerando dados falsos... aguarde.")
FAKE_DB = []
STATUS_OPTS = ["COMPLETED", "PROCESSING", "FAILED", "CANCELED"]
TYPES_OPTS = ["COMPANY", "PERSON"]

# Gera 5000 registros na memória ao iniciar
for _ in range(5000):
    created = fake.date_time_between(start_date='-30d', end_date='now')
    FAKE_DB.append({
        "id": fake.uuid4(),
        "id_workspace": fake.uuid4(),
        "workspace_name": fake.company(),
        "total_contacts": random.randint(10, 2000),
        "contact_type": random.choice(TYPES_OPTS),
        "status": random.choice(STATUS_OPTS),
        "created_at": created,
        "updated_at": created + timedelta(minutes=random.randint(1, 120))
    })
print("Dados gerados com sucesso!")

# --- ENDPOINTS DA FONTE (Ingestão) ---

@app.get("/v1/enrichments")
def get_enrichments(
    authorization: Optional[str] = Header(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    # 1. Validação do Token
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2. Simulação de Erro 429 (Rate Limit)
    if random.random() < 0.1: 
        raise HTTPException(status_code=429, detail="Too Many Requests")

    # 3. Paginação
    start = (page - 1) * limit
    end = start + limit
    total_items = len(FAKE_DB)
    total_pages = (total_items + limit - 1) // limit

    return {
        "meta": {
            "current_page": page,
            "items_per_page": limit,
            "total_items": total_items,
            "total_pages": total_pages
        },
        "data": FAKE_DB[start:end]
    }

# --- ENDPOINTS DE ANALYTICS (Dashboard) ---

@app.get("/analytics/overview")
def get_analytics_overview():
    """Retorna os KPIs principais lendo do Banco de Dados"""
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM gold_enrichments")).scalar()
        
        sucesso_count = conn.execute(text("SELECT COUNT(*) FROM gold_enrichments WHERE processamento_sucesso = true")).scalar()
        sucesso_pct = (sucesso_count / total * 100) if total and total > 0 else 0
        
        tempo = conn.execute(text("SELECT AVG(duracao_processamento_minutos) FROM gold_enrichments")).scalar()
        tempo = tempo if tempo else 0
        
        contatos = conn.execute(text("SELECT SUM(total_contatos) FROM gold_enrichments")).scalar()
        contatos = contatos if contatos else 0

    return {
        "total_processamentos": total,
        "taxa_sucesso": round(sucesso_pct, 1),
        "tempo_medio_minutos": round(tempo, 1),
        "total_contatos_processados": contatos
    }

@app.get("/analytics/charts")
def get_analytics_charts():
    """Retorna dados para gráficos"""
    with engine.connect() as conn:
        # Status
        res_status = conn.execute(text("SELECT status_processamento, COUNT(*) FROM gold_enrichments GROUP BY status_processamento")).fetchall()
        status_data = {row[0]: row[1] for row in res_status}
        
        # Tamanho
        res_tamanho = conn.execute(text("SELECT categoria_tamanho_job, COUNT(*) FROM gold_enrichments GROUP BY categoria_tamanho_job")).fetchall()
        tamanho_data = {row[0]: row[1] for row in res_tamanho}
        
    return {
        "status_distribution": status_data,
        "size_distribution": tamanho_data
    }

@app.get("/analytics/list")
def get_analytics_list():
    """Retorna lista detalhada"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM gold_enrichments ORDER BY data_atualizacao DESC LIMIT 100")).mappings().all()
        data = [dict(row) for row in result]
        
    return data

@app.get("/")
def read_root():
    return {"status": "API da Driva rodando!", "mode": "Analytics Enabled"}