function Header() {
  return (
    <header className="header">
      <div>
        <h1>AI Software Engineering Team</h1>
        <p>
          Local multi-agent AI system for automated software development
        </p>
      </div>

      <div className="backend-status">
        <span className="status-dot"></span>
        Local AI
      </div>
    </header>
  );
}

export default Header;