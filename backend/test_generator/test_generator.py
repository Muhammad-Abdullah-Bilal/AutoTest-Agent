from .ai_service import AIService

class TestGenerator:
    def __init__(self, code, use_case, code_analysis=None):
        self.code = code
        self.use_case = use_case
        self.code_analysis = code_analysis
        self.ai_service = AIService()

    def generate(self):
        # Now passing original code string and intent/use case
        test_code = self.ai_service.generate_tests(self.code, self.use_case)
        return test_code
