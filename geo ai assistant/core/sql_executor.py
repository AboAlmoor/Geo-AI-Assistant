"""
Simple SQL Executor - Basic SQL execution
"""

import os
from dotenv import load_dotenv
from typing import Dict, List
from qgis.core import QgsVectorLayer, QgsProject, QgsDataSourceUri, QgsMessageLog, Qgis
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery

# Load environment variables from .env file in plugin directory
PLUGIN_DIR = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(PLUGIN_DIR, ".env")
load_dotenv(env_path, override=True)


class SimpleSQLExecutor:
    """Simple SQL executor"""
    
    def __init__(self, iface):
        self.iface = iface
        self.project = QgsProject.instance()
    
    def get_context(self) -> str:
        """Get simple context string"""
        layers = self.project.mapLayers()
        context_parts = []
        
        for layer_id, layer in layers.items():
            if isinstance(layer, QgsVectorLayer):
                fields = [f.name() for f in layer.fields()]
                context_parts.append(f"Table: {layer.name()}, Fields: {', '.join(fields)}")
        
        return "\n".join(context_parts) if context_parts else "No layers available"
    
    def execute(self, sql: str) -> Dict:
        """Execute SQL on active layer"""
        layer = self.iface.activeLayer()
        if not layer:
            return {"error": "No active layer selected", "success": False}
        
        if not isinstance(layer, QgsVectorLayer):
            return {"error": "Active layer is not a vector layer", "success": False}
        
        provider_type = layer.dataProvider().name().lower()
        
        try:
            if "postgres" in provider_type:
                return self._execute_postgres(sql, layer)
            elif provider_type in ["spatialite", "ogr"]:
                return self._execute_spatialite(sql, layer)
            else:
                return {"error": "Unsupported layer type", "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _execute_postgres(self, sql: str, layer: QgsVectorLayer) -> Dict:
        """Execute SQL on PostgreSQL/PostGIS"""
        uri = QgsDataSourceUri(layer.source())
        
        # Use layer credentials, fallback to .env if not provided
        host = uri.host() or os.getenv('DB_HOST', 'localhost')
        port = int(uri.port()) if uri.port() else int(os.getenv('DB_PORT', 5432))
        database = uri.database() or os.getenv('DB_NAME', '')
        username = uri.username() or os.getenv('DB_USER', '')
        password = uri.password() or os.getenv('DB_PASSWORD', '')
        
        # Log connection details (without exposing password)
        QgsMessageLog.logMessage(
            f"PostgreSQL connection: {username}@{host}:{port}/{database}",
            "GeoAI",
            Qgis.Info
        )
        
        if not password:
            error_msg = "Database password not provided. Set DB_PASSWORD in .env file or layer connection."
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            return {"error": error_msg, "success": False}
        
        connection_name = f"GeoAI_Simple_{database}"
        if QSqlDatabase.contains(connection_name):
            QSqlDatabase.removeDatabase(connection_name)
        
        db = QSqlDatabase.addDatabase("QPSQL", connection_name)
        db.setHostName(host)
        db.setPort(port)
        db.setDatabaseName(database)
        db.setUserName(username)
        db.setPassword(password)
        
        if not db.open():
            error_msg = f"Database connection failed: {db.lastError().text()}"
            QgsMessageLog.logMessage(error_msg, "GeoAI", Qgis.Critical)
            return {"error": error_msg, "success": False}
        
        QgsMessageLog.logMessage(
            "PostgreSQL connection successful",
            "GeoAI",
            Qgis.Info
        )
        
        query = QSqlQuery(db)
        if not query.exec_(sql):
            error = query.lastError().text()
            db.close()
            QSqlDatabase.removeDatabase(connection_name)
            QgsMessageLog.logMessage(f"Query error: {error}", "GeoAI", Qgis.Critical)
            return {"error": error, "success": False}
        
        # Collect results
        results = []
        record = query.record()
        field_names = [record.fieldName(i) for i in range(record.count())]
        
        while query.next():
            row = {name: query.value(i) for i, name in enumerate(field_names)}
            results.append(row)
        
        db.close()
        QSqlDatabase.removeDatabase(connection_name)
        
        return {"rows": results, "row_count": len(results), "success": True}
    
    def _execute_spatialite(self, sql: str, layer: QgsVectorLayer) -> Dict:
        """Execute SQL on SpatiaLite"""
        import sqlite3
        
        source = layer.source().split("|")[0]
        
        try:
            conn = sqlite3.connect(source)
            conn.enable_load_extension(True)
            try:
                conn.load_extension("mod_spatialite")
            except Exception:
                pass
            
            cursor = conn.cursor()
            cursor.execute(sql)
            
            if sql.strip().upper().startswith("SELECT"):
                columns = [desc[0] for desc in cursor.description]
                rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                conn.close()
                return {"rows": rows, "row_count": len(rows), "success": True}
            
            conn.commit()
            conn.close()
            return {"message": "Query executed successfully", "success": True}
            
        except Exception as e:
            return {"error": str(e), "success": False}

