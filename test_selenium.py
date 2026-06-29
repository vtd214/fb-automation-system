import os
import sys
import json
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def extract_local_data():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # Chạy ẩn danh không cần mở cửa sổ trình duyệt
    driver = webdriver.Chrome(options=options)
    
    try:
        # Đường dẫn tuyệt đối tới file HTML vừa tạo
        file_path = os.path.abspath("test_site.html")
        driver.get(f"file:///{file_path}")
        
        # 1. Các bước debug tiêu chuẩn
        logging.info(f"📍 URL hiện tại: {driver.current_url}")
        logging.info(f"🏷️ Tiêu đề trang: {driver.title}")
        
        # 2. Dùng WebDriverWait để đợi các thùng chứa bài viết hiển thị
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "post-container")))
        
        # 3. Trích xuất dữ liệu cấu trúc
        posts_elements = driver.find_elements(By.CLASS_NAME, "post-container")
        extracted_data = []
        
        for idx, post in enumerate(posts_elements):
            title = post.find_element(By.CLASS_NAME, "post-title").text
            content = post.find_element(By.CLASS_NAME, "post-content").text
            group_url = post.find_element(By.CLASS_NAME, "group-link").get_attribute("href")
            
            extracted_data.append({
                "post_id": f"p{101+idx}",
                "title": title,
                "content": content,
                "group_url": group_url
            })
            
        # 4. Lưu dữ liệu thô sạch ra file JSON
        with open("posts_data.json", "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)
            
        logging.info("✅ Đã trích xuất và lưu dữ liệu thành công vào file posts_data.json!")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    extract_local_data()