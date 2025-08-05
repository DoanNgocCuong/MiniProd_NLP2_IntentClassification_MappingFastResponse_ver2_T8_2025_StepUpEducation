#!/usr/bin/env python3
"""
Parser script to extract JSON data from assistant_response column in Excel file.
"""

import pandas as pd
import json
import re
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_paths():
    """Setup file paths using pathlib."""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    
    input_file = project_root / "dataProcessing" / "3_callOpenAIgenFastResponseDataTool" / "output_data_v2.xlsx"
    output_file = current_dir / "parsed_output_data.xlsx"
    
    return input_file, output_file

def clean_json_string(json_str):
    """
    Clean the JSON string by removing markdown code block markers.
    
    Args:
        json_str (str): Raw string containing JSON wrapped in markdown
        
    Returns:
        str: Cleaned JSON string
    """
    if pd.isna(json_str) or not isinstance(json_str, str):
        return None
    
    # Remove markdown code block markers
    cleaned = re.sub(r'^```.*?\n', '', json_str.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r'\n```$', '', cleaned.strip(), flags=re.MULTILINE)
    
    return cleaned.strip()

def parse_assistant_response(response_str):
    """
    Parse the assistant_response JSON string and extract fields.
    
    Args:
        response_str (str): JSON string from assistant_response column
        
    Returns:
        dict: Dictionary with extracted fields or None values if parsing fails
    """
    default_result = {
        'last_robot_answer': None,
        'last_user_answer': None,
        'user_intent': None,
        'fast_response': None,
        'main_answer': None
    }
    
    try:
        # Clean the JSON string
        cleaned_json = clean_json_string(response_str)
        if not cleaned_json:
            return default_result
        
        # Parse JSON
        data = json.loads(cleaned_json)
        
        # Extract fields with fallback to None
        result = {
            'last_robot_answer': data.get('last_robot_answer'),
            'last_user_answer': data.get('last_user_answer'),
            'user_intent': data.get('user_intent'),
            'fast_response': data.get('fast_response'),
            'main_answer': data.get('main_answer')
        }
        
        return result
        
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}")
        logger.debug(f"Problematic JSON string: {cleaned_json}")
        return default_result
    except Exception as e:
        logger.warning(f"Unexpected error parsing JSON: {e}")
        return default_result

def process_excel_file(input_file, output_file):
    """
    Process the Excel file and parse assistant_response column.
    
    Args:
        input_file (Path): Path to input Excel file
        output_file (Path): Path to output Excel file
    """
    try:
        logger.info(f"Reading Excel file: {input_file}")
        
        # Read the first sheet of the Excel file
        df = pd.read_excel(input_file, sheet_name=0)
        
        logger.info(f"Loaded data with shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Check if assistant_response column exists
        if 'assistant_response' not in df.columns:
            logger.error("Column 'assistant_response' not found in the Excel file!")
            logger.info(f"Available columns: {list(df.columns)}")
            return
        
        logger.info(f"Found {len(df)} rows with assistant_response data")
        
        # Parse each assistant_response entry
        parsed_data = []
        for idx, response in enumerate(df['assistant_response']):
            if idx % 100 == 0:
                logger.info(f"Processing row {idx + 1}/{len(df)}")
            
            parsed = parse_assistant_response(response)
            parsed_data.append(parsed)
        
        # Create new columns from parsed data
        for key in ['last_robot_answer', 'last_user_answer', 'user_intent', 'fast_response', 'main_answer']:
            df[key] = [item[key] for item in parsed_data]
        
        # Save to new Excel file
        logger.info(f"Saving parsed data to: {output_file}")
        df.to_excel(output_file, index=False)
        
        # Print summary statistics
        logger.info("Parsing summary:")
        for col in ['last_robot_answer', 'last_user_answer', 'user_intent', 'fast_response', 'main_answer']:
            non_null_count = df[col].notna().sum()
            logger.info(f"  {col}: {non_null_count}/{len(df)} non-null values")
        
        # Show sample of user_intent values
        intent_counts = df['user_intent'].value_counts()
        logger.info(f"User intent distribution: {dict(intent_counts)}")
        
        logger.info("Processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {e}")
        raise

def main():
    """Main function to run the parser."""
    try:
        # Setup paths
        input_file, output_file = setup_paths()
        
        # Check if input file exists
        if not input_file.exists():
            logger.error(f"Input file not found: {input_file}")
            return
        
        logger.info(f"Input file: {input_file}")
        logger.info(f"Output file: {output_file}")
        
        # Process the file
        process_excel_file(input_file, output_file)
        
    except Exception as e:
        logger.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()
