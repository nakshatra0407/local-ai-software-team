function DebuggingAttempts({ attempts }) {
  return (
    <section className="card">
      <h2>Debugging Attempts</h2>

      {attempts.length === 0 ? (
        <p className="muted">
          No debugging was required.
        </p>
      ) : (
        <div className="debug-list">

          {attempts.map((attempt, index) => (
            <div
              className="debug-item"
              key={index}
            >
              <h3>
                Debugging Attempt {index + 1}
              </h3>

              <p>
                <strong>File:</strong>{" "}
                {attempt.file_modified}
              </p>

              <p>
                <strong>Analysis:</strong>{" "}
                {attempt.error_analysis}
              </p>

              <p>
                <strong>Action:</strong>{" "}
                {attempt.explanation}
              </p>
            </div>
          ))}

        </div>
      )}
    </section>
  );
}

export default DebuggingAttempts;