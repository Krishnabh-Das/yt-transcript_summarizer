from flask import Flask, request, jsonify
from summarizer import Summarizer
from summarizer import sbert
from sbert import SBertSummarizer
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

app = Flask(__name__)

model = SBertSummarizer('paraphrase-MiniLM-L6-v2')

def summarize_text(text):
    sentences = nltk.sent_tokenize(text)
    summary = sentences[0]
    for sentence in sentences[1:]:
        summary += ' ' + sentence
    summary = summary[:500] + '...' if len(summary) > 500 else summary
    return summary

def clean_text(text):
    # Remove extra spaces and spaces before punctuation
    cleaned_text = re.sub(r'\s+', ' ', text)
    cleaned_text = re.sub(r'\s([.,;!?])', r'\1', cleaned_text)
    return cleaned_text.strip()

def remove_bracketed_words(text):
    # Remove words enclosed in square brackets including the brackets
    cleaned_text = re.sub(r'\[.*?\]', '', text)
    return cleaned_text

def get_summary_from_link(link):
    try:
        if '=' in link:
            video_id = link.split("=")[1]
        else:
            video_id = link.split("e/")[1]

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        result = ""
        for i in transcript:
            result += i['text']+' '

        result = model(body, num_sentences=5)

        cleaned_out = remove_bracketed_words(result)  # Remove words and brackets
        cleaned_out = clean_text(cleaned_out)
        
        return cleaned_out

    except TranscriptsDisabled as e:
        return "Transcripts are disabled for this video."

    except Exception as e:
        return "An error occurred: " + str(e)

@app.route('/summarize', methods=['POST'])
def summarize_route():
    try:
        video_link = str(request.form.get('video_link'))

        final_summary = get_summary_from_link(video_link)
        return jsonify({'summary': final_summary})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
