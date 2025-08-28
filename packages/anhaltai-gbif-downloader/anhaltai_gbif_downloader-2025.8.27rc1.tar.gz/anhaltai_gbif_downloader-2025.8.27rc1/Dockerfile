FROM python:3.12

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY src/gbif_extractor /gbif_extractor
COPY config/config.yaml /config/config.yaml
COPY data /data

ENV PYTHONUNBUFFERED=1

CMD ["python3", "gbif_extractor/main.py"]
