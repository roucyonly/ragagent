import asyncio
import os
import re

from jinja2 import Environment, FileSystemLoader

from app.config import settings

env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))

POSITION_LABELS = {"past": "过去", "present": "现在", "future": "未来"}


def _parse_sections(detail_text: str) -> list[dict]:
    if not detail_text:
        return []
    parts = re.split(r'【([^】]+)】', detail_text)
    sections = []
    if parts and parts[0].strip():
        if len(parts) >= 2:
            sections.append({"label": "✦ 引言 ✦", "content": parts[0].strip()})
        else:
            return [{"label": "✦ 完整解读 ✦", "content": detail_text}]
    for i in range(1, len(parts) - 1, 2):
        header = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        sections.append({"label": f"✦ {header} ✦", "content": content})
    return sections if sections else [{"label": "✦ 完整解读 ✦", "content": detail_text}]


def _render_image(html_content: str, output_path: str):
    """Synchronous Playwright call, runs in a thread."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 375, "height": 1200})
        page.set_content(html_content, wait_until="networkidle")
        page.screenshot(path=output_path, full_page=True)
        browser.close()


async def generate_share_image(reading_id: str, reading_data: dict, user_data: dict) -> str:
    cards = []
    for card in reading_data.get("cards_drawn", []):
        cards.append({
            "name_cn": card.get("name_cn", "?"),
            "position_label": POSITION_LABELS.get(card.get("position", ""), card.get("position", "")),
        })

    brief_text = reading_data.get("brief_reading", "") or ""
    detail_text = reading_data.get("detailed_reading", "") or ""
    date_str = reading_data.get("created_at", "") or ""

    sections = []
    if detail_text:
        sections = _parse_sections(detail_text)
    elif brief_text:
        sections = [{"label": "✦ 简要解读 ✦", "content": brief_text}]

    template = env.get_template("reading_card.html")
    html_content = template.render(
        user_name=user_data.get("name") or "神秘访客",
        topic=reading_data.get("topic_name", ""),
        cards=cards,
        brief=brief_text[:300] + ("..." if len(brief_text) > 300 else ""),
        sections=sections,
        date_display=date_str[:10] if len(date_str) >= 10 else date_str,
    )

    output_dir = os.path.join(settings.STATIC_DIR, "generated")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{reading_id}.png")

    await asyncio.to_thread(_render_image, html_content, output_path)

    return f"/static/generated/{reading_id}.png"
