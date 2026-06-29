import time
import random
import os
import urllib.parse
import pyotp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# ==============================================================================
# --- 1. BẢNG CẤU HÌNH THỜI GIAN & KỊCH BẢN (ĐẠT TỰ CHỈNH THEO Ý MUỐN) ---
# ==============================================================================
# Thời gian chờ tải trang hoàn tất (Giây)
DELAY_LOAD_PAGE = (8, 12)  

# Thời gian robot cuộn chuột lướt đọc bài viết giả lập người thật (Giây)
DELAY_READ_POST = (5, 10)  

# Tốc độ gõ từng ký tự (Giây/phím) -> Càng ngẫu nhiên càng giống người thật
DELAY_TYPING_SPEED = (0.08, 0.25)  

# Thời gian nghỉ giãn cách an toàn giữa các nhóm (Giây)
# CHÚ Ý: Khi chạy thực tế nuôi nick nên để từ (180, 300) giây (tức 3 - 5 phút/nhóm)
DELAY_BETWEEN_GROUPS = (30, 60)  

# Số lượng nhóm tối đa muốn tương tác cho mỗi từ khóa chủ đề
MAX_GROUPS_PER_KEYWORD = 2  

# Danh sách kịch bản câu bình luận (Robot sẽ bốc ngẫu nhiên để tránh trùng lặp)
COMMENT_TEMPLATES = [
    "Bài viết chia sẻ rất chi tiết, cảm ơn thớt nhiều nhé!",
    "Đúng chủ đề mình đang quan tâm luôn, thông tin bổ ích quá ạ.",
    "Nội dung hay quá, chấm một chấm để lưu lại ngâm cứu dần.",
    "Cảm ơn bạn đã tổng hợp kiến thức hữu ích này nha!"
]

# --- THÔNG TIN VIA FACEBOOK ---
FB_UID = "61586925999382"
FB_PASS = "duongadalia040a"
FB_2FA = "ZRQ6PFJXBDI4CDTSYISLNXEFDQCP4AR6"
COOKIE_RAW = "c_user=61586925999382; xs=6%3ATf104H9T3XjFEA%3A2%3A1773153682%3A-1%3A-1; presence=C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1776249113457%2C%22v%22%3A1%7D; wd=1056x600; dpr=0.22140221297740936; sb=ji2waWVJGIBvtahT4n8828b2; pas=61586925999382%3Ae853PxqDRc; wl_cbv=v2%3Bclient_version%3A3108%3Btimestamp%3A1773153713; datr=4QN2aaHrd5un0UCFqQXOB6Kg; m_pixel_ratio=0.47999998927116394; locale=vi_VN; fbl_st=100427394%3BT%3A29552561; fr=0kGsKzrTwQVOLkgpx.AWcL80HsIlLSG-vcfuJcgJJNV8o92p3em5LRomFlCO1OwqxOJRM.BpdgRy..AAA.0.0.Bp32kW.AWcof8RcDwp8Hd8h-RA3mfCnd1U;"

KEYWORDS = [
    "Đồ án chi tiết máy",
    "Học vi điều khiển STM32 PIC",
    "Cộng đồng lập trình C C# Python"
]

# ==============================================================================
# --- 2. KHỞI TẠO TRÌNH DUYỆT CÁCH LY ---
# ==============================================================================
print("🌐 Đang khởi chạy Google Chrome cách ly chống quét...")
options = webdriver.ChromeOptions()
tool_user_data = os.path.join(os.getcwd(), 'profile_robot_uyen')
options.add_argument(f'--user-data-dir={tool_user_data}')
options.add_argument('--profile-directory=Default')

options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--start-maximized")

try:
    driver = webdriver.Chrome(options=options)
    print("🚀 Mở Chrome thành công!")
except Exception as e:
    print(f"\n❌ Lỗi khởi chạy trình duyệt: {e}")
    exit()

# --- 3. ĐĂNG NHẬP COOKIE & 2FA TỰ ĐỘNG ---
print("\n🔑 Đang kiểm tra trạng thái đăng nhập Facebook...")
driver.get("https://www.facebook.com/")
time.sleep(3)

try:
    for item in COOKIE_RAW.split(';'):
        if '=' in item:
            name, value = item.strip().split('=', 1)
            driver.add_cookie({
                'name': name,
                'value': value,
                'domain': '.facebook.com',
                'path': '/'
            })
    driver.refresh()
    time.sleep(5)
except Exception as e:
    pass

if "login" in driver.current_url or driver.find_elements(By.ID, "email"):
    print("🔄 Cần đăng nhập lại bằng Pass + 2FA...")
    try:
        driver.get("https://www.facebook.com/")
        time.sleep(2)
        driver.find_element(By.ID, "email").send_keys(FB_UID)
        time.sleep(1)
        driver.find_element(By.ID, "pass").send_keys(FB_PASS)
        time.sleep(1)
        driver.find_element(By.ID, "pass").send_keys(Keys.ENTER)
        time.sleep(5)
        
        if "checkpoint" in driver.current_url or driver.find_elements(By.ID, "approvals_code"):
            print("🔐 Đang tự động giải mã lấy OTP 2FA...")
            totp = pyotp.TOTP(FB_2FA.replace(" ", ""))
            otp_code = totp.now()
            code_box = driver.find_element(By.XPATH, "//input[@id='approvals_code' or @type='text']")
            code_box.send_keys(otp_code)
            time.sleep(1)
            code_box.send_keys(Keys.ENTER)
            time.sleep(5)
            try:
                driver.find_element(By.ID, "checkpointSubmitButton").click()
                time.sleep(4)
            except: pass
    except Exception as e:
        print(f"❌ Lỗi đăng nhập: {e}")

