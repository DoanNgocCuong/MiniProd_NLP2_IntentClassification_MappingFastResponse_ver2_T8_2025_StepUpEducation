Ah! Tôi thấy vấn đề rồi!

Từ cách bạn viết: `order	user_input 	system_prompt` - tôi thấy có **khoảng trắng** sau `user_input`.

**Vấn đề:** Tên cột trong Excel có thể là `'user_input '` (có space ở cuối) thay vì `'user_input'` (không có space).

**Giải pháp:**

1. **Cách 1:** Sửa tên cột trong Excel - xóa khoảng trắng thừa
2. **Cách 2:** Sửa code để handle khoảng trắng
