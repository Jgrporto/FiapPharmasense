FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

RUN useradd -m -u 1000 appuser

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY src/ ./src/
COPY assets/ ./assets/
COPY styles.css ./

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

