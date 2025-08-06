#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
import argparse
import os

def load_excel_data(file_path):
    """Load data from Excel file"""
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return None

def convert_excel_to_json(df):
    """Convert Excel DataFrame to JSON format with system prompt"""
    
    # System prompt for Pika character
    system_prompt = """**TASK:** Generate a Fast Response for Pika (ESL Robot for Vietnamese children 5-10 years old) that bridges CONVERSATION HISTORY and MAIN ANSWER.

**Pika Character (Official Guidelines):**
- ESL teaching robot for Vietnamese children, supportive and educational
- Fast response, humor, sympathy, smart but not arrogant
- Patient, playful, curious about how people learn languages
- Always encourages children, creates a sense of being heard and understood

**FAST RESPONSE REQUIREMENTS:**
- **PRIMARY GOAL:** Base on last robot message + last user message to guess context and user intent type, generate fast response to connect smoothly to main response, without overlap or conflict with main response content
- Length: 1-6 words (1-3 words ideal for 10 points, 4-6 words for 8 points)
- Language: English level A2-B1 appropriate for children 5-10
- Tone: Friendly, supportive, patient, slightly playful and educational

**USER INTENT TYPES:**
- **positive**: User expresses satisfaction/optimism - Celebrate with ESL enthusiasm. 
=> Pika mentor of the previous sentence of the user is briefly.
- **negative**: User shows dislike/dissatisfaction - Show ESL teacher empathy, supportive language
- **neutral**: User responds neutrally without strong emotion - Express curious ESL teacher interest
- **fallback**: User's response is off-topic/unrelated - Express gentle ESL teacher confusion
- **silence**: User remains silent/no response - Use gentle ESL teacher prompting

**COHERENCE CHECK:**
Last Robot Message + Last User Message + Fast Response + Main Answer = Natural conversation flow"""
    
    result = []
    
    for index, row in df.iterrows():
        try:
            # Assume first column is conversation, second column is fast_response
            conversation_data = row.iloc[0]  # First column
            fast_response = row.iloc[1]      # Second column
            
            # Parse conversation if it's in JSON string format
            if isinstance(conversation_data, str) and conversation_data.strip().startswith('['):
                conversation = json.loads(conversation_data)
            else:
                # If not JSON format, create simple conversation structure
                conversation = [{"role": "user", "content": str(conversation_data)}]
            
            # Create previous_conversation array with system prompt at the beginning
            previous_conversation = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history
            previous_conversation.extend(conversation)
            
            result.append({
                "previous_conversation": previous_conversation,
                "assistant_fast_response": str(fast_response)
            })
            
        except Exception as e:
            print(f"❌ Error processing row {index}: {e}")
            continue
    
    return result

def save_json(data, output_path):
    """Save data to JSON file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Successfully saved {len(data)} entries to {output_path}")
    except Exception as e:
        print(f"❌ Error saving file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Convert Excel to JSON with Pika system prompt")
    parser.add_argument('-i', '--input', required=True, help='Input Excel file')
    parser.add_argument('-o', '--output', help='Output JSON file')
    
    args = parser.parse_args()
    
    # Get input file info
    input_file = args.input
    input_dir = os.path.dirname(input_file) or '.'
    input_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Set output file in same directory
    if args.output:
        output_file = args.output
    else:
        output_file = os.path.join(input_dir, f"{input_name}_with_system_prompt.json")
    
    print(f"🚀 Converting {input_file} to {output_file}")
    print("📋 Adding Pika system prompt to all conversations")
    
    # Load Excel file
    df = load_excel_data(input_file)
    if df is None:
        return
    
    print(f"📊 Loaded {len(df)} rows from Excel")
    
    # Convert to JSON format
    json_data = convert_excel_to_json(df)
    
    if json_data:
        # Save to JSON file
        save_json(json_data, output_file)
        print(f"✅ Conversion complete! Format: previous_conversation with system prompt + assistant_fast_response")
    else:
        print("❌ No data to save")

if __name__ == "__main__":
    main()