from PIL import Image
import os
import time
import sys
import subprocess
from typing import Dict
from qgis.core import QgsMessageLog, Qgis

# Load environment variables
PLUGIN_DIR = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(PLUGIN_DIR, ".env")

try:
    from dotenv import load_dotenv
except ImportError:
    # Try to install python-dotenv if missing
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv", "-q"])
        from dotenv import load_dotenv
    except Exception as e:
        QgsMessageLog.logMessage(f"Failed to install python-dotenv: {e}", "GeoAI", Qgis.Warning)
        def load_dotenv(path=None, override=False):
            pass  # No-op if dotenv not available

load_dotenv(env_path)


class ImageProcessor:
    """Process Model Builder images and convert to code using Azure Computer Vision"""
    
    def __init__(self, llm_handler):
        self.llm = llm_handler
        self.azure_client = None
        self._initialize_azure_client()
    
    def _initialize_azure_client(self):
        """Initialize Azure Computer Vision client from .env"""
        try:
            from azure.cognitiveservices.vision.computervision import ComputerVisionClient
            from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
            from msrest.authentication import CognitiveServicesCredentials
        except ImportError as e:
            # Try to auto-install Azure SDK
            QgsMessageLog.logMessage(
                "Azure SDK not found. Attempting to install...",
                "GeoAI",
                Qgis.Info
            )
            try:
                packages = [
                    "azure-cognitiveservices-vision-computervision",
                    "msrest"
                ]
                for pkg in packages:
                    QgsMessageLog.logMessage(f"Installing {pkg}...", "GeoAI", Qgis.Info)
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", pkg, "-q"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                
                # Try importing again
                from azure.cognitiveservices.vision.computervision import ComputerVisionClient
                from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
                from msrest.authentication import CognitiveServicesCredentials
                
                QgsMessageLog.logMessage(
                    "Azure SDK installed successfully. Please restart QGIS.",
                    "GeoAI",
                    Qgis.Info
                )
                return
            except Exception as install_error:
                error_msg = (
                    f"Failed to auto-install Azure SDK: {str(install_error)}\n\n"
                    "Manual installation required:\n"
                    "1. Open QGIS Python Console (Plugins → Python Console)\n"
                    "2. Paste this code:\n"
                    "   import subprocess, sys\n"
                    "   subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'azure-cognitiveservices-vision-computervision', 'msrest'])\n"
                    "3. Restart QGIS"
                )
                QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
                return
        
        try:
            # Reload .env file to get latest credentials
            load_dotenv(env_path, override=True)
            
            endpoint = os.getenv("AZURE_VISION_ENDPOINT")
            subscription_key = os.getenv("AZURE_VISION_SUBSCRIPTION_KEY")
            
            # Log what we found (without exposing the key)
            QgsMessageLog.logMessage(
                f"Loading Azure credentials from: {env_path}",
                "GeoAI",
                Qgis.Info
            )
            
            if not endpoint:
                QgsMessageLog.logMessage(
                    f"AZURE_VISION_ENDPOINT not found in .env file at {env_path}",
                    "GeoAI",
                    Qgis.Warning
                )
            if not subscription_key:
                QgsMessageLog.logMessage(
                    "AZURE_VISION_SUBSCRIPTION_KEY not found in .env file",
                    "GeoAI",
                    Qgis.Warning
                )
            
            if not endpoint or not subscription_key:
                error_msg = (
                    f"Azure Computer Vision credentials not found in .env file.\n"
                    f"File path: {env_path}\n"
                    f"Endpoint found: {bool(endpoint)}\n"
                    f"Key found: {bool(subscription_key)}\n\n"
                    "Please configure in Settings tab:\n"
                    "1. Go to Settings tab\n"
                    "2. Enter Azure endpoint and subscription key\n"
                    "3. Click 'Save Azure Credentials'\n"
                    "4. Restart QGIS"
                )
                QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Warning)
                return
            
            # Strip any whitespace
            endpoint = endpoint.strip()
            subscription_key = subscription_key.strip()
            
            # Create client
            self.azure_client = ComputerVisionClient(
                endpoint,
                CognitiveServicesCredentials(subscription_key)
            )
            self.VisualFeatureTypes = VisualFeatureTypes
            
            QgsMessageLog.logMessage(
                f"Azure Computer Vision client initialized successfully",
                "GeoAI",
                Qgis.Info
            )
            QgsMessageLog.logMessage(
                f"Endpoint: {endpoint}",
                "GeoAI",
                Qgis.Info
            )
            
        except Exception as e:
            error_msg = f"Error initializing Azure client: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            import traceback
            QgsMessageLog.logMessage(traceback.format_exc(), "GeoAI", Qgis.Critical)
    
    def reload_azure_client(self):
        """Reload Azure client (useful after updating credentials)"""
        QgsMessageLog.logMessage("Reloading Azure Computer Vision client...", "GeoAI", Qgis.Info)
        self.azure_client = None
        
        # Force reload .env file
        load_dotenv(env_path, override=True)
        
        self._initialize_azure_client()
        
        if self.azure_client:
            QgsMessageLog.logMessage("Azure client reloaded successfully", "GeoAI", Qgis.Info)
        else:
            QgsMessageLog.logMessage("Azure client reload failed - check logs above", "GeoAI", Qgis.Warning)
        
        return self.azure_client is not None
    
    def analyze_image_with_azure(self, image_path: str) -> Dict:
        """
        Analyze image using Azure Computer Vision to extract description, shapes, and colors
        
        Args:
            image_path: Path to image file
        """
        if not self.azure_client:
            error_msg = "Azure Computer Vision client not initialized. Check .env file."
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Warning)
            return {"error": error_msg}
        
        if not os.path.exists(image_path):
            error_msg = f"Image file not found: {image_path}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Warning)
            return {"error": error_msg}
        
        try:
            QgsMessageLog.logMessage(f"Starting Azure analysis for: {image_path}", "GeoAI", Qgis.Info)
            
            # Analyze image with all features including color
            with open(image_path, "rb") as image_stream:
                QgsMessageLog.logMessage("Sending image to Azure for analysis...", "GeoAI", Qgis.Info)
                analysis = self.azure_client.analyze_image_in_stream(
                    image_stream,
                    visual_features=[
                        self.VisualFeatureTypes.description,
                        self.VisualFeatureTypes.objects,
                        self.VisualFeatureTypes.tags,
                        self.VisualFeatureTypes.brands,
                        self.VisualFeatureTypes.categories,
                        self.VisualFeatureTypes.color,  # Color detection
                        self.VisualFeatureTypes.image_type,  # Image type
                    ]
                )
                QgsMessageLog.logMessage("Azure analysis completed", "GeoAI", Qgis.Info)
            
            # OCR (text detection)
            QgsMessageLog.logMessage("Starting OCR text detection...", "GeoAI", Qgis.Info)
            with open(image_path, "rb") as image_stream:
                ocr_result = self.azure_client.read_in_stream(image_stream, raw=True)
            
            operation_location = ocr_result.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]
            
            # Wait for OCR to complete
            max_attempts = 30
            attempt = 0
            while attempt < max_attempts:
                result = self.azure_client.get_read_result(operation_id)
                if result.status not in ["notStarted", "running"]:
                    QgsMessageLog.logMessage(f"OCR completed with status: {result.status}", "GeoAI", Qgis.Info)
                    break
                attempt += 1
                time.sleep(1)
            
            if attempt >= max_attempts:
                QgsMessageLog.logMessage("OCR timed out", "GeoAI", Qgis.Warning)
                result = None
            
            # Generate comprehensive description
            description = self._generate_full_description(analysis, result)
            QgsMessageLog.logMessage(f"Generated description length: {len(description)} characters", "GeoAI", Qgis.Info)
            
            return {
                "success": True,
                "description": description,
                "analysis": analysis,
                "text_result": result
            }
            
        except Exception as e:
            error_msg = f"Azure vision analysis error: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            import traceback
            QgsMessageLog.logMessage(traceback.format_exc(), "GeoAI", Qgis.Critical)
            return {"error": error_msg}
    
    def _generate_full_description(self, analysis, text_result=None) -> str:
        """Generate full textual description from Azure analysis including shapes and colors"""
        parts = []
        
        # Main caption
        if analysis.description.captions:
            parts.append("Main Caption: " + analysis.description.captions[0].text)
        
        # Color information
        if hasattr(analysis, 'color') and analysis.color:
            color_info = []
            if analysis.color.dominant_colors:
                color_info.append(f"Dominant colors: {', '.join(analysis.color.dominant_colors)}")
            if analysis.color.accent_color:
                color_info.append(f"Accent color: {analysis.color.accent_color}")
            if analysis.color.is_bw_img:
                color_info.append("Image is black and white")
            if color_info:
                parts.append("Colors: " + " | ".join(color_info))
        
        # Objects (shapes and items)
        if analysis.objects:
            obj_names = [obj.object_property for obj in analysis.objects[:10]]  # top 10 objects
            parts.append("Key objects/shapes: " + ", ".join(obj_names))
        
        # Tags
        if analysis.tags:
            tag_names = [tag.name for tag in analysis.tags[:15]]  # top 15 tags
            parts.append("Tags: " + ", ".join(tag_names))
        
        # Categories
        if analysis.categories:
            category_names = [cat.name for cat in analysis.categories[:5]]
            parts.append("Categories: " + ", ".join(category_names))
        
        # OCR text
        if text_result and text_result.status == "succeeded":
            text_lines = []
            for page in text_result.analyze_result.read_results:
                for line in page.lines[:15]:  # top 15 lines
                    text_lines.append(line.text)
            if text_lines:
                parts.append("Text in image: " + " | ".join(text_lines))
        
        return "\n".join(parts)
    
    def process_model_image(self, image_path: str, output_type: str = 'sql', model_provider: str = 'ollama', model_name: str = 'phi3') -> Dict:
        """
        Process model builder screenshot and convert to code
        
        Args:
            image_path: Path to model builder screenshot
            output_type: 'sql', 'python', or 'both'
            model_provider: 'ollama', 'openrouter', or other LLM provider
            model_name: Model name (e.g., 'phi3', 'mistral-7b-instruct')
        """
        QgsMessageLog.logMessage(
            f"Processing image: {image_path} | Type: {output_type} | Provider: {model_provider} | Model: {model_name}",
            "GeoAI",
            Qgis.Info
        )
        
        if not os.path.exists(image_path):
            error_msg = f"Image file not found: {image_path}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            return {"error": error_msg}
        
        # Validate image
        try:
            img = Image.open(image_path)
            img.verify()
            QgsMessageLog.logMessage(f"Image validated: {img.size[0]}x{img.size[1]} pixels", "GeoAI", Qgis.Info)
        except Exception as e:
            error_msg = f"Invalid image file: {str(e)}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            return {"error": error_msg}
        
        # Check if Azure is available first
        if not self.azure_client:
            # Try to reload Azure client in case it wasn't initialized
            QgsMessageLog.logMessage("Azure client is None, attempting to reload...", "GeoAI", Qgis.Warning)
            self.reload_azure_client()
            
            if not self.azure_client:
                # Check what the actual issue is
                error_details = []
                
                # Check if SDK is installed
                try:
                    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
                    error_details.append("✅ Azure SDK is installed")
                except ImportError:
                    error_details.append("❌ Azure SDK is NOT installed - Install with: pip install azure-cognitiveservices-vision-computervision msrest")
                
                # Check .env file
                if os.path.exists(env_path):
                    error_details.append(f"✅ .env file exists: {env_path}")
                else:
                    error_details.append(f"❌ .env file NOT found: {env_path}")
                
                # Check credentials
                load_dotenv(env_path, override=True)
                endpoint = os.getenv("AZURE_VISION_ENDPOINT")
                key = os.getenv("AZURE_VISION_SUBSCRIPTION_KEY")
                
                if endpoint:
                    error_details.append(f"✅ Endpoint found: {endpoint[:50]}...")
                else:
                    error_details.append("❌ Endpoint NOT found in .env")
                
                if key:
                    error_details.append("✅ Subscription key found")
                else:
                    error_details.append("❌ Subscription key NOT found in .env")
                
                error_msg = (
                    "Azure Computer Vision is not configured.\n\n"
                    "Diagnostic Information:\n" + "\n".join(error_details) + "\n\n"
                    "Please:\n"
                    "1. Install Azure SDK if not installed (see error above)\n"
                    "2. Check .env file has credentials\n"
                    "3. Go to Settings tab and verify credentials\n"
                    "4. Click 'Save Azure Credentials'\n"
                    "5. Restart QGIS\n\n"
                    "Azure Computer Vision is required for image analysis."
                )
                QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
                return {"error": error_msg}
        
        # First, analyze with Azure Computer Vision
        QgsMessageLog.logMessage("Step 1: Analyzing image with Azure Computer Vision...", "GeoAI", Qgis.Info)
        azure_result = self.analyze_image_with_azure(image_path)
        
        if "error" in azure_result:
            # Azure failed - return error with helpful message
            error_info = azure_result.get('error', 'Unknown error')
            error_msg = (
                f"Azure Computer Vision analysis failed: {error_info}\n\n"
                "Please check:\n"
                "1. Azure credentials are correct in Settings tab\n"
                "2. Azure endpoint is accessible\n"
                "3. Subscription key is valid\n"
                "4. You have internet connection"
            )
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            return {"error": error_msg}
        
        if not azure_result.get("description"):
            # No description generated - this shouldn't happen if Azure worked
            error_msg = "Azure analysis completed but no description was generated. Please try again."
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Warning)
            return {"error": error_msg}
        
        # Azure succeeded - use description to generate code
        description = azure_result.get("description", "")
        QgsMessageLog.logMessage(f"Azure description received ({len(description)} chars)", "GeoAI", Qgis.Info)
        QgsMessageLog.logMessage(f"Azure description preview: {description[:200]}...", "GeoAI", Qgis.Info)
        
        # Generate code using the description
        QgsMessageLog.logMessage(f"Step 2: Generating {output_type} code using {model_provider}/{model_name}...", "GeoAI", Qgis.Info)
        result = self.llm.generate_code_from_image_description(
            description,
            output_type,
            model_provider,
            model_name
        )
        
        if "error" in result:
            error_msg = f"Code generation failed: {result.get('error')}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            return result
        
        # Parse and structure the response
        structured = self._structure_code_output(result)
        structured["azure_description"] = description
        
        # Log success
        has_sql = structured.get("sql_code") is not None
        has_python = structured.get("python_code") is not None
        QgsMessageLog.logMessage(
            f"Image processing completed successfully | SQL: {has_sql} | Python: {has_python}",
            "GeoAI",
            Qgis.Info
        )
        
        return structured
    
    def _structure_code_output(self, raw_result: Dict) -> Dict:
        """Structure the code output from LLM"""
        import re
        
        # If result already has sql_code or python_code fields, it's from the new handler
        if raw_result.get("sql_code") or raw_result.get("python_code"):
            return {
                "success": bool(raw_result.get("sql_code") or raw_result.get("python_code")),
                "explanation": raw_result.get("explanation", ""),
                "sql_code": raw_result.get("sql_code"),
                "python_code": raw_result.get("python_code"),
                "raw_response": raw_result.get("code", "")
            }
        
        # Otherwise, parse from raw code content (legacy format)
        code_content = raw_result.get('code', '') or raw_result.get('explanation', '')
        
        if not code_content or not code_content.strip():
            return {
                "success": False,
                "explanation": "No code generated",
                "sql_code": None,
                "python_code": None,
                "raw_response": code_content
            }
        
        # Extract code blocks with various formats
        sql_blocks = re.findall(r'```sql\n(.*?)\n```', code_content, re.DOTALL)
        python_blocks = re.findall(r'```python\n(.*?)\n```', code_content, re.DOTALL)
        
        # Try alternative formats if no code blocks found
        if not sql_blocks:
            # Look for SQL code blocks with lowercase
            sql_blocks = re.findall(r'```(?:sql|SQL)\n(.*?)\n```', code_content, re.DOTALL)
        
        if not python_blocks:
            # Look for Python code blocks with lowercase
            python_blocks = re.findall(r'```(?:python|Python|PY|py)\n(.*?)\n```', code_content, re.DOTALL)
        
        # If still no code blocks, try to detect code pattern
        if not sql_blocks and not python_blocks:
            # Look for SQL pattern (SELECT, CREATE, INSERT, UPDATE, DELETE, WITH)
            sql_pattern = re.search(
                r'(?:SELECT|CREATE|INSERT|UPDATE|DELETE|WITH)\s+.*?(?=\n(?:```|---|\n\n|$))',
                code_content,
                re.DOTALL | re.IGNORECASE
            )
            if sql_pattern:
                sql_blocks = [sql_pattern.group(0).strip()]
        
        if not python_blocks:
            # Look for Python pattern (def, import, from ... import, class)
            python_pattern = re.search(
                r'(?:def|import|from|class)\s+.*?(?=\n(?:```|---|\n\n|$))',
                code_content,
                re.DOTALL
            )
            if python_pattern:
                python_blocks = [python_pattern.group(0).strip()]
        
        # Check if entire content looks like code
        if not sql_blocks and not python_blocks:
            content_lower = code_content.lower()
            has_sql_keywords = any(keyword in content_lower for keyword in ['select', 'where', 'from', 'join', 'filter', 'create', 'insert', 'update', 'delete'])
            has_python_keywords = any(keyword in code_content for keyword in ['def ', 'import ', 'from ', 'for ', 'if ', 'class '])
            
            if has_sql_keywords:
                sql_blocks = [code_content.strip()]
            elif has_python_keywords:
                python_blocks = [code_content.strip()]
            else:
                # If no code detected, log what we got
                QgsMessageLog.logMessage(
                    f"No code patterns detected in response. Content preview: {code_content[:200]}",
                    "GeoAI",
                    Qgis.Warning
                )
        
        return {
            "success": bool(sql_blocks or python_blocks),
            "explanation": code_content,
            "sql_code": '\n\n'.join(sql_blocks) if sql_blocks else None,
            "python_code": '\n\n'.join(python_blocks) if python_blocks else None,
            "raw_response": code_content
        }