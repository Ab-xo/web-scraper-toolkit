"""
Groq LLM client — structured extraction plan with container + field selectors.
"""
from __future__ import annotations
import json
import httpx
from app.config import settings

SYSTEM_PROMPT = """\
You are an expert web scraping AI. You receive:
1. The DOM structure of a webpage (tag names + classes/ids)
2. The visible text content of the page
3. ALL links on the page with their exact text and href values
4. A user's plain-English extraction intent

Your job: return a precise JSON extraction plan.

CRITICAL RULES:
- "container": CSS selector for ONE repeating item (one book, one quote, one product row)
- "fields": selectors RELATIVE to each container element. Use "self" to extract the container's own text.
- "follow_url": MUST be copied EXACTLY from the "ALL LINKS" section — never invent URLs.
  Only set this when the user asks for content that lives on a different page (e.g. a category).
  Use the EXACT href from the links list. Never guess or construct URLs.
- If all needed content is on the current page, set follow_url to null.
- Return ONLY raw JSON. No markdown. No code fences. No explanation.

FIELD SELECTOR TIPS:
- For book titles on toscrape: "h3 a" (has title attribute with full name)
- For prices: ".price_color"
- For star ratings: ".star-rating" (class contains the rating word e.g. "star-rating Three")
- For availability: ".availability"
- For quote text: ".text" or "span.text"
- For quote author: ".author" or "small.author"

RESPONSE FORMAT (strict JSON):
{
  "container": "<css selector>",
  "fields": {"field_name": "<relative css selector or 'self'>"},
  "follow_url": null,
  "summary": "<one sentence describing what will be extracted>"
}

EXAMPLES:

Intent: "find all books"
{
  "container": "article.product_pod",
  "fields": {"title": "h3 a", "price": ".price_color", "rating": ".star-rating"},
  "follow_url": null,
  "summary": "Extracting title, price and rating for all books on this page."
}

Intent: "get all quotes and authors"
{
  "container": "div.quote",
  "fields": {"quote": "span.text", "author": "small.author", "tags": "div.tags"},
  "follow_url": null,
  "summary": "Extracting quote text, author name and tags for all quotes."
}

Intent: "find all travel books" (when Travel link exists in links section)
{
  "container": "article.product_pod",
  "fields": {"title": "h3 a", "price": ".price_color", "rating": ".star-rating"},
  "follow_url": "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
  "summary": "Navigating to Travel category page and extracting all travel books."
}

Intent: "show all navigation links"
{
  "container": "nav ul li",
  "fields": {"text": "self"},
  "follow_url": null,
  "summary": "Extracting all navigation menu items."
}
"""


async def ask_groq(skeleton: str, intent: str) -> dict:
    """Returns extraction plan: {container, fields, follow_url, summary}"""
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is not configured")

    payload = {
        "model": settings.ai_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Page content:\n{skeleton}\n\nUser intent: {intent}"},
        ],
        "temperature": 0.0,
        "max_tokens": 600,
    }

    async with httpx.AsyncClient(timeout=25.0) as client:
        response = await client.post(
            f"{settings.ai_base_url}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {settings.groq_api_key}", "Content-Type": "application/json"},
        )
        if not response.is_success:
            raise ValueError(f"Groq API error {response.status_code}: {response.text[:500]}")

    try:
        content = response.json()["choices"][0]["message"]["content"].strip()
        # strip markdown fences if model adds them
        if content.startswith("```"):
            content = content.split("```")[1].lstrip("json").strip()
        plan = json.loads(content)
        return {
            "container":  str(plan.get("container", "")).strip(),
            "fields":     plan.get("fields") or {"text": "self"},
            "follow_url": plan.get("follow_url") or None,
            "summary":    str(plan.get("summary", "")).strip(),
        }
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unexpected LLM response: {exc}") from exc
