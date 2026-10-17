const agents = [
  "Project Manager",
  "Architect",
  "Coding Agent",
  "Testing Agent",
  "Debugger"
];

function Pipeline({ status, iterations }) {
  const completed = status === "completed";
  const failed = status === "failed";
  const running = status === "running";

  return (
    <section className="card">
      <h2>AI Pipeline</h2>

      <div className="pipeline">

        {agents.map((agent, index) => (
          <div key={agent}>

            <div
              className={`pipeline-step ${
                completed
                  ? "completed"
                  : running
                  ? "running"
                  : "waiting"
              }`}
            >
              <span className="pipeline-icon">
                {completed ? "✓" : running ? "●" : "○"}
              </span>

              <span>{agent}</span>
            </div>

            {index < agents.length - 1 && (
              <div className="pipeline-arrow">↓</div>
            )}

          </div>
        ))}

        <div className="pipeline-arrow">↓</div>

        <div
          className={`pipeline-step ${
            completed
              ? "completed"
              : failed
              ? "failed"
              : "waiting"
          }`}
        >
          <span className="pipeline-icon">
            {completed ? "✓" : failed ? "✕" : "○"}
          </span>

          <span>Completed</span>
        </div>

      </div>

      {iterations > 0 && (
        <p className="iteration-info">
          Debugging iterations: {iterations}
        </p>
      )}
    </section>
  );
}

export default Pipeline;