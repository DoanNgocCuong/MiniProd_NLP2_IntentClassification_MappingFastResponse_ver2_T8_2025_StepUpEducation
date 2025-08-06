
31/07/2025

Dạ vâng ạ, em cảm ơn mn. 

1. Số lượng turn để em thử 2-3 turns => để gen data. Khả năng cao kết quả sẽ tốt hơn. 

Còn lúc apply chạy thì khả năng cao sẽ giới hạn tối đa 2 turns. Vì nhiều turns hơn khả năng cao sẽ làm tăng time của response 

2. Về model thì hiện em đang nhận phần từ a Hoài. 
(là từ 1-2-3 turns của Bot + AI => ra được LLMs Fast Response luôn, thay cho việc: Detect Intent rồi mapping hiện tại). 
(phần này em trả lời cho câu hỏi của a Trúc bên trên luôn ạ :D )

3. ...
4. là gen fast response trực tiếp luôn a Trúc ạ. 

---
Anh @Cuong Vu Cao , anh @Truc Le Van , chị @Trang Nguyen Thu



01/08/2025

Em summary lại xíu: 

Chị Trang comment: 
Option 1 (hiện tại): câu fast_response đang có cảm thán trong đó. 
=> Em đem đi fine tune trước, ngon, thì sẽ chỉnh sửa main_answer để bỏ đi câu cảm thán.
Option 2 fast_response trung tính hơn. 
+, Nếu nhanh: tuning prompt để có fast_response trung tính hơn. 
+, Nếu lâu quá, thì trong thời gian finetune Option 1: chỉnh prompt để fast_response trung tính hơn. 

Anh Cường comment: 
20% tổng số fast-response là được mention lại ý của users chỉ khi đúng intent (trả lời đúng), ví dụ "tớ thích voi" --> "ồ voi à, tớ cũng rất thích voi" 

---
=> Next steps: 
1. Em đưa ver 1 đi finetune trước (cắm máy) 
2. Trong thời gian đó: tuning thêm ver2 với 2 tiêu chí : TRUNG TÍNH + MENTION LẠI INTENT USER 
- Gửi lại anh chị đánh giá ạ. 

Anh @Cuong Vu Cao , chị @Trang Nguyen Thu