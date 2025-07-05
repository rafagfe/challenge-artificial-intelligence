# Testes da Refatoração

Este diretório contém todos os testes unitários e de integração para a refatoração do sistema de aprendizado adaptativo.

## Estrutura dos Testes

### Testes Principais

1. **test_config.py** - Testa as funções de configuração
   - Carregamento de variáveis de ambiente
   - Validação de API keys
   - Configurações do Streamlit e ChromaDB

2. **test_processors.py** - Testa os processadores de arquivos
   - Processamento de texto, PDF, JSON, imagens e vídeos
   - Tratamento de erros e arquivos inválidos

3. **test_ai_client.py** - Testa os clientes de IA
   - Criação de clientes Groq, OpenAI e LangSmith
   - Tratamento de API keys válidas/inválidas

4. **test_core_indexing.py** - Testa o sistema de indexação
   - Processamento de diretórios
   - Indexação de documentos
   - Gerenciamento de estado

5. **test_media_generators.py** - Testa os geradores de mídia
   - Geração de áudio (gTTS, ElevenLabs, OpenAI)
   - Geração de vídeo (D-ID)
   - Tratamento de erros de API

6. **test_ui_components.py** - Testa os componentes da interface
   - Componentes de entrada de dados
   - Componentes de exibição
   - Controles da sidebar

7. **test_main_application.py** - Testa a aplicação principal
   - Importação de módulos
   - Fluxo da aplicação
   - Integração entre componentes

8. **test_helpers.py** - Testa funções auxiliares
   - Validação de dados
   - Formatação de strings
   - Tratamento de erros

## Como Executar os Testes

### Executar todos os testes:
```bash
cd /home/rgf/personal/challenge-artificial-intelligence2
python -m pytest tests/ -v
```

### Executar um teste específico:
```bash
python -m pytest tests/test_config.py -v
```

### Executar testes com cobertura:
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Executar testes em paralelo:
```bash
python -m pytest tests/ -n auto
```

## Dependências de Teste

As seguintes bibliotecas são necessárias para executar os testes:

```bash
pip install pytest pytest-cov pytest-mock pytest-xdist
```

## Cobertura de Testes

Os testes cobrem:

- ✅ Configuração e carregamento de settings
- ✅ Processamento de diferentes tipos de arquivo
- ✅ Criação e gerenciamento de clientes de IA
- ✅ Sistema de indexação e busca
- ✅ Geração de mídia (áudio e vídeo)
- ✅ Componentes da interface do usuário
- ✅ Integração entre módulos
- ✅ Tratamento de erros e casos extremos

## Padrões de Teste

### Estrutura dos Testes

Cada arquivo de teste segue o padrão:

```python
class TestModuleName:
    """Test module description."""
    
    def test_specific_function(self):
        """Test specific functionality."""
        # Arrange
        input_data = "test_input"
        
        # Act
        result = function_to_test(input_data)
        
        # Assert
        assert result == expected_output
```

### Mocking

Os testes usam `unittest.mock` para simular:
- Chamadas de API externas
- Operações de arquivo
- Componentes do Streamlit
- Clientes de IA

### Testes de Integração

Testes de integração verificam:
- Fluxo completo da aplicação
- Comunicação entre módulos
- Persistência de dados
- Tratamento de erros em cenários reais

### Casos de Teste

Cada função é testada com:
- Entrada válida normal
- Entrada inválida/nula
- Casos extremos
- Tratamento de erros
- Diferentes tipos de dados

## Estrutura de Arquivos

```
tests/
├── __init__.py
├── pytest.ini                 # Configuração do pytest
├── README.md                  # Este arquivo
├── test_config.py             # Testes de configuração
├── test_processors.py         # Testes de processadores
├── test_ai_client.py          # Testes de clientes de IA
├── test_core_indexing.py      # Testes de indexação
├── test_media_generators.py   # Testes de geração de mídia
├── test_ui_components.py      # Testes de componentes UI
├── test_main_application.py   # Testes da aplicação principal
└── test_helpers.py            # Testes de funções auxiliares
```

## Métricas de Qualidade

Os testes garantem:

- **Cobertura de código**: >80% das linhas testadas
- **Cobertura de funções**: >90% das funções testadas
- **Casos de erro**: Todos os casos de erro tratados
- **Integração**: Todos os fluxos principais testados
- **Robustez**: Tratamento de entradas inválidas

## Execução Contínua

Para executar testes automaticamente durante o desenvolvimento:

```bash
# Instalar pytest-watch
pip install pytest-watch

# Executar testes automaticamente
ptw tests/
```

## Debugging

Para debug dos testes:

```bash
# Executar com output detalhado
python -m pytest tests/ -v -s

# Parar no primeiro erro
python -m pytest tests/ -x

# Executar apenas testes que falharam
python -m pytest tests/ --lf
```

## Contribuindo

Ao adicionar novos testes:

1. Siga o padrão de nomenclatura: `test_<module>_<function>`
2. Use docstrings descritivas
3. Teste casos positivos e negativos
4. Use mocks para dependências externas
5. Verifique a cobertura de código

## Notas Importantes

- Os testes são independentes e podem ser executados em qualquer ordem
- Nenhum teste modifica arquivos do sistema permanentemente
- Todos os testes usam arquivos temporários quando necessário
- Mocks são usados para evitar chamadas reais de API
- A configuração do pytest está em `pytest.ini` 