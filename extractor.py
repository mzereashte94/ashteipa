import json
import requests

CHECK0VER_SOURCE = "https://check0ver.site/repo.json"

def fetch_check0ver():
    try:
        response = requests.get(CHECK0VER_SOURCE, timeout=30)
        if response.status_code == 200:
            data = response.json()
            with open("apps.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"سەرکەوتوو بوو! ئەپەکانی Check0ver خرانە ناو apps.json")
        else:
            print(f"هەڵە لە وەڵام: {response.status_code}")
    except Exception as e:
        print(f"کێشە لە پەیوەندی: {e}")

if __name__ == "__main__":
    fetch_check0ver()
