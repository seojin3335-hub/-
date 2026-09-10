import json
import os
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

def youtube_get(path, params):
    params = dict(params)
    params["key"] = YOUTUBE_API_KEY
    url = "https://www.googleapis.com/youtube/v3/" + path + "?" + urlencode(params)
    req = Request(url, headers={"User-Agent": "AI-Travel-Video-Finder/0.1"})
    with urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def parse_duration(value):
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value or "")
    if not m:
        return ""
    h, mi, s = [int(x or 0) for x in m.groups()]
    if h:
        return f"{h}:{mi:02d}:{s:02d}"
    return f"{mi}:{s:02d}"

def score_video(title, description, views, topic):
    text = (title + " " + description).lower()
    words = [w for w in re.findall(r"[0-9A-Za-z가-힣ぁ-んァ-ン一-龯]+", topic.lower()) if len(w) > 1]
    matches = sum(1 for w in words if w in text)
    relevance = min(100, 45 + matches * 18)
    popularity = min(100, int((max(views, 0) ** 0.5) / 100))
    return min(100, int(relevance * 0.7 + popularity * 0.3))

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/search")
def search():
    if not YOUTUBE_API_KEY:
        return jsonify({
            "ok": False,
            "error": "YOUTUBE_API_KEY가 설정되지 않았습니다."
        }), 500

    topic = request.args.get("topic", "").strip()
    language = request.args.get("language", "ko").strip() or "ko"
    max_results = min(max(int(request.args.get("max_results", "10")), 1), 25)

    if not topic:
        return jsonify({"ok": False, "error": "검색 주제를 입력하세요."}), 400

    try:
        search_data = youtube_get("search", {
            "part": "snippet",
            "q": topic,
            "type": "video",
            "maxResults": max_results,
            "relevanceLanguage": language,
            "safeSearch": "moderate",
        })

        ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
        if not ids:
            return jsonify({"ok": True, "items": []})

        video_data = youtube_get("videos", {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(ids),
        })

        items = []
        for v in video_data.get("items", []):
            sn = v.get("snippet", {})
            st = v.get("statistics", {})
            cd = v.get("contentDetails", {})
            views = int(st.get("viewCount", 0))
            title = sn.get("title", "")
            desc = sn.get("description", "")
            items.append({
                "video_id": v["id"],
                "title": title,
                "channel": sn.get("channelTitle", ""),
                "published_at": sn.get("publishedAt", "")[:10],
                "duration": parse_duration(cd.get("duration", "")),
                "views": views,
                "views_text": f"{views:,}",
                "thumbnail": sn.get("thumbnails", {}).get("medium", {}).get("url", ""),
                "url": f"https://www.youtube.com/watch?v={v['id']}",
                "score": score_video(title, desc, views, topic),
            })

        items.sort(key=lambda x: (x["score"], x["views"]), reverse=True)
        return jsonify({"ok": True, "topic": topic, "items": items})

    except HTTPError as e:
        try:
            detail = e.read().decode("utf-8")
        except Exception:
            detail = str(e)
        return jsonify({"ok": False, "error": f"YouTube API 오류: {detail}"}), 502
    except (URLError, TimeoutError) as e:
        return jsonify({"ok": False, "error": f"네트워크 오류: {e}"}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": f"서버 오류: {e}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
