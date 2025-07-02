"""
LLM Service for generating summaries and insights
Supports multiple LLM providers with fallback options
"""

import os
import json
from typing import Dict, Any, Optional, List
import requests
from .models import SummaryRequest, SummaryResponse


class LLMService:
    """Service for interacting with various LLM providers"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "mock").lower()
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "")
        self.model = os.getenv("LLM_MODEL", "llama2:7b-chat")
        
    def generate_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Generate a summary based on the request type and data"""
        
        # Normalize summary_type
        if request.summary_type == "general":
            request.summary_type = "overview"
        
        if self.provider == "mock":
            return self._mock_summary(request)
        elif self.provider == "openai":
            return self._openai_summary(request)
        elif self.provider == "ollama":
            return self._ollama_summary(request)
        elif self.provider == "local":
            return self._local_summary(request)
        else:
            return self._mock_summary(request)
    
    def _mock_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Generate a mock summary for testing"""
        
        summary_type = request.summary_type
        data_info = request.data_info
        
        if summary_type == "overview":
            summary = f"This dataset contains {data_info.get('row_count', 'unknown')} rows and {data_info.get('column_count', 'unknown')} columns. "
            summary += f"The columns are: {', '.join(data_info.get('columns', []))}. "
            summary += "This appears to be a structured dataset suitable for analysis."
            
        elif summary_type == "statistical":
            summary = "Statistical Summary:\n"
            summary += f"- Total rows: {data_info.get('row_count', 'N/A')}\n"
            summary += f"- Total columns: {data_info.get('column_count', 'N/A')}\n"
            summary += f"- Data types: {data_info.get('data_types', {})}\n"
            summary += "- Key insights: This dataset shows structured information with various data types."
            
        elif summary_type == "insights":
            summary = "Key Insights:\n"
            summary += "1. The dataset appears to be well-structured\n"
            summary += "2. Multiple data types are present\n"
            summary += "3. The data could be useful for analysis and visualization\n"
            summary += "4. Consider exploring relationships between columns"
            
        else:
            summary = f"General summary of the dataset with {data_info.get('row_count', 'unknown')} records."
        
        return SummaryResponse(
            success=True,
            summary=summary,
            summary_type=summary_type,
            provider="mock",
            model="mock-model",
            tokens_used=len(summary.split()),
            processing_time=0.1
        )
    
    def _openai_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Generate summary using OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = self._build_prompt(request)
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful data analyst assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result["choices"][0]["message"]["content"]
                tokens_used = result["usage"]["total_tokens"]
                
                return SummaryResponse(
                    success=True,
                    summary=summary,
                    summary_type=request.summary_type,
                    provider="openai",
                    model=self.model,
                    tokens_used=tokens_used,
                    processing_time=0.5
                )
            else:
                raise Exception(f"OpenAI API error: {response.status_code}")
                
        except Exception as e:
            # Fallback to mock
            return self._mock_summary(request)
    
    def _ollama_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Generate summary using Ollama API"""
        try:
            prompt = self._build_prompt(request)
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=60
            )
            if response.status_code == 200:
                result = response.json()
                summary = result.get("response", "")
                if not summary:
                    raise Exception("Ollama returned empty response")
                return SummaryResponse(
                    success=True,
                    summary=summary,
                    summary_type=request.summary_type,
                    provider="ollama",
                    model=self.model,
                    tokens_used=len(summary.split()),
                    processing_time=1.0
                )
            else:
                error_msg = f"Ollama API error: {response.status_code} - {response.text}"
                raise Exception(error_msg)
        except Exception as e:
            return SummaryResponse(
                success=False,
                summary="",
                summary_type=request.summary_type,
                provider="ollama",
                model=self.model,
                tokens_used=0,
                processing_time=0.0,
                error=str(e)
            )
    
    def _local_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Generate summary using local LLM (placeholder)"""
        # This would integrate with local LLM libraries
        # For now, return mock summary
        return self._mock_summary(request)
    
    def _build_prompt(self, request: SummaryRequest) -> str:
        """Build a prompt for the LLM based on the request"""
        
        base_prompt = f"""
        Please analyze this dataset and provide a {request.summary_type} summary.
        
        Dataset Information:
        - Rows: {request.data_info.get('row_count', 'Unknown')}
        - Columns: {request.data_info.get('column_count', 'Unknown')}
        - Column names: {', '.join(request.data_info.get('columns', []))}
        - Data types: {request.data_info.get('data_types', {})}
        
        Sample data (first few rows):
        {request.data_info.get('sample_data', 'No sample data available')}
        
        Please provide a comprehensive {request.summary_type} summary that includes:
        """
        
        if request.summary_type == "overview":
            base_prompt += """
            - Overall structure and purpose of the dataset
            - Key characteristics of the data
            - Potential use cases for analysis
            """
        elif request.summary_type == "statistical":
            base_prompt += """
            - Statistical overview of the data
            - Data quality assessment
            - Notable patterns or anomalies
            """
        elif request.summary_type == "insights":
            base_prompt += """
            - Key insights and observations
            - Potential relationships between variables
            - Recommendations for further analysis
            """
        
        return base_prompt.strip()
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available LLM providers"""
        return [
            {
                "name": "mock",
                "description": "Mock provider for testing",
                "requires_api_key": False,
                "supports_streaming": False
            },
            {
                "name": "openai",
                "description": "OpenAI GPT models",
                "requires_api_key": True,
                "supports_streaming": True
            },
            {
                "name": "ollama",
                "description": "Local Ollama models",
                "requires_api_key": False,
                "supports_streaming": True
            },
            {
                "name": "local",
                "description": "Local LLM models",
                "requires_api_key": False,
                "supports_streaming": False
            }
        ] 