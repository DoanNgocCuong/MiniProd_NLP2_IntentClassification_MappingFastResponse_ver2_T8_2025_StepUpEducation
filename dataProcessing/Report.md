Em đang có 1 số options sau: 
1. Option 1: Mang 3 turns (1 turn = 1 câu robot + 1 câu user) + response gồm user_intent + fast_response đem đi finetune 
2. Option 2:  Mang 3 turns (1 turn = 1 câu robot + 1 câu user) + response gồm mỗi fast_response đem đi fine tune 

---
lúc mang test thì có 3 options: 
- Dùng 1 turn, Dùng 2 turns, Dùng 3 turns
Bài Fast Response em hiện có 2 options như này. Em có tham vấn qua anh Hoài, ---
+, Opt1: Gần như là COT, chất lượng trả ra ngon hơn. Nhưng về sau dùng -> nó ra JSON + dài => response time cao hơn. +, Opt2: Ra Text + Ngắn hơn => Nhanh hơn. 
---
Em thử option 1 trước anh nhen (ạ). 