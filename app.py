import os
import cv2
import sys
import time
import configparser
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
from chat import AIChatLibrary
from image_clean_up import ImageCleanUp
from flask import Flask, jsonify, request, render_template, redirect, url_for

# 初始化 Flask 應用程式和所需的類別
app = Flask(__name__)
config = configparser.ConfigParser()

# 全域變數
input_text = ""        # 使用者輸入的文字
input_image = None     # 使用者上傳的圖片
num = 1               # 圖片計數器

def admin_account_password():
    config.read('set\key.ini')
    admin_account = config['account']['account-admin']
    admin_password = config['password']['password-admin']
    return admin_account, admin_password

@app.route('/login', methods=['GET', 'POST'])
def login(admin_account, admin_password):
    if request.method == 'POST':
        admin_account_password()
        username = request.values.get('account')
        password = request.values.get('password')
        if username == admin_account and password == admin_password:
            return redirect(url_for('setting'))
    return render_template('login.html')

@app.route('/setting')
def setting():
    if request.method == 'POST':
        groq_api = request.values.get("groq_api")
        google_api = request.values.get("groq_api")
        cse_id = request.values.get("groq_api")
        system_prompt = request.values.get("system_prompt")
    else:
        return render_template('setting.html')
    return groq_api, google_api, cse_id, system_prompt

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/server/user/input', methods=['POST'])
def upload_data():
    """
    處理使用者上傳的資料
    接受 POST 請求，可處理文字或圖片輸入
    回傳處理結果的 JSON 回應
    """
    global input_text, input_image
    
    # 取得請求中的 JSON 資料
    data = request.json
    
    # 從請求中提取文字與圖片，並進行相應處理
    if (input_text := data.get('text')) or (input_image := data.get('image')):
        result_image = image_clean_up()
        image_response = {"image": result_image}
        return jsonify(image_response), 200
        
    # 處理純文字輸入
    if input_text:
        result_text = generate_text()
        text_response = {"text": result_text}
        return jsonify(text_response), 200
    
    # 若無任何輸入則回傳錯誤
    return jsonify({"error": "未提供任何輸入"}), 400

def image_clean_up():
    """
    處理圖片的函式
    1. 生成唯一的檔名
    2. 處理圖片
    3. 儲存並回傳處理後的圖片
    """
    global num
    # 產生時間戳記的檔名
    local_time = time.localtime()
    formatted_time = time.strftime("%Y-%m-%d-%H:%M:%S", local_time)
    file_name = f"{formatted_time}_{num}.jpg"
    num += 1

    # 讀取並處理圖片
    image_data = cv2.imdecode(input_image, cv2.IMREAD_COLOR)
    result = ImageCleanUp.process_image(image_data)
    
    # 儲存處理後的圖片並回傳
    cv2.imwrite(file_name, result)
    _, buffer = cv2.imencode('.jpg', result)
    return buffer.tobytes()

def generate_text():
    """
    處理文字的函式
    1. 判斷是否需要生成待辦事項
    2. 判斷是否需要搜尋網路資料
    3. 生成回應並記錄
    """
    # 判斷是否需要處理代辦事項或 Google 搜尋
    using_todo = AIChatLibrary.whether_making_todo(input_text)
    using_google = AIChatLibrary.whether_search(input_text)

    # 根據需求生成待辦事項和搜尋關鍵字
    todo_sept = "" if using_todo else AIChatLibrary.making_todo(input_text)
    search_keyword = "" if using_google else AIChatLibrary.google_search_keyword(input_text)

    
    # 取得網頁內容並生成回應
    text_list = AIChatLibrary.webpage2text(search_keyword) if search_keyword else []
    reply = AIChatLibrary.chat(todo_sept, input_text, text_list)
    AIChatLibrary.log(reply)
    
    return reply

if __name__ == '__main__':
    app.run(debug=True)
