function RequirementInput({
  requirement,
  setRequirement,
  onStart,
  loading
}) {
  return (
    <section className="card">
      <h2>Project Requirement</h2>

      <textarea
        value={requirement}
        onChange={(event) => setRequirement(event.target.value)}
        placeholder="Describe the software you want the AI team to build..."
        rows="6"
        disabled={loading}
      />

      <button
        onClick={onStart}
        disabled={loading || !requirement.trim()}
      >
        {loading ? "AI Team Working..." : "Start Project"}
      </button>
    </section>
  );
}

export default RequirementInput;