import requests
from noctis.models.ollama_adapter import OllamaAdapter

if __name__ == "__main__":
    try:
        # Initialize the adapter. You can set a default model here if you want.
        # For example: adapter = OllamaAdapter(model="llama2")
        adapter = OllamaAdapter()

        # Call the chat method, specifying the model to use for this call.
        # Make sure the model 'gemma3:270m' is available in your Ollama instance.
        print("Sending request to Ollama with model 'deepseek-r1:8b'...")
        reply = adapter.chat(
            messages=[{"role": "user", "content": "IM A DEVelopper and im tired so much and i wanna enjoy and find a work im an ai enginner"}],
            model="deepseek-r1:8b"
        )

        # The 'reply' variable already contains the content of the response.
        print("\nAgent's reply:")
        print(reply)

    except requests.exceptions.RequestException as e:
        print(f"\nError: Could not connect to Ollama.")
        print(f"Details: {e}")
        print("Please ensure the Ollama server is running and accessible.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")