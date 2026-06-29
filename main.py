import os
import sys
import json
import time
import random
import logging
import urllib.parse
from datetime import datetime

import pyotp
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ==============================================================================
# 1. HỆ THỐNG LOGGING ĐẦY ĐỦ
# ==============================================================================
os.makedirs("logs", exist_ok=True)
log_filename = f"logs/{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

load_dotenv()

try:
    api_key_env = os.getenv("GEMINI_API_KEY")
    if not api_key_env:
        raise ValueError("Không tìm thấy biến GEMINI_API_KEY trong file .env")
        
    client = genai.Client(
        api_key=api_key_env,
        http_options={"api_version": "v1"}
    )
except Exception as e:
    logging.critical(f"❌ Không thể khởi tạo Client AI: {e}")
    sys.exit(1)

CONFIG = {
    "keywords": ["STM32 mechatronics", "Siemens PLC SCL"],
    "settings": {
        "max_groups_per_keyword": 3, 
        "heartbeat_interval_minutes": 10
    },
    "delays": {
        "delay_load_page_min": 5, 
        "delay_load_page_max": 8
    }
}
if os.path.exists("config.json"):
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            CONFIG = json.load(f)
    except Exception:
        logging.warning("Không đọc được config.json, sử dụng cấu hình mặc định.")

