import tiktoken
from typing import List, Tuple
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def get_initial_chunk_prompt(full_content: str) -> str:
    """Generate a prompt for creating the initial chunk."""
    prompt = f"""You are a content chunking assistant. Your task is to create the first chunk of content from the provided text.
Full content to process:
{full_content}

Please create the first chunk that:
1. Is a complete, coherent section
2. Stays within 3500 tokens
3. Ends at a natural breaking point (end of section, paragraph, etc.)
4. Captures the beginning of the document appropriately

Return ONLY the chunk content without any additional explanation or formatting."""

    return prompt

def get_next_chunk_prompt(full_content: str, previous_chunks: List[str]) -> str:
    """Generate a prompt for creating the next chunk."""
    context = "\n".join(previous_chunks)
    
    prompt = f"""You are a content chunking assistant. Your task is to create the next chunk of content.
Previous chunks for context:
{context}

Full content to process:
{full_content}

Please create the next chunk that:
1. Is a complete, coherent section
2. Stays within 3500 tokens
3. Maintains context from previous chunks
4. Ends at a natural breaking point (end of section, paragraph, etc.)
5. Does not overlap with previous chunks
6. Continues from where the last chunk ended
7. repeating the headers wherever required to maintain the context of the new chunk

Return ONLY the chunk content without any additional explanation or formatting."""

    return prompt

def create_initial_chunk(full_content: str, max_tokens: int = 3500) -> str:
    """Create the initial chunk from the full content."""
    prompt = get_initial_chunk_prompt(full_content)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a content chunking assistant that helps break down large documents into smaller, coherent parts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=max_tokens
    )
    
    initial_chunk = response.choices[0].message.content.strip()
    
    # Verify token count
    chunk_tokens = count_tokens(initial_chunk)
    if chunk_tokens > max_tokens:
        print(f"Warning: Initial chunk exceeds token limit ({chunk_tokens} tokens)")
    
    print(f"Created initial chunk with {chunk_tokens} tokens")
    return initial_chunk

def create_next_chunk(full_content: str, previous_chunks: List[str], max_tokens: int = 3500) -> str:
    """Create the next chunk using full content and previous chunks."""
    prompt = get_next_chunk_prompt(full_content, previous_chunks)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a content chunking assistant that helps break down large documents into smaller, coherent parts."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=max_tokens
    )
    
    next_chunk = response.choices[0].message.content.strip()
    
    # Verify token count
    chunk_tokens = count_tokens(next_chunk)
    if chunk_tokens > max_tokens:
        print(f"Warning: Chunk exceeds token limit ({chunk_tokens} tokens)")
    
    print(f"Created chunk {len(previous_chunks) + 1} with {chunk_tokens} tokens")
    return next_chunk

def chunk_markdown_file(file_path: str, max_tokens: int = 3500) -> List[str]:
    """
    Chunk a markdown file into smaller parts using GPT-4.
    
    Args:
        file_path: Path to the markdown file
        max_tokens: Maximum tokens per chunk
        
    Returns:
        List of chunks
    """
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        full_content = file.read()
    
    chunks = []
    
    # Create initial chunk
    initial_chunk = create_initial_chunk(full_content, max_tokens)
    chunks.append(initial_chunk)
    
    # Create subsequent chunks
    while True:
        next_chunk = create_next_chunk(full_content, chunks, max_tokens)
        
        # Check if we've reached the end of the content
        if not next_chunk or next_chunk in chunks:
            break
            
        chunks.append(next_chunk)
        
        # Optional: Add a maximum chunk limit to prevent infinite loops
        if len(chunks) >= 100:  # Arbitrary limit
            print("Warning: Reached maximum chunk limit")
            break
    
    return chunks

def save_chunks(chunks: List[str], output_dir: str, base_filename: str):
    """Save chunks to separate files."""
    os.makedirs(output_dir, exist_ok=True)
    
    for i, chunk in enumerate(chunks, 1):
        output_path = os.path.join(output_dir, f"{base_filename}_chunk_{i}.md")
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(chunk)
        print(f"Saved chunk {i} to {output_path}")

def main():
    # Example usage
    input_file = "input.md"  # Replace with your input file path
    output_dir = "chunks"    # Directory to save chunks
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    print(f"Processing file: {input_file}")
    chunks = chunk_markdown_file(input_file)
    
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    save_chunks(chunks, output_dir, base_filename)
    print(f"Successfully created {len(chunks)} chunks")

if __name__ == "__main__":
    main() 
