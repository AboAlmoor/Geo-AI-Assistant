"""
Unified LLM Handler - Supports multiple providers with dynamic model selection
Supports: OpenAI, OpenRouter, Anthropic, Google Gemini, Ollama, HuggingFace
"""

import os
import re
import base64
import requests
from typing import Dict, List, Optional
from qgis.core import QgsMessageLog, Qgis
from dotenv import load_dotenv

PLUGIN_DIR = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(PLUGIN_DIR, ".env")
load_dotenv(env_path)


class LLMHandler:
    """Unified handler for all LLM interactions with multiple providers."""

    def __init__(self):
        """Initialize LLM client based on selected provider (.env)"""
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        load_dotenv(os.path.join(plugin_dir, ".env"))

        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        self.client = None
        self.api_url = None
        self.text_model = os.getenv("LLM_MODEL_TEXT")
        self.vision_model = os.getenv("LLM_MODEL_VISION")
        self.api_key = None
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        # Initialize provider-specific clients
        if self.provider == "openai":
            import openai
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in .env")
            self.client = openai.OpenAI(api_key=self.api_key)
            if not self.text_model:
                self.text_model = "gpt-4o-mini"
            if not self.vision_model:
                self.vision_model = "gpt-4o"

        elif self.provider == "openrouter":
            import openai
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError("OPENROUTER_API_KEY not found in .env")
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "https://qgis.local"),
                    "X-Title": os.getenv("OPENROUTER_APP_NAME", "GeoAI Assistant")
                }
            )
            if not self.text_model:
                self.text_model = "mistralai/mistral-7b-instruct"
            if not self.vision_model:
                self.vision_model = "openai/gpt-4o"

        elif self.provider == "anthropic":
            import anthropic
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in .env")
            self.client = anthropic.Anthropic(api_key=self.api_key)
            if not self.text_model:
                self.text_model = "claude-3-5-sonnet-20241022"
            if not self.vision_model:
                self.vision_model = "claude-3-5-sonnet-20241022"

        elif self.provider == "google":
            try:
                import google.generativeai as genai
                self.api_key = os.getenv("GOOGLE_API_KEY")
                if not self.api_key:
                    raise ValueError("GOOGLE_API_KEY not found in .env")
                genai.configure(api_key=self.api_key)
                self.client = genai
                if not self.text_model:
                    self.text_model = "models/gemini-pro-latest"
                if not self.vision_model:
                    self.vision_model = "models/gemini-2.5-flash-image"
            except ImportError:
                QgsMessageLog.logMessage(
                    "Google Generative AI SDK not installed. Install with: pip install google-generativeai",
                    "GeoAI",
                    Qgis.Warning
                )
                raise ValueError("Google Generative AI SDK not installed")

        elif self.provider == "ollama":
            self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            if not self.text_model:
                self.text_model = "phi3"
            if not self.vision_model:
                self.vision_model = "phi3"
            self.client = None

        elif self.provider == "huggingface":
            self.api_key = os.getenv("HF_API_KEY")
            if not self.api_key:
                raise ValueError("HF_API_KEY not found in .env")
            if not self.text_model:
                self.text_model = "HuggingFaceH4/zephyr-7b-beta"
            if not self.vision_model:
                self.vision_model = ""
            self.api_url = f"https://api-inference.huggingface.co/models/{self.text_model}"
            self.client = None

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _ollama_query(self, prompt: str, system_prompt: str = "", model: str = None, images: Optional[List[str]] = None) -> str:
        """Call Ollama API with retry logic"""
        if model is None:
            model = self.text_model

        url = f"{self.ollama_base_url}/api/generate"
        
        # Get timeout from environment or use default
        timeout = int(os.getenv('OLLAMA_TIMEOUT', 120))
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
        if images:
            payload["images"] = images

        # Retry logic for better reliability
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                QgsMessageLog.logMessage(
                    f"Connecting to Ollama at {self.ollama_base_url} (attempt {attempt + 1}/{max_retries}, timeout={timeout}s)",
                    "GeoAI",
                    Qgis.Info
                )
                
                response = requests.post(url, json=payload, timeout=timeout)
                
                if response.status_code != 200:
                    error_text = response.text
                    raise Exception(f"Ollama error (status {response.status_code}): {error_text}")
                
                data = response.json()
                QgsMessageLog.logMessage(
                    f"Ollama query successful with model {model}",
                    "GeoAI",
                    Qgis.Info
                )
                return data.get("response", "").strip()
                
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    QgsMessageLog.logMessage(
                        f"Ollama connection failed (attempt {attempt + 1}), retrying in {retry_delay}s...",
                        "GeoAI",
                        Qgis.Warning
                    )
                    import time
                    time.sleep(retry_delay)
                else:
                    error_msg = (
                        f"Could not connect to Ollama at {self.ollama_base_url} after {max_retries} attempts.\n"
                        f"Error: {str(e)}\n\n"
                        "Please ensure:\n"
                        "1. Ollama is running (ollama serve)\n"
                        "2. Ollama base URL is correct: {self.ollama_base_url}\n"
                        "3. Model is available: {model}\n"
                        "4. No firewall is blocking localhost:11434"
                    )
                    raise Exception(error_msg)
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    QgsMessageLog.logMessage(
                        f"Ollama request timed out (attempt {attempt + 1}), retrying...",
                        "GeoAI",
                        Qgis.Warning
                    )
                    import time
                    time.sleep(retry_delay)
                else:
                    error_msg = (
                        f"Ollama request timed out after {max_retries} attempts (120s timeout).\n"
                        "The model might be too slow or overloaded.\n"
                        f"URL: {self.ollama_base_url}\n"
                        f"Model: {model}"
                    )
                    raise Exception(error_msg)
                    
            except Exception as e:
                error_msg = f"Ollama connection error: {str(e)}"
                QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
                raise

    def _hf_query(self, prompt: str) -> str:
        """Call Hugging Face Inference API"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(
            self.api_url,
            headers=headers,
            json={"inputs": prompt},
            timeout=120,
        )
        if response.status_code != 200:
            raise Exception(f"Hugging Face error: {response.text}")
        data = response.json()
        if isinstance(data, list) and len(data) and "generated_text" in data[0]:
            return data[0]["generated_text"]
        return str(data)

    def _query_with_provider(self, prompt: str, system_prompt: str = None, 
                            model_provider: str = None, model_name: str = None) -> str:
        """Generic query method that supports dynamic provider/model selection"""
        provider = model_provider.lower() if model_provider else self.provider
        model = model_name if model_name else self.text_model

        if provider == "ollama":
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            return self._ollama_query(full_prompt, "", model)

        elif provider == "openrouter":
            import openai
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY not found in .env")
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "https://qgis.local"),
                    "X-Title": os.getenv("OPENROUTER_APP_NAME", "GeoAI Assistant")
                }
            )
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content

        elif provider == "openai":
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in .env")
            client = openai.OpenAI(api_key=api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content

        elif provider == "anthropic":
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found in .env")
            client = anthropic.Anthropic(api_key=api_key)

            system_msg = system_prompt if system_prompt else ""
            response = client.messages.create(
                model=model,
                max_tokens=4000,
                system=system_msg,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        elif provider == "google":
            try:
                import google.generativeai as genai
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    raise ValueError("GOOGLE_API_KEY not found in .env")
                genai.configure(api_key=api_key)
                model_instance = genai.GenerativeModel(model)
                response = model_instance.generate_content(
                    [system_prompt, prompt] if system_prompt else [prompt],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7, top_p=0.0, top_k=1, max_output_tokens=2000
                    ),
                    safety_settings=[
                        {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_NONE'},
                        {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_NONE'},
                        {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_NONE'},
                        {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_NONE'}
                    ]
                )
                try:
                    return response.text
                except ValueError:
                    safety_feedback = response.prompt_feedback.safety_ratings
                    block_reason = "Content blocked due to safety policies."
                    if safety_feedback:
                        block_reason += f" Feedback: {safety_feedback}"
                    QgsMessageLog.logMessage(f"Gemini API Blocked: {block_reason}", "GeoAI", Qgis.Warning)
                    raise Exception(f"AI response blocked: {block_reason}")
            except ImportError:
                QgsMessageLog.logMessage(
                    "Google Generative AI SDK not installed. Install with: pip install google-generativeai",
                    "GeoAI",
                    Qgis.Warning
                )
                raise ValueError("Google Generative AI SDK not installed")

        elif provider == "huggingface":
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            return self._hf_query(full_prompt)

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def generate_sql(self, prompt: str, context: Dict, model_provider: str = None, model_name: str = None) -> Dict:
        """Generate SQL from natural language prompt."""
        system_prompt = self._build_sql_system_prompt(context)

        QgsMessageLog.logMessage(f"LLM Context (generate_sql): {context}", "GeoAI", Qgis.Info)

        try:
            content = self._query_with_provider(prompt, system_prompt, model_provider, model_name)
            return self._parse_sql_response(content)

        except Exception as e:
            QgsMessageLog.logMessage(f"LLM Error: {str(e)}", "GeoAI", Qgis.Critical)
            return {"error": str(e)}

    def fix_sql_error(self, sql: str, error: str, context: Dict, model_provider: str = None, model_name: str = None) -> Dict:
        """Fix SQL query that produced an error"""
        # Build field list (without pre-quoting since LLM will add quotes)
        fields_list = []
        for layer_name, fields in context.get('table_fields', {}).items():
            fields_list.append(f"  - {layer_name}: {', '.join(fields)}")
        
        fields_text = "\n".join(fields_list) if fields_list else ""
        newline = "\n"
        
        prompt = (
            f"Fix this SQL query that produced an error:{newline}{newline}"
            f"SQL:{newline}```sql{newline}{sql}{newline}```{newline}{newline}Error:{newline}{error}{newline}{newline}"
            f"Context:{newline}Database: {context.get('db_type','Unknown')}{newline}"
            f"Tables: {', '.join(context.get('tables', []))}{newline}"
            f"All Layer Fields:{newline}"
            f"{fields_text}{newline}"
        )
        system_prompt = (
            "You are a SQL expert specializing in geospatial databases (PostGIS, SpatiaLite). "
            "Fix SQL errors and explain the solution. IMPORTANT: Wrap ALL column names and table names in double quotes."
        )

        try:
            content = self._query_with_provider(prompt, system_prompt, model_provider, model_name)
            return self._parse_sql_response(content)
        except Exception as e:
            return {"error": str(e)}

    def analyze_image_to_code(self, image_path: str, conversion_type: str, 
                              model_provider: str = None, model_name: str = None) -> Dict:
        """Analyze Model Builder image and convert to code - supports direct image analysis"""
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

        extraction_prompt = (
            "Analyze this QGIS Model Builder diagram. List all:\n"
            "1. Input layers/data sources\n"
            "2. Processing steps/algorithms\n"
            "3. Parameters and settings\n"
            "4. Output layers\n"
            "5. Connections between steps\n"
            "Provide detailed, structured information."
        )

        provider = model_provider.lower() if model_provider else self.provider
        model = model_name if model_name else self.vision_model

        try:
            if provider == "anthropic":
                r = self.client.messages.create(
                    model=model,
                    max_tokens=4000,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": image_data,
                                    },
                                },
                                {"type": "text", "text": extraction_prompt},
                            ],
                        }
                    ],
                )
                extracted_info = r.content[0].text
            elif provider == "openai":
                r = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": extraction_prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_data}",
                                    },
                                },
                            ],
                        }
                    ],
                )
                extracted_info = r.choices[0].message.content
            elif provider == "google":
                import google.generativeai as genai
                model_instance = self.client.GenerativeModel(model)
                response = model_instance.generate_content(
                    [extraction_prompt, genai.upload_file(image_path)],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.4, top_p=0.0, top_k=1, max_output_tokens=3000
                    ),
                    safety_settings=[
                        {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_NONE'},
                        {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_NONE'},
                        {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_NONE'},
                        {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_NONE'}
                    ]
                )
                try:
                    extracted_info = response.text
                except ValueError:
                    safety_feedback = response.prompt_feedback.safety_ratings
                    block_reason = "Content blocked due to safety policies."
                    if safety_feedback:
                        block_reason += f" Feedback: {safety_feedback}"
                    QgsMessageLog.logMessage(f"Gemini API Blocked (Vision): {block_reason}", "GeoAI", Qgis.Warning)
                    return {"error": f"AI response blocked (Vision): {block_reason}"}
            elif provider == "ollama":
                extracted_info = self._ollama_query(extraction_prompt, images=[image_data], model=model)
            else:
                return {"error": f"Image analysis not supported for {provider}. Use Anthropic, OpenAI, or Google."}

            # Step 2: Convert extracted info to code using text model
            code_prompt = (
                f"Based on this QGIS Model Builder analysis, generate {conversion_type} code:\n\n"
                f"{extracted_info}\n\n"
                f"Generate clean, executable {conversion_type} code with comments."
            )

            code_result = self.generate_sql(code_prompt, {}, model_provider, model_name)

            return {
                "code": code_result.get("sql", "") if conversion_type.lower() == "sql" else extracted_info,
                "type": conversion_type,
                "extracted_info": extracted_info
            }

        except Exception as e:
            return {"error": str(e)}

    def generate_code_from_image_description(self, description: str, output_type: str = 'sql',
                                             model_provider: str = 'ollama', model_name: str = 'phi3') -> Dict:
        """Generate code from Azure Computer Vision image description"""
        
        # Normalize output_type
        output_type = output_type.lower().strip()
        
        # Determine what code to generate
        generate_sql = output_type in ['sql', 'both']
        generate_python = output_type in ['python', 'both']
        
        results = {}
        
        if generate_sql:
            QgsMessageLog.logMessage("Generating SQL code from image description...", "GeoAI", Qgis.Info)
            system_prompt = """You are an expert SQL developer. Your task is to convert QGIS Model Builder workflows described in natural language to working SQL code.

