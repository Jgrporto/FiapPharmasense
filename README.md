# 🚚 PharmaSense AI - Otimização Logística e Distribuição

Sistema de monitoramento e análise de eficiência da cadeia de suprimentos farmacêutica, desenvolvido para otimizar processos logísticos, reduzir custos e melhorar a sustentabilidade ambiental.

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Configuração](#instalação-e-configuração)
- [Uso](#uso)
- [Dados](#dados)
- [Notebooks](#notebooks)
- [Docker](#docker)
- [Comandos Make](#comandos-make)

## 🎯 Sobre o Projeto

O **PharmaSense AI** é uma plataforma de análise e otimização logística desenvolvida para o setor farmacêutico. O sistema oferece:

- **Dashboard Interativo**: Visualização em tempo real de métricas de desempenho logístico
- **Análise de Estoque**: Monitoramento de demanda, estoque e stock out
- **Otimização de Rotas**: Análise de eficiência de distribuição por região e estado
- **Sustentabilidade**: Rastreamento de emissões de CO2 e impacto ambiental
- **Alertas Inteligentes**: Identificação de atrasos, rupturas de estoque e condições críticas

## ✨ Funcionalidades

### Dashboard de Logística
- Métricas de impacto e desempenho (redução de tempo, custos, emissões)
- Análise de eficiência de distribuição ao longo do tempo
- Desempenho por região e estado
- Monitoramento de rotas com alertas de condições
- Análise de otimização de custo e sustentabilidade

### Dashboard de Estoque e Demanda
- Métricas principais de estoque (taxa de atendimento, stock out, demanda não atendida)
- Análise temporal de demanda vs estoque
- Stock out por região e estado
- Análise de atendimento e nível de serviço
- Monitoramento de estoque baixo e alertas de stock out

## 🛠️ Tecnologias Utilizadas

### Backend e Análise
- **Python 3.12+**: Linguagem principal
- **Pandas**: Manipulação e análise de dados
- **NumPy**: Computação numérica
- **Scikit-learn**: Machine learning e análise preditiva

### Visualização e Dashboard
- **Streamlit**: Framework para criação de dashboards interativos
- **Plotly**: Gráficos interativos e visualizações avançadas
- **Matplotlib**: Visualizações estáticas
- **Seaborn**: Visualizações estatísticas

### Banco de Dados
- **PostgreSQL 15**: Banco de dados relacional
- **psycopg2**: Driver Python para PostgreSQL

### Infraestrutura
- **Docker**: Containerização da aplicação
- **Docker Compose**: Orquestração de containers
- **uv**: Gerenciador de pacotes Python moderno e rápido

### Desenvolvimento
- **Jupyter Notebooks**: Análise exploratória de dados
- **ipykernel**: Kernel Jupyter para Python

## 📁 Estrutura do Projeto

```
FiapPharmasense/
├── assets/                      # Arquivos de dados
│   ├── demanda_estoque.csv      # Dados simulados de demanda e estoque
│   └── logistica_simulada.csv   # Dados simulados de logística
├── notebooks/                   # Notebooks Jupyter para análise
│   ├── importar_dados.ipynb     # Importação de dados CSV para PostgreSQL
│   ├── analise_logistica.ipynb  # Análise exploratória de dados logísticos
│   └── analise_estoque.ipynb    # Análise exploratória de estoque e demanda
├── src/                         # Código fonte da aplicação
│   └── main.py                  # Aplicação Streamlit principal
├── docker-compose.yml           # Configuração Docker Compose
├── Dockerfile                   # Imagem Docker da aplicação
├── Makefile                     # Comandos auxiliares
├── pyproject.toml               # Configuração do projeto e dependências
├── uv.lock                      # Lock file das dependências (gerado automaticamente)
├── styles.css                   # Estilos customizados para o Streamlit
└── README.md                    # Este arquivo
```

## 📦 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.12+**
- **Docker** e **Docker Compose** (para execução via containers)
- **uv** (gerenciador de pacotes Python) - pode ser instalado com: `pip install uv`
- **PostgreSQL 15** (se executar localmente sem Docker)

## 🚀 Instalação e Configuração

### Opção 1: Execução com Docker (Recomendado)

1. **Clone o repositório** (se aplicável):
```bash
git clone <url-do-repositorio>
cd FiapPharmasense
```

2. **Construa e inicie os containers**:
```bash
make build
make up
```

Ou manualmente:
```bash
docker compose build
docker compose up -d
```

3. **Acesse o dashboard**:
   - Abra seu navegador em: `http://localhost:8501`

### Opção 2: Execução Local

1. **Instale as dependências**:
```bash
make setup
```

Ou manualmente:
```bash
uv sync
```

2. **Configure o banco de dados PostgreSQL**:
   - Crie um arquivo `.env` na raiz do projeto:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pharmasense
DB_USER=pharmasense
DB_PASSWORD=pharmasense_pass
```

3. **Inicie o banco de dados** (se usar Docker apenas para PostgreSQL):
```bash
docker compose up -d postgres
```

4. **Importe os dados** (opcional):
   - Execute o notebook `notebooks/importar_dados.ipynb` para importar os dados CSV para o PostgreSQL

5. **Execute a aplicação Streamlit**:
```bash
make run
```

Ou manualmente:
```bash
uv run streamlit run src/main.py
```

## 💻 Uso

### Dashboard Streamlit

Após iniciar a aplicação, você terá acesso a um dashboard interativo com duas abas principais:

#### 📦 Aba Logística
- **Métricas de Impacto**: Redução de tempo de resposta, tempo médio de entrega, taxa de atraso, pegada de carbono
- **Visualizações**: Tendências de eficiência, desempenho por região, análise de custo vs. emissões
- **Monitoramento**: Tabela de rotas com destaque para atrasos e condições críticas

#### 📊 Aba Estoque e Demanda
- **Métricas de Estoque**: Taxa de atendimento, stock out total, estoque final médio, demanda não atendida
- **Visualizações**: Tendências de demanda e estoque, stock out por região, taxa de atendimento
- **Alertas**: Monitoramento de estoque baixo e stock out com destaque visual

### Filtros Disponíveis

O dashboard oferece filtros na barra lateral:
- **Período**: Selecione um intervalo de datas
- **Região**: Filtre por uma ou mais regiões
- **Estado**: Filtre por estados específicos (quando disponível)

## 📊 Dados

O projeto utiliza dados simulados para demonstração:

### `logistica_simulada.csv`
Contém dados de rotas logísticas com as seguintes informações:
- Rota_ID, Data, Região, Estado
- Status (Entregue, Atrasado)
- Tempo_Resposta_Previsto, Tempo_Resposta_Real
- Custo_Logistico_USD
- Emissao_CO2_kg

### `demanda_estoque.csv`
Contém dados de demanda e estoque com:
- Data, Estado, Região
- Demanda_Diaria, Demanda_Atendida, Demanda_Nao_Atendida
- Estoque_Disponivel, Estoque_Final
- Stock_Out, Reabastecimento
- Taxa_Atendimento
- Indicadores de Estoque_Baixo e Stock_Out

## 📓 Notebooks

O projeto inclui três notebooks Jupyter para análise e importação de dados:

### `importar_dados.ipynb`
- Importa dados dos arquivos CSV para o banco de dados PostgreSQL
- Cria as tabelas `logistica` e `demanda_estoque`
- Requer configuração das variáveis de ambiente do banco de dados

### `analise_logistica.ipynb`
- Análise exploratória dos dados de logística
- Análise de tempos de entrega por região e estado
- Análise de custos logísticos e emissões de CO2
- Identificação de padrões e tendências

### `analise_estoque.ipynb`
- Análise detalhada de demanda e estoque
- Análise de stock out e demanda não atendida
- Métricas de atendimento e nível de serviço
- Análise temporal de estoque

## 🐳 Docker

### Serviços Docker Compose

O projeto utiliza Docker Compose com dois serviços:

#### `streamlit`
- Container da aplicação Streamlit
- Porta: `8501`
- Volumes montados: `./assets`, `./src`
- Build a partir do `Dockerfile`

#### `postgres`
- Banco de dados PostgreSQL 15
- Porta: `5432`
- Database: `pharmasense`
- User: `pharmasense`
- Password: `pharmasense_pass`
- Volume persistente para dados

### Comandos Docker Úteis

```bash
# Construir imagens
docker compose build

# Iniciar containers
docker compose up -d

# Parar containers
docker compose down

# Ver logs
docker compose logs -f

# Reiniciar containers
docker compose restart

# Listar containers
docker compose ps
```

## 🔧 Comandos Make

O projeto inclui um `Makefile` com comandos auxiliares:

```bash
make setup      # Instala as dependências do projeto
make run        # Executa o Streamlit no arquivo main.py
make build      # Constrói a imagem Docker
make up         # Sobe o container Docker
make down       # Para o container Docker
make logs       # Mostra os logs do container
make restart    # Reinicia o container Docker
make ps         # Lista containers em execução
make help       # Mostra todos os comandos disponíveis
```

## 🎨 Personalização

### Estilos Customizados

O projeto inclui um arquivo `styles.css` com tema customizado para o Streamlit:
- Tema escuro futurista
- Cores personalizadas (ciano, azul)
- Estilização de cards, KPIs e componentes

Para aplicar os estilos, o Streamlit deve ser configurado para usar o arquivo CSS (geralmente via configuração do Streamlit ou tema customizado).

## 📝 Notas Importantes

- Os dados são simulados para fins de demonstração
- O projeto utiliza `uv` como gerenciador de pacotes Python moderno
- As configurações do banco de dados podem ser ajustadas no arquivo `.env`
- O dashboard utiliza cache de dados (TTL de 60 segundos) para melhor performance

## 🤝 Contribuindo

Este é um projeto acadêmico desenvolvido para a FIAP. Para contribuições:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos no contexto do curso FIAP.

## 👥 Autores

Projeto desenvolvido para o **PharmaSense AI** - Otimização Logística e Distribuição.

---

**PharmaSense AI** - Transformando a cadeia de suprimentos farmacêutica através de dados e inteligência artificial.

