function ExecutionStatus({
  projectId,
  status,
  testsPassed,
  iterations
}) {
  let statusText = "Waiting to start";
  let statusClass = "waiting";

  if (status === "running") {
    statusText = "AI pipeline is running";
    statusClass = "running";
  }

  if (status === "completed") {
    statusText = testsPassed
      ? "Project completed successfully"
      : "Project completed with failing tests";

    statusClass = testsPassed ? "success" : "failed";
  }

  if (status === "failed") {
    statusText = "Project execution failed";
    statusClass = "failed";
  }

  return (
    <section className="card">
      <h2>Execution Status</h2>

      <div className={`execution-status ${statusClass}`}>
        {statusText}
      </div>

      {projectId && (
        <p className="project-id">
          Project ID: {projectId}
        </p>
      )}

      <div className="status-grid">
        <div>
          <strong>Tests</strong>
          <span>
            {testsPassed === null
              ? "Not run"
              : testsPassed
              ? "Passed"
              : "Failed"}
          </span>
        </div>

        <div>
          <strong>Iterations</strong>
          <span>{iterations}</span>
        </div>
      </div>
    </section>
  );
}

export default ExecutionStatus;