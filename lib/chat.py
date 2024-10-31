import os
import requests
from contextlib import suppress
from bs4 import BeautifulSoup
from groq import Groq

class AIChatLibrary:
    def __init__(self):
        # self.console = Console()
        self.system_prompt = "1.使用繁體中文，沒有資料就從英文翻譯 2.使用台灣用語 3.不要過度依賴步驟 4.不要有無意義的字"
        self.client = self.initialize_client()

    def initialize_client(self):
        Groq_api_key = self.get_api_key("Groq_api_key.txt", "首次使用，請輸入您的 Groq API 金鑰 \n Groq API 金鑰可到 https://console.groq.com/keys 申請： ")
        print("Groq API 金鑰為:", Groq_api_key)
        client = Groq(api_key=Groq_api_key)

        api_key = self.get_api_key("google_search_api_key.txt", "首次使用，請輸入您的 Google Search API 金鑰 \n 設定 Google 程式化搜尋引擎--> https://programmablesearchengine.google.com/controlpanel/all： ")
        print("Google Search API 金鑰為:", api_key)

        cse_id = self.get_api_key("cse_id.txt", "請輸入您的Google Search cse_id \n 由Google 程式化搜尋引擎介面複製： ")
        print("Google Search cse_id 為:", cse_id)

        return client, api_key, cse_id

    def get_api_key(self, file_name, prompt):
        if os.path.exists(file_name):
            with open(file_name, "r") as file:
                api_key = file.read().strip()
            print(f"{file_name} 已載入。")
        else:
            api_key = input(prompt)
            with open(file_name, "w") as file:
                file.write(api_key)
            print(f"{file_name} 已儲存。")
        return api_key

    def making_todo(self, input_text):
        making_todo = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "1. Create a problem-solving process 2. Develop a solution plan" + {input_text},
                }
            ],
            model="gemma-7b-it",
            max_tokens=8192,
        )
        return making_todo.choices[0].message.content

    def chat(self, todo_sept, input_text, text_list):
        chat = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": self.system_prompt + todo_sept + input_text + "".join(text_list),
                }
            ],
            model="llama-3.2-90b-vision-preview",
            max_tokens=8192,
        )
        return chat.choices[0].message.content

    def whether_search(self, input_text):
        whether_search = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Analyze whether the following text needs to be searched on the Internet. If it is necessary, output 1, and if it is not necessary, output 0." + "'" + input_text + "'",
                },
            ],
            model="gemma2-9b-it",
            max_tokens=8192,
        )
        return whether_search.choices[0].message.content == "0"

    def google_search(self, query):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": self.api_key,
            "cx": self.cse_id
        }
        response = requests.get(url, params=params)
        return response.json()

    def google_search_keyword(self, input_text):
        response = self.client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[
                {
                    "role": "user",
                    "content": "Give me keywords to search on google '" + {input_text} + "'",
                }
            ],
            max_tokens=8192,
        )
        return response.choices[0].message.content

    def webpage2text(self, keywords):
        results = self.google_search(keywords)
        webpage_text_list = []
        for i in range(min(3, len(results.get("items", [])))):
            try:
                url = results["items"][i]["link"]
                response = requests.get(url)
                response.encoding = "utf-8"
                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()
                webpage_text = soup.get_text(separator="\n").strip()
                webpage_text_list.append(webpage_text)
            except Exception:
                with suppress(Exception):
                    pass  # Silence any exceptions

    def whether_making_todo(self, input_text):
        whether_making_todo = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Analyze whether the following text needs to make todo. If it is necessary, output 1, and if it is not necessary, output 0." + "'" + input_text + "'",
                },
            ],
            model="gemma2-9b-it",
            max_tokens=8192,
        )
        return whether_making_todo.choices[0].message.content == "0"

    def log(self, reply):
        with open('example.txt', 'w', encoding='utf-8') as file:
            file.write(reply + "\n\n")
