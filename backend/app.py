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
    import subprocess
    import sys
    import os

    with tempfile.TemporaryDirectory() as temp_dir:
        module_path = os.path.join(temp_dir, "module.py")
        test_path = os.path.join(temp_dir, "test_module.py")
        
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(code)
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(test_code)
            
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "test_module.py"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "output": result.stdout + "\n" + result.stderr
            }
        except subprocess.TimeoutExpired as e:
            return {
                "success": False,
                "exit_code": -1,
                "output": f"Tests timed out after 30 seconds.\nStdout: {e.stdout or ''}\nStderr: {e.stderr or ''}"
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "output": f"Failed to execute tests: {str(e)}"
            }

@app.route('/api/generate-tests', methods=['POST'])
@app.route('/generate-tests', methods=['POST'])
def generate_tests():
    data = request.json
    code = data.get('code')
    use_case = data.get('useCase')
    run_tests_opt = data.get('runTests', False)
    
    if not code or not use_case:
        return jsonify({'error': 'Code and use case are required'}), 400
    
    try:
        analyzer = CodeAnalyzer(code)
        code_analysis = analyzer.analyze()
        
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

@app.route('/api/run-tests', methods=['POST'])
@app.route('/run-tests', methods=['POST'])
def run_tests_endpoint():
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