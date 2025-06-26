# Resolve Issue Agent

An intelligent agent built with Google ADK that automates the process of resolving GitHub issues by analyzing the issue, implementing code fixes, and creating pull requests.

## Overview

This agent performs the following workflow:
1. **Fetch Issue Details** - Retrieves GitHub issue information using GitHub CLI
2. **Analyze the Issue** - Explores the repository to identify files and changes needed
3. **Implement the Fix** - Makes necessary code changes based on the analysis
4. **Create Pull Request** - Creates a new branch, commits changes, and opens a PR

## Features

- Automated GitHub issue resolution
- Repository analysis and code change identification
- Intelligent code modification using bash tools
- Automated pull request creation
- Comprehensive error handling and validation
- JSON-formatted responses with detailed status information

## Requirements

- Python 3.11+
- GitHub CLI (`gh`) installed and authenticated
- Git repository access
- Required API keys (see Environment Variables)

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   or
   ```bash
   pip install google-adk>=1.0.0 litellm>=1.68.0
   ```

3. Set up environment variables (see Environment Variables section)
4. Authenticate with GitHub CLI:
   ```bash
   gh auth login
   ```

## Usage

Run the agent with a GitHub issue URL:

```bash
python agent/main.py --issue-url https://github.com/owner/repo/issues/123
```

### Command Line Options

- `--issue-url` (required): GitHub issue URL to resolve
- `--user-id` (optional): User ID for session (default: "user123")
- `--app-name` (optional): Application name (default: "resolve_issue_app")

### Example

```bash
python agent/main.py --issue-url https://github.com/myorg/myproject/issues/42
```

## Environment Variables

Create a `.env` file in the project root (use `.env.example` as template):

```bash
# GitHub CLI Authentication (usually handled by gh auth login)
# GITHUB_TOKEN=your_github_personal_access_token

# Required: Gemini API key for LLM functionality
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Additional LLM API keys as fallbacks
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Response Format

The agent returns a JSON response with the following structure:

```json
{
  "success": true,
  "error": null,
  "issue_details": {
    "title": "Issue title",
    "description": "Issue description"
  },
  "analysis": "Analysis of required changes in XML format",
  "implementation_summary": "Summary of changes made",
  "pull_request": {
    "url": "PR URL",
    "branch": "branch name",
    "commit_message": "commit message"
  }
}
```

In case of errors:
```json
{
  "success": false,
  "error": "Error message",
  "issue_details": null,
  "analysis": null,
  "implementation_summary": null,
  "pull_request": null
}
```

## Agent Behavior

The agent uses a multi-step workflow implemented with Google ADK:

1. **Input Validation**: Validates the GitHub issue URL format
2. **Issue Fetching**: Uses GitHub CLI to retrieve issue details
3. **Code Analysis**: Explores repository structure and identifies modification targets
4. **Implementation**: Makes precise code changes using bash tools
5. **PR Creation**: Creates branch, commits changes, and opens pull request

## Error Handling

The agent handles various error scenarios:
- Invalid or missing issue URL
- GitHub API access issues
- Repository access problems
- Code analysis failures
- Implementation errors
- Pull request creation failures

## Limitations

- Only modifies source code files (not test files)
- Uses bash tools for file operations (no piping/chaining)
- Requires GitHub CLI authentication
- Depends on LLM API availability

## Dependencies

- **google-adk**: Google Agent Development Kit for multi-agent workflows
- **litellm**: LLM integration library for model access
- **GitHub CLI**: Command-line interface for GitHub operations
- **Git**: Version control system for repository management