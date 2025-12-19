"""
Simple Dialog - Single dialog interface
"""

from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QMessageBox, QComboBox, QFileDialog,
    QScrollArea, QFrame, QSplitter, QTabWidget, QLineEdit
)
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtGui import QPixmap, QFont
from qgis.core import QgsMessageLog, Qgis, QgsRasterLayer
import os

from ..modules.llm_handler import LLMHandler
from ..modules.sql_executor import SQLExecutor
from ..modules.image_processor import ImageProcessor
from dotenv import load_dotenv


class WorkerThread(QThread):
    """Worker thread for async operations"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, func, *args):
        super().__init__()
        self.func = func
        self.args = args
    
    def run(self):
        try:
            result = self.func(*self.args)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class SimpleDialog(QDockWidget):
    """Simple single-dialog interface"""
    
    def __init__(self, iface, llm_handler, sql_executor, image_processor):
        super().__init__("GeoAI Assistant Simple", iface.mainWindow())
        self.iface = iface
        
        # Use injected handlers
        self.llm_handler = llm_handler
        self.sql_executor = sql_executor
        self.image_processor = image_processor
        
        # Image path
        self.image_path = None
        
        self.setup_ui()
        # Force docking behavior: allow only left/right docking and disable floating
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # Remove float feature so the dock cannot open as a separate floating window
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.setFloating(False)
        QgsMessageLog.logMessage("Simple dialog initialized", "GeoAI Simple", Qgis.Info)
    
    def setup_ui(self):
        """Setup the user interface"""
        main_widget = QWidget()
        self.setWidget(main_widget)
        
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Title
        title = QLabel("<h2>GeoAI Assistant Simple</h2>")
        layout.addWidget(title)
        
        # Model Selector
        model_widget = QFrame()
        model_widget.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        model_layout = QHBoxLayout()
        model_widget.setLayout(model_layout)
        
        model_layout.addWidget(QLabel("🤖 Provider:"))
        self.model_provider_combo = QComboBox()
        self.model_provider_combo.addItems([
            "Ollama", "OpenRouter", "OpenAI", "Anthropic", "Google", "HuggingFace"
        ])
        self.model_provider_combo.setCurrentText("Ollama")
        self.model_provider_combo.currentTextChanged.connect(self.update_model_list)
        model_layout.addWidget(self.model_provider_combo)
        
        model_layout.addWidget(QLabel("Model:"))
        self.model_name_combo = QComboBox()
        self.update_model_list()
        model_layout.addWidget(self.model_name_combo)
        model_layout.addStretch()
        
        layout.addWidget(model_widget)
        
        # Tab widget for SQL and Image
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # SQL Tab
        sql_tab = QWidget()
        sql_layout = QVBoxLayout()
        sql_tab.setLayout(sql_layout)
        
        # Input
        sql_layout.addWidget(QLabel("Describe what you want to do:"))
        self.input = QTextEdit()
        self.input.setPlaceholderText(
            "Example: Find all buildings within 500 meters of parks"
        )
        self.input.setMaximumHeight(100)
        sql_layout.addWidget(self.input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.generate_btn = QPushButton("Generate SQL")
        self.generate_btn.clicked.connect(self.generate_sql)
        button_layout.addWidget(self.generate_btn)
        
        self.execute_btn = QPushButton("Execute SQL")
        self.execute_btn.clicked.connect(self.execute_sql)
        self.execute_btn.setEnabled(False)
        button_layout.addWidget(self.execute_btn)
        
        sql_layout.addLayout(button_layout)
        
        # SQL Display
        sql_layout.addWidget(QLabel("Generated SQL:"))
        self.sql_display = QTextEdit()
        self.sql_display.setReadOnly(True)
        self.sql_display.setMaximumHeight(150)
        sql_layout.addWidget(self.sql_display)
        
        # Results
        sql_layout.addWidget(QLabel("Results:"))
        self.results_table = QTableWidget()
        sql_layout.addWidget(self.results_table)
        
        tabs.addTab(sql_tab, "🔍 SQL Generator")
        
        # Image Tab
        image_tab = QWidget()
        image_layout = QVBoxLayout()
        image_tab.setLayout(image_layout)
        
        # Image Upload
        upload_layout = QHBoxLayout()
        upload_btn = QPushButton("📁 Upload Image")
        upload_btn.clicked.connect(self.upload_image)
        upload_layout.addWidget(upload_btn)
        
        self.image_path_label = QLabel("No image selected")
        upload_layout.addWidget(self.image_path_label)
        upload_layout.addStretch()
        image_layout.addLayout(upload_layout)
        
        # Image Preview
        image_layout.addWidget(QLabel("Image Preview:"))
        self.image_preview_scroll = QScrollArea()
        self.image_preview_scroll.setWidgetResizable(True)
        self.image_preview_scroll.setMinimumHeight(200)
        self.image_preview_scroll.setMaximumHeight(300)
        
        self.image_preview_label = QLabel()
        self.image_preview_label.setAlignment(Qt.AlignCenter)
        self.image_preview_label.setText("No image selected")
        self.image_preview_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.image_preview_scroll.setWidget(self.image_preview_label)
        image_layout.addWidget(self.image_preview_scroll)
        
        # Add to QGIS button
        add_to_qgis_btn = QPushButton("➕ Add Image to QGIS Map")
        add_to_qgis_btn.clicked.connect(self.add_image_to_qgis)
        image_layout.addWidget(add_to_qgis_btn)
        
        # Conversion type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Convert to:"))
        self.conversion_type = QComboBox()
        self.conversion_type.addItems(["SQL", "Python", "Both"])
        type_layout.addWidget(self.conversion_type)
        type_layout.addStretch()
        image_layout.addLayout(type_layout)
        
        # Azure description
        image_layout.addWidget(QLabel("Azure Image Analysis:"))
        self.azure_description = QTextEdit()
        self.azure_description.setReadOnly(True)
        self.azure_description.setMaximumHeight(100)
        self.azure_description.setVisible(False)
        image_layout.addWidget(self.azure_description)
        
        # Convert button
        convert_btn = QPushButton("🔄 Analyze & Generate Code")
        convert_btn.clicked.connect(self.analyze_and_convert_image)
        convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        image_layout.addWidget(convert_btn)
        
        # Generated code
        image_layout.addWidget(QLabel("Generated Code:"))
        self.image_code_output = QTextEdit()
        self.image_code_output.setReadOnly(True)
        self.image_code_output.setFont(QFont("Courier", 10))
        image_layout.addWidget(self.image_code_output)
        
        tabs.addTab(image_tab, "🖼️ Image to Code")
        
        # Status
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Settings tab: database credentials
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        settings_tab.setLayout(settings_layout)

        settings_layout.addWidget(QLabel("Database Connection Settings"))

        form_layout = QVBoxLayout()

        self.db_host_input = QLineEdit()
        self.db_port_input = QLineEdit()
        self.db_name_input = QLineEdit()
        self.db_user_input = QLineEdit()
        self.db_password_input = QLineEdit()
        self.db_password_input.setEchoMode(QLineEdit.Password)

        form_layout.addWidget(QLabel("Host:"))
        form_layout.addWidget(self.db_host_input)
        form_layout.addWidget(QLabel("Port:"))
        form_layout.addWidget(self.db_port_input)
        form_layout.addWidget(QLabel("Database name:"))
        form_layout.addWidget(self.db_name_input)
        form_layout.addWidget(QLabel("User:"))
        form_layout.addWidget(self.db_user_input)
        form_layout.addWidget(QLabel("Password:"))
        form_layout.addWidget(self.db_password_input)

        settings_layout.addLayout(form_layout)

        btns = QHBoxLayout()
        self.save_db_btn = QPushButton("Save DB Credentials")
        self.save_db_btn.clicked.connect(self.save_db_credentials)
        btns.addWidget(self.save_db_btn)

        self.test_db_btn = QPushButton("Test DB Connection")
        self.test_db_btn.clicked.connect(self.test_db_connection)
        btns.addWidget(self.test_db_btn)

        btns.addStretch()
        settings_layout.addLayout(btns)

        tabs.addTab(settings_tab, "⚙️ Settings")

        # Load existing settings
        self._load_settings()
    
    def generate_sql(self):
        """Generate SQL from natural language"""
        prompt = self.input.toPlainText().strip()
        
        if not prompt:
            QMessageBox.warning(self, "Warning", "Please enter a description")
            return
        
        if not self.llm_handler or not self.sql_executor:
            QMessageBox.critical(self, "Error", "LLM handler or SQL executor not initialized")
            return
        
        self.status_label.setText("Generating SQL...")
        self.generate_btn.setEnabled(False)
        
        # Get context
        context = self.sql_executor.get_context()
        
        # Use selected model
        provider = self.get_selected_provider()
        model = self.get_selected_model()
        
        # Run in thread
        self.worker = WorkerThread(
            self.llm_handler.generate_sql,
            prompt,
            context,
            provider,
            model
        )
        self.worker.finished.connect(self.on_sql_generated)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_sql_generated(self, result):
        """Handle SQL generation result"""
        self.generate_btn.setEnabled(True)
        
        if "error" in result:
            error = result.get("error", "Unknown error")
            QMessageBox.critical(self, "Error", error)
            self.status_label.setText(f"Error: {error}")
            self.sql_display.setText(f"ERROR: {error}")
            QgsMessageLog.logMessage(f"SQL generation error: {error}", "GeoAI Simple", Qgis.Critical)
        else:
            sql = result.get("sql", "")
            self.sql_display.setText(sql)
            self.execute_btn.setEnabled(True)
            self.status_label.setText("SQL generated successfully")
            QgsMessageLog.logMessage("SQL generated", "GeoAI Simple", Qgis.Info)
    
    def execute_sql(self):
        """Execute generated SQL"""
        sql = self.sql_display.toPlainText().strip()
        
        if not sql:
            QMessageBox.warning(self, "Warning", "No SQL to execute")
            return
        
        self.status_label.setText("Executing SQL...")
        self.execute_btn.setEnabled(False)
        
        # Run in thread - use execute_sql method
        self.worker = WorkerThread(self.sql_executor.execute_sql, sql)
        self.worker.finished.connect(self.on_sql_executed)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_sql_executed(self, result):
        """Handle SQL execution result"""
        self.execute_btn.setEnabled(True)
        
        if "error" in result:
            error = result.get("error", "Unknown error")
            QMessageBox.critical(self, "Error", error)
            self.status_label.setText(f"Error: {error}")
            QgsMessageLog.logMessage(f"SQL execution error: {error}", "GeoAI Simple", Qgis.Critical)
        else:
            rows = result.get("rows", [])
            self.display_results(rows)
            row_count = len(rows) if rows else 0
            self.status_label.setText(f"Query executed: {row_count} rows")
            QgsMessageLog.logMessage(f"SQL executed: {row_count} rows", "GeoAI Simple", Qgis.Info)
    
    def display_results(self, rows):
        """Display results in table"""
        if not rows:
            self.results_table.setRowCount(0)
            self.results_table.setColumnCount(0)
            return
        
        # Get column names
        columns = list(rows[0].keys())
        
        # Setup table
        self.results_table.setColumnCount(len(columns))
        self.results_table.setRowCount(len(rows))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        # Fill table
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_name in enumerate(columns):
                value = str(row_data.get(col_name, ""))
                self.results_table.setItem(row_idx, col_idx, QTableWidgetItem(value))
        
        self.results_table.resizeColumnsToContents()
    
    def on_error(self, error_msg):
        """Handle worker thread error"""
        self.generate_btn.setEnabled(True)
        self.execute_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)
        self.status_label.setText(f"Error: {error_msg}")
    
    def update_model_list(self):
        """Update model list based on selected provider"""
        provider = self.model_provider_combo.currentText().lower()
        self.model_name_combo.clear()
        
        if provider == "ollama":
            self.model_name_combo.addItems([
                "phi3", "llama3", "mistral", "mixtral", "codellama", "gemma", "qwen"
            ])
        elif provider == "openrouter":
            self.model_name_combo.addItems([
                "mistralai/mistral-7b-instruct",
                "meta-llama/llama-3.1-8b-instruct",
                "google/gemma-7b-it",
                "anthropic/claude-3-haiku"
            ])
        elif provider == "openai":
            self.model_name_combo.addItems([
                "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"
            ])
        elif provider == "anthropic":
            self.model_name_combo.addItems([
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ])
        elif provider == "google":
            self.model_name_combo.addItems([
                "gemini-pro", "gemini-pro-vision"
            ])
        elif provider == "huggingface":
            self.model_name_combo.addItems([
                "mistralai/Mistral-7B-Instruct-v0.2",
                "meta-llama/Llama-2-7b-chat-hf"
            ])

    def _get_env_path(self) -> str:
        """Return plugin .env file path"""
        plugin_dir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(plugin_dir, ".env")

    def _load_settings(self):
        """Load DB fields from .env"""
        env_path = self._get_env_path()
        load_dotenv(env_path, override=True)

        self.db_host_input.setText(os.getenv('DB_HOST', 'localhost'))
        self.db_port_input.setText(os.getenv('DB_PORT', '5432'))
        self.db_name_input.setText(os.getenv('DB_NAME', ''))
        self.db_user_input.setText(os.getenv('DB_USER', ''))
        self.db_password_input.setText(os.getenv('DB_PASSWORD', ''))

    def save_db_credentials(self):
        """Save DB credentials to the plugin .env file"""
        env_path = self._get_env_path()

        # Read existing .env content
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

        keys = {
            'DB_HOST': self.db_host_input.text().strip(),
            'DB_PORT': self.db_port_input.text().strip(),
            'DB_NAME': self.db_name_input.text().strip(),
            'DB_USER': self.db_user_input.text().strip(),
            'DB_PASSWORD': self.db_password_input.text().strip(),
        }

        # Update or append keys while preserving file structure
        out_lines = []
        seen = set()
        for raw in lines:
            stripped = raw.strip()
            if not stripped or stripped.startswith('#') or '=' not in raw:
                out_lines.append(raw)
                continue

            k, _, v = raw.partition('=')
            k = k.strip()
            if k in keys:
                out_lines.append(f"{k}={keys[k]}\n")
                seen.add(k)
            else:
                out_lines.append(raw)

        for k, v in keys.items():
            if k not in seen:
                out_lines.append(f"{k}={v}\n")

        # Write back
        try:
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(out_lines)
            load_dotenv(env_path, override=True)
            QMessageBox.information(self, "Saved", "Database credentials saved to .env")
            QgsMessageLog.logMessage("DB credentials saved to .env", "GeoAI Simple", Qgis.Info)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save .env: {e}")
            QgsMessageLog.logMessage(f"Failed to save .env: {e}", "GeoAI Simple", Qgis.Critical)

    def test_db_connection(self):
        """Test the DB connection using QSqlDatabase"""
        host = self.db_host_input.text().strip() or '127.0.0.1'
        port = int(self.db_port_input.text().strip() or '5432')
        database = self.db_name_input.text().strip()
        username = self.db_user_input.text().strip()
        password = self.db_password_input.text().strip()

        if host.lower() == 'localhost':
            host = '127.0.0.1'

        conn_name = f"GeoAI_Test_{int(time.time())}"
        from qgis.PyQt.QtSql import QSqlDatabase
        if QSqlDatabase.contains(conn_name):
            QSqlDatabase.removeDatabase(conn_name)

        db = QSqlDatabase.addDatabase('QPSQL', conn_name)
        db.setHostName(host)
        db.setPort(port)
        db.setDatabaseName(database)
        db.setUserName(username)
        db.setPassword(password)
        db.setConnectOptions('connect_timeout=5')

        if db.open():
            QMessageBox.information(self, "Success", "Connection successful")
            db.close()
            QSqlDatabase.removeDatabase(conn_name)
            QgsMessageLog.logMessage("Test DB connection successful", "GeoAI Simple", Qgis.Info)
        else:
            err = db.lastError().text()
            QMessageBox.critical(self, "Failed", f"Connection failed: {err}")
            QSqlDatabase.removeDatabase(conn_name)
            QgsMessageLog.logMessage(f"Test DB connection failed: {err}", "GeoAI Simple", Qgis.Critical)
    
    def get_selected_provider(self):
        """Get selected provider"""
        return self.model_provider_combo.currentText().lower()
    
    def get_selected_model(self):
        """Get selected model name"""
        return self.model_name_combo.currentText()
    
    def upload_image(self):
        """Upload and preview image"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)"
        )
        
        if file_path:
            self.image_path = file_path
            self.image_path_label.setText(os.path.basename(file_path))
            
            # Display image preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to fit
                scaled_pixmap = pixmap.scaled(
                    400, 300,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_preview_label.setPixmap(scaled_pixmap)
                self.image_preview_label.setText("")
            else:
                self.image_preview_label.setText("Failed to load image")
            
            QgsMessageLog.logMessage(f"Image loaded: {file_path}", "GeoAI Simple", Qgis.Info)
    
    def add_image_to_qgis(self):
        """Add image to QGIS map"""
        if not self.image_path or not os.path.exists(self.image_path):
            QMessageBox.warning(self, "Warning", "Please select an image first")
            return
        
        try:
            layer_name = os.path.splitext(os.path.basename(self.image_path))[0]
            layer = QgsRasterLayer(self.image_path, layer_name)
            
            if not layer.isValid():
                QMessageBox.critical(self, "Error", f"Failed to load image: {layer.error().message()}")
                return
            
            from qgis.core import QgsProject
            QgsProject.instance().addMapLayer(layer)
            self.iface.mapCanvas().setExtent(layer.extent())
            self.iface.mapCanvas().refresh()
            
            QMessageBox.information(self, "Success", f"Image '{layer_name}' added to QGIS map")
            self.status_label.setText(f"Image added to map: {layer_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add image: {str(e)}")
    
    def analyze_and_convert_image(self):
        """Analyze image with Azure and generate code"""
        if not self.image_path or not os.path.exists(self.image_path):
            QMessageBox.warning(self, "Warning", "Please upload an image first")
            return
        
        if not self.image_processor:
            QMessageBox.critical(self, "Error", "Image processor not initialized")
            return
        
        conversion_type = self.conversion_type.currentText().lower()
        provider = self.get_selected_provider()
        model = self.get_selected_model()
        
        self.status_label.setText(f"Analyzing image and generating {conversion_type}...")
        self.image_code_output.setText("Processing...")
        
        # Run in thread
        self.worker = WorkerThread(
            self.image_processor.process_model_image,
            self.image_path,
            conversion_type,
            provider,
            model
        )
        self.worker.finished.connect(self.on_image_converted)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_image_converted(self, result):
        """Handle image conversion result"""
        if "error" in result:
            error = result.get("error", "Unknown error")
            QMessageBox.critical(self, "Error", error)
            self.image_code_output.setText(f"ERROR: {error}")
            self.status_label.setText(f"Error: {error}")
            
            # Show Azure error details if available
            if "Azure Computer Vision" in error:
                self.azure_description.setText(error)
                self.azure_description.setVisible(True)
        else:
            # Show Azure description if available
            azure_desc = result.get("azure_description", "")
            if azure_desc:
                self.azure_description.setText(azure_desc)
                self.azure_description.setVisible(True)
            
            # Get the appropriate code based on conversion type
            conversion_type = self.conversion_type.currentText().lower()
            
            # Try to get the right code (sql_code, python_code, or code)
            code = ""
            sql_code = result.get("sql_code", "")
            python_code = result.get("python_code", "")
            
            # Handle "Both" type by combining both codes
            if conversion_type == 'both':
                parts = []
                if sql_code:
                    parts.append("-- SQL Code:\n" + sql_code)
                if python_code:
                    if parts:
                        parts.append("\n\n# Python Code:\n" + python_code)
                    else:
                        parts.append("# Python Code:\n" + python_code)
                code = "\n".join(parts)
            elif conversion_type == 'sql':
                code = sql_code
            elif conversion_type == 'python':
                code = python_code
            
            # Fall back to general code field
            if not code:
                code = result.get("code", "")
            
            # As last resort, get explanation if it looks like code
            if not code:
                explanation = result.get("explanation", "")
                if explanation and any(keyword in explanation.lower() for keyword in ['select', 'def ', 'import ', 'create']):
                    code = explanation
            
            if code and code.strip():
                self.image_code_output.setText(code)
                self.status_label.setText("Code generated successfully")
            else:
                # Show raw response for debugging
                raw = result.get("raw_response", "")
                if raw:
                    self.image_code_output.setText(f"Raw Response:\n\n{raw}")
                    self.status_label.setText("Code extraction failed - showing raw response")
                else:
                    self.image_code_output.setText("No code generated")
                    self.status_label.setText("Conversion completed but no code returned")


