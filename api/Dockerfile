FROM python:3.10-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia arquivos de requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código
COPY . .

# Comando para rodar a api assim que o docker ligar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]