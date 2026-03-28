FROM python:3.9

RUN apt-get update && apt-get install -y ca-certificates && update-ca-certificates
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org \
    confluent-kafka[avro] certifi fastavro requests
    
COPY consumer.py /app/consumer.py
CMD ["python", "/app/consumer.py"]