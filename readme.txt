Este projeto representa a etapa técnica do processo seletivo para a vaga de Estagiário em Automação da empresa Driva, sendo uma Pipeline de dados End-to-End para monitorar a operação de enriquecimento de dados.
O sistema simula um fluxo completo de enriquecimento de dados, contendo a ingestão através de uma API transacional, armazenamento Bronze/Gold, e exposição em API de Analytics com visualização em um Dashboard.


Componentes:

-	API para simular dados de fonte externa (Python/FastAPI): Gera dados utilizando a biblioteca Faker. Inclui histórico de atualizações (updates) e simulação de falhas (erros 429).
-	Orquestração(n8n): Diferentes workflows trabalhando em conjunto responsáveis pela ingestão periódica, a cada 5 minutos). Responsável por paginação e retries em caso de erro na camada bronze
-	Data Warehouse (PostgresSQL): Tendo duas camadas: Bronze Layer que armazena dados crus para auditoria e processamento. Gold Layer: Dados tratados e prontos para análise
-	Analytics Layer (API): Camada de serviço que isola banco de dados do frontend
-	Visualização (Streamlit): Dashboard interativo que consome API de Analytics


Tecnologias Utilizadas:

-	Python 3.10 (Linguagem)
-	FastAPI (Backend e API)
-	Uvicorn (Backend e API)
-	n8n (ETL e Orquestração)
-	PostgresSQL 14 (Banco de Dados)
-	Streamlit (Visualização)
-	Plotly (Visualização)
-	Docker (Infraestrutura)


Como executar

1) Clone o repositório:

git clone https://github.com/seu-usuario/driva-analytics.git
cd driva-analytics

2) Suba os conteiners:

docker compose up -d --build

3) Acesse interfaces (Observação: Na primeira execução, acesse o n8n e ative o workflow de ingestão para começar a popular o banco)

-	Dashboard: http://localhost:8501
-	n8n: http://localhost:5678 (na primeira inicialização pode apenas dar next quando pedir credenciais ou outros dados, pode preencher com dados aleatórios)
-	API Docs: http://localhost:3000/docs


Decisões, notas e observações:

-	A arquitetura ETL foi feita de maneira modular, composta por 3 arquivos principais: Orquestrador (que chama os outros dois), Ingestão - Bronze, Processamento - Gold.
-	Foi criado também um workflow de limpeza que reseta o Banco de Dados.
-	Em uma primeira versão a arquitetura foi feita de maneira linear com apenas um workflow, sendo funcional do mesmo jeito. Esse workflow está nesse repositório para demonstrar um alternativa à forma como o projeto foi realizado.
-	Foi optado por não conectar diretamente o Dashboard ao PostgreSQL, em visão de preservar a segurança e de possibilitar escalar o backend de maneira independente do banco de dados.
-	API não gera somente dados aleatórios (possui lógica de memória para simular atualizações/updates), para testar e evidenciar a capacidade da pipeline de lidar com atualização de dados
-	API simula erros de rate limit (429) e utiliza a estratégia de retry com backoff, garantindo que a ingestão não falhe em momentos de instabilidade