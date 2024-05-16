import PySimpleGUI as sg
from PIL import Image

# 画像をリサイズする関数
def resize_image(input_image_path, output_image_path, size):
    original_image = Image.open(input_image_path)
    resized_image = original_image.resize(size)
    resized_image.save(output_image_path)

# 画像のリサイズ
resize_image('./images/play.png', './images/play_resized.png', (70, 50))
resize_image('./images/stop.png', './images/stop_resized.png', (40, 40))
resize_image('./images/maid.png', './images/maid_resized.png', (400, 400))

# レイアウト
layout = [
    [sg.Image(filename='./images/maid_resized.png', key='-IMAGE-')],
    [sg.Image(filename='./images/play_resized.png', key='-PLAY-', enable_events=True), 
     sg.Image(filename='./images/stop_resized.png', key='-STOP-', enable_events=True)]
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
    elif event == '-STOP-':
        print('停止ボタンがクリックされました')

window.close()
