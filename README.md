# 🦙 RAG with LLaMa 13B — Legal Assistant

Este proyecto implementa un sistema de **Retrieval-Augmented Generation (RAG)** utilizando el modelo **LLaMa 13B Chat** para consultas legales. El objetivo es integrar **transformers de Hugging Face** y **LangChain** para construir un asistente legal que pueda responder preguntas sobre expedientes judiciales y documentos legales.

---

## Características principales

- Uso del modelo `meta-llama/Llama-2-13b-chat-hf` para generación de texto.  
- Integración con LangChain para crear un **pipeline de QA con recuperación de información**.  
- Generación de embeddings con `sentence-transformers/all-MiniLM-L6-v2`.  
- Vector store local usando **Chroma** para búsquedas eficientes.  


---

## Requisitos previos

Antes de ejecutar el notebook, asegúrate de tener instaladas las siguientes librerías:

```bash
pip install transformers==4.33.0 accelerate==0.22.0 einops==0.6.1 langchain==0.0.300 xformers==0.0.21 bitsandbytes==0.41.1 sentence_transformers==2.2.2 chromadb==0.4.12
```

También necesitas:
- Acceso autorizado a los modelos de LLaMa 2.  
- Una GPU con suficiente memoria.  
- Datos legales en archivos `.txt` para indexarlos en la base vectorial.

---

## Ejecución rápida

1. **Inicializa el modelo y embeddings**  
   - Llama 13B se descarga e inicializa automáticamente.  
   - El pipeline usa HuggingFace con `BitsAndBytes` para optimizar memoria.

2. **Carga de documentos**  
   - Almacena tus archivos `.txt` en una carpeta.
   - El código los carga, los divide en chunks y genera embeddings.

3. **Construcción del Vector Store**  
   - Se usa Chroma para almacenar y recuperar información de manera eficiente.

4. **Consulta de expedientes**  
   - Puedes hacer consultas como:
     ```python
     query = "Cual es el estado del Expediente N° 00114-2023-0-2001-JP-FC-07"
     run_my_rag(qa, query)
     ```

---

## Tecnologías utilizadas

- 🐍 Python  
- 🤗 Transformers  
- 🧠 LangChain  
- 🗂️ Chroma  
- 🔢 Sentence Transformers

---


## 📨 Contacto

Si necesitas acceder a la **base de datos**, ten en cuenta que se trata de información proveniente del Poder Judicial de Piura, por lo que su distribución se realiza únicamente de forma directa y controlada, sin publicación abierta.
 **nabanto18@gmail.com**

---

## Notas

- El uso del modelo LLaMa requiere acceso aprobado.  
- Ejecutar en CPU es posible pero muy lento. Se recomienda usar GPU.  
- Ajusta parámetros como `temperature` y `max_new_tokens` según tus necesidades.

---
