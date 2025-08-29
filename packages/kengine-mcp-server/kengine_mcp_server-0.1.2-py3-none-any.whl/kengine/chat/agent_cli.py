"""
Agent Chat CLI

A simple command-line interface to test the agent-based chat service.
"""

import argparse
import json
import sys
from typing import Optional

from .agent_chat_service import AgentChatService
from .models import ChatRequest, MessageRole
from .conversion import ConversationManager


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="Agent Chat CLI")
    parser.add_argument("--repo", required=True, help="Repository name (format: group/repo)")
    parser.add_argument("--message", required=True, help="User message")
    parser.add_argument("--conversation-id", help="Existing conversation ID")
    parser.add_argument("--context-limit", type=int, default=10, help="Context limit")
    parser.add_argument("--show-tools", action="store_true", help="Show available tools")
    
    args = parser.parse_args()
    
    # Initialize services
    conversation_manager = ConversationManager()
    agent_service = AgentChatService(conversation_manager)
    
    # Create chat request
    request = ChatRequest(
        message=args.message,
        conversation_id=args.conversation_id,
        repo_name=args.repo,
        enable_agent_mode=True,
        context_limit=args.context_limit
    )
    
    # Show available tools if requested
    if args.show_tools:
        if args.conversation_id:
            tools = agent_service.get_available_tools(args.conversation_id)
            print("Available tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        else:
            print("No conversation ID provided, tools will be available after first message")
    
    # Stream chat response
    print(f"User: {args.message}")
    print("Assistant: ", end="", flush=True)
    
    conversation_id = None
    full_response = ""
    
    try:
        for chunk in agent_service.stream_chat(request):
            if chunk.type == "content":
                print(chunk.data, end="", flush=True)
                full_response += chunk.data
            elif chunk.type == "error":
                print(f"\nError: {chunk.data}")
                sys.exit(1)
            elif chunk.type == "end":
                conversation_id = chunk.metadata.get("conversation_id")
                print(f"\n\nConversation ID: {conversation_id}")
                print(f"Sources: {chunk.metadata.get('num_sources', 0)}")
                break
            elif chunk.type == "metadata":
                try:
                    metadata = json.loads(chunk.data)
                    if "tools_used" in metadata:
                        print(f"\n\nTools used: {', '.join(metadata['tools_used'])}")
                except json.JSONDecodeError:
                    pass
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
