import PySimpleGUI as sg
import requests
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# 画像をリサイズする関数
def resize_image(input_image_path, output_image_path, size):
    original_image = Image.open(input_image_path)
    resized_image = original_image.resize(size)
    resized_image.save(output_image_path)

# 画像のリサイズ
resize_image('./images/play.png', './images/play_resized.png', (70, 50))
resize_image('./images/maid.png', './images/maid_resized.png', (300, 300))

# 環境変数からAPP_KEYを取得する
APP_KEY = os.getenv('APP_KEY')

URL = "https://acp-api.amivoice.com/v1/recognize"

# 認識対象の音声ファイルパス
AUDIO_FILE = "test.wav"

def play_action():
    # 音声ファイルを開く
    with open(AUDIO_FILE, "rb") as f:
        audio_data = f.read()

    # リクエストのパラメータを設定
    params = {
        "d": "-a-general"
    }
    files = {
        "u": (None, APP_KEY),
        "a": ("test.wav", audio_data)
    }

    # POSTリクエストを送信
    response = requests.post(URL, params=params, files=files)

    # レスポンスを処理
    if response.status_code == 200:
        result = response.json()
        return result["text"]
    else:
        return "エラー: " + response.text

# レイアウト
layout = [
    [
        sg.Frame('AIメイド', layout=[
            [sg.Image(filename='./images/maid_resized.png', key='-IMAGE-')],
            [sg.Multiline(size=(50, 10), key='-LOG-', autoscroll=True, disabled=True)]
        ]),
        sg.Column([
            [sg.Button(image_filename='./images/play_resized.png', key='-PLAY-', enable_events=True, border_width=0, pad=(20, 0))]
        ])
    ]
]

# ウィンドウ作成
window = sg.Window('再生ボタンと停止ボタン', layout)

# イベントループ
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == '-PLAY-':
        print('再生ボタンがクリックされました')
        # Curlプロセスを実行
        result_text = play_action()
        window['-LOG-'].print(result_text)

window.close()
