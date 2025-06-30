# Data Explorer and LLM Summary Dashboard

A web-based dashboard that allows users to upload data files (CSV, JSON, PDF, Excel), explore and query the data using SQL, and receive insights or summaries using a local LLM without any paid API keys.

## 🚀 Features

- **📁 File Upload**: Support for CSV, JSON, PDF, and Excel files
- **🔍 Data Querying**: SQL editor with DuckDB backend for fast queries
- **📄 PDF Data Extraction**: Extract structured content from PDFs
- **🤖 Local LLM Summarization**: Generate insights using local language models
- **🌐 Public Data APIs**: Pull data from free public APIs
- **📊 Interactive Data Tables**: Sort, paginate, and export query results
- **🎨 Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS

## 🛠️ Tech Stack

### Frontend
- **React 18** with modern hooks and functional components
- **Tailwind CSS** for styling and responsive design
- **Lucide React** for beautiful icons
- **React Dropzone** for file uploads
- **React Syntax Highlighter** for SQL editing
- **Axios** for API communication

### Backend
- **FastAPI** for high-performance API
- **DuckDB** for in-memory/persisted database
- **Pandas** for data manipulation
- **PDFPlumber** for PDF text extraction
- **Local LLM Support**: Ollama, llama-cpp-python, Transformers
- **LangChain** for prompt templating

### Database
- **DuckDB** - Fast analytical database with SQL support

## 📦 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- 8GB+ RAM (for LLM functionality)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd data_explorer_llm_dashboard

# Run the setup script
./setup.sh  # On macOS/Linux
# OR
setup.bat   # On Windows
```

### 2. Configure LLM (Optional but Recommended)

See [LLM_SETUP.md](./LLM_SETUP.md) for detailed instructions.

**Quick Ollama setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2:7b-chat

# Start Ollama
ollama serve
```

### 3. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 4. Access the Dashboard

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 Usage Guide

### 1. Upload Data Files

1. Go to the "Upload Data" tab
2. Drag and drop or click to browse for files
3. Supported formats: CSV, JSON, PDF, Excel (.xlsx, .xls)
4. Files are automatically processed and stored in DuckDB

### 2. Query Your Data

1. Navigate to the "SQL Query" tab
2. Write SQL queries in the editor
3. Use sample queries or write your own
4. View results in the interactive data table
5. Export results as CSV

### 3. Generate AI Summaries

1. Go to the "AI Summary" tab
2. Select a table to analyze
3. Choose summary type:
   - **General**: Comprehensive overview
   - **Statistical**: Quantitative insights
   - **Business**: Actionable recommendations
4. Adjust sample size as needed
5. Generate AI-powered insights

### 4. Fetch Public Data

1. Visit the "Public Data" tab
2. Choose from available sources:
   - COVID-19 statistics
   - Weather data
   - Stock market information
3. Data is automatically imported for analysis

## 🔧 Configuration

### Environment Variables

Edit `backend/.env`:

```env
# LLM Configuration
LLM_PROVIDER=ollama                    # ollama, llama-cpp, transformers
LLM_MODEL_PATH=./models/llama-2-7b-chat.gguf
OLLAMA_BASE_URL=http://localhost:11434

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

## 📊 Sample Data

The project includes sample data files in the `sample_data/` directory:

- `sample.csv` - Employee data with 10 records
- `sample.json` - Same data in JSON format

Use these files to test the application functionality.

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload data files |
| `/query` | POST | Execute SQL queries |
| `/summarize` | POST | Generate AI summaries |
| `/tables` | GET | List available tables |
| `/public-data` | POST | Fetch public data |
| `/health` | GET | Health check |

## 🎯 LLM Integration

The application supports multiple local LLM providers:

### Ollama (Recommended)
- Easiest setup
- Automatic model management
- Good performance

### llama-cpp-python
- Better performance
- More control over parameters
- Requires manual model download

### Transformers
- Maximum flexibility
- Hugging Face model support
- Higher resource requirements

See [LLM_SETUP.md](./LLM_SETUP.md) for detailed setup instructions.

## 🚀 Deployment

### Development
```bash
# Backend with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development server
npm start
```

### Production
```bash
# Build frontend
cd frontend
npm run build

# Serve with production server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend connection failed**
   - Check if backend is running on port 8000
   - Verify firewall settings
   - Check logs for specific errors

2. **LLM not working**
   - Verify LLM service is running
   - Check model path in `.env`
   - Ensure sufficient RAM/VRAM

3. **File upload errors**
   - Check file size limits
   - Verify file format support
   - Ensure upload directory exists

4. **Database errors**
   - Check DuckDB file permissions
   - Verify data directory exists
   - Restart backend if needed

### Performance Tips

- Use quantized models for better performance
- Enable GPU acceleration if available
- Adjust sample sizes based on your data
- Use appropriate model sizes for your hardware

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [DuckDB](https://duckdb.org/) for fast analytical database
- [Ollama](https://ollama.ai/) for easy local LLM deployment
- [FastAPI](https://fastapi.tiangolo.com/) for modern Python web framework
- [React](https://reactjs.org/) for the frontend framework
- [Tailwind CSS](https://tailwindcss.com/) for utility-first CSS

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check the README and LLM_SETUP.md
- **Community**: Join discussions in the repository

---

**Built with ❤️ for privacy-focused data analysis** 