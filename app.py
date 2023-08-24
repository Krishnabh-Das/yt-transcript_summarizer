from flask import Flask, request, jsonify
import re
from transformers import pipeline
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

app = Flask(__name__)

model_name = "facebook/bart-small-cnn"
summarizer = pipeline('summarization', model=model_name, revision="a4f8f3e")

def processing(result, value):
    def clean_text(text):
        cleaned_text = re.sub(r'\s+', ' ', text)
        cleaned_text = re.sub(r'\s([.,;!?])', r'\1', cleaned_text)
        return cleaned_text.strip()

    def remove_bracketed_words(text):
        cleaned_text = re.sub(r'\[.*?\]', '', text)
        return cleaned_text

    def summarize(text):
        summarized_text1 = summarizer(text, max_length=1000 * value, min_length=30 * value, do_sample=True)
        cleaned_out = remove_bracketed_words(summarized_text1)
        cleaned_out = clean_text(cleaned_out)
        return cleaned_out

    summarized_text = summarize(result)

    bullet_pointed_text = re.sub(r'([.?!"\'\n])\s+', r'\1\n• ', summarized_text)
    bullet_pointed_text = bullet_pointed_text.replace('• ', '\n• ')

    return bullet_pointed_text

def get_summary_from_link(link, value):
    try:
        if '=' in link:
            video_id = link.split("=")[1]
        else:
            video_id = link.split("e/")[1]

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        result = " ".join([i['text'] for i in transcript])

        cleaned_summary = processing(result, value)
        return cleaned_summary

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
