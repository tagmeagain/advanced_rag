from markdown_chunker import MarkdownChunker
import json
from pathlib import Path

def print_chunk_details(chunk):
    """Print detailed information about a chunk."""
    print("\n" + "="*80)
    print(f"Title: {chunk.title}")
    print(f"Level: {chunk.level}")
    print(f"Chunk ID: {chunk.chunk_id}")
    print(f"Parent ID: {chunk.parent_id}")
    print("\nContent Preview:")
    print("-"*40)
    print(chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content)
    print("\nMetadata:")
    print("-"*40)
    print(f"Code Blocks: {len(chunk.code_blocks)}")
    for i, code_block in enumerate(chunk.code_blocks, 1):
        print(f"\nCode Block {i}:")
        print(f"Language: {code_block['language']}")
        print(f"Content Preview: {code_block['content'][:100]}...")
    
    print(f"\nLinks: {len(chunk.links)}")
    for i, link in enumerate(chunk.links, 1):
        print(f"\nLink {i}:")
        print(f"Text: {link['text']}")
        print(f"URL: {link['url']}")

def main():
    # Create the sample_docs directory if it doesn't exist
    Path("sample_docs").mkdir(exist_ok=True)
    
    # Initialize the chunker
    chunker = MarkdownChunker(
        min_chunk_size=100,
        max_chunk_size=1000,
        overlap_size=50,
        preserve_code_blocks=True,
        preserve_tables=True
    )
    
    # Path to the sample markdown file
    markdown_file = "sample_docs/test_markdown.md"
    
    print(f"Processing markdown file: {markdown_file}")
    print("="*80)
    
    # Chunk the markdown file
    chunks = chunker.chunk_file(markdown_file)
    
    # Print summary
    print(f"\nTotal chunks created: {len(chunks)}")
    print("\nChunk Hierarchy:")
    print("-"*40)
    
    # Create a simple hierarchy visualization
    for chunk in chunks:
        indent = "  " * (chunk.level - 1)
        print(f"{indent}├─ {chunk.title} (Level {chunk.level})")
    
    # Print detailed information for each chunk
    print("\nDetailed Chunk Information:")
    for chunk in chunks:
        print_chunk_details(chunk)
    
    # Save chunks to JSON for inspection
    chunks_data = [
        {
            "title": chunk.title,
            "level": chunk.level,
            "chunk_id": chunk.chunk_id,
            "parent_id": chunk.parent_id,
            "content": chunk.content,
            "code_blocks": chunk.code_blocks,
            "links": chunk.links
        }
        for chunk in chunks
    ]
    
    with open("sample_docs/chunks_output.json", "w") as f:
        json.dump(chunks_data, f, indent=2)
    
    print("\nChunks have been saved to sample_docs/chunks_output.json")

if __name__ == "__main__":
    main() 