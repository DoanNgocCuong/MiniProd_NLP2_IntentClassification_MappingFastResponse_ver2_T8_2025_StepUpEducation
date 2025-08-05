python -m venv myvenv
.\myvenv\Scripts\activate

python PromptTuning_OpenAI_v5_BatchSize_NumWorkers.py --input-file fastResponse_v3_demo.xlsx --num-rows 15 --sheet demo_IDs


python PromptTuning_OpenAI_v5_BatchSize_NumWorkers.py --input-file 1.2_fastResponse_v3_1Turns_v4_3Turns_demo20250804.xlsx --num-rows 3 --sheet 120ConversationID_7000Data

nohup python PromptTuning_OpenAI_v5_BatchSize_NumWorkers.py --input-file 1.2_fastResponse_v3_1Turns_v4_3Turns_demo20250804.xlsx --sheet 120ConversationID_7000Data > nohup.out 2>&1 &