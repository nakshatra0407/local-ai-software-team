import { useState } from "react";

import Header from "./components/Header";
import RequirementInput from "./components/RequirementInput";
import Pipeline from "./components/Pipeline";
import ExecutionStatus from "./components/ExecutionStatus";
import TestResults from "./components/TestResults";
import DebuggingAttempts from "./components/DebuggingAttempts";
import FileViewer from "./components/FileViewer";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [requirement, setRequirement] = useState("");

  const [projectId, setProjectId] = useState(null);

  const [status, setStatus] = useState("created");

  const [testsPassed, setTestsPassed] = useState(null);

  const [iterations, setIterations] = useState(0);

  const [testResult, setTestResult] = useState(null);

  const [files, setFiles] = useState([]);

  const [debuggingAttempts, setDebuggingAttempts] =
    useState([]);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  async function startProject() {
    setError("");
    setLoading(true);

    try {
      /*
       * STEP 1
       * Create project
       */
      const createResponse = await fetch(
        `${API_URL}/projects`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            requirement
          })
        }
      );

      if (!createResponse.ok) {
        const errorData =
          await createResponse.json();

        throw new Error(
          errorData.detail ||
          "Failed to create project."
        );
      }

      const project =
        await createResponse.json();

      setProjectId(project.project_id);
      setStatus("running");

      /*
       * STEP 2
       * Run the complete AI pipeline
       */
      const runResponse = await fetch(
        `${API_URL}/projects/${project.project_id}/run`,
        {
          method: "POST"
        }
      );

      if (!runResponse.ok) {
        const errorData =
          await runResponse.json();

        throw new Error(
          errorData.detail ||
          "Project execution failed."
        );
      }

      const runResult =
        await runResponse.json();

      setStatus(runResult.status);
      setTestsPassed(
        runResult.tests_passed
      );
      setIterations(
        runResult.iterations
      );

      /*
       * STEP 3
       * Get final status
       */
      const statusResponse = await fetch(
        `${API_URL}/projects/${project.project_id}/status`
      );

      if (statusResponse.ok) {
        const statusData =
          await statusResponse.json();

        setDebuggingAttempts(
          statusData.debugging_attempts || []
        );
      }

      /*
       * STEP 4
       * Get test results
       */
      const testResponse = await fetch(
        `${API_URL}/projects/${project.project_id}/tests`
      );

      if (testResponse.ok) {
        const testData =
          await testResponse.json();

        setTestResult(testData);
      }

      /*
       * STEP 5
       * Get generated files
       */
      const filesResponse = await fetch(
        `${API_URL}/projects/${project.project_id}/files`
      );

      if (filesResponse.ok) {
        const filesData =
          await filesResponse.json();

        setFiles(filesData.files || []);
      }

    } catch (requestError) {
      console.error(requestError);

      setError(
        requestError.message ||
        "Something went wrong."
      );

      setStatus("failed");

    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">

      <Header />

      <main className="dashboard">

        <RequirementInput
          requirement={requirement}
          setRequirement={setRequirement}
          onStart={startProject}
          loading={loading}
        />

        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        <Pipeline
          status={status}
          iterations={iterations}
        />

        <ExecutionStatus
          projectId={projectId}
          status={status}
          testsPassed={testsPassed}
          iterations={iterations}
        />

        <TestResults
          testResult={testResult}
        />

        <DebuggingAttempts
          attempts={debuggingAttempts}
        />

        <FileViewer
          files={files}
        />

      </main>

    </div>
  );
}

export default App;