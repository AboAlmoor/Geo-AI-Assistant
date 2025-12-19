"""
SQL Executor - Executes SQL queries and extracts context from QGIS layers and databases
Supports: PostgreSQL/PostGIS, SpatiaLite, GeoPackage, Shapefiles
"""

import os
from qgis.core import (
    QgsVectorLayer, QgsProject, QgsDataSourceUri,
    QgsMessageLog, Qgis, QgsFeature
)
from qgis.PyQt.QtSql import QSqlDatabase, QSqlQuery
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file in plugin directory
PLUGIN_DIR = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(PLUGIN_DIR, ".env")
load_dotenv(env_path, override=True)


class SQLExecutor:
    """Executes SQL queries and extracts context from QGIS layers and databases."""

    def __init__(self, iface):
        self.iface = iface
        self.project = QgsProject.instance()

    def get_context(self) -> Dict:
        """Collect detailed QGIS layer context for accurate SQL generation."""

        project = QgsProject.instance()
        layers = project.mapLayers()

        context = {
            "layers": [],
            "tables": [],
            "table_fields": {},
            "db_type": "Unknown",
            "crs": project.crs().authid() if project.crs().isValid() else "Unknown",
            "selected_count": 0,
            "active_layer": self.iface.activeLayer().name() if self.iface.activeLayer() else None,
        }

        for layer_id, layer in layers.items():
            if not isinstance(layer, QgsVectorLayer):
                continue

            fields = [f.name() for f in layer.fields()]
            geom_field = self._detect_geom_column(layer)

            info = {
                "name": layer.name(),
                "provider": layer.providerType(),
                "geometry_field": geom_field,
                "geometry_type": layer.wkbType(),
                "feature_count": layer.featureCount(),
                "fields": fields,
            }

            # Detect database type
            source = layer.source().lower()
            if "postgresql" in source or "postgis" in source or "host=" in source:
                context["db_type"] = "PostgreSQL/PostGIS"
            elif "spatialite" in source:
                context["db_type"] = "SpatiaLite"
            elif "gpkg" in source:
                context["db_type"] = "GeoPackage"
            elif "shp" in source:
                context["db_type"] = "Shapefile"

            context["layers"].append(info)
            context["tables"].append(layer.name())
            context["table_fields"][layer.name()] = fields

            # Count selections
            if layer.selectedFeatureCount() > 0:
                context["selected_count"] += layer.selectedFeatureCount()

        return context

    def _detect_geom_column(self, layer: QgsVectorLayer) -> str:
        """Try to detect the geometry column name for PostGIS/SpatiaLite layers."""
        try:
            uri = QgsDataSourceUri(layer.source())
            geom = uri.geometryColumn()
            if geom:
                return geom
        except Exception:
            pass

        # Fallback for local datasets
        try:
            provider_fields = layer.dataProvider().fields()
            for f in provider_fields:
                if f.typeName().lower() in ["geometry", "geom"]:
                    return f.name()
        except Exception:
            pass

        return "geom"

    def execute_sql(self, sql: str, layer_name: Optional[str] = None) -> Dict:
        """Execute SQL query on specified layer or database."""

        try:
            if layer_name:
                layers = self.project.mapLayersByName(layer_name)
                if not layers:
                    return {"error": f"Layer '{layer_name}' not found"}
                layer = layers[0]
            else:
                layer = self.iface.activeLayer()
                if not layer:
                    return {"error": "No active layer selected"}

            provider_type = layer.dataProvider().name().lower()

            if "postgres" in provider_type:
                return self._execute_postgres(sql, layer)
            elif provider_type in ["spatialite", "ogr"]:
                return self._execute_spatialite(sql, layer)
            else:
                return self._execute_attribute_query(sql, layer)

        except Exception as e:
            return {"error": str(e)}

    def _execute_postgres(self, sql: str, layer: QgsVectorLayer) -> Dict:
        """Execute SQL on PostgreSQL/PostGIS database."""

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
            return {"error": error_msg}

        connection_name = f"GeoAI_{database}_{username}"
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
            return {"error": error_msg}

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
            return {"error": error, "sql": sql}

        # Collect query results
        results = []
        record = query.record()
        field_names = [record.fieldName(i) for i in range(record.count())]

        while query.next():
            row = {name: query.value(i) for i, name in enumerate(field_names)}
            results.append(row)

        db.close()
        QSqlDatabase.removeDatabase(connection_name)

        QgsMessageLog.logMessage(
            f"Query executed successfully - {len(results)} rows returned",
            "GeoAI",
            Qgis.Info
        )

        return {"success": True, "rows": results, "row_count": len(results)}

    def _execute_spatialite(self, sql: str, layer: QgsVectorLayer) -> Dict:
        """Execute SQL on SpatiaLite or GeoPackage."""
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
                return {"success": True, "rows": rows, "row_count": len(rows)}

            conn.commit()
            conn.close()
            return {"success": True, "message": "Query executed successfully"}

        except Exception as e:
            return {"error": str(e), "sql": sql}

    def _execute_attribute_query(self, sql: str, layer: QgsVectorLayer) -> Dict:
        """Execute simple attribute queries on in-memory or shapefile layers."""
        import re

        where_match = re.search(r"WHERE\s+(.+?)(?:ORDER|LIMIT|$)", sql, re.IGNORECASE)
        if not where_match:
            return {"error": "Unsupported query format for non-database layer."}

        where_clause = where_match.group(1).strip()
        layer.selectByExpression(where_clause)

        results = []
        for feature in layer.selectedFeatures():
            row = {field.name(): feature[field.name()] for field in layer.fields()}
            results.append(row)

        return {"success": True, "rows": results, "row_count": len(results)}

    def create_layer_from_sql(self, sql: str, layer_name: str) -> Dict:
        """Create a temporary memory layer from SQL query results."""
        result = self.execute_sql(sql)
        if "error" in result:
            return result
        if not result.get("rows"):
            return {"error": "Query returned no results"}

        # Define memory layer schema
        uri = "Point?crs=epsg:4326"
        for field_name in result["rows"][0].keys():
            uri += f"&field={field_name}:string"

        layer = QgsVectorLayer(uri, layer_name, "memory")
        provider = layer.dataProvider()

        features = []
        for row in result["rows"]:
            feature = QgsFeature()
            feature.setAttributes(list(row.values()))
            features.append(feature)

        provider.addFeatures(features)
        layer.updateExtents()
        self.project.addMapLayer(layer)

        return {
            "success": True,
            "message": f"Layer '{layer_name}' created with {len(features)} features",
        }

