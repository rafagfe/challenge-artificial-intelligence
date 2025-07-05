# 🧪 CI Simples

Este projeto implementa um processo **robusto de CI** para demonstrar conhecimento de integração contínua.

## 📋 O que faz

### CI (Continuous Integration)
- ✅ **Testes automatizados** quando há push/PR
- 🎨 **Formatação** com Black
- 📏 **Linting** com Flake8
- 📊 **Cobertura** de código com Codecov
- 🔒 **Security scanning** com Safety e Bandit

## 🔧 Como funciona

1. **Push/PR** → Executa testes e análise de qualidade
2. **Security scan** → Verifica vulnerabilidades (non-blocking)
3. **Coverage** → Upload automático para Codecov
4. **Quality gates** → Merge apenas se tudo passar

## 📁 Arquivos

- `.github/workflows/simple-ci.yml` - Pipeline principal
- `.pre-commit-config.yaml` - Hooks básicos

## 🛠️ Setup local

```bash
# Instalar pre-commit
pip install pre-commit
pre-commit install

# Executar testes
pytest tests/ --cov=src

# Validar formato
black src/ tests/
flake8 src/ tests/

# Security scan
pip install safety bandit
safety check
bandit -r src/
```

## 🚀 Deploy Manual

O deploy é feito manualmente via Docker:

```bash
# Build e execução
docker-compose up --build

# Acesso
http://localhost:8501
```

**Objetivo**: Demonstrar processo completo de CI de forma robusta e funcional. 