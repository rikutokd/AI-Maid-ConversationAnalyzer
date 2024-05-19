import PySimpleGUI as sg
import requests
import os
import time
import MeCab
import ipadic

from gensim.models import Word2Vec
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# OpenAI APIのエンドポイント
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 形態素解析器の初期化
tagger = MeCab.Tagger(ipadic.MECAB_ARGS)

# 画像をリサイズする関数
def resize_image(input_image_path, output_image_path, size):
    original_image = Image.open(input_image_path)
    resized_image = original_image.resize(size)
    resized_image.save(output_image_path)

# テキストを形態素解析して単語に分割する関数
def tokenize(text):
    words = []
    node = tagger.parseToNode(text)
    while node:
        if node.feature.split(',')[0] == '名詞':  # 名詞のみを抽出する例
            words.append(node.surface)
        node = node.next
    return words

# ChatGPT APIへのリクエストを送信する関数
def get_chatgpt_response(text):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-2024-05-13",
        "messages": [
            {"role": "system", "content": "You are the maid. Your answers will always be returned in Japanese. You will return in the first person as “私”."},
            {"role": "user", "content": text}
        ]
    }
    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    response_data = response.json()
    if response.status_code == 200:
        return response_data['choices'][0]['message']['content']
    else:
        return f"Error: {response_data.get('error', {}).get('message', 'Unknown error')}"

# 音声認識APIの設定
APP_KEY = os.getenv('APP_KEY')
URL = "https://acp-api.amivoice.com/v1/recognize"
AUDIO_FILE = "test.wav"

def play_action():
    # 音声ファイルを開く
    with open(AUDIO_FILE, "rb") as f:
        audio_data = f.read()

    # リクエストのパラメータを設定
    params = {"d": "-a-general"}
    files = {"u": (None, APP_KEY), "a": ("test.wav", audio_data)}

    # POSTリクエストを送信
    response = requests.post(URL, params=params, files=files)
    if response.status_code == 200:
        result = response.json()
        result_text = result["text"]
        return result_text
    else:
        return f"Error: {response.status_code}"

def analyze_response(response_text, window):
    # 形態素解析して単語に分割
    words = tokenize(response_text)
    # Word2Vecモデルの学習
    model = Word2Vec([words], vector_size=100, window=5, min_count=1, workers=4)
    # 類似語を取得
    similar_words = model.wv.most_similar(words[0])
    # 類似語毎に改行して表示
    similar_words_text = '\n'.join([f"{word}: {similarity}" for word, similarity in similar_words])

    # ユーザのテキストデータのベクトル表現を取得
    user_vectors = [model.wv[word] for word in words]
    # ベクトルの平均化
    average_vector = sum(user_vectors) / len(user_vectors)
    # 平均ベクトルから類似する単語を取得
    average_similar_words = model.wv.most_similar([average_vector])
    # 解析ログを更新（平均化した類似語の一番上だけ表示）
    average_similar_word_text = f"{average_similar_words[0][0]}: {average_similar_words[0][1]}"
    window['-analyze_LOG-'].update(value=f"音声の類似語:\n{similar_words_text}\n\n平均化した類似語:\n{average_similar_word_text}\n")

# 一文字ずつ表示する関数
def display_text_slowly(window, key, text, delay=0.05):
    for char in text:
        window[key].update(value=window[key].get() + char)
        time.sleep(delay)
        window.refresh()

# GUIのレイアウト
layout = [
    [
        sg.Frame('AIメイド', layout=[
            [sg.Image(filename='./images/maid_resized.png', key='-IMAGE-')],
            [sg.Multiline(size=(40, 10), key='-LOG-', autoscroll=True, disabled=True)]
        ]),
        sg.Frame('あなた', layout=[
            [sg.Multiline(size=(40, 29), key='-YOUR_LOG-', autoscroll=True, disabled=True)]
        ]),
        sg.Frame('解析結果', layout=[
            [sg.Multiline(size=(35, 29), key='-analyze_LOG-', autoscroll=True, disabled=True)]
        ]),
        sg.Column([
            [sg.Button(image_filename='./images/play_resized.png', key='-PLAY-', enable_events=True, border_width=0, pad=(20, 0))]
        ])
    ]
]

# ウィンドウ作成
window = sg.Window('AIメイド', layout)

# イベントループ
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == '-PLAY-':
        print('再生ボタンがクリックされました')
        # 音声認識を実行してテキストを取得
        result_text = play_action()
        # テキストを「あなた」のログに一文字ずつ表示
        display_text_slowly(window, '-YOUR_LOG-', result_text + '\n')
        # ChatGPTにテキストを送信して応答を取得
        chatgpt_response = get_chatgpt_response(result_text)
        # 応答をログに一文字ずつ表示（リクエストテキストを除く）
        display_text_slowly(window, '-LOG-', chatgpt_response + '\n')
        # 音声分析の結果を表示
        analyze_response(result_text, window)
        window.refresh()

window.close()