Rules:
- Generate ONLY valid SQL code
- Wrap the code in ```sql``` code blocks
- No explanations or markdown outside the code block
- Handle spatial operations if mentioned (e.g., ST_Contains, ST_Intersects)
- Be specific with table and column names from the description
- Return working, executable SQL"""

            prompt = f"""Convert this QGIS Model Builder workflow to SQL code:

WORKFLOW DESCRIPTION:
{description}

REQUIREMENTS:
- Output type: SQL
- Generate complete, working SQL code
- Wrap code in ```sql``` code block
- No explanations, only code

Generate the SQL code now:"""

            try:
                content = self._query_with_provider(
                    prompt,
                    system_prompt,
                    model_provider,
                    model_name
                )
                
                if content and content.strip():
                    results["sql_code"] = content
                    QgsMessageLog.logMessage(f"SQL code generated ({len(content)} chars)", "GeoAI", Qgis.Info)
                else:
                    QgsMessageLog.logMessage("SQL code generation returned empty response", "GeoAI", Qgis.Warning)
            except Exception as e:
                error_msg = f"Error generating SQL code: {str(e)}"
                QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
                results["sql_error"] = error_msg
        
        if generate_python:
            QgsMessageLog.logMessage("Generating Python code from image description...", "GeoAI", Qgis.Info)
            system_prompt = """You are an expert Python/QGIS developer. Your task is to convert QGIS Model Builder workflows described in natural language to working Python code.

