# SettingsOS

Uma biblioteca Python com ferramentas essenciais para desenvolvimento de RPA (Robotic Process Automation) e/ou ML (Machine Learning), oferecendo recursos para conexão com bancos de dados, logging, estruturação de projetos, ORM e monitoramento de performance.

> OBS.: O importe da seguinte maneira:
>
> from settings_os import ...
>
> import settings_os as sos

## 🚀 Recursos

### 📊 Connection

Módulo flexível para conexão com diversos bancos de dados:

- SQLite
- MySQL
- PostgreSQL
- SQL Server

### 📝 Logs

Sistema de logging avançado com capacidade de:

- Gerar logs em arquivo
- Registrar logs em banco de dados (quando integrado com Connection)
- Personalização de formatos e níveis de log

### 🏗️ Make Structure

Gerador de estruturas de projeto:

- MVC simplificado
- Estrutura para projetos ML
- Estruturas personalizadas via configuração

### 🔄 ORM

Mapeamento Objeto-Relacional simplificado:

- Criação de entidades a partir de DataFrames
- Mapeamento de tabelas existentes

### ⚡ Performance

Decorators para monitoramento de performance:

- Medição de tempo de execução
- Monitoramento de uso de memória RAM

## 📦 Instalação

```bash
pip install settings-os

```

## 🔧 Requisitos

Python 3.12+
