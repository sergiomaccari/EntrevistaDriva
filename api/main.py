from fastapi import FastAPI, HTTPException, Header, Query
from typing import Optional, List
from pydantic import BaseModel
from faker import Faker
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import os

app = FastAPI()
fake = Faker('pt_BR')
API_TOKEN = "driva_test_key_abc123xyz789"

try:
    DB_HOST = os.getenv("DB_HOST", "postgres")
    DB_URL = f"postgresql://driva_user:driva_password@{DB_HOST}:5432/driva_db"
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        pass
    print("Conectado ao banco via Docker")
except:
    DB_URL = "postgresql://driva_user:driva_password@localhost:5432/driva_db"
    engine = create_engine(DB_URL)
    print("Conectado ao banco via Localhost")

STATUS_OPTS = ["COMPLETED", "PROCESSING", "FAILED", "CANCELED"]
TYPES_OPTS = ["COMPANY", "PERSON"]

ID_HISTORY = []

def gerar_lote_falso(quantidade):
    lote = []
    
    for _ in range(quantidade):
        is_update = len(ID_HISTORY) > 0 and random.random() < 0.20
        
        if is_update:
            the_id = random.choice(ID_HISTORY)
            status_atual = random.choice(STATUS_OPTS)
            updated_at = fake.date_time_between(start_date='-2d', end_date='now')
            created_at = updated_at - timedelta(days=random.randint(5, 30))
        else:
            the_id = fake.uuid4()
            ID_HISTORY.append(the_id)
            status_atual = random.choice(STATUS_OPTS)
            created_at = fake.date_time_between(start_date='-30d', end_date='now')
            updated_at = created_at + timedelta(seconds=random.randint(0, 59))

        lote.append({
            "id": the_id,
            "id_workspace": fake.uuid4(),
            "workspace_name": fake.company(),
            "total_contacts": random.randint(10, 2000),
            "contact_type": random.choice(TYPES_OPTS),
            "status": status_atual,
            "created_at": created_at,
            "updated_at": updated_at
        })
    return lote

@app.get("/v1/enrichments")
def get_enrichments(
    authorization: Optional[str] = Header(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100)
):
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if random.random() < 0.1: 
        raise HTTPException(status_code=429, detail="Too Many Requests")

    dados_frescos = gerar_lote_falso(limit)
    total_fake = 5000
    
    return {
        "meta": {
            "current_page": page,
            "items_per_page": limit,
            "total_items": total_fake,
            "total_pages": total_fake // limit
        },
        "data": dados_frescos
    }

@app.get("/analytics/overview")
def get_analytics_overview():
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM gold_enrichments")).scalar()
        sucesso_count = conn.execute(text("SELECT COUNT(*) FROM gold_enrichments WHERE processamento_sucesso = true")).scalar()
        sucesso_pct = (sucesso_count / total * 100) if total and total > 0 else 0
        tempo = conn.execute(text("SELECT AVG(duracao_processamento_minutos) FROM gold_enrichments")).scalar()
        contatos = conn.execute(text("SELECT SUM(total_contatos) FROM gold_enrichments")).scalar()
    
    return {
        "total_processamentos": total,
        "taxa_sucesso": round(sucesso_pct, 1),
        "tempo_medio_minutos": round(tempo if tempo else 0, 1),
        "total_contatos_processados": contatos if contatos else 0
    }

@app.get("/analytics/charts")
def get_analytics_charts():
    with engine.connect() as conn:
        res_status = conn.execute(text("SELECT status_processamento, COUNT(*) FROM gold_enrichments GROUP BY status_processamento")).fetchall()
        status_data = {row[0]: row[1] for row in res_status}
        res_tamanho = conn.execute(text("SELECT categoria_tamanho_job, COUNT(*) FROM gold_enrichments GROUP BY categoria_tamanho_job")).fetchall()
        tamanho_data = {row[0]: row[1] for row in res_tamanho}
        
    return {"status_distribution": status_data, "size_distribution": tamanho_data}

@app.get("/analytics/list")
def get_analytics_list():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM gold_enrichments ORDER BY data_atualizacao DESC")).mappings().all()
        return [dict(row) for row in result]