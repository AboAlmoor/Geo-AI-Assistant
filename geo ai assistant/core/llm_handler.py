"""
Simple LLM Handler - Ollama only
"""

import requests
from typing import Dict
from qgis.core import QgsMessageLog, Qgis


class SimpleLLMHandler:
    """Simple Ollama-only LLM handler"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "phi3"
    
    def generate_sql(self, prompt: str, context: str = "") -> Dict:
        """Generate SQL from natural language prompt"""
        # Build full prompt
        system_prompt = (
            "You are an expert in geospatial SQL (PostGIS, SpatiaLite). "
            "Generate valid SQL queries from natural language descriptions. "
            "Return only the SQL query, no explanations."
        )
        
        full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nUser: {prompt}\n\nSQL:"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                sql = response.json().get("response", "").strip()
                # Clean up SQL (remove markdown if present)
                if sql.startswith("```sql"):
                    sql = sql.replace("```sql", "").replace("```", "").strip()
                elif sql.startswith("```"):
                    sql = sql.replace("```", "").strip()
                
                return {"sql": sql, "success": True}
            else:
                error_msg = f"Ollama error: {response.text}"
                QgsMessageLog.logMessage(error_msg, "GeoAI Simple", Qgis.Warning)
                return {"error": error_msg, "success": False}
                
        except requests.exceptions.ConnectionError:
            error_msg = f"Could not connect to Ollama at {self.base_url}. Make sure Ollama is running."
            QgsMessageLog.logMessage(error_msg, "GeoAI Simple", Qgis.Critical)
            return {"error": error_msg, "success": False}
        except Exception as e:
            error_msg = f"Error generating SQL: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "GeoAI Simple", Qgis.Critical)
            return {"error": error_msg, "success": False}