# ==============================================================================
# 2. HÀM AI ENGINE - PHÂN TÍCH BÀI VIẾT + BÌNH LUẬN
# ==============================================================================
def analyze_post_and_comments(post_text, comments_list, keyword):
    if not post_text or post_text.strip() == "":
        return "Không có dữ liệu bài viết để phân tích."
        
    formatted_comments = "\n".join([f"- Người khác cmt: {c}" for c in comments_list])
    
    prompt = f"""
    Bạn là một kỹ sư chuyên ngành Cơ điện tử và Tự động hóa. 
    Hãy phân tích bài viết trong nhóm về từ khóa '{keyword}' và các bình luận hiện có để đưa ra một câu phản hồi phù hợp nhất.
    
    [NỘI DUNG BÀI VIẾT VỪA ĐĂNG]
    {post_text}
    
    [CÁC BÌNH LUẬN HIỆN CÓ CỦA NGƯỜI KHÁC]
    {formatted_comments if comments_list else "Chưa có bình luận nào."}
    
    Yêu cầu:
    Dựa vào ngữ cảnh trên, hãy viết 1 câu bình luận phản hồi (dưới 30 từ). 
    - Nếu bài viết hỏi đáp kỹ thuật (PLC, STM32, PID...), câu cmt phải mang tính đóng góp giải pháp hoặc gợi ý chuyên môn.
    - Không viết trùng lặp ý với các bình luận hiện có của người khác.
    - Lịch sự, ngắn gọn, dùng thuật ngữ chuyên ngành chuẩn xác. Do không dùng emoji.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip().replace('"', '') # Loại bỏ dấu ngoặc kép nếu AI tự thêm vào
    except Exception as e:
        logging.error(f"Lỗi gọi Gemini AI: {e}")
        return "Bài viết chia sẻ chuyên môn rất hay, cảm ơn bạn!"

# ==============================================================================
# 3. LÕI TỰ ĐỘNG HÓA CHÍNH (SELENIUM FLOW)
# ==============================================================================
def run_automation_flow():
    logging.info("🌐 Đang khởi chạy Google Chrome với Profile...")
    options = webdriver.ChromeOptions()
    tool_user_data = os.path.join(os.getcwd(), 'profile_robot_uyen')
    options.add_argument(f'--user-data-dir={tool_user_data}')
    options.add_argument('--profile-directory=Default')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    
    try:
        # --- BƯỚC 1: XỬ LÝ ĐĂNG NHẬP / COOKIE ---
        logging.info("🔑 Truy cập Facebook để thiết lập phiên đăng nhập...")
        driver.get("https://www.facebook.com/")
        time.sleep(4)
        
        try:
            cookies = os.getenv("COOKIE_RAW", "")
            if cookies:
                logging.info("🍪 Đang nạp Cookie thô vào trình duyệt...")
                for item in cookies.split(';'):
                    if '=' in item:
                        name, value = item.strip().split('=', 1)
                        driver.add_cookie({'name': name, 'value': value, 'domain': '.facebook.com', 'path': '/'})
                driver.refresh()
                time.sleep(4)
        except Exception as e:
            logging.debug(f"Bỏ qua lỗi nạp cookie ban đầu: {e}")

        if driver.find_elements(By.ID, "email") or "login" in driver.current_url:
            logging.warning("⚠️ Không có session hoặc cookie hết hạn! Đăng nhập bằng tài khoản + 2FA...")
            wait.until(EC.presence_of_element_located((By.ID, "email"))).send_keys(os.getenv("FB_UID"))
            driver.find_element(By.ID, "pass").send_keys(os.getenv("FB_PASS"))
            driver.find_element(By.ID, "pass").send_keys(Keys.ENTER)
            time.sleep(5)
            
            try:
                code_box = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@id='approvals_code' or @type='text']")))
                logging.info("🔐 Phát hiện màn hình 2FA! Đang tính toán mã OTP...")
                secret_2fa = os.getenv("FB_2FA", "").replace(" ", "")
                totp = pyotp.TOTP(secret_2fa)
                current_otp = totp.now()
                
                logging.info(f"🔑 Nhập mã OTP tự động sinh ra: {current_otp}")
                code_box.send_keys(current_otp)
                code_box.send_keys(Keys.ENTER)
                time.sleep(6)
            except Exception:
                logging.info("Không phát hiện yêu cầu nhập mã 2FA (hoặc đã vào thẳng).")
        else:
            logging.info("🎉 Đã đăng nhập thành công từ bước nạp Cookie/Session!")

        # --- BƯỚC 2: DUYỆT QỦA DANH SÁCH TỪ KHÓA ---
        keywords = CONFIG["keywords"]
        for keyword in keywords:
            logging.info(f"🔍 Bắt đầu tìm kiếm từ khóa: {keyword}")
            search_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Tìm kiếm trên Facebook' or @aria-label='Tìm kiếm trên Facebook']")))
            search_box.click()
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)
            
            for char in keyword:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.2))
            search_box.send_keys(Keys.ENTER)
            time.sleep(6)
            
            logging.info("🎛️ Click chọn bộ lọc 'Nhóm'...")
            group_filter_xpath = "//span[contains(text(), 'Nhóm') or contains(text(), 'Groups')]/ancestor::a"
            click_success = False
            for attempt in range(3):
                try:
                    time.sleep(1.5)
                    group_filter = wait.until(EC.element_to_be_clickable((By.XPATH, group_filter_xpath)))
                    group_filter.click()
                    click_success = True
                    logging.info("✅ Click bộ lọc Nhóm thành công!")
                    break
                except Exception:
                    logging.warning(f"⚠️ Trình duyệt đang tải lại DOM (Thử lại lần {attempt + 1}/3)...")
                    
            if not click_success:
                logging.error("❌ Không click được bộ lọc, ép buộc điều hướng URL trực tiếp.")
                kw_encoded = urllib.parse.quote(keyword)
                driver.get(f"https://www.facebook.com/search/groups/?q={kw_encoded}")
                time.sleep(6)

            driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(3)
            
            js_links = driver.execute_script("return Array.from(document.querySelectorAll('a')).map(a => a.href);")
            group_urls = []
            for href in js_links:
                if href and "/groups/" in href:
                    clean_url = href.split("?")[0].split("&")[0]
                    if "search" not in clean_url and not clean_url.endswith("/groups") and not clean_url.endswith("/groups/"):
                        if clean_url not in group_urls:
                            group_urls.append(clean_url)
            
            clean_targets = [url for url in group_urls if url.strip() not in ["https://www.facebook.com/groups/", "https://www.facebook.com/groups"]]
            targets = clean_targets[:CONFIG["settings"]["max_groups_per_keyword"]]
            
            logging.info(f"📋 Tìm thấy {len(targets)} nhóm sạch cho từ khóa '{keyword}': {targets}")
            
            # --- BƯỚC 3: VÀO TỪNG NHÓM ĐỌC BÀI VIẾT + BÌNH LUẬN VÀ THỰC HIỆN CMT ---
            for target_group in targets:
                logging.info(f"➔ Đang tiến vào nhóm: {target_group}")
                driver.get(target_group)
                time.sleep(random.randint(CONFIG["delays"]["delay_load_page_min"], CONFIG["delays"]["delay_load_page_max"]))
                
                driver.execute_script("window.scrollTo(0, 400);")
                time.sleep(2)
                
                post_content = ""
                comments_extracted = []
                
                try:
                    # Lấy nội dung bài viết
                    post_element = driver.find_element(By.XPATH, "//div[@data-ad-preview='message' or @data-testid='post_message'] | //div[@dir='auto' and not(@class)]")
                    post_content = post_element.text.strip()
                    
                    # Lấy các bình luận cũ làm ngữ cảnh
                    comment_elements = driver.find_elements(By.XPATH, "//div[@role='article']//div[@dir='auto']")
                    for cmt in comment_elements[:4]:
                        text = cmt.text.strip()
                        if text and text != post_content:
                            comments_extracted.append(text)
                except Exception as e:
                    logging.debug(f"Không lấy được thông tin bài viết chi tiết: {e}")
                
                if post_content:
                    logging.info(f"📝 Bắt được bài viết. Đang yêu cầu AI sinh câu trả lời...")
                    ai_suggested_comment = analyze_post_and_comments(post_content, comments_extracted, keyword)
                    
                    print("\n" + "="*60)
                    print(f"✨ AI ĐƯA RA CÂU CMT:\n👉 {ai_suggested_comment}")
                    print("="*60 + "\n")
                    
                    # ------------------------------------------------------------------
                    # ĐOẠN PHÁT TRIỂN MỚI: TÌM Ô CMT VÀ TIẾN HÀNH BÌNH LUẬN TỰ ĐỘNG
                    # ------------------------------------------------------------------
                    try:
                        logging.info("🎯 Đang tìm kiếm hộp thoại Bình luận (Comment Box)...")
                        
                        # Định vị ô viết bình luận (Facebook có nhiều lớp div bọc ngoài nút viết cmt thực tế)
                        comment_box_xpath = (
                            "//div[@aria-label='Viết bình luận...' or @aria-label='Write a comment...']"
                            "| //div[@role='textbox' and contains(@aria-label, 'bình luận')]"
                        )
                        
                        # Cuộn nhẹ để đảm bảo nút bình luận hiển thị trên màn hình nhằm tránh lỗi click
                        comment_boxes = driver.find_elements(By.XPATH, comment_box_xpath)
                        
                        if comment_boxes:
                            comment_box = comment_boxes[0]
                            # Di chuyển chuột đến ô comment và click để kích hoạt
                            actions = ActionChains(driver)
                            actions.move_to_element(comment_box).perform()
                            time.sleep(1)
                            comment_box.click()
                            time.sleep(1.5)
                            
                            # Nhập liệu theo kiểu mô phỏng người thật gõ chữ (Né checkpoint)
                            logging.info("✍️ Đang gõ bình luận từng ký tự...")
                            # Lấy lại element đang active để tránh lỗi lệch focus
                            active_comment_box = driver.switch_to.active_element
                            
                            for char in ai_suggested_comment:
                                active_comment_box.send_keys(char)
                                time.sleep(random.uniform(0.05, 0.15))
                                
                            time.sleep(1)
                            # Nhấn Enter để gửi bình luận
                            active_comment_box.send_keys(Keys.ENTER)
                            logging.info("✅ Đã gửi bình luận thành công lên bài viết!")
                            
                            # Chờ một chút để Facebook kịp ghi nhận dữ liệu
                            time.sleep(random.randint(4, 7))
                        else:
                            logging.warning("❌ Không tìm thấy ô nhập bình luận công khai trên bài viết này (Có thể tính năng cmt bị khóa).")
                            
                    except Exception as comment_error:
                        logging.error(f"❌ Thất bại khi thực hiện tương tác bình luận: {comment_error}")
                else:
                    logging.warning(f"⚠️ Không đọc được dữ liệu bài viết của nhóm này: {target_group}")
                    
                time.sleep(random.randint(3, 5))
                
    except Exception as e:
        logging.exception(f"💥 Lỗi hệ thống: {e}")
    finally:
        logging.info("🚪 Đang đóng trình duyệt giải phóng RAM...")
        driver.quit()

if __name__ == "__main__":
    run_automation_flow()