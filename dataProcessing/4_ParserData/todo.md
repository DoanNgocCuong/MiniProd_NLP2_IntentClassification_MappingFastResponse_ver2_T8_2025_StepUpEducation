# Parser Data Tasks

## Objective
Parse the assistant_response column from Excel file and extract JSON data into separate columns.

## Tasks
1. ✅ Create todo.md file
2. ✅ Read Excel file: `dataProcessing/3_callOpenAIgenFastResponseDataTool/output_data_v2.xlsx`
3. ✅ Find and read the first sheet
4. ✅ Locate the `assistant_response` column
5. ✅ Parse JSON content from the column (remove markdown code blocks)
6. ✅ Extract the following fields into separate columns:
   - `last_robot_answer`
   - `last_user_answer`
   - `user_intent`
   - `fast_response`
   - `main_answer`
7. ✅ Save the parsed data to a new Excel file
8. ✅ Handle error cases (invalid JSON, missing fields)
9. [ ] Test the script by running it

## Notes
- Use pathlib for file path handling
- The assistant_response column contains JSON wrapped in markdown code blocks
- Need to strip the ```json and ``` markers before parsing
- Handle potential JSON parsing errors gracefully