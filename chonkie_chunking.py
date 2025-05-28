import pandas as pd
from chonkie import RecursiveChunker, RecursiveRules, RecursiveLevel

# Define markdown-specific chunking rules
markdown_rules = RecursiveRules(levels=[
    RecursiveLevel(separator="\n## ", prepend_separator=True),
    RecursiveLevel(separator="\n### ", prepend_separator=True),
    RecursiveLevel(separator="\n#### ", prepend_separator=True),
    RecursiveLevel(separator="\n\n", prepend_separator=False),
])

# Recursive chunking function for a single piece of text
def chunk_markdown_text(text, chunk_size=384, min_chars=50):
    chunker = RecursiveChunker(
        rules=markdown_rules,
        chunk_size=chunk_size,
        min_character_per_chunk=min_chars,
        return_type='texts'
    )
    return [chunk.strip() for chunk in chunker(text) if len(chunk.strip()) >= 10]

# Function to apply chunking across DataFrame rows
def chunk_dataframe(df, content_col='file_content'):
    all_chunks = []
    chunk_counter = 1

    for idx, row in df.iterrows():
        text = row[content_col]
        chunks = chunk_markdown_text(text)
        for chunk in chunks:
            chunk_id = f"chunk_{chunk_counter}"
            new_row = row.to_dict()
            new_row['chunk_id'] = chunk_id
            new_row['chunk_text'] = chunk
            all_chunks.append(new_row)
            chunk_counter += 1

    return pd.DataFrame(all_chunks)

# ---------------------------
# 📂 Main Execution
# ---------------------------
# Replace this with your actual file
csv_path = 'your_file.csv'

# Read the CSV
df = pd.read_csv(csv_path)

# Apply chunking
chunked_df = chunk_dataframe(df, content_col='file_content')

# Save or display result
chunked_df.to_csv('chunked_output.csv', index=False)

# Display a preview
import ace_tools as tools; tools.display_dataframe_to_user(name="Chunked Markdown Data", dataframe=chunked_df)
