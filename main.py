import os
import json
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.markdown import Markdown
from groq import Groq

console = Console()
system_prompt = "1.使用繁體中文，沒有資料就從英文翻譯 2.使用台灣用語 3.不要過度依賴步驟 4.不要有無意義的字"

client = Groq(api_key="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")
api_key = "AIzaSyCwMYqcZZsvpRqT5rG0n6mOFEpw8IiV3fw"
cse_id = "24ff8ad308a194f43"

def making_todo(input_text):
    # 創建待辦事項
    making_todo = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "1. Create a problem-solving process 2. Develop a solution plan" + input_text,
            }
        ],
        model="gemma-7b-it",
        max_tokens=8192,  # 加上token限制
    )
    todo_sept = making_todo.choices[0].message.content
    return todo_sept

def chat(todo_sept, input_text, text_list):
    # 進行聊天
    chat = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": system_prompt + todo_sept + input_text + "".join(text_list),
            }
        ],
        model="llama-3.2-90b-vision-preview",
        max_tokens=8192,  # 加上token限制
    )
    reply = chat.choices[0].message.content
    return reply

def weather_search(input_text):
    # 檢查是否需要搜尋天氣
    weather_search = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Analyze whether the following text needs to be searched on the Internet. If it is necessary, output 1, and if it is not necessary, output 0." + "'" + input_text + "'",
            },
        ],
        model="gemma2-9b-it",
        max_tokens=8192,  # 加上token限制
    )
    weather_search_reply = weather_search.choices[0].message.content
    weather_search_reply_y_n = weather_search_reply == "0"
    return weather_search_reply_y_n

def google_search(query, api_key, cse_id):
    # 使用 Google API 進行搜尋
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cse_id
    }
    response = requests.get(url, params=params)
    google_search_reply = response.json()
    print(google_search_reply)  # 輸出搜尋結果
    return google_search_reply

def google_search_keyword(input_text):
    # 獲取搜尋關鍵字
    response = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {
                "role": "user",
                "content": "Give me keywords to search on google '" + input_text + "'",
            }
        ],
        max_tokens=8192,  # 加上token限制
    )
    keywords = response.choices[0].message.content
    print(keywords)  # 輸出關鍵字
    search_keyword = keywords
    return search_keyword

def webpage2text(keywords):
    # 將網頁內容轉換為文字
    results = google_search(keywords, api_key, cse_id)
    webpage_text_list = []
    for i in range(min(3, len(results.get("items", [])))):
        try:
            url = results["items"][i]["link"]
            response = requests.get(url)
            response.encoding = "utf-8"
            
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 移除 script 和 style 等不需要的標籤
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 取得乾淨的文字內容，並去掉多餘空白
            webpage_text = soup.get_text(separator="\n").strip()
            webpage_text_list.append(webpage_text)
            
        except Exception as e:
            print(f"處理網頁 {url} 時發生錯誤: {e}")
    
    print(webpage_text_list)  # 檢查清洗後的結果
    return webpage_text_list

def weather_making_todo(input_text):  # 修改為接受 input_text 參數
    # 檢查是否需要創建待辦事項
    weather_making_todo = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Analyze whether the following text needs to make todo. If it is necessary, output 1, and if it is not necessary, output 0." + "'" + input_text + "'",
            },
        ],
        model="gemma2-9b-it",
        max_tokens=8192,  # 加上token限制
    )
    weather_making_todo_reply = weather_making_todo.choices[0].message.content
    weather_making_todo_reply_y_n = weather_making_todo_reply == "0"
    return weather_making_todo_reply_y_n

def log(reply):
    # 將回覆寫入檔案
    with open('example.txt', 'w', encoding='utf-8') as file:
        file.write(reply + "\n\n")    

while True:
    input_text = input("你的問題?")
    using_todo = weather_making_todo(input_text)
    using_google = weather_search(input_text)
    
    if (using_todo == False):
        todo = making_todo(input_text)
    else:
        todo = ""

    if (using_google == False):
        search_keyword = google_search_keyword(input_text)  # 先獲取搜尋關鍵字
        text_list = webpage2text(search_keyword)  # 然後使用關鍵字進行網頁搜尋
        reply = chat(todo, input_text, text_list)
        markdown_text = reply
        log(reply)
        console.print(Markdown(markdown_text))
    else:
        reply = chat(todo, input_text, [])  # 如果不需要搜尋，傳入空列表
        markdown_text = reply
        log(reply)
        console.print(Markdown(markdown_text))