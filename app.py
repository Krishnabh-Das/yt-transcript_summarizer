from flask import Flask, request, jsonify
import importlib
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled

app = Flask(__name__)

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

        
        # Import sumy.parsers.plaintext
        PlaintextParser = importlib.import_module("sumy.parsers.plaintext").PlaintextParser
        
        # Import sumy.nlp.tokenizers
        Tokenizer = importlib.import_module("sumy.nlp.tokenizers").Tokenizer
        
        # Import sumy.summarizers.lsa
        LsaSummarizer = importlib.import_module("sumy.summarizers.lsa").LsaSummarizer
        
        # Your long text
        long_text = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus gravida nulla nec dui ultrices, vitae tincidunt purus accumsan. Donec eu justo tortor. Ut nec diam eget urna fringilla cursus. Proin ullamcorper leo at tellus bibendum luctus. Nullam sit amet facilisis libero. Sed nec libero vel justo malesuada eleifend. Suspendisse euismod libero a odio faucibus, id euismod quam scelerisque. In hac habitasse platea dictumst. Quisque condimentum lectus vel odio bibendum, a interdum sapien finibus. Integer fringilla vitae leo sit amet fermentum.
        """
        
        # Initialize the parser and tokenizer
        parser = PlaintextParser.from_string(long_text, Tokenizer("english"))
        
        # Initialize the summarizer
        summarizer = LsaSummarizer()
        
        # Get the summary
        summary = summarizer(parser.document, sentences_count=3)  # Adjust the number of sentences as needed
        
        cleaned_out = remove_bracketed_words(summary)  # Remove words and brackets
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
