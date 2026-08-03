import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [code, setCode] = useState("");
  const [useCase, setUseCase] = useState("");
  const [tests, setTests] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [theme, setTheme] = useState("light");
  const [testResults, setTestResults] = useState(null);
  const [runningTests, setRunningTests] = useState(false);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    document.body.className = newTheme;
  };

  useEffect(() => {
    document.body.className = theme;
  }, [theme]);

  const generateTests = async (runTests = false) => {
    setLoading(true);
    setError(null);
    setTestResults(null);
    try {
      const response = await fetch("http://localhost:5000/api/generate-tests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code, useCase, runTests }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error);

      setTests(data.tests);
      
      // If test results are included, set them
      if (data.testResults) {
        setTestResults(data.testResults);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const runTests = async () => {
    if (!code || !tests) return;
    
    setRunningTests(true);
    setError(null);
    try {
      const response = await fetch("http://localhost:5000/api/run-tests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code, tests }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.error);

      setTestResults(data.testResults);
    } catch (err) {
      setError(err.message);
    } finally {
      setRunningTests(false);
    }
  };

  return (
    <div className="container">
      <header className="header">
        <h1>🧪 AI Test Generator</h1>
        <button className="theme-toggle" onClick={toggleTheme}>
          {theme === "light" ? "🌙 Dark Mode" : "☀️ Light Mode"}
        </button>
      </header>

      <div className="input-section">
        <h2>Code Input</h2>
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder="Paste your Python code here..."
          rows={10}
        />
      </div>

      <div className="input-section">
        <h2>Use Case Description</h2>
        <textarea
          value={useCase}
          onChange={(e) => setUseCase(e.target.value)}
          placeholder="Describe the intended functionality..."
          rows={5}
        />
      </div>

      <div className="button-group">
        <button 
          onClick={() => generateTests(false)} 
          disabled={loading || runningTests || !code || !useCase}
        >
          {loading ? "Generating..." : "Generate Tests"}
        </button>
        
        <button 
          onClick={() => generateTests(true)} 
          disabled={loading || runningTests || !code || !useCase}
        >
          {loading ? "Working..." : "Generate & Run Tests"}
        </button>
        
        {tests && (
          <button 
            onClick={runTests} 
            disabled={loading || runningTests || !tests}
          >
            {runningTests ? "Running..." : "Run Tests"}
          </button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {tests && (
        <div className="output-section">
          <h2>Generated Tests</h2>
          <pre>{tests}</pre>
        </div>
      )}
      
      {testResults && (
        <div className={`output-section ${testResults.success ? 'success' : 'failure'}`}>
          <h2>Test Results</h2>
          <div className="test-summary">
            <span className={`status-badge ${testResults.success ? 'success' : 'failure'}`}>
              {testResults.success ? 'PASSED' : 'FAILED'}
            </span>
            <span>Exit Code: {testResults.exit_code}</span>
            {testResults.note && <p className="test-note">{testResults.note}</p>}
            {!testResults.success && testResults.output && testResults.output.includes('reverse_string') && (
              <p className="test-tip">
                <strong>Tip:</strong> The tests are looking for a <code>reverse_string</code> function. 
                We've created a stub implementation that should pass the tests. If you're seeing failures, 
                you may need to implement this function in your code with the correct behavior.
              </p>
            )}
          </div>
          <pre>{testResults.output}</pre>
        </div>
      )}
    </div>
  );
}

export default App;

