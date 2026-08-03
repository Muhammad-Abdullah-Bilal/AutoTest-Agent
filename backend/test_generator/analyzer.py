import ast

class CodeAnalyzer:
    def __init__(self, code):
        self.code = code
        self.tree = None

    def analyze(self):
        try:
            self.tree = ast.parse(self.code)
            analysis = {
                'functions': self._get_functions(),
                'classes': self._get_classes(),
                'imports': self._get_imports()
            }
            return analysis
        except Exception as e:
            raise Exception(f'Failed to analyze code: {str(e)}')

    def _get_functions(self):
        functions = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'returns': self._get_return_type(node)
                })
        return functions

    def _get_classes(self):
        classes = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'methods': self._get_class_methods(node)
                })
        return classes

    def _get_class_methods(self, class_node):
        methods = []
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                methods.append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args]
                })
        return methods

    def _get_imports(self):
        imports = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(f'{node.module}.{node.names[0].name}')
        return imports

    def _get_return_type(self, node):
        returns = []
        for n in ast.walk(node):
            if isinstance(n, ast.Return) and n.value:
                returns.append(type(n.value).__name__)
        return returns if returns else None