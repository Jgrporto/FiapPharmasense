.PHONY: setup run help

help:
	@echo "Comandos disponíveis:"
	@echo "  make setup  - Instala as dependências do projeto"
	@echo "  make run    - Executa o Streamlit no arquivo main.py"

setup:
	@echo "Instalando dependências..."
	uv sync

run:
	@echo "Iniciando Streamlit..."
	uv run streamlit run src/main.py