print("🎉 ĐĂNG NHẬP HOÀN TẤT! Chuẩn bị quy trình tương tác người thật.")

# ==============================================================================
# --- 4. QUY TRÌNH TƯƠNG TÁC CHUẨN NGƯỜI THẬT ---
# ==============================================================================
for kw in KEYWORDS:
    print(f"\n🔍 --------------------------------------------------")
    print(f"🔎 Đang tìm kiếm từ khóa chủ đề: {kw}")
    
    kw_encoded = urllib.parse.quote(kw)
    search_url = f"https://www.facebook.com/search/groups/?q={kw_encoded}"
    
    try:
        driver.get(search_url)
        time.sleep(random.randint(*DELAY_LOAD_PAGE))
        
        # Quét lấy danh sách link nhóm hiển thị
        group_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/') and @role='link']")
        group_urls = []
        for elem in group_elements:
            href = elem.get_attribute("href")
            if href and "/groups/" in href:
                clean_url = href.split("?")[0]
                if clean_url not in group_urls and "search" not in clean_url:
                    group_urls.append(clean_url)
        
        print(f"📋 Tìm thấy {len(group_urls)} nhóm liên quan.")
        
        # Lọc bớt nhóm, lấy số lượng cấu hình chạy thử nghiệm
        targets = group_urls[:MAX_GROUPS_PER_KEYWORD]
        
        for index, target_group in enumerate(targets):
            print(f"\n➔ [{index+1}/{len(targets)}] Đang tiến hành vào nhóm: {target_group}")
            driver.get(target_group)
            time.sleep(random.randint(*DELAY_LOAD_PAGE))
            
            # --- HÀNH VI 1: CUỘN CHUỘT LƯỚT XEM BÀI VIẾT (SCROLL) ---
            scroll_pixels = random.randint(400, 800)
            print(f"📜 Giả lập người thật: Cuộn chuột xuống {scroll_pixels}px để tìm bài viết...")
            driver.execute_script(f"window.scrollTo(0, {scroll_pixels});")
            
            read_time = random.randint(*DELAY_READ_POST)
            print(f"⏳ Dừng lại 'đọc' bài viết trong {read_time} giây...")
            time.sleep(read_time)
            
            # --- HÀNH VI 2: TỰ ĐỘNG BẤM LIKE BÀI VIẾT ---
            try:
                # XPATH tìm nút Thích/Like của bài viết đang xem
                like_btn = driver.find_element(By.XPATH, "//*[@role='button' and (contains(@aria-label, 'Thích') or contains(@aria-label, 'Like'))]")
                like_btn.click()
                print("👍 Đã bấm Thích bài viết thành công!")
                time.sleep(random.uniform(1.5, 3.0))
            except:
                print("⚠️ Không bấm được Like bài viết (Có thể đã Like hoặc nút bị ẩn).")
            
            # --- HÀNH VI 3: BÌNH LUẬN BIẾN THỂ NGẪU NHIÊN ---
            # Bốc ngẫu nhiên 1 câu nội dung trong bảng mẫu câu
            comment_text = random.choice(COMMENT_TEMPLATES)
            
            try:
                comment_box = driver.find_element(By.XPATH, "//*[@role='textbox' and (contains(@aria-label, 'bình luận') or contains(@aria-label, 'comment') or contains(@aria-label, 'Viết...'))]")
                comment_box.click()
                time.sleep(1.0)
                
                print(f"⌨️ Robot đang gõ chữ ngẫu nhiên: '{comment_text}'")
                for char in comment_text:
                    comment_box.send_keys(char)
                    # Gõ từng phím theo thời gian delay cấu hình ở mục 1
                    time.sleep(random.uniform(*DELAY_TYPING_SPEED))
                
                time.sleep(1.5)
                comment_box.send_keys(Keys.ENTER)
                print("✅ Đã gửi bình luận thành công!")
                
                # --- HÀNH VI 4: THỜI GIAN NGHỈ AN TOÀN GIỮA CÁC NHÓM ---
                rest_time = random.randint(*DELAY_BETWEEN_GROUPS)
                print(f"⏳ Hệ thống tạm nghỉ {rest_time} giây trước khi chuyển mục tiếp theo...")
                time.sleep(rest_time)
                
            except Exception as e:
                print(f"❌ Không tìm thấy ô cmt (Nhóm yêu cầu tham gia trước hoặc bài viết khóa cmt).")
                continue
                
    except Exception as e:
        print(f"❌ Gặp lỗi khi quét từ khóa này, chuyển từ khóa tiếp theo.")
        continue

print("\n🏁 [HOÀN THÀNH] Robot đã hoàn thành ca làm việc an toàn!")
driver.quit()
print("🔒 Trình duyệt đã được đóng và giải phóng bộ nhớ.")