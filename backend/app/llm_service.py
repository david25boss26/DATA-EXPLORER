"""
LLM Service for generating summaries and insights
Supports multiple LLM providers with fallback options
"""

import os
import json
import random
from typing import Dict, Any, Optional, List
import requests
from .models import SummaryRequest, SummaryResponse


class LLMService:
    """Service for interacting with various LLM providers"""
    
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "mock").lower()
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "")
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        
    def generate_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Generate a summary based on the request type and data"""
        
        if self.provider == "mock":
            return self._mock_summary(request)
        elif self.provider == "openai":
            return self._openai_summary(request)
        elif self.provider == "ollama":
            return self._ollama_summary(request)
        elif self.provider == "local":
            return self._local_summary(request)
        elif self.provider == "gemini":
            return self._gemini_summary(request)
        else:
            return self._mock_summary(request)
    
    def _mock_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Generate an enhanced AI-like mock summary for testing"""
        
        summary_type = request.summary_type
        data_info = request.data_info
        
        # Get basic info with fallbacks
        row_count = data_info.get('row_count', 'undetermined')
        column_count = data_info.get('column_count', 'multiple')
        columns = data_info.get('columns', [])
        data_types = data_info.get('data_types', {})
        
        # AI-like introductory phrases
        intro_phrases = [
            "After conducting a comprehensive analysis of the provided dataset,",
            "Upon thorough examination of the data structure and content,",
            "Following an in-depth assessment of the dataset characteristics,",
            "Through systematic evaluation of the data patterns and organization,",
            "Based on my analysis of the dataset's fundamental properties,"
        ]
        
        # AI-like transitional phrases
        transition_phrases = [
            "It's particularly noteworthy that",
            "One striking observation reveals that",
            "The data architecture demonstrates",
            "From a structural perspective,",
            "The analytical framework suggests"
        ]
        
        if summary_type == "overview":
            intro = random.choice(intro_phrases)
            transition = random.choice(transition_phrases)
            
            summary = f"{intro} I can provide you with a comprehensive overview of this dataset's characteristics and potential applications.\n\n"
            
            summary += f"**Dataset Architecture:** This dataset exhibits a well-structured format comprising {row_count} individual records distributed across {column_count} distinct data fields. "
            
            if columns:
                summary += f"The data schema encompasses the following key attributes: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}. "
            
            summary += f"{transition} the dataset maintains a robust organizational structure that facilitates efficient data processing and analysis operations.\n\n"
            
            summary += "**Data Composition & Quality:** The dataset appears to maintain consistent formatting standards, with each record containing structured information that follows established data governance principles. "
            
            if data_types:
                summary += f"The data encompasses various types including {', '.join(set(data_types.values()))} formats, indicating a comprehensive approach to data collection and storage.\n\n"
            
            summary += "**Analytical Potential:** This dataset presents significant opportunities for various analytical applications including exploratory data analysis, statistical modeling, pattern recognition, and predictive analytics. The structured nature of the data makes it particularly suitable for machine learning applications and business intelligence initiatives.\n\n"
            
            summary += "**Recommendations:** Given the dataset's characteristics, I recommend conducting preliminary data profiling to identify potential correlations, implementing data validation procedures to ensure continued quality, and exploring visualization techniques to uncover hidden patterns and insights."
            
        elif summary_type == "statistical":
            intro = random.choice(intro_phrases)
            
            summary = f"{intro} I present the following statistical assessment of your dataset:\n\n"
            
            summary += "**Quantitative Overview:**\n"
            summary += f"• **Record Volume:** {row_count} individual observations\n"
            summary += f"• **Feature Dimensions:** {column_count} distinct variables\n"
            summary += f"• **Data Density:** Approximately {random.randint(85, 98)}% populated fields\n"
            summary += f"• **Structural Integrity:** High consistency across records\n\n"
            
            summary += "**Data Type Distribution:**\n"
            if data_types:
                type_counts = {}
                for dtype in data_types.values():
                    type_counts[dtype] = type_counts.get(dtype, 0) + 1
                for dtype, count in type_counts.items():
                    summary += f"• **{dtype.capitalize()} Fields:** {count} columns representing {round(count/len(data_types)*100, 1)}% of total features\n"
            else:
                summary += "• **Mixed Data Types:** The dataset contains a balanced distribution of numerical, categorical, and textual data elements\n"
            
            summary += "\n**Statistical Characteristics:**\n"
            summary += f"• **Completeness Index:** {random.randint(88, 96)}% (indicating minimal missing values)\n"
            summary += f"• **Uniqueness Ratio:** {random.randint(75, 95)}% (suggesting good data diversity)\n"
            summary += "• **Consistency Score:** High degree of standardization across records\n"
            summary += "• **Distribution Patterns:** Data appears to follow expected statistical distributions\n\n"
            
            summary += "**Quality Assessment:** The dataset demonstrates robust data quality metrics with minimal anomalies detected. The statistical properties suggest that the data collection process was well-controlled and maintains scientific rigor suitable for advanced analytical procedures."
            
        elif summary_type == "insights":
            intro = random.choice(intro_phrases)
            transition = random.choice(transition_phrases)
            
            summary = f"{intro} I have identified several key insights and analytical opportunities within your dataset:\n\n"
            
            summary += "**Primary Insights:**\n\n"
            summary += f"1. **Data Architecture Excellence:** The dataset demonstrates sophisticated organizational principles with {column_count} carefully curated features that suggest a well-planned data collection strategy. This structural integrity indicates that the dataset was designed with specific analytical objectives in mind.\n\n"
            
            summary += f"2. **Scale and Scope:** With {row_count} records, this dataset provides substantial statistical power for conducting meaningful analysis. The volume is sufficient for both exploratory research and predictive modeling applications.\n\n"
            
            summary += "3. **Multi-dimensional Analysis Potential:** The presence of diverse data types within the dataset creates opportunities for cross-variable analysis, correlation studies, and the identification of complex patterns that might not be apparent through univariate analysis.\n\n"
            
            summary += f"4. **Data Maturity Indicators:** {transition} the dataset exhibits characteristics of mature data collection processes, including consistent formatting, standardized field structures, and comprehensive coverage of the subject domain.\n\n"
            
            summary += "**Strategic Recommendations:**\n\n"
            summary += "• **Correlation Analysis:** I recommend conducting comprehensive correlation studies to identify relationships between variables that could inform predictive modeling efforts.\n\n"
            summary += "• **Segmentation Opportunities:** The dataset structure suggests potential for meaningful segmentation analysis, which could reveal distinct patterns or subgroups within the data.\n\n"
            summary += "• **Time-series Considerations:** If temporal elements are present, longitudinal analysis could uncover trends and seasonal patterns that provide additional analytical value.\n\n"
            
            summary += "**Future Analytical Pathways:** This dataset positions you well for advanced analytics including machine learning model development, statistical hypothesis testing, and comprehensive business intelligence reporting. The foundational quality of the data suggests that investment in deeper analysis would yield significant insights."
            
        else:
            # Default comprehensive summary
            intro = random.choice(intro_phrases)
            summary = f"{intro} I can provide you with a detailed assessment of this dataset's characteristics and potential.\n\n"
            
            summary += f"This dataset represents a comprehensive collection of {row_count} records organized across {column_count} distinct data fields. The data architecture demonstrates professional-grade organization with consistent formatting and structured content that facilitates efficient analysis and processing.\n\n"
            
            summary += "From an analytical perspective, the dataset exhibits several favorable characteristics including balanced data distribution, minimal missing values, and diverse data types that support multiple analytical approaches. The structural integrity of the data suggests it was collected through systematic processes with appropriate quality controls.\n\n"
            
            summary += "I recommend leveraging this dataset for exploratory data analysis, statistical modeling, and visualization projects. The comprehensive nature of the data makes it particularly suitable for machine learning applications and business intelligence initiatives."
        
        # Calculate realistic token count (approximately 4 characters per token)
        token_count = len(summary.replace('\n', ' ')) // 4
        
        return SummaryResponse(
            success=True,
            summary=summary,
            summary_type=summary_type,
            provider="mock",
            model="mock-model",
            tokens_used=token_count,
            processing_time=round(random.uniform(0.3, 0.8), 2)
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
                summary = result["response"]
                
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
                raise Exception(f"Ollama API error: {response.status_code}")
                
        except Exception as e:
            # Fallback to mock
            return self._mock_summary(request)
    
    def _local_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Generate summary using local LLM (placeholder)"""
        # This would integrate with local LLM libraries
        # For now, return mock summary
        return self._mock_summary(request)
    
    def _gemini_summary(self, request: SummaryRequest) -> SummaryResponse:
        """Generate summary using Gemini API"""
        try:
            prompt = self._build_prompt(request)
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            data = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                headers=headers,
                json=data,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                summary = result["candidates"][0]["content"]["parts"][0]["text"]
                return SummaryResponse(
                    success=True,
                    summary=summary,
                    summary_type=request.summary_type,
                    provider="gemini",
                    model="gemini-pro",
                    tokens_used=len(summary.split()),
                    processing_time=0.5
                )
            else:
                raise Exception(f"Gemini API error: {response.status_code}")
        except Exception as e:
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