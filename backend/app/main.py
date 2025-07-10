from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from typing import List, Optional
import pandas as pd
import requests
from datetime import datetime
from fastapi.staticfiles import StaticFiles
import re

from .models import (
    QueryRequest, QueryResponse, SummaryRequest, SummaryResponse,
    UploadResponse, TablesResponse, TableInfo, PublicDataRequest, PublicDataResponse
)
from .database import db_manager
from .file_processor import FileProcessor
from .llm_service import LLMService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Data Explorer and LLM Summary Dashboard",
    description="A web-based dashboard for data exploration and AI-powered insights",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
file_processor = FileProcessor()
llm_service = LLMService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting Data Explorer and LLM Summary Dashboard")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Data Explorer and LLM Summary Dashboard")
    db_manager.close()

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Data Explorer and LLM Summary Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /upload",
            "query": "POST /query",
            "summarize": "POST /summarize",
            "tables": "GET /tables",
            "public-data": "POST /public-data"
        }
    }

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process data files (CSV, JSON, PDF, Excel)."""
    try:
        # Validate file type
        allowed_extensions = ['.csv', '.json', '.pdf', '.xlsx', '.xls']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Save file temporarily
        file_path = file_processor.save_uploaded_file(file_content, file.filename)
        
        try:
            # Process file
            df = file_processor.process_file(file_path, file.filename)
            
            if df is None or df.empty:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to process file or file is empty"
                )
            
            # Generate table name from filename
            table_name = os.path.splitext(file.filename)[0]
            
            # Store in database
            result = db_manager.create_table_from_dataframe(df, table_name)
            
            if not result.get("success", False):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to store data in database: {result.get('error', 'Unknown error')}"
                )
            
            # Get file info
            file_info = file_processor.get_file_info(df)

            # Generate plots if CSV
            plot_urls = []
            if file_extension == '.csv':
                plot_files = file_processor.generate_graphical_analysis(df, file.filename)
                # Convert file paths to URLs
                plot_urls = ["/static/plots/" + os.path.basename(p) for p in plot_files]
            
            return UploadResponse(
                success=True,
                table_name=result["table_name"],
                row_count=file_info['row_count'],
                columns=file_info['columns'],
                message=f"Successfully uploaded {file.filename} with {file_info['row_count']} rows",
                plot_urls=plot_urls
            )
            
        finally:
            # Clean up temporary file
            file_processor.cleanup_file(file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """Execute SQL query and return results."""
    try:
        result = db_manager.execute_query(request.query)
        
        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=f"Query execution failed: {result.get('error', 'Unknown error')}"
            )
        
        return QueryResponse(
            success=True,
            data=result.get("data", []),
            columns=result.get("columns", []),
            row_count=result.get("row_count", 0),
            error=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        return QueryResponse(
            success=False,
            data=[],
            columns=[],
            row_count=0,
            error=str(e)
        )

@app.post("/summarize", response_model=SummaryResponse)
async def generate_summary(request: SummaryRequest):
    """Generate AI-powered summary of data."""
    try:
        # Get table data for summarization
        table_data = db_manager.get_table_data(request.table_name, limit=request.sample_size)
        
        if not table_data.get("success", False):
            raise HTTPException(
                status_code=404,
                detail=f"Table '{request.table_name}' not found or error accessing data"
            )
        
        if not table_data.get("data"):
            raise HTTPException(
                status_code=400,
                detail="No data available for summarization"
            )
        
        # Prepare data info for LLM
        data_info = {
            "row_count": table_data.get("total_count", 0),
            "column_count": len(table_data.get("columns", [])),
            "columns": table_data.get("columns", []),
            "data_types": {},  # Could be enhanced to include actual data types
            "sample_data": table_data.get("data", [])
        }
        
        # Update request with data info
        request.data_info = data_info
        
        # Generate summary using LLM
        summary_response = llm_service.generate_summary(request)
        
        return SummaryResponse(
            success=True,
            summary=summary_response.summary,
            summary_type=summary_response.summary_type,
            provider=summary_response.provider,
            model=summary_response.model,
            tokens_used=summary_response.tokens_used,
            processing_time=summary_response.processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tables", response_model=TablesResponse)
async def get_tables():
    """Get list of all tables in the database."""
    try:
        tables = db_manager.list_tables()
        
        table_list = []
        for table in tables:
            if "error" not in table:
                table_list.append(TableInfo(
                    name=table["name"],
                    row_count=table["info"].get("row_count", 0),
                    columns=table["info"].get("columns", [])
                ))
        
        return TablesResponse(
            success=True,
            tables=table_list,
            count=len(table_list)
        )
        
    except Exception as e:
        logger.error(f"Error getting tables: {e}")
        return TablesResponse(
            success=False,
            tables=[],
            count=0
        )

@app.post("/public-data", response_model=PublicDataResponse)
async def fetch_public_data(request: PublicDataRequest):
    """Fetch data from public APIs (COVID, weather, stocks)."""
    try:
        if request.data_type == "covid":
            return await _fetch_covid_data()
        elif request.data_type == "weather":
            return await _fetch_weather_data(request.params)
        elif request.data_type == "stocks":
            return await _fetch_stocks_data(request.params)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported data type: {request.data_type}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching public data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _fetch_covid_data() -> PublicDataResponse:
    """Fetch COVID-19 data from a public API."""
    try:
        # Using a simple COVID API
        url = "https://disease.sh/v3/covid-19/countries"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Convert to DataFrame format
            df_data = []
            for country in data[:10]:  # Limit to 10 countries
                df_data.append({
                    "country": country.get("country", ""),
                    "cases": country.get("cases", 0),
                    "deaths": country.get("deaths", 0),
                    "recovered": country.get("recovered", 0),
                    "active": country.get("active", 0)
                })
            
            return PublicDataResponse(
                success=True,
                data=df_data,
                columns=["country", "cases", "deaths", "recovered", "active"],
                row_count=len(df_data),
                data_type="covid",
                message="COVID-19 data fetched successfully"
            )
        else:
            raise Exception(f"API returned status code: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error fetching COVID data: {e}")
        return PublicDataResponse(
            success=False,
            data=[],
            columns=[],
            row_count=0,
            data_type="covid",
            message=f"Failed to fetch COVID data: {str(e)}"
        )

async def _fetch_weather_data(params: Optional[dict]) -> PublicDataResponse:
    """Fetch weather data (mock implementation)."""
    try:
        # Mock weather data
        weather_data = [
            {"city": "New York", "temperature": 22, "humidity": 65, "condition": "Sunny"},
            {"city": "London", "temperature": 15, "humidity": 80, "condition": "Cloudy"},
            {"city": "Tokyo", "temperature": 25, "humidity": 70, "condition": "Rainy"},
            {"city": "Sydney", "temperature": 18, "humidity": 75, "condition": "Partly Cloudy"},
            {"city": "Paris", "temperature": 20, "humidity": 60, "condition": "Clear"}
        ]
        
        return PublicDataResponse(
            success=True,
            data=weather_data,
            columns=["city", "temperature", "humidity", "condition"],
            row_count=len(weather_data),
            data_type="weather",
            message="Weather data fetched successfully"
        )
        
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        return PublicDataResponse(
            success=False,
            data=[],
            columns=[],
            row_count=0,
            data_type="weather",
            message=f"Failed to fetch weather data: {str(e)}"
        )

async def _fetch_stocks_data(params: Optional[dict]) -> PublicDataResponse:
    """Fetch stocks data (mock implementation)."""
    try:
        # Mock stocks data
        stocks_data = [
            {"symbol": "AAPL", "price": 150.25, "change": 2.5, "volume": 1000000},
            {"symbol": "GOOGL", "price": 2750.80, "change": -15.20, "volume": 500000},
            {"symbol": "MSFT", "price": 320.45, "change": 8.75, "volume": 750000},
            {"symbol": "AMZN", "price": 3400.00, "change": 25.50, "volume": 800000},
            {"symbol": "TSLA", "price": 750.30, "change": -12.80, "volume": 1200000}
        ]
        
        return PublicDataResponse(
            success=True,
            data=stocks_data,
            columns=["symbol", "price", "change", "volume"],
            row_count=len(stocks_data),
            data_type="stocks",
            message="Stocks data fetched successfully"
        )
        
    except Exception as e:
        logger.error(f"Error fetching stocks data: {e}")
        return PublicDataResponse(
            success=False,
            data=[],
            columns=[],
            row_count=0,
            data_type="stocks",
            message=f"Failed to fetch stocks data: {str(e)}"
        )

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "").lower()
    # Demo logic: simple keyword-based routing
    if any(kw in message for kw in ["summary", "summarize", "overview", "insight"]):
        try:
            tables = db_manager.list_tables()
            if not tables:
                return JSONResponse({"type": "text", "text": "No data available. Please upload a CSV first."})
            table_name = tables[-1]["name"] if isinstance(tables[-1], dict) else tables[-1]
            from .models import SummaryRequest
            req = SummaryRequest(table_name=table_name, sample_size=10)
            summary = llm_service.generate_summary(req)
            return JSONResponse({"type": "text", "text": summary.summary})
        except Exception as e:
            return JSONResponse({"type": "text", "text": "Sorry, I couldn't process your request."})
    elif "graph" in message or "plot" in message or "histogram" in message or "box" in message or "pie" in message:
        # For demo, use the most recent uploaded table if available
        tables = db_manager.list_tables()
        if not tables:
            return JSONResponse({"type": "text", "text": "No data available for plotting. Please upload a CSV first."})
        table_name = tables[-1]["name"] if isinstance(tables[-1], dict) else tables[-1]
        table_data = db_manager.get_table_data(table_name, limit=1000)
        if not table_data.get("success") or not table_data.get("data"):
            return JSONResponse({"type": "text", "text": "No data found in the table for plotting."})
        df = pd.DataFrame(table_data["data"])
        # Try to extract column name from message
        import re
        col_match = re.search(r"(?:of|for|plot|graph|histogram|box|pie) ([\w_]+)", message)
        col = col_match.group(1) if col_match and col_match.group(1) in df.columns else None
        # Generate only for the requested column if found, else all
        if col:
            plot_files = file_processor.generate_graphical_analysis(df[[col]], f"{table_name}_chat.csv")
        else:
            plot_files = file_processor.generate_graphical_analysis(df, f"{table_name}_chat.csv")
        plot_urls = ["/static/plots/" + os.path.basename(p) for p in plot_files]
        return JSONResponse({"type": "graph", "text": f"Here are the graphs for {col or 'your data'}:", "plot_urls": plot_urls})
    elif "sql" in message or "query" in message:
        # For demo, return a sample SQL query
        tables = db_manager.list_tables()
        if not tables:
            return JSONResponse({"type": "text", "text": "No tables found. Please upload data first."})
        table_name = tables[-1]["name"] if isinstance(tables[-1], dict) else tables[-1]
        sql = f"SELECT * FROM {table_name} LIMIT 10;"
        return JSONResponse({"type": "sql", "text": f"Here is a sample SQL query for table '{table_name}':", "sql": sql})
    else:
        # Fallback: try to use LLM summary as a general answer
        try:
            tables = db_manager.list_tables()
            if not tables:
                return JSONResponse({"type": "text", "text": "No data available. Please upload a CSV first."})
            table_name = tables[-1]["name"] if isinstance(tables[-1], dict) else tables[-1]
            from .models import SummaryRequest
            req = SummaryRequest(table_name=table_name, sample_size=10)
            summary = llm_service.generate_summary(req)
            return JSONResponse({"type": "text", "text": summary.summary})
        except Exception as e:
            return JSONResponse({"type": "text", "text": "Sorry, I couldn't process your request."})

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 