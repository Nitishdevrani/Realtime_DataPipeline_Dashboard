import pandas as pd
import time
import os

def load_data():
    # Set the path to the Parquet file
    parquet_file = "C:/Users/adaml/Downloads/sample_serverless.parquet"
    output_file = "data/intermediate/raw_data.csv"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Read the entire Parquet file into a DataFrame
    df = pd.read_parquet(parquet_file)
    
    # Define the chunk size
    chunk_size = 10
    
    # Write data to the CSV file in chunks
    header_written = False
    for i in range(0, len(df), chunk_size):
        # Extract a chunk
        chunk = df.iloc[i:i + chunk_size]
        
        # Append the chunk to the CSV file
        chunk.to_csv(output_file, mode='a', header=not header_written, index=False)
        
        # Set header_written to True after writing the first chunk
        if not header_written:
            header_written = True
        
        # Simulate a delay for streaming data
        time.sleep(1)

if __name__ == "__main__":
    load_data()
