import pandas as pd
import tiktoken
from typing import List, Dict
import json

class TokenChunker:
    def __init__(self, target_chunk_size: int = 1000, overlap: int = 250):
        """
        Initialize the TokenChunker with target chunk size and overlap.
        
        Args:
            target_chunk_size (int): Target number of tokens per chunk (default: 1000)
            overlap (int): Number of tokens to overlap between chunks (default: 250)
        """
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap
        self.encoding = tiktoken.encoding_for_model("gpt-4")  # Using GPT-4 tokenizer
    
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a text using GPT-4 tokenizer.
        
        Args:
            text (str): The text to count tokens for
        
        Returns:
            int: Number of tokens
        """
        return len(self.encoding.encode(text))
    
    def split_into_chunks(self, text: str) -> List[str]:
        """
        Split text into chunks with specified size and overlap.
        
        Args:
            text (str): The text to split into chunks
        
        Returns:
            List[str]: List of chunks
        """
        # Encode the text into tokens
        tokens = self.encoding.encode(text)
        chunks = []
        
        # Calculate number of chunks needed
        total_tokens = len(tokens)
        tokens_per_chunk = self.target_chunk_size - self.overlap
        
        # Split into chunks
        start_idx = 0
        while start_idx < total_tokens:
            # Calculate end index for this chunk
            end_idx = min(start_idx + self.target_chunk_size, total_tokens)
            
            # Decode tokens back to text
            chunk_text = self.encoding.decode(tokens[start_idx:end_idx])
            chunks.append(chunk_text)
            
            # Move start index forward, accounting for overlap
            start_idx = end_idx - self.overlap if end_idx < total_tokens else end_idx
        
        return chunks
    
    def process_csv(self, input_file: str, content_column: str = 'file_content', output_file: str = None) -> Dict:
        """
        Process a CSV file and split its contents into chunks.
        
        Args:
            input_file (str): Path to the input CSV file
            content_column (str): Name of the column containing the content to process (default: 'file_content')
            output_file (str, optional): Path to save the output JSON file
        
        Returns:
            Dict: Dictionary containing chunk information
        """
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        # Add token count column
        df['token_count'] = df[content_column].apply(self.count_tokens)
        
        # Initialize results dictionary
        results = {
            "chunks": [],
            "statistics": {
                "total_rows": len(df),
                "total_chunks": 0,
                "average_chunk_size": 0,
                "total_tokens": df['token_count'].sum()
            }
        }
        
        # Process each row
        for idx, row in df.iterrows():
            content = row[content_column]
            chunks = self.split_into_chunks(content)
            
            # Add chunks to results
            for chunk_idx, chunk in enumerate(chunks):
                chunk_info = {
                    "row_index": idx,
                    "chunk_index": chunk_idx,
                    "content": chunk,
                    "token_count": self.count_tokens(chunk)
                }
                results["chunks"].append(chunk_info)
        
        # Update statistics
        results["statistics"]["total_chunks"] = len(results["chunks"])
        if results["chunks"]:
            avg_tokens = sum(chunk["token_count"] for chunk in results["chunks"]) / len(results["chunks"])
            results["statistics"]["average_chunk_size"] = round(avg_tokens, 2)
        
        # Save to file if output_file is provided
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results

def main():
    # Example usage
    chunker = TokenChunker(target_chunk_size=1000, overlap=250)
    
    # Process your CSV file
    results = chunker.process_csv(
        input_file="your_input.csv",
        content_column="file_content",  # Default column name
        output_file="chunks_output.json"
    )
    
    # Print statistics
    stats = results["statistics"]
    print(f"\nProcessing Statistics:")
    print(f"Total rows processed: {stats['total_rows']}")
    print(f"Total chunks created: {stats['total_chunks']}")
    print(f"Total tokens: {stats['total_tokens']}")
    print(f"Average chunk size: {stats['average_chunk_size']} tokens")

if __name__ == "__main__":
    main() 
