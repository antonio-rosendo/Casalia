# Image for the forecasts API (ml/app). The API only serves the published
# forecasts, so it needs FastAPI but none of the training stack.
#
#   docker build -t casalia-api .
#   docker run -p 8000:8000 casalia-api        -> http://localhost:8000/docs
FROM python:3.13-slim

WORKDIR /srv
COPY ml/requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY ml/app ./app
COPY web/public/forecasts.json ./forecasts.json
ENV CASALIA_FORECASTS=/srv/forecasts.json

RUN useradd --no-create-home api
USER api

EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
