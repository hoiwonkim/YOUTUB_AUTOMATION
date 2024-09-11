from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import os

def edit_video(video_path, subtitles, music_path, analysis):
    video = VideoFileClip(video_path)
    
    subtitle_clips = [
        TextClip(txt, fontsize=24, color='white', bg_color='black')
        .set_pos(('center', 'bottom'))
        .set_start(start)
        .set_duration(end - start)
        for start, end, txt in subtitles
    ]
    
    video_with_subtitles = CompositeVideoClip([video] + subtitle_clips)
    
    # 실제 환경에서는 아래 주석을 해제하고 적절한 음악 파일을 사용해야 합니다
    # background_music = AudioFileClip(music_path).volumex(0.1)
    # final_audio = CompositeAudioClip([video.audio, background_music])
    # final_video = video_with_subtitles.set_audio(final_audio)
    
    final_video = video_with_subtitles
    
    output_path = f"edited_{os.path.basename(video_path)}"
    final_video.write_videofile(output_path)
    
    return output_path