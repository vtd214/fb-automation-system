import time
import random
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# --- 1. CẤU HÌNH ---
EXCEL_FILE = "Ke_hoach_Van_hanh_He_thong_Facebook_114.xlsx"
SHEET_NAME = "4. Danh Sach 50 Group"
DOLPHIN_API_URL = "http://localhost:3001/v1/profiles/"
PROFILE_ID = "ĐIỀN_ID_PROFILE_CỦA_BẠN_VÀO_ĐÂY" 

# --- 2. ĐỌC EXCEL ---
print("📊 Đang đọc danh sách Group từ Excel...")
try:
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    df_target = df.head(3) # Chạy thử nghiệm trước với 3 dòng đầu tiên
except Exception as e:
    print(f"❌ Không đọc được file Excel. Kiểm tra lại tên file/sheet! Lỗi: {e}")
    exit()

# --- 3. MỞ TRÌNH DUYỆT QUA API ---
print(f"🌐 Đang kết nối tới Profile ID: {PROFILE_ID}...")
start_url = f"{DOLPHIN_API_URL}{PROFILE_ID}/start"
try:
    response = requests.get(start_url).json()
except:
    print("❌ Lỗi: Bạn chưa bật phần mềm Dolphin{anty} hoặc chưa kích hoạt API!")
    exit()

if response.get("status") == "success":
    chrome_driver_port = response["automation"]["port"]
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_driver_port}")
    driver = webdriver.Chrome(options=options)
    print("🚀 Kết nối trình duyệt thành công! Bắt đầu chạy...")

    # --- 4. CHẠY CUỐN CHIẾU ---
    for index, row in df_target.iterrows():
        group_url = row['Đường Dẫn (Link Group)']
        comment_text = "Bài viết hay quá, cảm ơn thớt đã chia sẻ kiến thức bổ ích này!" 
        
        print(f"\n➔ Đang vào nhóm: {group_url}")
        driver.get(group_url)
        time.sleep(random.randint(5, 8)) # Đợi tải trang
        
        try:
            # Tìm ô bình luận (XPATH thông minh tự động nhận diện tiếng Anh/Việt)
            comment_box = driver.find_element(By.XPATH, "//*[@role='textbox' and (contains(@aria-label, 'bình luận') or contains(@aria-label, 'comment'))]")
            comment_box.click()
            time.sleep(1)
            
            print("⌨️ Robot đang giả lập gõ từng phím...")
            for char in comment_text:
                comment_box.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15)) # Tốc độ gõ ngẫu nhiên
            
            time.sleep(1)
            comment_box.send_keys(Keys.ENTER)
            print("✅ Đã bình luận thành công!")
            
            wait_time = random.randint(15, 30) # Thời gian nghỉ để test (khi chạy thật đổi thành 240-300)
            print(f"⏳ Nghỉ {wait_time} giây trước khi chuyển nhóm...")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"❌ Bỏ qua nhóm này (Không tìm thấy ô cmt hoặc cần duyệt bài).")
            continue

    print("\n🏁 Hoàn thành ca làm việc!")
    requests.get(f"{DOLPHIN_API_URL}{PROFILE_ID}/stop")
    print("🔒 Đã đóng trình duyệt an toàn.")
else:
    print("❌ Không mở được Profile. Kiểm tra lại PROFILE_ID!")