import cv2
import time
from chat import AIChatLibrary
from image_clean_up import ImageCleanUp
from flask import Flask, jsonify, request

local_time = time.localtime()  # 獲取當前本地時間
formatted_time = time.strftime("%Y-%m-%d-%H:%M:%S", local_time)  # 格式化時間

app = Flask(__name__)
ai_chat = AIChatLibrary()
cleaner = ImageCleanUp()

text = ""
image = None  # 初始化 `image` 變數為 None
num = 1

system_prompt = "1.使用繁體中文，沒有資料就從英文翻譯 2.使用台灣用語 3.不要過度依賴步驟 4.不要有無意義的字"

@app.route('/server/user/input', methods=['POST'])  # 確認路徑正確
def upload_data():
    global input_text, input_image  # 指定變更全域變數
    
    # 取得請求中的 JSON 資料
    data = request.json
    
    # 從請求中提取 `text` 與 `image`
    input_text = data.get('text')
    input_image = data.get('image')
    
    # 處理圖片
    if input_image:
        result_image = image_clean_up()
        image_response = {"image": result_image}
        return jsonify(image_response), 200
        
    # 處理文字
    if input_text:
        result_text = generate_text()
        text_response = {"text": result_text}
        return jsonify(text_response), 200
    
    # 如果沒有輸入則回傳錯誤
    return jsonify({"error": "未提供任何輸入"}), 400

def image_clean_up():
    # 計數
    file_name = formatted_time + num + ".jpg"
    num = num + 1

    # 讀取圖片
    image_data = input_image
    
    # 處理圖片
    result = cleaner.process_image(image_data)        
    
    # 儲存結果
    cv2.imwrite(file_name, result)
    image_reply = cv2.imwrite()         # 回傳

def generate_text():    
    # input_text = input("你的問題?")
    using_todo = ai_chat.whether_making_todo(input_text)
    using_google = ai_chat.whether_search(input_text)

    if not using_todo:
        todo_sept = ai_chat.making_todo(input_text)
    else:
        todo_sept = ""

    if not using_google:
        search_keyword = ai_chat.google_search_keyword(input_text)
        text_list = ai_chat.webpage2text(search_keyword)
        reply = ai_chat.chat(todo_sept, input_text, text_list)
        ai_chat.log(reply)
        print(reply)  # 使用 print 代替 console.print
    else:
        reply = ai_chat.chat(todo_sept, input_text, [])
        ai_chat.log(reply)
        print(reply)  # 使用 print 代替 console.print

if __name__ == '__main__':
    app.run(debug=True)

# pip install lama-cleaner