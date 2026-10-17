function TestResults({ testResult }) {
  if (!testResult) {
    return (
      <section className="card">
        <h2>Test Results</h2>
        <p className="muted">
          Test results will appear after the project runs.
        </p>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>Test Results</h2>

      <div
        className={
          testResult.tests_passed
            ? "test-summary success"
            : "test-summary failed"
        }
      >
        {testResult.tests_passed
          ? "✓ Tests Passed"
          : "✕ Tests Failed"}
      </div>

      <p>
        <strong>Exit code:</strong>{" "}
        {testResult.exit_code}
      </p>

      <h3>Pytest Output</h3>

      <pre className="terminal-output">
        {testResult.stdout || "No output"}
      </pre>

      {testResult.stderr && (
        <>
          <h3>Error Output</h3>

          <pre className="terminal-output error">
            {testResult.stderr}
          </pre>
        </>
      )}
    </section>
  );
}

export default TestResults;