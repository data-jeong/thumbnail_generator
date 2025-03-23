import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import numpy as np
from datetime import datetime

def get_edge_color(image, position='top'):
    """이미지 가장자리의 대표 색상을 추출합니다."""
    img_array = np.array(image)
    if position == 'top':
        edge_pixels = img_array[0, :, :]
    elif position == 'bottom':
        edge_pixels = img_array[-1, :, :]
    elif position == 'left':
        edge_pixels = img_array[:, 0, :]
    else:  # right
        edge_pixels = img_array[:, -1, :]
    
    # 가장자리 픽셀들의 중앙값을 계산하여 대표 색상으로 사용
    median_color = np.median(edge_pixels, axis=0).astype(int)
    return tuple(median_color)

def resize_and_pad_image(image, target_width, target_height):
    # Calculate aspect ratios
    target_ratio = target_width / target_height
    img_ratio = image.width / image.height
    
    # Convert image to RGBA if it isn't already
    image = image.convert('RGBA')
    
    # Resize image maintaining aspect ratio
    if img_ratio > target_ratio:
        # Image is wider than target
        new_height = int(target_width / img_ratio)
        resized_img = image.resize((target_width, new_height), Image.Resampling.LANCZOS)
        # Get colors from top and bottom edges
        top_color = get_edge_color(resized_img, 'top')
        bottom_color = get_edge_color(resized_img, 'bottom')
        # Create new image with edge colors
        padded_img = Image.new('RGBA', (target_width, target_height), top_color)
        # Calculate padding
        padding = (target_height - new_height) // 2
        # Paste resized image in the middle
        padded_img.paste(resized_img, (0, padding))
        # Fill bottom part with bottom edge color
        bottom_part = Image.new('RGBA', (target_width, padding), bottom_color)
        padded_img.paste(bottom_part, (0, target_height - padding))
    else:
        # Image is taller than target
        new_width = int(target_height * img_ratio)
        resized_img = image.resize((new_width, target_height), Image.Resampling.LANCZOS)
        # Get colors from left and right edges
        left_color = get_edge_color(resized_img, 'left')
        right_color = get_edge_color(resized_img, 'right')
        # Create new image with edge colors
        padded_img = Image.new('RGBA', (target_width, target_height), left_color)
        # Calculate padding
        padding = (target_width - new_width) // 2
        # Paste resized image in the middle
        padded_img.paste(resized_img, (padding, 0))
        # Fill right part with right edge color
        right_part = Image.new('RGBA', (padding, target_height), right_color)
        padded_img.paste(right_part, (target_width - padding, 0))
    
    return padded_img

def create_thumbnail(uploaded_image, width, height, add_gradient=True):
    # Process uploaded image
    if uploaded_image:
        img = Image.open(uploaded_image)
        img = resize_and_pad_image(img, width, height)
    else:
        img = Image.new('RGB', (width, height), color='white')
    
    # Add gradient overlay if requested
    if add_gradient:
        gradient = np.array([
            [
                (33 - int(33 * y/height), 150 - int(50 * y/height), 243 - int(83 * y/height), int(128 * (1 - y/height)))
                for x in range(width)
            ]
            for y in range(height)
        ], dtype=np.uint8)
        gradient_img = Image.fromarray(gradient, 'RGBA')
        
        # Convert base image to RGBA
        img = img.convert('RGBA')
        # Overlay gradient
        img = Image.alpha_composite(img, gradient_img)
    
    return img

def main():
    st.set_page_config(page_title="썸네일 생성기", layout="wide")
    
    st.title("블로그/SNS 썸네일 생성기 🎨")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("썸네일 설정")
        
        platform = st.selectbox(
            "플랫폼 선택",
            ["TISTORY (1200x600)", "Instagram (1080x1080)"]
        )
        
        uploaded_file = st.file_uploader("이미지 업로드", type=['png', 'jpg', 'jpeg'])
        add_gradient = st.checkbox("그라데이션 효과 추가", value=True)
        
        if st.button("썸네일 생성"):
            if platform == "TISTORY (1200x600)":
                width, height = 1200, 600
            else:  # Instagram
                width, height = 1080, 1080
                
            thumbnail = create_thumbnail(uploaded_file, width, height, add_gradient)
            
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