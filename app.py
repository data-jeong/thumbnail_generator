import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np
from datetime import datetime

def create_thumbnail(width, height, title, subtitle, tech_stack, duration):
    # Create base image with gradient background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    gradient = np.array([
        [
            (33 - int(33 * y/height), 150 - int(50 * y/height), 243 - int(83 * y/height))
            for x in range(width)
        ]
        for y in range(height)
    ], dtype=np.uint8)
    gradient_img = Image.fromarray(gradient)
    img.paste(gradient_img)
    
    # Load fonts (using default fonts for now - you can replace with custom fonts)
    try:
        title_font = ImageFont.truetype("arial.ttf", size=int(height/10))
        subtitle_font = ImageFont.truetype("arial.ttf", size=int(height/20))
        tech_font = ImageFont.truetype("arial.ttf", size=int(height/30))
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        tech_font = ImageFont.load_default()
    
    # Draw title
    draw.text((width/20, height/6), title, font=title_font, fill='white')
    
    # Draw subtitle
    draw.text((width/20, height/2.5), subtitle, font=subtitle_font, fill='white')
    
    # Draw tech stack
    tech_y = height/1.8
    for tech in tech_stack:
        draw.text((width/20, tech_y), f"• {tech}", font=tech_font, fill='white')
        tech_y += height/20
    
    # Draw duration
    draw.text((width/20, height - height/6), duration, font=tech_font, fill='white')
    
    return img

def main():
    st.set_page_config(page_title="Tech Blog Thumbnail Generator", layout="wide")
    
    st.title("Tech Blog Thumbnail Generator 🎨")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("썸네일 설정")
        
        platform = st.selectbox(
            "플랫폼 선택",
            ["TISTORY (1200x600)", "Instagram (1080x1080)"]
        )
        
        title = st.text_input("제목", "Advanced Data\nEngineering Stack")
        subtitle = st.text_input("부제목", "데이터 분석가를 위한 엔터프라이즈 분석 플랫폼 구축기 🚀")
        
        tech_stack = st.text_area(
            "기술 스택 (한 줄에 하나씩)",
            "PostgreSQL\nMongoDB\nRedis\nApache Spark\nApache Kafka"
        ).split('\n')
        
        duration = st.text_input("기간", "4주 과정 · 총 20편")
        
        if st.button("썸네일 생성"):
            if platform == "TISTORY (1200x600)":
                width, height = 1200, 600
            else:  # Instagram
                width, height = 1080, 1080
                
            thumbnail = create_thumbnail(width, height, title, subtitle, tech_stack, duration)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            thumbnail.save(img_bytes, format='PNG')
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            platform_name = "tistory" if platform.startswith("TISTORY") else "instagram"
            filename = f"thumbnail_{platform_name}_{timestamp}.png"
            
            with col2:
                st.subheader("생성된 썸네일")
                st.image(thumbnail, use_column_width=True)
                
                # Download button
                st.download_button(
                    label="썸네일 다운로드",
                    data=img_bytes.getvalue(),
                    file_name=filename,
                    mime="image/png"
                )

if __name__ == "__main__":
    main() 