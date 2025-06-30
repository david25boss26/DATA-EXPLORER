import pandas as pd
import json
import pdfplumber
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class FileProcessor:
    """Handles file upload and processing for various file formats."""
    
    def __init__(self, upload_dir: str = "./uploads"):
        """Initialize file processor with upload directory."""
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    def process_file(self, file_path: str, filename: str) -> Optional[pd.DataFrame]:
        """Process uploaded file and return DataFrame."""
        try:
            file_extension = Path(filename).suffix.lower()
            
            if file_extension == '.csv':
                return self._process_csv(file_path)
            elif file_extension == '.json':
                return self._process_json(file_path)
            elif file_extension == '.pdf':
                return self._process_pdf(file_path)
            elif file_extension in ['.xlsx', '.xls']:
                return self._process_excel(file_path)
            else:
                logger.error(f"Unsupported file format: {file_extension}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            return None
    
    def _process_csv(self, file_path: str) -> Optional[pd.DataFrame]:
        """Process CSV file."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    logger.info(f"Successfully read CSV with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                logger.error("Failed to read CSV with any encoding")
                return None
            
            # Clean column names
            df.columns = [str(col).strip().replace(' ', '_').replace('-', '_') for col in df.columns]
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            return None
    
    def _process_json(self, file_path: str) -> Optional[pd.DataFrame]:
        """Process JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                # List of objects
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Single object or nested structure
                if any(isinstance(v, list) for v in data.values()):
                    # Find the list with the most elements
                    max_len = 0
                    list_key = None
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > max_len:
                            max_len = len(value)
                            list_key = key
                    
                    if list_key:
                        df = pd.DataFrame(data[list_key])
                    else:
                        df = pd.DataFrame([data])
                else:
                    df = pd.DataFrame([data])
            else:
                logger.error("Unsupported JSON structure")
                return None
            
            # Clean column names
            df.columns = [str(col).strip().replace(' ', '_').replace('-', '_') for col in df.columns]
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing JSON file: {e}")
            return None
    
    def _process_pdf(self, file_path: str) -> Optional[pd.DataFrame]:
        """Process PDF file and extract text data."""
        try:
            extracted_data = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        extracted_data.append({
                            'page': page_num + 1,
                            'text': text.strip(),
                            'page_width': page.width,
                            'page_height': page.height
                        })
                    
                    # Extract tables
                    tables = page.extract_tables()
                    for table_num, table in enumerate(tables):
                        if table and len(table) > 1:  # At least header + one row
                            # Convert table to DataFrame
                            table_df = pd.DataFrame(table[1:], columns=table[0])
                            table_df['page'] = page_num + 1
                            table_df['table_num'] = table_num + 1
                            
                            # If this is the first table, use it as the main DataFrame
                            if not extracted_data:
                                return table_df
            
            # If no tables found, create DataFrame from text
            if extracted_data:
                df = pd.DataFrame(extracted_data)
                return df
            else:
                logger.warning("No extractable content found in PDF")
                return None
                
        except Exception as e:
            logger.error(f"Error processing PDF file: {e}")
            return None
    
    def _process_excel(self, file_path: str) -> Optional[pd.DataFrame]:
        """Process Excel file."""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            
            # If only one sheet, read it directly
            if len(excel_file.sheet_names) == 1:
                df = pd.read_excel(file_path)
            else:
                # If multiple sheets, read the first non-empty sheet
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    if not df.empty:
                        logger.info(f"Using sheet: {sheet_name}")
                        break
                else:
                    logger.error("No non-empty sheets found in Excel file")
                    return None
            
            # Clean column names
            df.columns = [str(col).strip().replace(' ', '_').replace('-', '_') for col in df.columns]
            
            return df
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            return None
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to disk."""
        try:
            file_path = os.path.join(self.upload_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            logger.info(f"Saved uploaded file: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
            raise
    
    def cleanup_file(self, file_path: str):
        """Remove temporary file after processing."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {e}")
    
    def get_file_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get information about the processed DataFrame."""
        info = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': df.columns.tolist(),
            'data_types': df.dtypes.astype(str).to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'null_counts': df.isnull().sum().to_dict()
        }
        
        # Add sample data
        sample_size = min(5, len(df))
        info['sample_data'] = df.head(sample_size).to_dict('records')
        
        return info 