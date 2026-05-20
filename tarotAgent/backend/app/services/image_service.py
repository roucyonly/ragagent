import os

from jinja2 import Environment, FileSystemLoader

from app.config import settings

env = Environment(loader=FileSystemLoader(settings.TEMPLATES_DIR))


async def generate_share_image(reading_id: str, reading_data: dict, user_data: dict) -> str:
    template = env.get_template("reading_card.html")
    html_content = template.render(
        user_name=user_data.get("name", "神秘访客"),
        topic=reading_data.get("topic_name", ""),
        cards=reading_data.get("cards_drawn", []),
        brief=reading_data.get("brief_reading", ""),
        detail_summary=reading_data.get("detailed_reading", "")[:200] if reading_data.get("detailed_reading") else "",
        date=reading_data.get("created_at", ""),
    )

    output_dir = os.path.join(settings.STATIC_DIR, "generated")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{reading_id}.png")

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={"width": 375, "height": 800})
            await page.set_content(html_content, wait_until="networkidle")
            await page.screenshot(path=output_path, full_page=True)
            await browser.close()
    except Exception as e:
        html_path = os.path.join(output_dir, f"{reading_id}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        raise RuntimeError(f"Image generation failed, HTML saved to {html_path}: {e}")

    return f"/static/generated/{reading_id}.png"
