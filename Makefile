.PHONY: setup run help build up down logs restart ps

help:
	@echo "Comandos disponíveis:"
	@echo "  make setup    - Instala as dependências do projeto"
	@echo "  make run      - Executa o Streamlit no arquivo main.py"
	@echo "  make build    - Constrói a imagem Docker"
	@echo "  make up       - Sobe o container Docker"
	@echo "  make down     - Para o container Docker"
	@echo "  make logs     - Mostra os logs do container"
	@echo "  make restart  - Reinicia o container Docker"
	@echo "  make ps       - Lista containers em execução"

setup:
	@echo "Instalando dependências..."
	uv sync

run:
	@echo "Iniciando Streamlit..."
	uv run streamlit run src/main.py

build:
	@echo "Construindo imagem Docker..."
	docker compose build

up:
	@echo "Subindo container Docker..."
	docker compose up -d

down:
	@echo "Parando container Docker..."
	docker compose down

logs:
	@echo "Mostrando logs do container..."
	docker compose logs -f

restart:
	@echo "Reiniciando container Docker..."
	docker compose restart

ps:
	@echo "Containers em execução:"
	docker compose ps

