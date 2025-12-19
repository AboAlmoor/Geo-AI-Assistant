"""
Smart Assistant - Intelligent assistant for QGIS operations with layer-specific suggestions
"""

from qgis.core import QgsProject, QgsVectorLayer
from typing import Dict, List


class SmartAssistant:
    """Intelligent assistant for QGIS operations"""

    def __init__(self, llm_handler, iface, sql_executor=None):
        self.llm = llm_handler
        self.iface = iface
        self.project = QgsProject.instance()
        self.sql_executor = sql_executor

    def analyze_project(self) -> Dict:
        """Analyze current project and provide insights"""

        layers = self.project.mapLayers()
        analysis = {
            "total_layers": len(layers),
            "vector_layers": 0,
            "raster_layers": 0,
            "total_features": 0,
            "crs_list": set(),
            "geometry_types": {}
        }

        for layer_id, layer in layers.items():
            if isinstance(layer, QgsVectorLayer):
                analysis["vector_layers"] += 1
                analysis["total_features"] += layer.featureCount()
                analysis["crs_list"].add(layer.crs().authid())

                geom_type = layer.geometryType()
                analysis["geometry_types"][layer.name()] = geom_type
            else:
                analysis["raster_layers"] += 1

        return analysis

    def get_suggestions(self, model_provider: str = None, model_name: str = None) -> List[str]:
        """Get smart suggestions based on project state"""

        # Get comprehensive context from sql_executor if available
        if self.sql_executor:
            context = self.sql_executor.get_context()
        else:
            context = {
                "layers": [],
                "active_layer": self.iface.activeLayer().name() if self.iface.activeLayer() else None,
                "crs": self.project.crs().authid() if self.project.crs().isValid() else "Unknown",
                "db_type": "Unknown"
            }

        layers_info = context.get('layers', [])
        active_layer = context.get('active_layer')

        # If no active layer, try to pick the first vector layer if available
        if not active_layer and layers_info:
            for layer in layers_info:
                if layer.get('geometry_type') is not None:
                    active_layer = layer.get('name')
                    break

        # If still no active layer, return a message
        if not active_layer:
            return ["No active layer found to provide suggestions. Please add or select a layer."]

        # Prepare context for LLM, focusing on general suggestions
        llm_context = {
            "active_layer": active_layer,
            "layers": layers_info,
            "crs": context.get('crs'),
            "project_analysis": self.analyze_project()
        }

        return self.llm.get_smart_suggestions(llm_context, model_provider=model_provider, model_name=model_name)

    def suggest_analysis(self, layer_name: str, model_provider: str = None, model_name: str = None) -> Dict:
        """Suggest analyses for specific layer"""

        layer = self.project.mapLayersByName(layer_name)
        if not layer:
            return {"error": f"Layer '{layer_name}' not found"}

        layer = layer[0]

        if not isinstance(layer, QgsVectorLayer):
            return {"error": "Only vector layers are supported"}

        # Get comprehensive context from sql_executor if available
        if self.sql_executor:
            context = self.sql_executor.get_context()
        else:
            context = {"layers": [], "crs": "Unknown", "db_type": "Unknown"}

        # Find the specific layer's detailed info from the context
        target_layer_info = None
        for l in context.get('layers', []):
            if l.get('name') == layer_name:
                target_layer_info = l
                break

        if not target_layer_info:
            return {"error": f"Detailed info for layer '{layer_name}' not found in context."}

        # Prepare context for LLM
        llm_context = {
            "active_layer": layer_name,
            "layers": context.get('layers', []),
            "target_layer_info": target_layer_info,
            "crs": context.get('crs'),
            "db_type": context.get('db_type'),
            "project_analysis": self.analyze_project()
        }

        prompt = (
            f"Provide a comprehensive analysis and suggest useful operations for the QGIS vector layer named '{layer_name}'.\n"
            "Include summary statistics, potential spatial analyses, attribute insights, and relevant SQL or Python code examples. "
            "Focus on providing a 'full analysis for everything' related to this layer. "
            "Ensure all column names are used exactly as provided and wrapped in double quotes (e.g., SELECT \"Name\" FROM table).\n"
            "Organize the output with clear headings and code blocks."
        )

        suggestions = self.llm.get_smart_suggestions(llm_context, prompt=prompt, 
                                                    model_provider=model_provider, model_name=model_name)

        return {
            "success": True,
            "layer": layer_name,
            "suggestions": suggestions
        }

    def generate_style_from_description(self, layer_name: str, description: str) -> Dict:
        """Generate map styling based on natural language description"""

        layer = self.project.mapLayersByName(layer_name)
        if not layer:
            return {"error": f"Layer '{layer_name}' not found"}

        layer = layer[0]

        prompt = f"""
Generate QGIS styling code for this layer based on the description:

Layer: {layer_name}
Description: {description}

Provide Python code using QgsSymbol, QgsSimpleMarkerSymbolLayer, etc.
"""

        # This would need implementation to generate actual styling code
        return {
            "success": True,
            "message": "Style generation - to be implemented"
        }

