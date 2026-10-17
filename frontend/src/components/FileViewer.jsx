import { useState } from "react";

function FileViewer({ files }) {
  const [selectedFile, setSelectedFile] = useState(null);

  if (!files || files.length === 0) {
    return (
      <section className="card">
        <h2>Generated Files</h2>

        <p className="muted">
          Generated files will appear here.
        </p>
      </section>
    );
  }

  const activeFile =
    selectedFile || files[0].filename;

  const file =
    files.find(
      (item) => item.filename === activeFile
    ) || files[0];

  return (
    <section className="card">
      <h2>Generated Files</h2>

      <div className="file-viewer">

        <div className="file-list">
          {files.map((item) => (
            <button
              key={item.filename}
              className={
                item.filename === activeFile
                  ? "file-button selected"
                  : "file-button"
              }
              onClick={() =>
                setSelectedFile(item.filename)
              }
            >
              {item.filename}
            </button>
          ))}
        </div>

        <div className="code-panel">
          <div className="code-header">
            {file.filename}
          </div>

          <pre>
            {file.content}
          </pre>
        </div>

      </div>
    </section>
  );
}

export default FileViewer;