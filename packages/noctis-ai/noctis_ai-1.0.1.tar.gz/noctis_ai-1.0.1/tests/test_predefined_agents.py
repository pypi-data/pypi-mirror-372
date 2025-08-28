# test_agents_simple.py
from noctis import CodeReviewAgent, DebuggingAgent, SecurityAgent

def test_code_reviewer():
    print("=== Testing Code Review Agent ===")
    # You can specify the LLM here:
    # agent = CodeReviewAgent("gpt-4o")  # Use GPT-4
    # agent = CodeReviewAgent("gpt-3.5-turbo")  # Use GPT-3.5
    # agent = CodeReviewAgent("claude-3-sonnet-20240229")  # Use Claude
    # agent = CodeReviewAgent("gpt-4o-mini")  # Default, lightweight option
    
    # Ollama models (local inference):
    agent = CodeReviewAgent("gemma3:270m")  # Fast, good for code review
    # agent = CodeReviewAgent("llama2:13b")  # Better quality, slower
    # agent = CodeReviewAgent("codellama:7b")  # Specialized for code
    # agent = CodeReviewAgent("mistral:7b")  # Good balance
    
    code = """
def bad_function(x):
    return x + "hello"  # Potential type error
"""
    
    response = agent.ask(f"Review this code: {code}")
    print(f"Response: {response[:200]}...")
    print()

def test_debugger():
    print("=== Testing Debugging Agent ===")
    # You can specify the LLM here:
    # agent = DebuggingAgent("gpt-4o")  # Use GPT-4 for better reasoning
    # agent = DebuggingAgent("gpt-3.5-turbo")  # Use GPT-3.5 for faster response
    # agent = DebuggingAgent("gpt-4o-mini")  # Default, balanced option
    
    # Ollama models (local inference):
    agent = DebuggingAgent("gemma3:270m")  # Good for debugging
    # agent = DebuggingAgent("llama2:13b")  # Better reasoning
    # agent = DebuggingAgent("codellama:7b")  # Code-specialized
    # agent = DebuggingAgent("mistral:7b")  # Fast and capable
    
    error = "I'm getting 'TypeError: can only concatenate str (not \"int\") to str'"
    response = agent.ask(f"Help me debug this error: {error}")
    print(f"Response: {response[:200]}...")
    print()

def test_security_auditor():
    print("=== Testing Security Agent ===")
    # You can specify the LLM here:
    # agent = SecurityAgent("gpt-4o")  # Use GPT-4 for best security analysis
    # agent = SecurityAgent("claude-3-sonnet-20240229")  # Use Claude for security
    # agent = SecurityAgent("gpt-4o-mini")  # Default option
    
    # Ollama models (local inference):
    agent = SecurityAgent("gemma3:270m")  # Good for security analysis
    # agent = SecurityAgent("llama2:13b")  # Better security reasoning
    # agent = SecurityAgent("codellama:7b")  # Code-specialized security
    # agent = SecurityAgent("mistral:7b")  # Fast security analysis
    
    code = """
@app.route('/user/<id>')
def get_user(id):
    query = f"SELECT * FROM users WHERE id = {id}"
    return execute_query(query)
"""
    
    response = agent.ask(f"Audit this code for security issues: {code}")
    print(f"Response: {response[:200]}...")
    print()

if __name__ == "__main__":
    test_code_reviewer()
    test_debugger()
    test_security_auditor()
    test_security_auditor()