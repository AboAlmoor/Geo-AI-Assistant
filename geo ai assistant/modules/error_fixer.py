"""
Error Fixer - Automatically detect and fix SQL errors with LLM assistance
"""

from typing import Dict, List
from qgis.core import QgsMessageLog, Qgis


class ErrorFixer:
    """Automatically detect and fix SQL errors"""

    def __init__(self, llm_handler, sql_executor):
        self.llm = llm_handler
        self.sql_executor = sql_executor
        self.max_attempts = 3

    def execute_with_auto_fix(self, sql: str, layer_name: str = None, 
                              model_provider: str = None, model_name: str = None) -> Dict:
        """Execute SQL with automatic error fixing"""

        context = self.sql_executor.get_context()
        attempt = 0
        current_sql = sql
        history = []

        QgsMessageLog.logMessage(
            f"Starting auto-fix execution with max {self.max_attempts} attempts",
            "GeoAI",
            Qgis.Info
        )

        while attempt < self.max_attempts:
            attempt += 1

            QgsMessageLog.logMessage(
                f"Attempt {attempt}/{self.max_attempts}",
                "GeoAI",
                Qgis.Info
            )

            # Try to execute
            result = self.sql_executor.execute_sql(current_sql, layer_name)

            if result.get("success"):
                QgsMessageLog.logMessage(
                    f"SQL executed successfully on attempt {attempt}",
                    "GeoAI",
                    Qgis.Success
                )
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt,
                    "history": history,
                    "final_sql": current_sql
                }

            # If error, record it
            error = result.get("error", "Unknown error")

            QgsMessageLog.logMessage(
                f"Attempt {attempt} failed: {error}",
                "GeoAI",
                Qgis.Warning
            )

            history.append({
                "attempt": attempt,
                "sql": current_sql,
                "error": error
            })

            # If max attempts reached, return failure
            if attempt >= self.max_attempts:
                QgsMessageLog.logMessage(
                    "Max attempts reached, giving up",
                    "GeoAI",
                    Qgis.Critical
                )
                break

            # Ask LLM to fix
            QgsMessageLog.logMessage(
                "Asking LLM to fix the error...",
                "GeoAI",
                Qgis.Info
            )

            try:
                fix_result = self.llm.fix_sql_error(current_sql, error, context, model_provider, model_name)

                if "error" in fix_result:
                    QgsMessageLog.logMessage(
                        f"LLM failed to generate fix: {fix_result['error']}",
                        "GeoAI",
                        Qgis.Critical
                    )
                    return {
                        "success": False,
                        "error": f"Could not generate fix: {fix_result['error']}",
                        "history": history
                    }

                # Get the fixed SQL
                fixed_sql = fix_result.get("sql", "").strip()

                if not fixed_sql or fixed_sql == current_sql:
                    QgsMessageLog.logMessage(
                        "LLM returned same SQL or empty SQL",
                        "GeoAI",
                        Qgis.Warning
                    )
                    # Try to extract SQL from explanation
                    explanation = fix_result.get("explanation", "")
                    import re
                    sql_match = re.search(r"```sql\n(.*?)\n```", explanation, re.DOTALL)
                    if sql_match:
                        fixed_sql = sql_match.group(1).strip()
                    else:
                        break

                current_sql = fixed_sql
                QgsMessageLog.logMessage(
                    f"Trying fixed SQL: {current_sql[:100]}...",
                    "GeoAI",
                    Qgis.Info
                )

            except Exception as e:
                QgsMessageLog.logMessage(
                    f"Exception during fix generation: {str(e)}",
                    "GeoAI",
                    Qgis.Critical
                )
                return {
                    "success": False,
                    "error": f"Exception during fix: {str(e)}",
                    "history": history
                }

        # All attempts failed
        return {
            "success": False,
            "error": f"Failed after {self.max_attempts} attempts. Last error: {history[-1]['error'] if history else 'Unknown'}",
            "history": history,
            "final_sql": current_sql
        }

    def fix_sql_error(self, sql: str, error_msg: str, context: Dict = None,
                     model_provider: str = None, model_name: str = None) -> Dict:
        """Try to fix a SQL error with LLM assistance"""
        try:
            if not context:
                context = self.sql_executor.get_context()

            fix_result = self.llm.fix_sql_error(sql, error_msg, context, model_provider, model_name)

            if "error" in fix_result:
                return {
                    "error": fix_result["error"]
                }

            return {
                "sql": fix_result.get("sql", sql),
                "explanation": fix_result.get("explanation", "Fixed SQL syntax")
            }

        except Exception as e:
            return {
                "error": f"Error fixing SQL: {str(e)}"
            }

    def analyze_error(self, sql: str, error: str) -> Dict:
        """Analyze SQL error and provide suggestions"""

        error_lower = error.lower()
        suggestions = []

        # Common error patterns
        if "column" in error_lower and ("does not exist" in error_lower or "not found" in error_lower):
            suggestions.append("Column name may be incorrect or need to be quoted")
            suggestions.append('Try using double quotes and uppercase: "COLUMN_NAME"')

        if "table" in error_lower and ("does not exist" in error_lower or "not found" in error_lower):
            suggestions.append("Table name may be incorrect")
            suggestions.append("Check available tables in the context")

        if "syntax error" in error_lower:
            suggestions.append("SQL syntax error detected")
            suggestions.append("Check for missing commas, parentheses, or keywords")

        if "permission" in error_lower or "denied" in error_lower:
            suggestions.append("Permission error - check database access rights")

        if "geometry" in error_lower or "geom" in error_lower:
            suggestions.append("Geometry-related error")
            suggestions.append("Check if PostGIS/SpatiaLite is properly loaded")

        if not suggestions:
            suggestions.append("General SQL error")
            suggestions.append("Check SQL syntax and available tables/columns")

        return {
            "error": error,
            "suggestions": suggestions,
            "error_type": self._classify_error(error)
        }

    def _classify_error(self, error: str) -> str:
        """Classify error type"""
        error_lower = error.lower()

        if "column" in error_lower:
            return "COLUMN_ERROR"
        elif "table" in error_lower:
            return "TABLE_ERROR"
        elif "syntax" in error_lower:
            return "SYNTAX_ERROR"
        elif "permission" in error_lower or "denied" in error_lower:
            return "PERMISSION_ERROR"
        elif "geometry" in error_lower or "geom" in error_lower:
            return "GEOMETRY_ERROR"
        elif "connection" in error_lower:
            return "CONNECTION_ERROR"
        else:
            return "UNKNOWN_ERROR"

    def suggest_column_fix(self, column_name: str, available_columns: List[str]) -> List[str]:
        """Suggest similar column names"""
        from difflib import get_close_matches

        matches = get_close_matches(
            column_name.lower(),
            [c.lower() for c in available_columns],
            n=5,
            cutoff=0.6
        )

        suggestions = []
        for match in matches:
            # Find original case
            for col in available_columns:
                if col.lower() == match:
                    suggestions.append(f'"{col.upper()}"')
                    break

        return suggestions

