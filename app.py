import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
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

def create_blur_background(image, target_width, target_height):
    """이미지를 블러 처리하여 배경으로 사용"""
    # 이미지를 타겟 크기보다 크게 리사이즈
    scale = 1.2
    blur_width = int(target_width * scale)
    blur_height = int(target_height * scale)
    
    # 비율 유지하면서 리사이즈
    img_ratio = image.width / image.height
    target_ratio = blur_width / blur_height
    
    if img_ratio > target_ratio:
        new_width = blur_width
        new_height = int(new_width / img_ratio)
    else:
        new_height = blur_height
        new_width = int(new_height * img_ratio)
    
    # 이미지 리사이즈 및 블러 처리
    background = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(radius=10))
    
    # 중앙 부분 크롭
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    background = background.crop((left, top, left + target_width, top + target_height))
    
    return background

def resize_and_pad_image(image, target_width, target_height, is_tistory=False):
    """이미지 리사이징 및 패딩 처리"""
    # Convert image to RGBA if it isn't already
    image = image.convert('RGBA')
    
    if is_tistory:
        # 티스토리 썸네일용 최적화
        img_ratio = image.width / image.height
        target_ratio = target_width / target_height
        
        # 이미지 리사이징 (약간 더 크게)
        if img_ratio > target_ratio:
            # 이미지가 더 넓은 경우
            new_height = target_height
            new_width = int(new_height * img_ratio)
        else:
            # 이미지가 더 긴 경우
            new_width = target_width
            new_height = int(new_width / img_ratio)
        
        resized_img = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 중앙 부분 크롭
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        cropped_img = resized_img.crop((left, top, left + target_width, top + target_height))
        
        return cropped_img
    else:
        # 인스타그램 등 다른 형식
        img_ratio = image.width / image.height
        target_ratio = target_width / target_height
        
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
    
    if add_gradient and not is_tistory:  # 티스토리 썸네일에는 그라데이션 효과 제외
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
            ["TISTORY (230x300)", "Instagram (1080x1080)"]
        )
        
        uploaded_file = st.file_uploader("이미지 업로드", type=['png', 'jpg', 'jpeg'])
        add_gradient = st.checkbox("그라데이션 효과 추가", value=True)
        
        if st.button("썸네일 생성"):
            is_tistory = platform.startswith("TISTORY")
            if is_tistory:
                width, height = 230, 300
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
                # 티스토리 썸네일의 경우 실제 크기로 표시
                if is_tistory:
                    st.image(thumbnail, width=230)
                else:
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