Rules:
- Generate ONLY valid Python code
- Wrap the code in ```python``` code blocks
- No explanations or markdown outside the code block
- Use QGIS API where applicable (qgis.core, qgis.analysis)
- Include necessary imports
- Return working, executable Python code"""

            prompt = f"""Convert this QGIS Model Builder workflow to Python code:

WORKFLOW DESCRIPTION:
{description}

REQUIREMENTS:
- Output type: Python
- Generate complete, working Python code
- Wrap code in ```python``` code block
- No explanations, only code

Generate the Python code now:"""

            try:
                content = self._query_with_provider(
                    prompt,
                    system_prompt,
                    model_provider,
                    model_name
                )
                
                if content and content.strip():
                    results["python_code"] = content
                    QgsMessageLog.logMessage(f"Python code generated ({len(content)} chars)", "GeoAI", Qgis.Info)
                else:
                    QgsMessageLog.logMessage("Python code generation returned empty response", "GeoAI", Qgis.Warning)
            except Exception as e:
                error_msg = f"Error generating Python code: {str(e)}"
                QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
                results["python_error"] = error_msg
        
        # Check if any code was generated
        if not results or (not results.get("sql_code") and not results.get("python_code")):
            error_msg = f"No code could be generated. Errors: {results}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Warning)
            return {"error": error_msg}
        
        return {
            "code": results.get("sql_code") or results.get("python_code") or "",
            "sql_code": results.get("sql_code"),
            "python_code": results.get("python_code"),
            "explanation": f"SQL: {bool(results.get('sql_code'))} | Python: {bool(results.get('python_code'))}",
            "type": output_type,
            "success": True
        }

    def get_smart_suggestions(self, context: Dict, prompt: str = None,
                             model_provider: str = None, model_name: str = None) -> List[str]:
        """Generate intelligent, layer-specific QGIS operations"""

        active_layer_name = context.get("active_layer", "Unknown")
        layers_info = context.get("layers", [])
        crs = context.get("crs", "Unknown")
        db_type = context.get("db_type", "Unknown")
        project_analysis = context.get("project_analysis", {})
        target_layer_info = context.get("target_layer_info")

        system_message_parts = [
            "You are an expert GIS analyst and QGIS user. Provide insightful and actionable suggestions.",
            f"Current Project CRS: {crs}",
            f"Database Type: {db_type}"
        ]

        if project_analysis:
            system_message_parts.append(
                f"Project Summary: Total Layers={project_analysis.get('total_layers')}, "
                f"Vector Layers={project_analysis.get('vector_layers')}, "
                f"Total Features={project_analysis.get('total_features')}"
            )

        if target_layer_info:
            layer_name = target_layer_info.get('name')
            fields = target_layer_info.get("fields", [])
            fields_formatted = ', '.join([f'"{f}"' for f in fields])
            geometry_type = target_layer_info.get('geometry_type', 'Unknown')
            feature_count = target_layer_info.get('feature_count', 0)

            system_message_parts.append(f"Active Layer for Analysis: {layer_name}")
            system_message_parts.append(f"Geometry Type: {geometry_type}")
            system_message_parts.append(f"Feature Count: {feature_count}")
            system_message_parts.append(f"Available Fields: {fields_formatted}")

        elif active_layer_name and layers_info:
            active_info = None
            for layer in layers_info:
                if layer.get("name") == active_layer_name:
                    active_info = layer
                    break
            if active_info:
                fields = active_info.get("fields", [])
                fields_formatted = ', '.join(fields)
                system_message_parts.append(f"Active Layer: {active_layer_name}")
                system_message_parts.append(f"Available Fields: {fields_formatted}")

        system_prompt = "\n".join(system_message_parts) + "\n\nIMPORTANT: Use column names exactly as provided and wrapped in double quotes (e.g., SELECT \"Name\" FROM table). Provide explanations and code blocks for SQL or Python where appropriate. Format output clearly with headings."

        if prompt is None:
            prompt = (
                "Given the current QGIS project context, suggest 5 intelligent and practical QGIS operations. "
                "Focus on general project improvements, common geospatial analyses, or data management tasks. "
                "For each suggestion, provide a short title, a brief explanation, and relevant SQL or Python code examples."
            )

        try:
            content = self._query_with_provider(prompt, system_prompt, model_provider, model_name)

            if not content:
                return ["AI did not return any suggestions."]

            if "suggest 5 intelligent and practical QGIS operations" in prompt.lower():
                suggestions = re.split(r'\n\n(?:\d+\.\s)?', content)
                suggestions = [s.strip() for s in suggestions if s.strip()][:5]
                return suggestions if suggestions else [content]
            else:
                return [content]

        except Exception as e:
            QgsMessageLog.logMessage(f"Error getting suggestions: {str(e)}", "GeoAI", Qgis.Critical)
            return [f"Error getting suggestions: {str(e)}"]

    def _build_sql_system_prompt(self, context: Dict) -> str:
        """Build system prompt with proper column formatting"""
        tables_info = []
        for table_name, fields in context.get('table_fields', {}).items():
            fields_formatted = ', '.join(fields)
            tables_info.append(f"{table_name}: {fields_formatted}")

        tables_info_str = "\n".join(tables_info)

        return (
            "You are an expert in geospatial SQL (PostGIS, SpatiaLite). Your goal is to generate precise, correct, and simple SQL queries.\n"
            f"Database Type: {context.get('db_type','Unknown')}\n"
            f"CRS: {context.get('crs','EPSG:4326')}\n"
            "--- AVAILABLE TABLES AND COLUMNS ---\n"
            f"{tables_info_str}\n"
            "--- INSTRUCTIONS ---\n"
            "1. CRITICAL: Wrap ALL column names AND ALL table names in double quotes. Examples:\n"
            '   - SELECT "id", "name" FROM "cities" WHERE "population" > 1000\n'
            '   - SELECT * FROM "my_table" WHERE "geom" && ST_SetSRID(...)\n'
            "2. Use ONLY table and column names exactly as listed in AVAILABLE TABLES AND COLUMNS.\n"
            "3. Generate the SIMPLEST and most DIRECT SQL query without comments or placeholders.\n"
            "4. Provide SQL in a ```sql ... ``` block, followed by a clear explanation.\n"
            "5. Self-review your SQL to ensure proper quoting of all identifiers before output.\n"
        )

    def _parse_sql_response(self, content: str) -> Dict:
        """Parse SQL from LLM response"""
        QgsMessageLog.logMessage(f"Raw LLM content for SQL parsing: {content}", "GeoAI", Qgis.Info)

        sql = ""
        explanation = content

        sql_match = re.search(r"```sql\n(.*?)\n```", content, re.DOTALL)
        if sql_match:
            sql = sql_match.group(1).strip()
            pre_sql_content = content[:sql_match.start()].strip()
            post_sql_content = content[sql_match.end():].strip()

            if pre_sql_content and post_sql_content:
                explanation = f"{pre_sql_content}\n\n{post_sql_content}"
            elif pre_sql_content:
                explanation = pre_sql_content
            elif post_sql_content:
                explanation = post_sql_content
            else:
                explanation = ""

        else:
            python_match = re.search(r"```python\n(.*?)\n```", content, re.DOTALL)
            if python_match:
                sql = python_match.group(1).strip()
                explanation = content
            else:
                lines = content.split("\n")
                sql_candidates = []
                for line in lines:
                    stripped = line.strip()
                    if stripped.upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP")):
                        sql_candidates.append(line)

                if sql_candidates:
                    sql = "\n".join(sql_candidates)
                    remaining_lines = [line for line in lines if line not in sql_candidates]
                    explanation = "\n".join(remaining_lines).strip()

        if not explanation.strip() and content.strip():
            explanation = content.strip()

        QgsMessageLog.logMessage(f"Parsed SQL: {sql[:200]}...", "GeoAI", Qgis.Info)
        QgsMessageLog.logMessage(f"Parsed Explanation: {explanation[:200]}...", "GeoAI", Qgis.Info)

        return {"sql": sql, "explanation": explanation, "success": bool(sql.strip() or explanation.strip())}
