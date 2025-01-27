import pandas as pd
import time
import os

def transfer_data():
    input_path = 'data/intermediate/raw_data.csv'
    output_path = 'data/cleaned/cleaned_data.csv'
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    while True:
        try:
            if os.path.exists(input_path):
                # Read the latest data from the intermediate file
                df = pd.read_csv(input_path)
                
                # Handle missing values
                df.fillna(0, inplace=True)

                #numns to the appropriate type
                df['compile_duration_ms'] = pd.to_numeric(df['compile_duration_ms'], errors='coerce').fillna(0).astype(int)
                df['execution_duration_ms'] = pd.to_numeric(df['execution_duration_ms'], errors='coerce').fillna(0).astype(int)

                # Ensure the 'arrival_timestamp' column is correctly handled
                if 'arrival_timestamp' in df.columns:
                    df['arrival_timestamp'] = pd.to_datetime(df['arrival_timestamp'], format='%m/%d/%Y %I:%M %p', errors='coerce')

                # Calculate the percentage of execution time that accounts for compilation
                valid_data = df[(df['compile_duration_ms'] > 0) & (df['execution_duration_ms'] > 0)]
                ratios = valid_data['compile_duration_ms'] / valid_data['execution_duration_ms']
                average_ratio = ratios.mean()

                # Apply this average ratio to estimate compile_duration_ms where it's currently 0
                df.loc[df['compile_duration_ms'] == 0, 'compile_duration_ms'] = (df['execution_duration_ms'] * average_ratio).round().astype(int)

                print(f"Applied estimated compilation times based on {average_ratio:.2%} of execution durations.")

                # Check if the cleaned data file is empty to decide on writing headers
                write_header = not os.path.exists(output_path) or os.stat(output_path).st_size == 0
                df.to_csv(output_path, mode='a', header=write_header, index=False)
            
            time.sleep(10)  # Delay to simulate time between fetches
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    transfer_data()
