# Evidência Aplicação Funcionando - `Logging Terminal`

## Inicialização da Aplicação

```bash
(challenge-artificial-intelligence2) rgf@rafaelgf:~/personal/challenge-artificial-intelligence2$ streamlit run main.py --server.headless true
```

### URLs de Acesso `(Aplicação disponível)`
- **Local URL:** http://localhost:8501
- **Network URL:** http://172.xx.xxx.xxx:8501
- **External URL:** http://177.xxx.xxx.xx:8501

## Processo de Indexação Inicial dos arquivos disponíveis na pasta `./resources`

### 1. Configuração do Sistema 
```
2025-07-04 11:57:00,575 - INFO - Anonymized telemetry enabled
2025-07-04 11:57:00,900 - INFO - Media and project folders verified/created successfully
2025-07-04 11:57:00,924 - INFO - Database setup completed successfully
2025-07-04 11:57:00,925 - INFO - Resource files have changed or state file not found. Re-indexing...
2025-07-04 11:57:00,949 - INFO - ChromaDB collection initialized successfully
```

### 2. Processamento de Arquivos
#### Vídeo
```
2025-07-04 11:57:00,960 - INFO - Sending video for transcription to Groq (Whisper)...
2025-07-04 11:57:03,272 - INFO - HTTP Request: POST https://api.groq.com/openai/v1/audio/transcriptions "HTTP/1.1 200 OK"
2025-07-04 11:57:03,273 - INFO - Video transcription received successfully
2025-07-04 11:57:03,273 - INFO - Successfully processed video file: resources/Dica do professor.mp4 (9 chunks)
```

#### PDF
```
2025-07-04 11:57:03,849 - INFO - Accelerator device: 'cuda:0'
2025-07-04 11:57:08,588 - INFO - Processing document Capítulo do Livro.pdf
2025-07-04 11:57:34,186 - INFO - Finished converting document Capítulo do Livro.pdf in 32.90 sec
2025-07-04 11:57:34,235 - INFO - Successfully processed PDF file: resources/Capítulo do Livro.pdf
```

#### Texto
```
2025-07-04 11:57:34,289 - INFO - Successfully processed text file: resources/Apresentação.txt
```

#### Imagem
```
2025-07-04 11:57:39,770 - INFO - Processing document Infografico-1.jpg
2025-07-04 11:57:53,069 - INFO - Finished converting document Infografico-1.jpg in 18.78 sec
2025-07-04 11:57:53,073 - INFO - Successfully processed image file: resources/Infografico-1.jpg
```

#### JSON
```
2025-07-04 11:57:53,081 - INFO - Successfully processed JSON file: resources/Exercícios.json (5 items)
```

### 3. Conclusão da Indexação
```
2025-07-04 11:58:19,407 - INFO - Successfully indexed 17 documents in ChromaDB
2025-07-04 11:58:19,410 - INFO - Indexing complete and new state saved
```

## Interações do Usuário

### Pergunta 1: "sobre o que podemos falar?" `(Avaliando Contexto indexado no vector store)`
```
2025-07-04 11:59:22,602 - INFO - Found 5 relevant documents for query: 'sobre o que podemos falar?'
2025-07-04 11:59:23,476 - INFO - Scope validation: {'in_scope': True, 'confidence': 0.8}
2025-07-04 11:59:24,323 - INFO - Question classified as: scope with concise verbosity
2025-07-04 11:59:24,963 - INFO - Question analysis completed: beginner level
2025-07-04 11:59:26,306 - INFO - Successfully generated adaptive response
```

#### Geração de Mídia
- **Áudio:** `2025-07-04 11:59:33,831 - INFO - Successfully generated audio file: files_chat/audios/audio_7dd9ad0c.mp3`
- **Vídeo:** `2025-07-04 11:59:58,892 - INFO - Successfully generated video file: files_chat/videos/video_7dd9ad0c.mp4`

### Pergunta 2: "como criar um botao em html" `(Avaliando resposta dentro do contexto)`
```
2025-07-04 11:59:59,354 - INFO - Found 5 relevant documents for query: 'como criar um botao em html'
2025-07-04 12:00:00,211 - INFO - Scope validation: {'in_scope': True, 'confidence': 0.9}
2025-07-04 12:00:00,899 - INFO - Question classified as: technical with moderate verbosity
2025-07-04 12:00:01,533 - INFO - Question analysis completed: beginner level
2025-07-04 12:00:03,227 - INFO - Successfully generated adaptive response
```

#### Geração de Mídia
- **Áudio:** `2025-07-04 12:00:33,535 - INFO - Successfully generated audio file: files_chat/audios/audio_ddc6ea8a.mp3`
- **Vídeo:** `2025-07-04 12:02:00,713 - INFO - Successfully generated video file: files_chat/videos/video_ddc6ea8a.mp4`

### Pergunta 3: "quero falar de futebol. qual time vai ganhar hoje" `(Avaliando pergunta fora do contexto [guardrail])`
```
2025-07-04 12:03:45,833 - INFO - Found 5 relevant documents for query: 'quero falar de futebol. qual time vai ganhar hoje'
2025-07-04 12:03:46,610 - INFO - Scope validation: {'in_scope': False, 'confidence': 0.0}
2025-07-04 12:03:46,612 - INFO - Question out of scope: A pergunta do usuário está relacionada a futebol
2025-07-04 12:03:48,119 - INFO - Content analysis completed: 2 technologies, 5 topics identified
```