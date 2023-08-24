from flask import Flask, request, jsonify
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

app = Flask(__name__)

def get_summary_from_link(link, value):
    try:
        if '=' in link:
            video_id = link.split("=")[1]
        else:
            video_id = link.split("e/")[1]

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        result = " ".join([i['text'] for i in transcript])

        return result

    except TranscriptsDisabled as e:
        return "Transcripts are disabled for this video."

    except Exception as e:
        return "An error occurred: " + str(e)

@app.route('/summarize', methods=['POST'])
def summarize_route():
    try:
        video_link = str(request.form.get('video_link'))
        value = int(request.form.get('value'))

        final_summary = get_summary_from_link(video_link, value)
        return jsonify({'summary': final_summary})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
