import json
import random

# Function to generate an example entry
def generate_example(entry_id):
    """
    Generate Sample Json Data in format required after processing

    Args:
        entry_id (_type_): _description_

    Returns:
        JSon entry
    """
    return {
        entry_id: {
            'query_count': random.randint(1, 10),
            'total_execution_time': random.uniform(1000, 10000),
            'scanned': random.uniform(0, 500),
            'spilled': random.uniform(0, 100),
            'avg_spill': random.uniform(0, 10),
            'query_type_counts': {
                'insert': random.randint(0, 5),
                'select': random.randint(0, 5),
                'update': random.randint(0, 5),
            },
            'total_joins': random.randint(0, 5),
            'total_aggregations': random.randint(0, 10),
            'unique_tables': list({str(random.randint(1, 10)) for _ in range(random.randint(1, 5))}),
            'cluster_metrics': {
                str(i): {
                    'query_count': random.randint(1, 3),
                    'total_duration': random.uniform(10, 5000),
                } for i in range(random.randint(1, 5))
            },
            'aborted_queries': random.randint(0, 3),
            'avg_execution_time': random.uniform(500, 3000),
            'queue_time_percentage': random.uniform(0, 1),
            'compile_overhead_ratio': random.uniform(0.5, 1.5),
            'read_write_ratio': random.uniform(0.5, 2),
            'abort_rate': random.uniform(0, 0.1),
        }
    }

# Generate 100 examples
examples = {}
for i in range(100):
    examples.update(generate_example(i))

# Save the examples to a JSON file
output_file = "example_data.json"
with open(output_file, "w") as file:
    json.dump(examples, file, indent=4)

print(f"JSON file with 100 examples has been created at: {output_file}")
