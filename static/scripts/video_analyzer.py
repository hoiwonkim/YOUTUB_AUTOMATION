# static\scripts\video_analyzer.py

import cv2
import numpy as np
from collections import Counter
from google.cloud import translate
import random

def analyze_video(video_path, to_japanese=False):
    cap = cv2.VideoCapture(video_path)
    
    frame_count = 0
    brightness_values = []
    colors = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % 10 == 0:
            brightness = np.mean(frame)
            brightness_values.append(brightness)
            colors.extend(frame.reshape(-1, 3))
        
        frame_count += 1
    
    cap.release()
    
    avg_brightness = np.mean(brightness_values)
    dominant_color = get_dominant_color(colors)
    video_length = frame_count / cap.get(cv2.CAP_PROP_FPS)
    
    sentiment = "긍정적" if avg_brightness > 127 else "부정적"
    color_name = get_color_name(dominant_color)
    
    title_ko = f"{sentiment} 분위기의 {color_name} 톤 영상"
    description_ko = (f"이 영상은 {video_length:.1f}초 길이의 {sentiment} 분위기를 가진 콘텐츠입니다. "
                      f"주요 색상은 {color_name}이며, 평균 밝기는 {avg_brightness:.2f}입니다. "
                      f"이 자동 생성된 영상은 AI 기술을 활용하여 편집되었습니다.")
    
    tags_ko = ["자동생성", "AI편집", sentiment, color_name, f"{video_length:.0f}초"]
    
    result = {
        'title': {'ko': title_ko},
        'description': {'ko': description_ko},
        'tags': {'ko': tags_ko},
        'sentiment': sentiment,
        'avg_brightness': avg_brightness,
        'dominant_color': color_name,
        'video_length': video_length
    }
    
    if to_japanese:
        translate_client = translate.TranslationServiceClient()
        parent = translate_client.location_path("your-project-id", "global")
        
        def translate_text(text):
            response = translate_client.translate_text(
                parent=parent,
                contents=[text],
                mime_type="text/plain",
                source_language_code="ko",
                target_language_code="ja"
            )
            return response.translations[0].translated_text

        result['title']['ja'] = translate_text(title_ko)
        result['description']['ja'] = translate_text(description_ko)
        result['tags']['ja'] = [translate_text(tag) for tag in tags_ko]
    
    return result

def get_dominant_color(colors):
    return tuple(map(int, np.mean(colors, axis=0)))

def get_color_name(color):
    colors = {
        "빨강": (255, 0, 0), "초록": (0, 255, 0), "파랑": (0, 0, 255),
        "노랑": (255, 255, 0), "보라": (128, 0, 128), "주황": (255, 165, 0),
        "분홍": (255, 192, 203), "갈색": (165, 42, 42), "회색": (128, 128, 128)
    }
    return min(colors, key=lambda n: sum((c - color[i])**2 for i, c in enumerate(colors[n])))

def get_most_common(items, n):
    return [item for item, count in Counter(items).most_common(n)]