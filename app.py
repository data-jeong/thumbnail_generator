import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
import io
import numpy as np
from datetime import datetime

def get_dominant_color(image):
    """이미지의 주요 색상을 추출"""
    # 이미지를 작은 크기로 리사이즈하여 처리 속도 향상
    small_image = image.resize((50, 50))
    # numpy 배열로 변환
    img_array = np.array(small_image)
    # 픽셀을 2D로 재구성
    pixels = img_array.reshape(-1, 3)
    # 각 채널의 중앙값 계산
    median_color = np.median(pixels, axis=0).astype(int)
    return tuple(median_color)

def create_background(image, target_width, target_height):
    """원본 이미지를 기반으로 배경 생성"""
    # 블러 처리된 배경 생성
    background = image.copy()
    # 배경 이미지를 타겟 크기보다 크게 리사이즈
    scale = 2
    bg_width = int(target_width * scale)
    bg_height = int(target_height * scale)
    
    # 비율 유지하면서 리사이즈
    bg_ratio = bg_width / bg_height
    img_ratio = image.width / image.height
    
    if img_ratio > bg_ratio:
        new_height = bg_height
        new_width = int(new_height * img_ratio)
    else:
        new_width = bg_width
        new_height = int(new_width / img_ratio)
    
    background = background.resize((new_width, new_height), Image.Resampling.LANCZOS)
    # 더 강한 블러 효과 적용
    for _ in range(3):  # 여러 번 블러 적용
        background = background.filter(ImageFilter.GaussianBlur(radius=10))
    
    # 배경 이미지 중앙 크롭
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    background = background.crop((left, top, left + target_width, top + target_height))
    
    # 배경 이미지의 밝기 조정
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.5)  # 50% 어둡게
    
    return background

def resize_for_target(image, target_width, target_height):
    """이미지를 타겟 크기에 맞게 리사이즈 (비율 유지)"""
    img_ratio = image.width / image.height
    target_ratio = target_width / target_height
    
    if img_ratio > target_ratio:
        # 이미지가 더 넓은 경우
        new_height = target_height
        new_width = int(new_height * img_ratio)
    else:
        # 이미지가 더 긴 경우
        new_width = target_width
        new_height = int(new_width / img_ratio)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def resize_and_pad_image(image, target_width, target_height):
    """이미지 리사이징 및 패딩 처리"""
    # Convert image to RGBA
    image = image.convert('RGBA')
    
    # 1. 원본 이미지 비율 계산
    img_ratio = image.width / image.height
    target_ratio = target_width / target_height
    
    # 2. 패딩이 포함된 캔버스 크기 계산
    if img_ratio > target_ratio:
        # 이미지가 더 넓은 경우, 높이를 늘려서 맞춤
        canvas_width = image.width
        canvas_height = int(image.width / target_ratio)
    else:
        # 이미지가 더 긴 경우, 너비를 늘려서 맞춤
        canvas_height = image.height
        canvas_width = int(image.height * target_ratio)
    
    # 3. 흰색 배경의 캔버스 생성
    canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
    
    # 4. 원본 이미지를 캔버스 중앙에 배치
    paste_x = (canvas_width - image.width) // 2
    paste_y = (canvas_height - image.height) // 2
    canvas.paste(image, (paste_x, paste_y), image)
    
    # 5. 배경 이미지 생성 (블러 처리)
    background = image.copy()
    background = background.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
    for _ in range(3):
        background = background.filter(ImageFilter.GaussianBlur(radius=10))
    
    # 배경 이미지의 밝기 조정
    enhancer = ImageEnhance.Brightness(background)
    background = enhancer.enhance(0.5)  # 50% 어둡게
    
    # 6. 캔버스와 배경 합성
    final_img = background.copy()
    final_img.paste(canvas, (0, 0), canvas)
    
    # 7. 최종 타겟 크기로 리사이즈
    final_img = final_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    return final_img

def create_thumbnail(uploaded_image, width, height, add_gradient=True):
    """썸네일 생성"""
    if uploaded_image:
        img = Image.open(uploaded_image)
        img = resize_and_pad_image(img, width, height)
    else:
        img = Image.new('RGBA', (width, height), (255, 255, 255, 255))
    
    if add_gradient:  # 모든 썸네일에 그라데이션 효과 적용
        gradient = np.array([
            [
                (33 - int(33 * y/height), 150 - int(50 * y/height), 243 - int(83 * y/height), int(100 * (1 - y/height)))
                for x in range(width)
            ]
            for y in range(height)
        ], dtype=np.uint8)
        gradient_img = Image.fromarray(gradient, 'RGBA')
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
            if uploaded_file is None:
                st.error("이미지를 업로드해주세요!")
                return
                
            if platform.startswith("TISTORY"):
                width, height = 230, 300
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
                # 티스토리 썸네일의 경우 실제 크기로 표시
                if platform.startswith("TISTORY"):
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