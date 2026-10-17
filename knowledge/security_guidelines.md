# Security Guidelines

## Secrets

Never hardcode passwords, API keys, tokens, or credentials.

Store sensitive configuration outside source code.

## Input Validation

Validate all user-controlled input.

Do not assume that incoming data is safe.

## File Access

Restrict file operations to approved directories.

Prevent path traversal attacks.

Never allow an AI agent to access arbitrary files on the computer.

## Code Execution

Do not execute untrusted code without appropriate isolation.

Avoid shell commands when a safer programmatic alternative exists.

## AI Agents

Agents should have access only to the tools required for their task.

Tool permissions should be explicitly restricted.