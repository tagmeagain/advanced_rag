from token_chunker import TokenChunker

# Create a chunker instance
chunker = TokenChunker(target_chunk_size=1000, overlap=250)

# Process your CSV file
chunks_df = chunker.process_csv(
    input_file="your_input.csv",
    content_column="file_content"
)

# The chunks_df DataFrame contains:
# - row_index: original row index from input CSV
# - chunk_index: index of the chunk within that row
# - content: the actual chunk content
# - token_count: number of tokens in the chunk

# You can work with the DataFrame directly
print(chunks_df.head())
print(f"Total chunks: {len(chunks_df)}")
print(f"Average tokens per chunk: {chunks_df['token_count'].mean():.2f}")
