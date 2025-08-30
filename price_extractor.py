# Price extraction module for Flask app
import asyncio, re, json
from playwright.async_api import async_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

PRICE_RE = re.compile(r'(?:£|\$|€)\s?[0-9][0-9\.,]*')

async def goto_resilient(page, url: str, base_timeout=60000):
    # 1) fastest and most reliable on many sites
    await page.goto(url, wait_until="domcontentloaded", timeout=base_timeout)
    # 2) try to progress the state (don't fail the whole call)
    for state in ("load", "networkidle"):
        try:
            await page.wait_for_load_state(state, timeout=8000)
            break
        except Exception:
            pass

async def extract_price_from_jsonld(page):
    scripts = await page.locator('script[type="application/ld+json"]').all_inner_texts()
    for s in scripts:
        try:
            data = json.loads(s)
        except Exception:
            continue
        stack = data if isinstance(data, list) else [data]
        for obj in stack:
            if not isinstance(obj, dict):
                continue
            if "@graph" in obj and isinstance(obj["@graph"], list):
                stack.extend(obj["@graph"])
            if obj.get("@type") in ("Product", "Offer", "AggregateOffer"):
                offers = obj.get("offers", obj if "price" in obj else None)
                if isinstance(offers, list):
                    offers = offers[0] if offers else None
                if isinstance(offers, dict):
                    price = offers.get("price")
                    if price:
                        return str(price)
    return None

async def get_price(url, selector=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(user_agent=UA, locale="en-GB")
        page = await ctx.new_page()

        # one retry with different strategy
        for attempt in (1, 2):
            try:
                await goto_resilient(page, url, base_timeout=70000 if attempt == 1 else 90000)

                # try dismiss simple cookie banners (best-effort)
                for text in ["Accept all", "I agree", "Accept", "Allow all", "Accept Cookies"]:
                    try:
                        loc = page.get_by_text(text, exact=False)
                        if await loc.count() > 0:
                            await loc.first.click(timeout=1500)
                            break
                    except Exception:
                        pass

                # 1) JSON-LD
                raw = await extract_price_from_jsonld(page)
                if raw:
                    return raw

                # 2) explicit selector if provided
                if selector:
                    try:
                        el = page.locator(selector).first
                        await el.wait_for(timeout=5000)
                        txt = await el.inner_text()
                        if txt and PRICE_RE.search(txt):
                            return txt
                    except Exception:
                        pass

                # 3) price-ish elements
                for sel in [
                    ".price", ".product-price", ".woocommerce-Price-amount", ".amount",
                    "[itemprop='price']", "[data-price]"
                ]:
                    try:
                        el = page.locator(sel).first
                        if await el.count() > 0:
                            txt = await el.inner_text()
                            if txt and PRICE_RE.search(txt):
                                return txt
                    except Exception:
                        pass

                # 4) raw HTML scan
                html = await page.content()
                m = PRICE_RE.search(html)
                if m:
                    return m.group(0)

            except Exception as e:
                if attempt == 2:
                    raise
            # small backoff then retry
            await asyncio.sleep(1.2)

        await browser.close()
        return None