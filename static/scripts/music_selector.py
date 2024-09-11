import random

def select_background_music(analysis):
    mood_to_genre = {
        'POSITIVE': ['upbeat', 'pop', 'happy'],
        'NEGATIVE': ['melancholic', 'slow', 'sad'],
        'NEUTRAL': ['ambient', 'instrumental']
    }
    
    genres = mood_to_genre.get(analysis['sentiment'], ['instrumental'])
    
    # Simulating music selection
    selected_genre = random.choice(genres)
    return f"path/to/music/{selected_genre}_track.mp3"