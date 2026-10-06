import json
import re
import requests
from datetime import datetime

# APIی فەرمیی ماڵپەڕی IPAOMTK بۆ دەرهێنانی پۆست و ئەپەکان
WP_API_URL = "https://ipaomtk.com/wp-json/wp/v2/posts"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
}

def extract_ipaomtk():
    apps = []
    seen_urls = set()
    page = 1

    print("دەستکرا بە هێنانی ئەپ و یارییە فەرمییەکانی IPAOMTK...")

    while True:
        try:
            params = {
                "per_page": 50,
                "page": page
            }
            res = requests.get(WP_API_URL, headers=HEADERS, params=params, timeout=20)
            
            if res.status_code != 200:
                break
                
            posts = res.json()
            if not posts or not isinstance(posts, list):
                break

            for post in posts:
                content = post.get("content", {}).get("rendered", "")
                title = post.get("title", {}).get("rendered", "App")
                
                # پاککردنەوەی ناوی ئەپەکە لە کۆدی HTML
                clean_name = re.sub(r'<[^>]+>', '', title).strip()

                # دۆزینەوەی لینکی داگرتن لەسەر سێرڤەری file.ipaomtk.com
                ipa_links = re.findall(r'https?://file\.ipaomtk\.com/[^\s"\'<>]+\.ipa', content)
                
                if not ipa_links:
                    # ئەگەر ناونیشانی تری هەبوو کە بە .ipa تەواو دەبێت
                    ipa_links = re.findall(r'https?://[^\s"\'<>]+\.ipa', content)

                for link in ipa_links:
                    if link in seen_urls:
                        continue
                    seen_urls.add(link)

                    # دۆزینەوەی ئایکۆنی وێنەی ئەپەکە
                    img_match = re.search(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', content)
                    icon = img_match.group(1) if img_match else "https://ipaomtk.com/favicon.ico"

                    bundle_id = "com.ipaomtk." + re.sub(r'[^a-zA-Z0-9]', '', clean_name).lower()

                    apps.append({
                        "name": clean_name,
                        "bundleIdentifier": bundle_id,
                        "developerName": "IPAOMTK",
                        "version": "1.0",
                        "versionDate": datetime.now().strftime("%Y-%m-%d"),
                        "downloadURL": link,
                        "localizedDescription": f"{clean_name} - فەرمی لە IPAOMTK",
                        "iconURL": icon,
                        "size": 0
                    })

            print(f"پەڕەی {page} تەواو بوو. کۆی گشتی تا ئێستا: {len(apps)}")
            page += 1

            # دەتوانیت ژمارەی پەڕەکان دیاری بکەیت (لێرەدا تا 5 پەڕە وەردەگرێت بۆ خێرایی)
            if page > 5:
                break

        except Exception as e:
            print(f"کێشە لە پەڕەی {page}: {e}")
            break

    # فۆرماتی تایبەتی ستانداردی AltStore / Feather
    repo_data = {
        "name": "IPAOMTK Apps",
        "identifier": "com.ipaomtk.repo",
        "apps": apps
    }

    with open("apps.json", "w", encoding="utf-8") as f:
        json.dump(repo_data, f, ensure_ascii=False, indent=2)

    print(f"سەرکەوتوو بوو! بەستەری تەواوی {len(apps)} ئەپی ڕاستەقینەی IPAOMTK تۆمار کرا.")

if __name__ == "__main__":
    extract_ipaomtk()
