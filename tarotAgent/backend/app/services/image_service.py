import asyncio
import markdown
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
            sections.append({"label": "✦ 引言 ✦", "content": markdown.markdown(parts[0].strip())})
        else:
            return [{"label": "✦ 完整解读 ✦", "content": markdown.markdown(detail_text)}]
    for i in range(1, len(parts) - 1, 2):
        header = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        sections.append({"label": f"✦ {header} ✦", "content": markdown.markdown(content)})
    return sections if sections else [{"label": "✦ 完整解读 ✦", "content": markdown.markdown(detail_text)}]


def _render_image(html_content: str, output_path: str):
    """Synchronous Playwright call, runs in a thread."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 375, "height": 1200})
        page.set_content(html_content, wait_until="networkidle")
        page.screenshot(path=output_path, full_page=True, type="jpeg", quality=90)
        browser.close()


def _upload_to_oss(local_path: str, object_key: str) -> str:
    import oss2

    auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)
    bucket.put_object_from_file(
        object_key, local_path,
        headers={'Content-Type': 'image/jpeg', 'x-oss-object-acl': 'public-read'},
    )

    if settings.OSS_CDN_DOMAIN:
        return f"https://{settings.OSS_CDN_DOMAIN}/{object_key}"
    return f"https://{settings.OSS_BUCKET_NAME}.{settings.OSS_ENDPOINT}/{object_key}"


async def generate_share_image(reading_id: str, reading_data: dict, user_data: dict) -> str:
    cards = []
    for card in reading_data.get("cards_drawn", []):
        cards.append({
            "name_cn": card.get("name_cn", "?"),
            "position_label": POSITION_LABELS.get(card.get("position", ""), card.get("position", "")),
            "is_reversed": card.get("is_reversed", False),
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
        user_name=user_data.get("nickname") or user_data.get("name") or "神秘访客",
        topic=reading_data.get("topic_name", ""),
        cards=cards,
        brief=brief_text[:300] + ("..." if len(brief_text) > 300 else ""),
        sections=sections,
        date_display=date_str[:10] if len(date_str) >= 10 else date_str,
    )

    output_dir = os.path.join(settings.STATIC_DIR, "generated")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{reading_id}.jpg")

    await asyncio.to_thread(_render_image, html_content, output_path)

    # Always upload to OSS
    object_key = f"tarot/{reading_id}.jpg"
    image_url = await asyncio.to_thread(_upload_to_oss, output_path, object_key)
    # Clean up local temp file
    try:
        os.remove(output_path)
    except OSError:
        pass
    return image_url
