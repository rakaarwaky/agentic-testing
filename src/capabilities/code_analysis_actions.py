import ast
from src.taxonomy import ICodeAnalyzer


class AstAnalyzer(ICodeAnalyzer):
    """Static analysis using Python AST (Capability)."""

    async def analyze_file(self, file_path: str) -> dict:
        try:
            with open(file_path, "r") as f:
                tree = ast.parse(f.read())

            classes = [
                node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
            ]
            functions = [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef)
            ]

            # Simple complexity: count nodes
            complexity = len(list(ast.walk(tree))) / 10.0

            return {
                "file": file_path,
                "classes": classes,
                "functions": functions,
                "complexity_score": round(float(complexity), 2),
            }
        except Exception as e:
            return {"error": str(e)}
