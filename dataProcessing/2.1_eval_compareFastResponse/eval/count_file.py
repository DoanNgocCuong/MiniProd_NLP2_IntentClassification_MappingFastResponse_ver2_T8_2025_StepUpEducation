import os
import glob

def count_xlsx_files():
    """Đếm số file .xlsx trong folder hiện tại"""
    
    # Lấy đường dẫn folder hiện tại (nơi chứa file .py này)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Tìm tất cả file .xlsx trong folder hiện tại
    xlsx_pattern = os.path.join(current_dir, "*.xlsx")
    xlsx_files = glob.glob(xlsx_pattern)
    
    # Đếm số lượng
    count = len(xlsx_files)
    
    print(f"=== THỐNG KÊ FILE XLSX ===")
    print(f"Folder hiện tại: {current_dir}")
    print(f"Số file .xlsx: {count}")
    
    if count > 0:
        print(f"\nDanh sách file .xlsx:")
        for i, file_path in enumerate(xlsx_files, 1):
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            print(f"  {i}. {file_name} ({file_size:,} bytes)")
    else:
        print("Không tìm thấy file .xlsx nào!")
    
    return count, xlsx_files

if __name__ == "__main__":
    # Chạy function đếm file
    total_files, file_list = count_xlsx_files()
    
    print(f"\n=== KẾT QUẢ ===")
    print(f"Tổng cộng: {total_files} file .xlsx")

