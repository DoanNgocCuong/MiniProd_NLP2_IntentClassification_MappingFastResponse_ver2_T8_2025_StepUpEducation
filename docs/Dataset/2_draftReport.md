
Report ngắn: 

## 1. Vấn đề + Objective, Outcome, Metrics + Key Results Output
- **Outcome**: Fast Response mang lại wow cho người dùng.
- **Metrics**:
    - Response time < 200ms
    - Accuracy > 95%
    - User satisfaction score: đạt 9/10

Output: 
- Ver 1: Chốt được output Data mang đi fine tune 
- Ver 2: Chiều thứ 6 - deploy ver 1.2 

## 2. Cách trêển khai: 

- Step 1: Lấy lesson id chỗ chị Trang, => lấy conversation chỗ a Quân (dựa vào lesson id)
=> Chạy Prompt => gen Fast Response Data. 

- Step 2: Chạy finetune demo: Done. 
+, Card 3090, số 0 đang trống, số 1 đang 12%, số 2 đang 64% 
+, Model: 4B (đã tham vấn a Hoài)
> Còn sau muốn làm nâng cao hơn kiểu gen text nó có kịch bản, với cá tính rõ ràng thì 8b. Mỗi 1 tính cách lad 1 lora adpter
> Nếu fast response mà đơn giản thì em cũng xem hạ huống 1b xong tune cũng đc. Nhưng 1b hơi hên xui
> Nếu tune xong text nó mang ý ok r mà muốn nó tuân theo 1 quy chuẩn thì tune thêm với grpo nhé
- Một số thông số: 
+, Số lượng data: 3K dòng data. Format ... 
+, Text dài quá thì batch size. = 1
+, Format đem finetune: 
```bash
[
  {
    "previous_conversation": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "How do I reset my password?"}
    ],
    "assistant_fast_response": "Let me check that for you right away!"
  },
  {
    "previous_conversation": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What's the weather like today?"}
    ],
    "assistant_fast_response": "Just a moment while I get the latest update!"
  },
  ...
]
```

- Step 3: Tuning Prompt 
- Step 4: Gen Data 
- Step 5: Cắm vào chạy. 

## 3. Đánh giá lúc sau: 
- Đánh giá Response sau demo 
- Đánh giá Response sau fine tune. 

## Risk: ??? 
- Khó nhất đoạn: gen Data make sense để mang đi fine tune. 


====


1. 