from flask import Flask, request, jsonify
import openai
import traceback
from typing import Any, Callable
from openai import OpenAI
import os
from openai import AzureOpenAI
import warnings
import requests
from bs4 import BeautifulSoup
warnings.filterwarnings('ignore', message=".*deprecated.*")

app = Flask(__name__)

client = OpenAI(
  api_key=""
)


def ai_predict(final_text: str, model='gpt-3.5-turbo') -> str:
    """This function uses any ai model to provide an answer based on the text"""

    try:
        response = client.chat.completions.create(
            model=model,
            temperature =0.4,
            messages=[{"role": "user", "content": final_text}],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        traceback.print_exc()
        raise (e)

def retrieve_text_from_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            text = '\n'.join([p.get_text() for p in paragraphs])
            return text
        else:
            print("Failed to retrieve content. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None
    
@app.route('/generate-marketing-content', methods=['POST'])
def generate_marketing_content():
    data = request.json
    topic = data.get('topic')
    format = data.get('format')
     
    prompt = f"For the given format like {format} which is based on this {topic} as the expert in this {topic} for this {format} generate the Content for the same"
    generated_content = ai_predict(prompt)
    return jsonify({'text': generated_content})

@app.route('/answer_Question_based_on_url_content', methods=['POST'])
def generate_answer_from_url():
    data = request.json
    url = data.get('url')
    question = data.get('question')
    text = retrieve_text_from_url(url)
    response = "I don't know the answer."

    prompt = f"You are provided with this text: {text}. As a good reader, read the text properly. Now, answer the following question: {question}. Your answer should be based solely on the content you have read.Don't Include Other Innessary things Other than Answer in Responce and If you don't found the Answer then Return this {response} as Final Answer"
    generated_content = ai_predict(prompt)

    return jsonify({'text': generated_content})

if __name__ == '__main__':
    app.run(debug=True,port = 4000)
