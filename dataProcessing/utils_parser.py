import pandas as pd
import json
import re

# Read the CSV file
df = pd.read_csv('output_ver4.csv')

print("=== ORIGINAL DATA STRUCTURE ===")
print(f"Columns: {list(df.columns)}")
print(f"Shape: {df.shape}")
print(f"First few rows:")
print(df.head(3))

def extract_json_from_completion(completion_result):
    """Extract JSON data from completion result string"""
    try:
        if pd.isna(completion_result):
            return {}
        
        # The completion result is a JSON string containing an "output" field
        # which itself contains a JSON string
        completion_data = json.loads(completion_result)
        
        # Extract the output field which contains the actual JSON we want
        output_json_str = completion_data.get('output', '{}')
        
        # Clean up markdown code blocks (``` and ```json)
        output_json_str = clean_markdown_json(output_json_str)
        
        # Parse the inner JSON string
        output_data = json.loads(output_json_str)
        
        # Return all keys and values as dictionary
        return output_data
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error parsing JSON: {e}")
        print(f"Problematic data: {completion_result[:200]}...")
        return {}

def clean_markdown_json(json_str):
    """Remove markdown code block markers from JSON string"""
    if not isinstance(json_str, str):
        return json_str
    
    # Strip whitespace
    json_str = json_str.strip()
    
    # Remove ```json at the beginning
    if json_str.startswith('```json'):
        json_str = json_str[7:]  # Remove '```json'
    
    # Remove ``` at the beginning (for cases with just ```)
    elif json_str.startswith('```'):
        json_str = json_str[3:]  # Remove '```'
    
    # Remove ``` at the end
    if json_str.endswith('```'):
        json_str = json_str[:-3]  # Remove ending '```'
    
    # Strip whitespace again after removal
    json_str = json_str.strip()
    
    return json_str

# Process all rows and collect all possible keys
results = []
all_extracted_keys = set()
print("\n=== PROCESSING COMPLETION RESULTS ===")

for idx, row in df.iterrows():
    # Get the completion result
    completion_result = row.get('Completion result', '')
    
    # Extract all fields dynamically
    extracted_data = extract_json_from_completion(completion_result)
    
    # Track all keys found
    all_extracted_keys.update(extracted_data.keys())
    
    # Create new row with all original data plus extracted fields
    new_row = {}
    
    # Copy all original columns
    for col in df.columns:
        new_row[col] = row[col]
    
    # Add all extracted columns
    for key, value in extracted_data.items():
        new_row[key] = value
    
    results.append(new_row)
    
    if idx % 10 == 0:
        print(f"Processed {idx+1}/{len(df)} rows...")

print(f"Found keys in completion results: {sorted(all_extracted_keys)}")

# Create new DataFrame
output_df = pd.DataFrame(results)

print(f"\n=== PROCESSING COMPLETE ===")
print(f"Original columns: {list(df.columns)}")
print(f"New columns: {list(output_df.columns)}")
print(f"Total rows processed: {len(output_df)}")

# Show sample of extracted data
print(f"\n=== SAMPLE EXTRACTED DATA ===")
extracted_columns = sorted(list(all_extracted_keys))
sample_df = output_df[extracted_columns].head(5)
for idx, row in sample_df.iterrows():
    print(f"\nRow {idx+1}:")
    for col in extracted_columns:
        value = str(row[col]) if pd.notna(row[col]) else ""
        if len(value) > 100:
            value = value[:100] + "..."
        print(f"  {col}: {value}")

# Save to new Excel file
output_df.to_excel('parsed_result.xlsx', index=False)
print(f"\n=== OUTPUT SAVED ===")
print("File saved as: parsed_result.xlsx")

# Also save just the extracted columns
if extracted_columns:
    extracted_only_df = output_df[extracted_columns]
    extracted_only_df.to_excel('extracted_columns_only.xlsx', index=False)
    print("Extracted columns only saved as: extracted_columns_only.xlsx")

# Statistics
print(f"\n=== STATISTICS ===")
print(f"Total rows: {len(output_df)}")

# Count successful extractions (rows that have any extracted data)
successful_extractions = 0
for idx, row in output_df.iterrows():
    has_data = any(pd.notna(row.get(col)) and str(row.get(col)).strip() != "" for col in extracted_columns)
    if has_data:
        successful_extractions += 1

print(f"Successful extractions: {successful_extractions}")
print(f"Failed extractions: {len(output_df) - successful_extractions}")

# Show statistics for each extracted column
for col in extracted_columns:
    if col in output_df.columns:
        non_empty = output_df[col].notna().sum()
        print(f"\n{col}:")
        print(f"  Non-empty values: {non_empty}/{len(output_df)}")
        
        if col == 'user_intent' and non_empty > 0:
            intent_counts = output_df[col].value_counts()
            print(f"  Distribution:")
            for intent, count in intent_counts.items():
                print(f"    {intent}: {count}")
        
        if col == 'fast_response' and non_empty > 0:
            lengths = output_df[col].apply(lambda x: len(str(x).split()) if pd.notna(x) else 0)
            print(f"  Length stats (words):")
            print(f"    Average: {lengths.mean():.1f}")
            print(f"    Min: {lengths.min()}")
            print(f"    Max: {lengths.max()}")