#!/usr/bin/env python3
"""
Command Line Interface for Noctis predefined agents.

This CLI provides easy access to all specialized agents for common developer tasks.
"""

import argparse
import sys
from typing import Optional
from .predefined_agents import (
    get_available_agents, create_agent, list_agent_types,
    CodeReviewAgent, DebuggingAgent, DocumentationAgent, SecurityAgent,
    PerformanceAgent, TestingAgent, ArchitectureAgent, DevOpsAgent,
    CodeGenerationAgent, RefactoringAgent
)

def list_agents():
    """List all available agent types with descriptions."""
    print("Available Noctis Agents:")
    print("=" * 50)
    
    agent_descriptions = {
        "code_reviewer": "Review code for quality, bugs, and best practices",
        "debugger": "Help debug code issues and problems",
        "documentation_writer": "Write and improve technical documentation",
        "security_auditor": "Audit code for security vulnerabilities",
        "performance_optimizer": "Analyze and optimize code performance",
        "testing_specialist": "Create testing strategies and tests",
        "architect": "Design software architecture and systems",
        "devops_engineer": "Help with DevOps practices and CI/CD",
        "code_generator": "Generate code from specifications",
        "refactoring_specialist": "Refactor and improve existing code"
    }
    
    for agent_type in list_agent_types():
        description = agent_descriptions.get(agent_type, "No description available")
        print(f"  {agent_type:<20} - {description}")
    
    print("\nUsage: noctis <agent_type> [options]")

def interactive_mode(agent_type: str, model: str = "gpt-4o-mini"):
    """Run the agent in interactive mode."""
    try:
        agent = create_agent(agent_type, model)
        print(f"\n{agent_type.replace('_', ' ').title()} Agent initialized!")
        print("Type 'quit' or 'exit' to end the session.")
        print("Type 'help' for usage tips.")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                elif user_input.lower() in ['help', 'h']:
                    print("\nUsage Tips:")
                    print("- Ask specific questions about your code or development tasks")
                    print("- Provide code snippets for review or analysis")
                    print("- Describe problems you're trying to solve")
                    print("- Ask for best practices and recommendations")
                    print("- Type 'quit' to exit")
                elif user_input:
                    print(f"\n{agent_type.replace('_', ' ').title()}:")
                    response = agent.ask(user_input)
                    print(response)
                else:
                    continue
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        print(f"Error creating agent: {e}")
        sys.exit(1)

def single_query(agent_type: str, query: str, model: str = "gpt-4o-mini"):
    """Run a single query with the specified agent."""
    try:
        agent = create_agent(agent_type, model)
        print(f"Querying {agent_type.replace('_', ' ').title()} Agent...")
        print("-" * 50)
        response = agent.ask(query)
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Noctis - AI Agents for Developers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  noctis list                                    # List all available agents
  noctis code_reviewer                          # Start code review agent interactively
  noctis debugger -q "Help me fix this bug"     # Single query to debugger agent
  noctis security_auditor -m gpt-4              # Use specific model
  noctis performance_optimizer -i                # Interactive mode with performance agent
        """
    )
    
    parser.add_argument(
        "agent_type",
        nargs="?",
        help="Type of agent to use"
    )
    
    parser.add_argument(
        "-q", "--query",
        help="Single query to send to the agent (non-interactive mode)"
    )
    
    parser.add_argument(
        "-m", "--model",
        default="gpt-4o-mini",
        help="AI model to use (default: gpt-4o-mini)"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Force interactive mode even with query"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available agent types"
    )
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.list or not args.agent_type:
        list_agents()
        return
    
    # Validate agent type
    available_agents = list_agent_types()
    if args.agent_type not in available_agents:
        print(f"Error: Unknown agent type '{args.agent_type}'")
        print(f"Available types: {', '.join(available_agents)}")
        sys.exit(1)
    
    # Determine mode
    if args.query and not args.interactive:
        # Single query mode
        single_query(args.agent_type, args.query, args.model)
    else:
        # Interactive mode
        interactive_mode(args.agent_type, args.model)

if __name__ == "__main__":
    main()
