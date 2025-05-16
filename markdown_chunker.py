import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib
from pathlib import Path

@dataclass
class MarkdownChunk:
    """Represents a chunk of markdown content with metadata."""
    content: str
    title: str
    level: int  # Heading level (0 for no heading)
    chunk_id: str
    parent_id: Optional[str]
    metadata: Dict[str, str]
    code_blocks: List[Dict[str, str]]  # List of code blocks with language and content
    links: List[Dict[str, str]]  # List of links with text and URL
    tables: List[str]  # List of table contents

class MarkdownChunker:
    """Advanced chunking strategy for markdown files."""
    
    def __init__(self, 
                 min_chunk_size: int = 100,
                 max_chunk_size: int = 1000,
                 overlap_size: int = 50,
                 preserve_code_blocks: bool = True,
                 preserve_tables: bool = True):
        """
        Initialize the markdown chunker.
        
        Args:
            min_chunk_size: Minimum size of a chunk in characters
            max_chunk_size: Maximum size of a chunk in characters
            overlap_size: Number of characters to overlap between chunks
            preserve_code_blocks: Whether to keep code blocks intact
            preserve_tables: Whether to keep tables intact
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.preserve_code_blocks = preserve_code_blocks
        self.preserve_tables = preserve_tables
        
        # Regular expressions for markdown elements
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.code_block_pattern = re.compile(r'```(\w*)\n(.*?)\n```', re.DOTALL)
        self.table_pattern = re.compile(r'\|.*\|[\r\n]+\|[-:]+\|[\r\n]+(\|.*\|[\r\n]+)+')
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from markdown content."""
        metadata = {}
        
        # Extract title from first heading
        first_heading = self.heading_pattern.search(content)
        if first_heading:
            metadata['title'] = first_heading.group(2).strip()
        
        # Extract code blocks
        code_blocks = []
        for match in self.code_block_pattern.finditer(content):
            code_blocks.append({
                'language': match.group(1),
                'content': match.group(2)
            })
        metadata['code_blocks'] = code_blocks
        
        # Extract links
        links = []
        for match in self.link_pattern.finditer(content):
            links.append({
                'text': match.group(1),
                'url': match.group(2)
            })
        metadata['links'] = links
        
        return metadata
    
    def _get_heading_level(self, line: str) -> int:
        """Get the heading level of a line (0 if not a heading)."""
        match = self.heading_pattern.match(line)
        if match:
            return len(match.group(1))
        return 0
    
    def _generate_chunk_id(self, content: str, parent_id: Optional[str] = None) -> str:
        """Generate a unique ID for a chunk."""
        base = f"{content[:50]}{parent_id if parent_id else ''}"
        return hashlib.sha256(base.encode()).hexdigest()[:12]
    
    def _split_at_heading(self, content: str) -> List[Tuple[str, int, str]]:
        """Split content at headings, preserving the heading level and title."""
        chunks = []
        current_chunk = []
        current_level = 0
        current_title = "Introduction"
        
        for line in content.split('\n'):
            heading_level = self._get_heading_level(line)
            
            if heading_level > 0:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append(('\n'.join(current_chunk), current_level, current_title))
                    current_chunk = []
                
                current_level = heading_level
                current_title = line.lstrip('#').strip()
                current_chunk.append(line)
            else:
                current_chunk.append(line)
        
        # Add the last chunk
        if current_chunk:
            chunks.append(('\n'.join(current_chunk), current_level, current_title))
        
        return chunks
    
    def _preserve_special_blocks(self, content: str) -> str:
        """Preserve code blocks and tables by replacing them with placeholders."""
        if self.preserve_code_blocks:
            content = self.code_block_pattern.sub(lambda m: f"CODE_BLOCK_{hash(m.group(0))}", content)
        
        if self.preserve_tables:
            content = self.table_pattern.sub(lambda m: f"TABLE_{hash(m.group(0))}", content)
        
        return content
    
    def _restore_special_blocks(self, content: str, block_map: Dict[str, str]) -> str:
        """Restore code blocks and tables from placeholders."""
        for placeholder, original in block_map.items():
            content = content.replace(placeholder, original)
        return content
    
    def chunk_markdown(self, content: str, file_path: Optional[str] = None) -> List[MarkdownChunk]:
        """
        Chunk markdown content into semantic pieces.
        
        Args:
            content: The markdown content to chunk
            file_path: Optional file path for generating unique IDs
            
        Returns:
            List of MarkdownChunk objects
        """
        # Create block map for preserving special blocks
        block_map = {}
        
        # Preserve special blocks
        content = self._preserve_special_blocks(content)
        
        # Split content at headings
        heading_chunks = self._split_at_heading(content)
        
        chunks = []
        parent_ids = {}  # Map of heading levels to parent IDs
        
        for chunk_content, level, title in heading_chunks:
            # Generate chunk ID
            chunk_id = self._generate_chunk_id(chunk_content)
            
            # Find parent ID
            parent_id = None
            if level > 1:
                for l in range(level - 1, 0, -1):
                    if l in parent_ids:
                        parent_id = parent_ids[l]
                        break
            
            # Update parent IDs
            parent_ids[level] = chunk_id
            
            # Extract metadata
            metadata = self._extract_metadata(chunk_content)
            
            # Create chunk
            chunk = MarkdownChunk(
                content=chunk_content,
                title=title,
                level=level,
                chunk_id=chunk_id,
                parent_id=parent_id,
                metadata=metadata,
                code_blocks=metadata.get('code_blocks', []),
                links=metadata.get('links', []),
                tables=[]  # TODO: Implement table extraction
            )
            
            chunks.append(chunk)
        
        return chunks
    
    def chunk_file(self, file_path: str) -> List[MarkdownChunk]:
        """Chunk a markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.chunk_markdown(content, file_path)

def main():
    """Example usage of the markdown chunker."""
    chunker = MarkdownChunker()
    
    # Example markdown content
    markdown = """# Main Title
    
## Section 1
This is the first section with some content.

```python
def hello():
    print("Hello, world!")
```

## Section 2
This is the second section with a [link](https://example.com).

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
"""
    
    # Chunk the markdown
    chunks = chunker.chunk_markdown(markdown)
    
    # Print chunk information
    for chunk in chunks:
        print(f"\nChunk ID: {chunk.chunk_id}")
        print(f"Title: {chunk.title}")
        print(f"Level: {chunk.level}")
        print(f"Parent ID: {chunk.parent_id}")
        print(f"Content: {chunk.content[:100]}...")
        print(f"Code Blocks: {len(chunk.code_blocks)}")
        print(f"Links: {len(chunk.links)}")

if __name__ == "__main__":
    main() 