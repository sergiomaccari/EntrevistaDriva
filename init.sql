-- Criação da tabela BRONZE (Dados Brutos)
CREATE TABLE IF NOT EXISTS bronze_enrichments (
    id TEXT PRIMARY KEY, -- ID original do dado
    raw_data JSONB, -- O dado completo em formato JSON para garantir fidelidade
    dw_ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Quando entrou no DW
    dw_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Quando foi atualizado
);

-- Criação da tabela GOLD (Dados Refinados e Traduzidos)
CREATE TABLE IF NOT EXISTS gold_enrichments (
    id_enriquecimento TEXT PRIMARY KEY,
    id_workspace TEXT,
    nome_workspace TEXT,
    total_contatos INTEGER,
    tipo_contato TEXT,
    status_processamento TEXT,
    data_criacao TIMESTAMP,
    data_atualizacao TIMESTAMP,
    -- Campos Calculados
    duracao_processamento_minutos INTEGER,
    tempo_por_contato_minutos FLOAT,
    processamento_sucesso BOOLEAN,
    categoria_tamanho_job TEXT,
    necessita_reprocessamento BOOLEAN,
    -- Controle DW
    data_atualizacao_dw TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);