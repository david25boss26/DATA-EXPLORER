# Local LLM Setup Guide

This guide explains how to set up local Language Models (LLMs) for the Data Explorer and LLM Summary Dashboard.

## Overview

The application supports three different LLM providers:
1. **Ollama** (Recommended - Easiest setup)
2. **llama-cpp-python** (Good performance)
3. **Transformers** (Most flexible)

## Option 1: Ollama (Recommended)

Ollama is the easiest way to run local LLMs with minimal setup.

### Installation

#### macOS/Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Download from: https://ollama.ai/download

### Setup

1. **Install a model** (choose one):
   ```bash
   # Llama 2 (7B parameters - good balance)
   ollama pull llama2
   
   # Llama 2 Chat (better for conversations)
   ollama pull llama2:7b-chat
   
   # Mistral (7B parameters - good performance)
   ollama pull mistral
   
   # Code Llama (good for technical tasks)
   ollama pull codellama:7b
   ```

2. **Configure the application**:
   Edit `backend/.env`:
   ```env
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   ```

3. **Start Ollama**:
   ```bash
   ollama serve
   ```

### Usage
- Ollama will run on `http://localhost:11434`
- The application will automatically connect to it
- Models are downloaded once and cached locally

## Option 2: llama-cpp-python

For better performance and more control over model parameters.

### Installation

1. **Install llama-cpp-python**:
   ```bash
   cd backend
   pip install llama-cpp-python
   ```

2. **Download a GGUF model**:
   - Visit: https://huggingface.co/TheBloke
   - Download a GGUF model (e.g., `llama-2-7b-chat.gguf`)
   - Place it in `backend/models/`

3. **Configure the application**:
   Edit `backend/.env`:
   ```env
   LLM_PROVIDER=llama-cpp
   LLM_MODEL_PATH=./models/llama-2-7b-chat.gguf
   ```

### Recommended Models

- **Llama 2 7B Chat**: `llama-2-7b-chat.gguf`
- **Mistral 7B**: `mistral-7b-instruct-v0.2.Q4_K_M.gguf`
- **Code Llama 7B**: `codellama-7b-instruct.Q4_K_M.gguf`

## Option 3: Transformers

For maximum flexibility and Hugging Face model support.

### Installation

1. **Install transformers**:
   ```bash
   cd backend
   pip install transformers torch accelerate
   ```

2. **Download a model**:
   ```python
   from transformers import AutoTokenizer, AutoModelForCausalLM
   
   model_name = "microsoft/DialoGPT-medium"  # Example
   tokenizer = AutoTokenizer.from_pretrained(model_name)
   model = AutoModelForCausalLM.from_pretrained(model_name)
   ```

3. **Configure the application**:
   Edit `backend/.env`:
   ```env
   LLM_PROVIDER=transformers
   LLM_MODEL_PATH=./models/your-model-name
   ```

## Configuration

### Environment Variables

Edit `backend/.env` with your preferred settings:

```env
# LLM Configuration
LLM_PROVIDER=ollama                    # Options: ollama, llama-cpp, transformers
LLM_MODEL_PATH=./models/llama-2-7b-chat.gguf  # For llama-cpp and transformers
OLLAMA_BASE_URL=http://localhost:11434 # For Ollama

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# Database Configuration
DUCKDB_PATH=./data/database.duckdb

# File Upload Configuration
MAX_FILE_SIZE=104857600  # 100MB
UPLOAD_DIR=./uploads

# Public Data APIs
ENABLE_PUBLIC_APIS=true
```

## Model Recommendations

### For Data Analysis Tasks

1. **Llama 2 7B Chat** (Best overall)
   - Good at understanding data context
   - Balanced performance and resource usage
   - Available via Ollama: `ollama pull llama2:7b-chat`

2. **Mistral 7B** (Fast and efficient)
   - Excellent performance for its size
   - Good at structured reasoning
   - Available via Ollama: `ollama pull mistral`

3. **Code Llama 7B** (Technical tasks)
   - Excellent for SQL and data processing
   - Good at understanding technical concepts
   - Available via Ollama: `ollama pull codellama:7b`

### Resource Requirements

| Model Size | RAM Required | GPU VRAM | Performance |
|------------|--------------|----------|-------------|
| 7B         | 8GB          | 4GB      | Good        |
| 13B        | 16GB         | 8GB      | Better      |
| 30B        | 32GB         | 16GB     | Best        |

## Troubleshooting

### Common Issues

1. **"LLM not available" error**
   - Check if your LLM service is running
   - Verify the model path in `.env`
   - Check logs for specific error messages

2. **Slow response times**
   - Use a smaller model (7B instead of 13B)
   - Enable GPU acceleration if available
   - Reduce the sample size in the UI

3. **Out of memory errors**
   - Use a smaller model
   - Close other applications
   - Reduce batch size in configuration

### Performance Optimization

1. **GPU Acceleration** (if available):
   ```bash
   # For llama-cpp-python
   CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
   
   # For transformers
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **Model Quantization**:
   - Use quantized models (Q4_K_M, Q5_K_M)
   - Reduces memory usage with minimal quality loss

3. **Batch Processing**:
   - Process multiple queries together
   - Use appropriate sample sizes

## Testing Your Setup

1. **Start the backend**:
   ```bash
   cd backend
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   uvicorn app.main:app --reload
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm start
   ```

3. **Test the LLM**:
   - Upload a sample file
   - Go to the "AI Summary" tab
   - Generate a summary
   - Check the response quality

## Fallback Mode

If no LLM is configured or available, the application will use a fallback mode that provides basic data analysis without AI-powered insights.

## Support

For issues with specific LLM providers:
- **Ollama**: https://github.com/ollama/ollama
- **llama-cpp-python**: https://github.com/abetlen/llama-cpp-python
- **Transformers**: https://github.com/huggingface/transformers 