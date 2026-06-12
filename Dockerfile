# Usa uma imagem oficial do Python leve
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala as dependências do sistema necessárias para o psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Expõe a porta 8000 conforme o diagrama da arquitetura
EXPOSE 8000

# Comando para iniciar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  