import json
import requests

SOURCES = [
    "https://check0ver.site/repo.json",
    "https://raw.githubusercontent.com/swaggyP36000/TrollStore-IPAs/main/apps.json"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15"
}

def main():
    repo_data = None

    for url in SOURCES:
        try:
            print(f"داواکاری بۆ: {url}")
            res = requests.get(url, headers=HEADERS, timeout=25)
            if res.status_code == 200:
                data = res.json()
                if "apps" in data:
                    repo_data = data
                    print("سەرکەوتوو بوو لە هێنانی داتا.")
                    break
        except Exception as e:
            print(f"کێشە لە پەیوەندی: {e}")

    # ئەگەر هیچ وەڵامێک نەبوو، قالبێکی ئامادەکراو دروست دەکات تا فایلەکە بەتاڵ نەبێت
    if not repo_data:
        repo_data = {
            "name": "Check0ver & IPA Apps",
            "identifier": "com.check0ver.repo",
            "apps": []
        }

    # دڵنیابوونەوە لە دروستبوونی فایلی apps.json
    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_data, f, ensure_ascii=False, indent=2)

    print("فایلی apps.json بە سەرکەوتوویی دروست کرا.")

if __name__ == "__main__":
    main()
