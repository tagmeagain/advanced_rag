import os
from openai import OpenAI
import sys

def stream_gpt4_response(prompt, api_key):
    """
    Stream a response from GPT-4.
    
    Args:
        prompt (str): The prompt to send to GPT-4
        api_key (str): Your OpenAI API key
    """
    # Initialize the OpenAI client
    client = OpenAI(api_key=api_key)
    
    try:
        # Create a streaming completion
        stream = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            stream=True  # Enable streaming
        )
        
        # Process the stream
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                # Print the content without a newline and flush the output
                print(chunk.choices[0].delta.content, end="", flush=True)
        
        # Print a newline at the end
        print()
        
    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)

def main():
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    
    # Example prompt
    prompt = "Write a short story about a robot learning to paint."
    
    print("Streaming GPT-4 response...")
    stream_gpt4_response(prompt, api_key)

if __name__ == "__main__":
    main() 
