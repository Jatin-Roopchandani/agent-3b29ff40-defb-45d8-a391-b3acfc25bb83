import json
import os
from typing import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from tools.bash_tool import get_bash_tool
from tools.grep_tool import GrepTools


class ResolveIssueAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="resolve_issue_agent",
            description="Agent that automates resolving GitHub issues by analyzing, implementing fixes, and creating pull requests",
        )
        
        # Initialize tools
        self.bash_tools = get_bash_tool(
            allowed_commands=[
                "gh", "git", "ls", "find", "grep", "sed", "cat", 
                "wc", "cp", "mv", "rm", "mkdir", "touch"
            ],
            truncate_length=5000
        )
        self.grep_tools = GrepTools()

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        try:
            # Get user input from session state
            user_input = ctx.session.state.get("user_input", "")
            issue_url = ctx.session.state.get("issue_url", "")
            
            # Validate input
            if not issue_url:
                error_response = {
                    "success": False,
                    "error": "No issue_url provided",
                    "issue_details": None,
                    "analysis": None,
                    "implementation_summary": None,
                    "pull_request": None
                }
                yield Event(content={"role": "assistant", "parts": [{"text": json.dumps(error_response)}]})
                return

            # Validate issue URL format
            if not (issue_url.startswith("https://github.com/") and "/issues/" in issue_url):
                error_response = {
                    "success": False,
                    "error": "Invalid issue_url format",
                    "issue_details": None,
                    "analysis": None,
                    "implementation_summary": None,
                    "pull_request": None
                }
                yield Event(content={"role": "assistant", "parts": [{"text": json.dumps(error_response)}]})
                return

            # Step 1: Fetch Issue Details
            fetch_agent = LlmAgent(
                name="fetch_issue",
                model="gemini-2.0-flash",
                instruction=f"""
                Fetch the GitHub issue details from {issue_url} using the GitHub CLI.
                Use the gh command to get the issue details including title and description.
                Return the issue details in JSON format with 'title' and 'description' fields.
                If fetching fails, return an error message.
                """,
                tools=self.bash_tools,
                output_key="issue_details"
            )
            
            async for event in fetch_agent.run_async(ctx):
                yield event

            # Check if issue details were fetched
            if not ctx.session.state.get("issue_details"):
                error_response = {
                    "success": False,
                    "error": "No issue_details found",
                    "issue_details": None,
                    "analysis": None,
                    "implementation_summary": None,
                    "pull_request": None
                }
                yield Event(content={"role": "assistant", "parts": [{"text": json.dumps(error_response)}]})
                return

            # Step 2: Analyze the Issue
            analyze_agent = LlmAgent(
                name="analyze_issue",
                model="gemini-2.0-flash",
                instruction="""
                Analyze the GitHub issue to identify what needs to be fixed.
                
                1. Read the issue details from state['issue_details']
                2. Explore the repository structure to understand the codebase
                3. Identify relevant files and code sections that need modification
                4. Output your analysis in this exact XML format:
                
                <analysis>
                    <file>path/to/file.py</file>
                    <changes_needed>Description of changes needed in this file</changes_needed>
                </analysis>
                
                If multiple files need changes, use multiple <analysis> blocks.
                Focus on the actual source code files, not test files.
                """,
                tools=self.bash_tools + self.grep_tools.get_tools(),
                output_key="analysis"
            )
            
            async for event in analyze_agent.run_async(ctx):
                yield event

            # Check if analysis was completed
            if not ctx.session.state.get("analysis"):
                error_response = {
                    "success": False,
                    "error": "No analysis found", 
                    "issue_details": ctx.session.state.get("issue_details"),
                    "analysis": None,
                    "implementation_summary": None,
                    "pull_request": None
                }
                yield Event(content={"role": "assistant", "parts": [{"text": json.dumps(error_response)}]})
                return

            # Step 3: Implement the Fix
            implement_agent = LlmAgent(
                name="implement_fix",
                model="gemini-2.0-flash", 
                instruction="""
                Implement the code changes based on the analysis from state['analysis'].
                
                1. Read the analysis results to understand what changes are needed
                2. Make the necessary code changes to the identified files
                3. Use only the provided bash tools for file modifications
                4. Do NOT modify test files
                5. Verify your changes are correct
                6. Summarize what you implemented
                
                Use commands like sed, grep, cat to make precise code changes.
                Avoid piping, chaining, or redirection in bash commands.
                """,
                tools=self.bash_tools + self.grep_tools.get_tools()
            )
            
            async for event in implement_agent.run_async(ctx):
                yield event

            # Step 4: Create Pull Request
            pr_agent = LlmAgent(
                name="create_pr",
                model="gemini-2.0-flash",
                instruction="""
                Create a pull request for the implemented changes.
                
                1. Create a new branch with a descriptive name based on the issue
                2. Stage and commit the changes with a clear commit message
                3. Push the branch to the remote repository
                4. Create a pull request using the GitHub CLI
                5. Return the PR details including URL, branch name, and commit message
                
                Use git commands to manage the branch and GitHub CLI (gh) to create the PR.
                Make sure to provide a clear PR title and description.
                """,
                tools=self.bash_tools,
                output_key="pr_output"
            )
            
            async for event in pr_agent.run_async(ctx):
                yield event

            # Check if PR was created
            if not ctx.session.state.get("pr_output"):
                error_response = {
                    "success": False,
                    "error": "PR creation failed",
                    "issue_details": ctx.session.state.get("issue_details"),
                    "analysis": ctx.session.state.get("analysis"), 
                    "implementation_summary": "Changes were implemented but PR creation failed",
                    "pull_request": None
                }
                yield Event(content={"role": "assistant", "parts": [{"text": json.dumps(error_response)}]})
                return

            # Success response
            success_response = {
                "success": True,
                "error": None,
                "issue_details": ctx.session.state.get("issue_details"),
                "analysis": ctx.session.state.get("analysis"),
                "implementation_summary": "Successfully implemented code changes based on issue analysis",
                "pull_request": ctx.session.state.get("pr_output")
            }
            
            yield Event(content={"role": "assistant", "parts": [{"text": json.dumps(success_response)}]})

        except Exception as e:
            error_response = {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "issue_details": ctx.session.state.get("issue_details"),
                "analysis": ctx.session.state.get("analysis"),
                "implementation_summary": ctx.session.state.get("implementation_summary"),
                "pull_request": ctx.session.state.get("pr_output")
            }
            yield Event(content={"role": "assistant", "parts": [{"text": json.dumps(error_response)}]})