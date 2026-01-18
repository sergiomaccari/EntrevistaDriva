-- Tabela Bronze
CREATE TABLE IF NOT EXISTS bronze_enrichments (
    id TEXT PRIMARY KEY,
    raw_data JSONB,
    dw_ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dw_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela Gold
CREATE TABLE IF NOT EXISTS gold_enrichments (
    id_enriquecimento TEXT PRIMARY KEY,
    id_workspace TEXT,
    nome_workspace TEXT,
    total_contatos INTEGER,
    tipo_contato TEXT,
    status_processamento TEXT,
    data_criacao TIMESTAMP,
    data_atualizacao TIMESTAMP,
    duracao_processamento_minutos INTEGER,
    tempo_por_contato_minutos FLOAT,
    processamento_sucesso BOOLEAN,
    categoria_tamanho_job TEXT,
    necessita_reprocessamento BOOLEAN,
    data_atualizacao_dw TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);