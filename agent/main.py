import argparse
import asyncio
import json
import os
from pathlib import Path

from google.adk.runners import InMemoryRunner
from agent import ResolveIssueAgent


async def main():
    parser = argparse.ArgumentParser(description="Resolve GitHub Issue Agent")
    parser.add_argument("--issue-url", required=True, help="GitHub issue URL to resolve")
    parser.add_argument("--user-id", default="user123", help="User ID for session")
    parser.add_argument("--app-name", default="resolve_issue_app", help="Application name")
    
    args = parser.parse_args()
    
    # Load environment variables from .env file if it exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    
    # Initialize the agent and runner
    agent = ResolveIssueAgent()
    runner = InMemoryRunner(app_name=args.app_name, agent=agent)
    
    # Create session with initial state
    session = await runner.session_service.create_session(
        app_name=args.app_name,
        user_id=args.user_id,
        state={
            "issue_url": args.issue_url,
            "user_input": f"Please resolve the GitHub issue: {args.issue_url}"
        }
    )
    
    # Run the agent
    print(f"Resolving GitHub issue: {args.issue_url}")
    print("Processing...")
    
    async for event in runner.run_async(
        user_id=args.user_id,
        session_id=session.id,
        new_message={
            "role": "user", 
            "parts": [{"text": f"Please resolve the GitHub issue: {args.issue_url}"}]
        }
    ):
        # Print final response
        if hasattr(event, 'content') and event.content:
            if isinstance(event.content, dict) and 'parts' in event.content:
                for part in event.content['parts']:
                    if 'text' in part:
                        try:
                            # Try to parse as JSON for pretty printing
                            response = json.loads(part['text'])
                            print(json.dumps(response, indent=2))
                        except json.JSONDecodeError:
                            # If not JSON, print as-is
                            print(part['text'])


if __name__ == "__main__":
    asyncio.run(main())