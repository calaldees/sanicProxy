FROM python:alpine

WORKDIR /app/

RUN pip install --no-cache \
    sanic \
    aiohttp \
&& true

COPY . .

CMD ["python3", "-m", "sanic", "proxy:app", "--host=0.0.0.0", "--port=8000", "--debug", "--single-process"]
