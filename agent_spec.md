## Overview
Build an agent (the 'resolve issue' agent) that automates resolving a GitHub issue by analyzing the issue, identifying required code changes, implementing the fix, and creating a pull request.

**Note:** Bash tools and grep tools are already provided and available for use. You must use these tools to run git commands, make code changes, explore the repository, and perform all required shell operations. Use only these provided tools for all codebase and git operations (e.g., `gh`, `git`, `ls`, `find`, `grep`, `sed`, `cat`, `wc`, `cp`, `mv`, `rm`, `mkdir`, `touch`).

## Agent Structure Requirements
- Implement a single custom agent class (subclass of BaseAgent) that orchestrates the entire workflow.
- Inside this agent, each major step must be implemented as a separate LlmAgent instance:
  - Fetch issue details: LlmAgent with output_key="issue_details"
  - Analyze the issue: LlmAgent with output_key="analysis"
  - Implement the fix: LlmAgent (performs changes, no output_key required)
  - Create the pull request: LlmAgent with output_key="pr_output"
- The workflow agent should run each LlmAgent in sequence, passing data via session state (using output_key for each step).
- The main agent should yield events from each sub-agent and handle errors as in the attached implementation (e.g., check for required state after each step, yield error events if missing).
- Place all agent logic and workflow orchestration in `agent.py`.
- `main.py` should only contain a minimal entrypoint to run the agent (argument parsing, session initialization, running the agent). Do NOT put agent logic in main.py.

## User Workflow

### Input Requirements
The user provides:
- **Issue URL**: A link to the GitHub issue to be resolved.

### Output Requirements
Return a JSON response containing:
- **Issue Details** - The title and description of the issue.
- **Analysis** - Files and code sections identified for modification, with a description of required changes.
- **Implementation Summary** - Actions taken to resolve the issue.
- **Pull Request Info** - PR URL, branch name, and commit message.
- **Success** - Boolean indicating if the process completed successfully.
- **Error** - Error message if any step fails.

## Features

### Step 1: Fetch Issue Details
- Retrieve the issue's title and description using the GitHub CLI (via the provided bash tools).
- Implement this as a dedicated LlmAgent instance with output_key="issue_details".

### Step 2: Analyze the Issue
- Explore the repository structure using the provided tools.
- Identify relevant files and code sections for modification.
- Output findings in a structured format:

  `<analysis>
    <file>path/to/file.py</file>
    <changes_needed>Description of changes</changes_needed>
  </analysis>`
- Implement this as a dedicated LlmAgent instance with output_key="analysis".

### Step 3: Implement the Fix
- Edit source code files as per the analysis using only the provided bash and grep tools.
- **Do not** modify test files.
- Use only allowed bash commands (no piping, chaining, or redirection).
- Verify changes and handle edge cases.
- Implement this as a dedicated LlmAgent instance (no output_key required).

### Step 4: Create a Pull Request
- Create a new branch with a descriptive name using the provided tools.
- Stage, commit, and push changes.
- Open a PR using the GitHub CLI.
- Summarize actions taken.
- Implement this as a dedicated LlmAgent instance with output_key="pr_output".

## Error Handling
- The agent must validate the presence and format of the issue URL before proceeding. If the issue URL is missing or invalid, return a JSON response with `success: false` and `error: "No issue_url provided"` or `error: "Invalid issue_url format"`.
- If fetching issue details fails, return `success: false` and `error: "No issue_details found"`.
- If analysis fails, return `success: false` and `error: "No analysis found"`.
- If implementation fails, return `success: false` and `error: "Implementation failed"`.
- If PR creation fails, return `success: false` and `error: "PR creation failed"`.
- For any other error, return a clear, specific error message in the `error` field and set `success: false`.
- In all error cases, fields that are not available due to the error (e.g., `analysis`, `implementation_summary`, `pull_request`) should be null or omitted.

## Response Format
- Apply to `agent.py`

## Agent Behavior
- Accept requests with an issue URL.
- Validate input before proceeding.
- Return structured JSON responses.
- Include helpful error messages for invalid or failed steps.
- Use only the provided bash and grep tools for all codebase operations.

## Environment Variables
- Requires access to GitHub CLI and repository.
- No external API keys required beyond GitHub authentication.

## Dependencies
- **Python** (for agent logic)
- **Bash tools**: `gh`, `git`, `ls`, `find`, `grep`, `sed`, `cat`, `wc`, `cp`, `mv`, `rm`, `mkdir`, `touch`
- **JSON** for response formatting
