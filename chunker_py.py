import pandas as pd
import tiktoken
from typing import List, Dict

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
    
    def process_csv(self, input_file: str, content_column: str = 'file_content') -> pd.DataFrame:
        """
        Process a CSV file and split its contents into chunks while preserving all original columns.
        
        Args:
            input_file (str): Path to the input CSV file
            content_column (str): Name of the column containing the content to process (default: 'file_content')
        
        Returns:
            pd.DataFrame: DataFrame containing all original columns plus chunked content
        """
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        # Add token count column
        df['token_count'] = df[content_column].apply(self.count_tokens)
        
        # Create a list to store all chunks with their original row data
        all_chunks = []
        
        # Process each row
        for idx, row in df.iterrows():
            content = row[content_column]
            chunks = self.split_into_chunks(content)
            
            # Add chunks to results while preserving all original columns
            for chunk_idx, chunk in enumerate(chunks, 1):  # Start from 1 instead of 0
                # Create a copy of the original row
                chunk_row = row.to_dict()
                
                # Update the content column with the chunk
                chunk_row[content_column] = chunk
                
                # Add chunk-specific information with formatted chunk index
                chunk_row['chunk_index'] = f"chunk_{chunk_idx}"
                chunk_row['chunk_token_count'] = self.count_tokens(chunk)
                
                all_chunks.append(chunk_row)
        
        # Convert chunks to DataFrame
        chunks_df = pd.DataFrame(all_chunks)
        
        # Print statistics
        print(f"\nProcessing Statistics:")
        print(f"Total rows processed: {len(df)}")
        print(f"Total chunks created: {len(chunks_df)}")
        print(f"Total tokens: {df['token_count'].sum()}")
        print(f"Average chunk size: {chunks_df['chunk_token_count'].mean():.2f} tokens")
        
        return chunks_df

def main():
    # Example usage
    chunker = TokenChunker(target_chunk_size=1000, overlap=250)
    
    # Process your CSV file
    chunks_df = chunker.process_csv(
        input_file="your_input.csv",
        content_column="file_content"  # Default column name
    )
    
    # You can now work with the chunks DataFrame
    print("\nFirst few chunks:")
    print(chunks_df.head())
    
    # Save the results if needed
    chunks_df.to_csv("chunked_output.csv", index=False)

if __name__ == "__main__":
    main() 
