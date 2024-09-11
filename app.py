# app.py

import os
import json
import logging
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from static.scripts.video_analyzer import analyze_video
from static.scripts.subtitle_generator import generate_subtitles
from static.scripts.music_selector import select_background_music
from static.scripts.video_editor import edit_video

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
logging.basicConfig(level=logging.INFO)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        app.logger.info("POST request received")
        if 'video' not in request.files:
            app.logger.warning("No video file in request")
            return redirect(request.url)
        
        file = request.files['video']
        if file.filename == '':
            app.logger.warning("No selected file")
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            app.logger.info(f"File saved: {filepath}")
            
            to_japanese = 'to_japanese' in request.form
            app.logger.info(f"Japanese translation requested: {to_japanese}")
            
            try:
                # Analyze video
                app.logger.info("Starting video analysis")
                analysis = analyze_video(filepath, to_japanese)
                app.logger.info("Video analysis completed")
                
                # Generate subtitles
                app.logger.info("Starting subtitle generation")
                subtitles = generate_subtitles(filepath)
                app.logger.info("Subtitle generation completed")
                
                # Select background music
                app.logger.info("Selecting background music")
                music = select_background_music(analysis)
                app.logger.info("Background music selected")
                
                # Edit video
                app.logger.info("Starting video editing")
                edited_video_path = edit_video(filepath, subtitles, music, analysis)
                app.logger.info("Video editing completed")
                
                # Upload to YouTube
                app.logger.info("Starting YouTube upload")
                video_id = upload_to_youtube(edited_video_path, analysis)
                app.logger.info(f"YouTube upload completed. Video ID: {video_id}")
                
                return f'Video uploaded successfully! YouTube ID: {video_id}'
            except Exception as e:
                app.logger.error(f"An error occurred: {str(e)}")
                return f"An error occurred: {str(e)}"
    
    return render_template('index.html')

def upload_to_youtube(video_file, analysis):
    client_secrets_file = 'client_secrets.json'
    if not os.path.exists(client_secrets_file):
        app.logger.error("client_secrets.json file not found")
        return "Error: client_secrets.json file not found"
    
    credentials = Credentials.from_authorized_user_file(client_secrets_file, ['https://www.googleapis.com/auth/youtube.upload'])
    
    youtube = build('youtube', 'v3', credentials=credentials)
    
    request_body = {
        'snippet': {
            'title': analysis['title']['ko'],
            'description': analysis['description']['ko'],
            'tags': analysis['tags']['ko'],
            'categoryId': '22'  # People & Blogs category
        },
        'status': {
            'privacyStatus': 'private',  # You can change this to 'public' or 'unlisted'
            'selfDeclaredMadeForKids': False
        }
    }
    
    if 'ja' in analysis['title']:
        request_body['snippet']['title'] += f" / {analysis['title']['ja']}"
        request_body['snippet']['description'] += f"\n\n日本語:\n{analysis['description']['ja']}"
        request_body['snippet']['tags'].extend(analysis['tags']['ja'])
    
    media = MediaFileUpload(video_file, resumable=True)
    
    try:
        insert_request = youtube.videos().insert(
            part=','.join(request_body.keys()),
            body=request_body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = insert_request.next_chunk()
            if status:
                app.logger.info(f"Uploaded {int(status.progress() * 100)}%")
        
        return response['id']
    except Exception as e:
        app.logger.error(f"YouTube upload error: {str(e)}")
        return f"An error occurred during YouTube upload: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)