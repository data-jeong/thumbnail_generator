import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import numpy as np
from datetime import datetime

def get_edge_color(image, position='all'):
    """이미지 가장자리의 대표 색상을 추출"""
    img_array = np.array(image)
    
    if position == 'all':
        # 모든 가장자리 픽셀의 평균 색상
        edges = np.concatenate([
            img_array[0, :],  # top edge
            img_array[-1, :],  # bottom edge
            img_array[:, 0],  # left edge
            img_array[:, -1]  # right edge
        ])
        median_color = np.median(edges, axis=0).astype(int)
        return tuple(median_color)
    
    if position == 'top':
        edge_pixels = img_array[0, :, :]
    elif position == 'bottom':
        edge_pixels = img_array[-1, :, :]
    elif position == 'left':
        edge_pixels = img_array[:, 0, :]
    else:  # right
        edge_pixels = img_array[:, -1, :]
    
    median_color = np.median(edge_pixels, axis=0).astype(int)
    return tuple(median_color)

def resize_and_pad_image(image, target_width, target_height, is_tistory=False):
    """이미지 리사이징 및 패딩 처리"""
    # Calculate aspect ratios
    target_ratio = target_width / target_height
    img_ratio = image.width / image.height
    
    # Convert image to RGBA if it isn't already
    image = image.convert('RGBA')
    
    if is_tistory:
        # 티스토리의 경우 더 넓은 뷰를 보여주기 위해 이미지를 약간 축소
        margin_percent = 0.1  # 10% 여백
        content_width = int(target_width * (1 - 2 * margin_percent))
        content_height = int(target_height * (1 - 2 * margin_percent))
        
        # 이미지를 먼저 컨텐츠 크기에 맞게 리사이징
        if img_ratio > target_ratio:
            new_height = int(content_width / img_ratio)
            resized_img = image.resize((content_width, new_height), Image.Resampling.LANCZOS)
        else:
            new_width = int(content_height * img_ratio)
            resized_img = image.resize((new_width, content_height), Image.Resampling.LANCZOS)
        
        # 최종 크기의 새 이미지 생성
        final_img = Image.new('RGBA', (target_width, target_height), (255, 255, 255, 0))
        
        # 리사이즈된 이미지를 중앙에 배치
        paste_x = (target_width - resized_img.width) // 2
        paste_y = (target_height - resized_img.height) // 2
        
        # 가장자리 색상 추출 및 배경 채우기
        edge_color = get_edge_color(resized_img)
        background = Image.new('RGBA', (target_width, target_height), edge_color)
        final_img = Image.alpha_composite(background, final_img)
        
        # 리사이즈된 이미지 붙이기
        final_img.paste(resized_img, (paste_x, paste_y), resized_img)
        return final_img
    else:
        # 인스타그램 등 다른 형식은 기존 로직 유지
        if img_ratio > target_ratio:
            new_height = int(target_width / img_ratio)
            resized_img = image.resize((target_width, new_height), Image.Resampling.LANCZOS)
            padding = (target_height - new_height) // 2
            edge_color = get_edge_color(resized_img, 'top')
            padded_img = Image.new('RGBA', (target_width, target_height), edge_color)
            padded_img.paste(resized_img, (0, padding), resized_img)
        else:
            new_width = int(target_height * img_ratio)
            resized_img = image.resize((new_width, target_height), Image.Resampling.LANCZOS)
            padding = (target_width - new_width) // 2
            edge_color = get_edge_color(resized_img, 'left')
            padded_img = Image.new('RGBA', (target_width, target_height), edge_color)
            padded_img.paste(resized_img, (padding, 0), resized_img)
        return padded_img

def create_thumbnail(uploaded_image, width, height, add_gradient=True, is_tistory=False):
    """썸네일 생성"""
    if uploaded_image:
        img = Image.open(uploaded_image)
        img = resize_and_pad_image(img, width, height, is_tistory)
    else:
        img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    
    if add_gradient:
        # 반투명 그라데이션 오버레이 생성
        gradient = np.array([
            [
                (33 - int(33 * y/height), 150 - int(50 * y/height), 243 - int(83 * y/height), int(100 * (1 - y/height)))
                for x in range(width)
            ]
            for y in range(height)
        ], dtype=np.uint8)
        gradient_img = Image.fromarray(gradient, 'RGBA')
        
        # 그라데이션 오버레이 적용
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
            is_tistory = platform.startswith("TISTORY")
            if is_tistory:
                width, height = 1200, 600
            else:  # Instagram
                width, height = 1080, 1080
                
            thumbnail = create_thumbnail(uploaded_file, width, height, add_gradient, is_tistory)
            
            # Convert to bytes
            img_bytes = io.BytesIO()
            thumbnail.save(img_bytes, format='PNG')
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            platform_name = "tistory" if is_tistory else "instagram"
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