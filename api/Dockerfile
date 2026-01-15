# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código
COPY . .

# Comando para rodar a API quando o container ligar
# O host 0.0.0.0 é obrigatório para o Docker funcionar
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]