# skills/web_search.py — Web Search
import requests

def search_web(query):
    try:
        # DuckDuckGo instant answer
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }
        r = requests.get(url, params=params, timeout=5)
        data = r.json()

        if data.get("AbstractText"):
            return data["AbstractText"][:400]

        if data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"][:400]

        # Fallback to Google search
        try:
            from googlesearch import search
            results = list(search(query, num_results=3))
            if results:
                return f"Here's what I found for {query}: {results[0]}"
        except:
            pass

        return f"I searched for {query} but couldn't pull a clear result. Try rephrasing."

    except Exception as e:
        return f"Search failed: {e}"