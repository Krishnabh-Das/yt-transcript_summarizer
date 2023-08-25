
from flask import Flask, request, jsonify
from transformers import pipeline
import re
from tqdm import tqdm

app = Flask(__name__)

summarizer = pipeline('summarization')


def processing(result):
    global summarized_text

    def clean_text(text):
        # Remove extra spaces and spaces before punctuation
        cleaned_text = re.sub(r'\s+', ' ', text)
        cleaned_text = re.sub(r'\s([.,;!?])', r'\1', cleaned_text)
        return cleaned_text.strip()

    def remove_bracketed_words(text):
        # Remove words enclosed in square brackets including the brackets
        cleaned_text = re.sub(r'\[.*?\]', '', text)
        return cleaned_text

    def summarize(text):
        num_iters = int(len(text) / 1000)
        summarized_text1 = []

        for i in tqdm(range(num_iters + 1), desc="Summarizing"):
            start = i * 1000
            end = (i + 1) * 1000
            out = summarizer(text[start:end])  # Implement your summarization logic here
            out = out[0]['summary_text']
            cleaned_out = remove_bracketed_words(out)  # Remove words and brackets
            cleaned_out = clean_text(cleaned_out)  # Clean extra spaces and irregularities
            summarized_text1.append(cleaned_out)

        # Convert the list of cleaned summarized texts into a single string
        combined_cleaned_summarized_text = ' '.join(summarized_text1)

        return combined_cleaned_summarized_text

    # for i in range(value):
    summarized_text = summarize(result)

    # Adding bullet points after specific ends of paragraphs
    bullet_pointed_text = re.sub(r'([.?!"\'\n])\s+', r'\1\n• ', summarized_text)
    bullet_pointed_text = bullet_pointed_text.replace('• ', '\n• ')

    return bullet_pointed_text


@app.route('/summarize', methods=['POST'])
def summarize_route():  # Rename the route handler to avoid conflict
    try:
        text = str(request.form.get('text'))

        final_summary = processing(text)
        return jsonify({'summary_final': final_summary})

    except Exception as e:
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
