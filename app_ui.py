import streamlit as st
import json
import os

st.set_page_config(layout="wide", page_title="AI Mechatronics Analysis", page_icon="📊")
st.title("📊 Hệ Thống Phân Tích Nội Dung & Gợi Ý Phản Hồi Chuyên Ngành")

# Đọc file dữ liệu thật do ai_engine.py sinh ra
DATA_FILE = "logs/analyzed_posts.json"

if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
    st.warning("⚠️ Chưa có dữ liệu phân tích. Hãy chạy file ai_engine.py trước để tạo dữ liệu!")
else:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)

    for idx, post in enumerate(posts):
        # Hiển thị tiêu đề thẻ theo tên tác giả bài viết
        st.subheader(f"📝 Bài viết của: {post.get('author', 'Ẩn danh')} (ID: {post.get('post_id')})")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Nội dung gốc:**\n\n{post.get('content')}")
            st.write(f"🤖 **AI Tóm tắt:** {post.get('summary')}")
            
            # Hiển thị các từ khóa kỹ thuật dưới dạng các tag (dấu nhãn) nhỏ
            st.write("**📌 Từ khóa chuyên ngành:**")
            keywords = post.get('technical_keywords', [])
            st.caption(" | ".join([f"`{kw}`" for kw in keywords]))
            
        with col2:
            st.success("**💡 Phản hồi gợi ý từ Gemini (Có thể chỉnh sửa):**")
            final_reply = st.text_area(
                "Câu trả lời kỹ thuật gợi ý:", 
                value=post.get('suggested_reply', ''), 
                key=f"reply_{idx}",
                height=120
            )
            
            # Nút bấm mô phỏng việc copy/duyệt nội dung
            if st.button(f"📋 Copy câu trả lời của {post.get('author')}", key=f"btn_{idx}"):
                st.toast(f"Đã chọn nội dung phản hồi cho {post.get('author')}!")
                
        st.markdown("---")