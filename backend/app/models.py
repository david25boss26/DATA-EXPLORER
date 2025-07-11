from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pandas as pd

class QueryRequest(BaseModel):
    query: str
    table_name: Optional[str] = None

class QueryResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    error: Optional[str] = None

class SummaryRequest(BaseModel):
    table_name: str
    sample_size: int = 100
    summary_type: str = "general"  # general, statistical, insights
    data_info: Optional[Dict[str, Any]] = None

class SummaryResponse(BaseModel):
    success: bool
    summary: str
    summary_type: str
    provider: str
    model: str
    tokens_used: int
    processing_time: float
    error: Optional[str] = None

class UploadResponse(BaseModel):
    success: bool
    table_name: str
    row_count: int
    columns: List[str]
    message: str
    plot_data: Optional[list] = None
    error: Optional[str] = None

class TableInfo(BaseModel):
    name: str
    row_count: int
    columns: List[str]

class TablesResponse(BaseModel):
    tables: List[TableInfo]

class PublicDataRequest(BaseModel):
    source: str  # "covid", "weather", "stocks", etc.
    params: Optional[Dict[str, Any]] = None

class PublicDataResponse(BaseModel):
    success: bool
    table_name: str
    row_count: int
    message: str
    error: Optional[str] = None 