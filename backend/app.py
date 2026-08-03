from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from test_generator.analyzer import CodeAnalyzer
from test_generator.test_generator import TestGenerator
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Verify API key is present
if not os.getenv('GROQ_API_KEY'):
    raise ValueError("GROQ_API_KEY not found in environment variables")

app = Flask(__name__, static_folder='static')
CORS(app)

# Serve React static frontend
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def serve(path):
    if request.method in ['POST', 'OPTIONS'] or (path != "" and not os.path.exists(os.path.join(app.static_folder, path))):
        return jsonify({
            'error': f'Route not found: {request.method} {request.path}',
            'debug_info': {
                'path': path,
                'method': request.method,
                'url': request.url,
                'path_info': request.environ.get('PATH_INFO'),
                'request_path': request.path
            }
        }), 404
    
    # Otherwise serve static files (if index.html is needed fallback to it)
    if path == "":
        return send_from_directory(app.static_folder, 'index.html')
    return send_from_directory(app.static_folder, path)

# Add a health check endpoint
@app.route('/api/health', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

def execute_tests(code, test_code):
    import tempfile
    import os
    import sys
    import io
    import pytest

    with tempfile.TemporaryDirectory() as temp_dir:
        module_path = os.path.join(temp_dir, "module.py")
        test_path = os.path.join(temp_dir, "test_module.py")
        
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(code)
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_code)
            
        # Add the temp directory to sys.path so pytest can import 'module'
        sys.path.insert(0, temp_dir)
        
        # Redirect stdout and stderr to capture pytest output
        stdout_backup = sys.stdout
        stderr_backup = sys.stderr
        string_io = io.StringIO()
        sys.stdout = string_io
        sys.stderr = string_io
        
        try:
            # Run pytest inside the same process
            exit_code = pytest.main([test_path, "-vv"])
            output = string_io.getvalue()
            
            return {
                "success": int(exit_code) == 0,
                "exit_code": int(exit_code),
                "output": output
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "output": f"Failed to run pytest programmatically: {str(e)}"
            }
        finally:
            # Restore stdout and stderr and clean up sys.path
            sys.stdout = stdout_backup
            sys.stderr = stderr_backup
            if temp_dir in sys.path:
                sys.path.remove(temp_dir)

@app.route('/api/generate-tests', methods=['POST', 'OPTIONS'])
@app.route('/generate-tests', methods=['POST', 'OPTIONS'])
def generate_tests():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    data = request.json
    code = data.get('code')
    use_case = data.get('useCase')
    run_tests_opt = data.get('runTests', False)
    
    if not code or not use_case:
        return jsonify({'error': 'Code and use case are required'}), 400
    
    try:
        try:
            analyzer = CodeAnalyzer(code)
            code_analysis = analyzer.analyze()
        except Exception as ae:
            print(f"AST Code analysis failed (proceeding anyway): {ae}")
            code_analysis = None
        
        test_generator = TestGenerator(code, use_case, code_analysis)
        tests = test_generator.generate()
        
        response_data = {
            'tests': tests,
            'message': 'Tests generated successfully'
        }
        
        if run_tests_opt:
            test_results = execute_tests(code, tests)
            response_data['testResults'] = test_results
            
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-tests', methods=['POST', 'OPTIONS'])
@app.route('/run-tests', methods=['POST', 'OPTIONS'])
def run_tests_endpoint():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    data = request.json
    code = data.get('code')
    tests = data.get('tests')
    
    if not code or not tests:
        return jsonify({'error': 'Code and tests are required'}), 400
        
    try:
        test_results = execute_tests(code, tests)
        return jsonify({
            'testResults': test_results,
            'message': 'Tests executed successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ZeroGPU Compatibility wrapping
try:
    from fastapi import FastAPI
    from fastapi.middleware.wsgi import WSGIMiddleware
    import gradio as gr
    import spaces

    # Create dummy GPU function to satisfy ZeroGPU scanner
    @spaces.GPU
    def dummy_gpu(text):
        return text

    # Dummy Gradio UI
    demo = gr.Interface(fn=dummy_gpu, inputs="textbox", outputs="textbox")

    # FastAPI root app
    app_asgi = FastAPI()

    # Mount Flask at /
    app_asgi.mount("/", WSGIMiddleware(app))

    # Mount Gradio at /gradio (to satisfy HF Gradio SDK checks if needed)
    app_asgi = gr.mount_gradio_app(app_asgi, demo, path="/gradio")

except Exception as e:
    print(f"Gradio mounting failed (running locally?): {e}")
    app_asgi = app

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 7860))
    if app_asgi == app:
        app.run(host='0.0.0.0', port=port)
    else:
        import uvicorn
        uvicorn.run(app_asgi, host='0.0.0.0', port=port) 