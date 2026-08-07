FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir mlflow[extras] boto3 psycopg2-binary

EXPOSE 5000

CMD ["sh", "-c", "mlflow server --backend-store-uri ${MLFLOW_BACKEND_STORE_URI} --default-artifact-root ${MLFLOW_ARTIFACT_ROOT} --host 0.0.0.0 --port 5000"]
