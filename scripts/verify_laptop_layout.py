import asyncio
import json
import subprocess
import time
import urllib.request
import websockets
import os

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

async def test_viewport(width, height):
    port = 9222
    user_data_dir = os.path.join(os.environ.get("TEMP", "."), f"chrome_verify_{width}_{height}")
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--disable-gpu",
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        f"--window-size={width},{height}",
        "http://localhost:4173"
    ]
    proc = subprocess.Popen(cmd)
    try:
        await asyncio.sleep(2)
        # Fetch targets
        req = urllib.request.urlopen(f"http://localhost:{port}/json")
        targets = json.loads(req.read().decode())
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            # Evaluate layout script
            js_code = """
            (() => {
                const topBar = document.querySelector('.header-top-inner');
                const rightTools = document.querySelector('.header-right-tools');
                const brandGroup = document.querySelector('.brand-group');
                const navGrid = document.querySelector('.nav-tabs-grid');
                const tabs = Array.from(document.querySelectorAll('.nav-tab-btn'));
                const master = document.querySelector('.master-container');
                const consentBanner = document.querySelector('.consent-notification-bar');

                const topBarRect = topBar ? topBar.getBoundingClientRect() : null;
                const brandRect = brandGroup ? brandGroup.getBoundingClientRect() : null;
                const rightToolsRect = rightTools ? rightTools.getBoundingClientRect() : null;
                const masterRect = master ? master.getBoundingClientRect() : null;
                const consentRect = consentBanner ? consentBanner.getBoundingClientRect() : null;
                const tabTops = tabs.map(t => Math.round(t.getBoundingClientRect().top));
                const tabLefts = tabs.map(t => Math.round(t.getBoundingClientRect().left));

                const allTabsSameRow = tabTops.length === 4 && tabTops.every(val => Math.abs(val - tabTops[0]) <= 2);
                const headerNoWrap = brandRect && rightToolsRect && Math.abs(brandRect.top - rightToolsRect.top) < 20;
                const noHorizontalScroll = document.documentElement.scrollWidth <= window.innerWidth;

                return {
                    viewport: { width: window.innerWidth, height: window.innerHeight },
                    topBarHeight: Math.round(topBarRect?.height || 0),
                    headerNoWrap,
                    brandPosition: { left: Math.round(brandRect?.left || 0), top: Math.round(brandRect?.top || 0) },
                    rightToolsPosition: { left: Math.round(rightToolsRect?.left || 0), top: Math.round(rightToolsRect?.top || 0) },
                    allTabsSameRow,
                    tabCount: tabs.length,
                    tabPositions: tabTops.map((top, idx) => ({ idx, top, left: tabLefts[idx] })),
                    masterWidth: Math.round(masterRect?.width || 0),
                    consentBannerPresent: !!consentBanner,
                    consentBannerHeight: Math.round(consentRect?.height || 0),
                    noHorizontalScroll
                };
            })()
            """
            msg = {
                "id": 1,
                "method": "Runtime.evaluate",
                "params": {"expression": js_code, "returnByValue": True}
            }
            await ws.send(json.dumps(msg))
            resp = await ws.recv()
            result = json.loads(resp)
            return result["result"]["result"]["value"]
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except Exception:
            proc.kill()

async def main():
    print("Testing 1366x768 (Standard Laptop)...")
    res_1366 = await test_viewport(1366, 768)
    print("1366x768 Result:", json.dumps(res_1366, indent=2))

    print("\nTesting 1920x1080 (Full HD Display)...")
    res_1920 = await test_viewport(1920, 1080)
    print("1920x1080 Result:", json.dumps(res_1920, indent=2))

    # Assertions
    for name, res in [("1366x768", res_1366), ("1920x1080", res_1920)]:
        assert res["headerNoWrap"], f"Header wrapped on {name}!"
        assert res["allTabsSameRow"], f"Tabs not in 1 row on {name}!"
        assert res["noHorizontalScroll"], f"Horizontal scroll detected on {name}!"
        assert res["masterWidth"] <= 1280, f"Master container exceeded max-w-7xl on {name}!"
        print(f"[PASS] {name} verification passed perfectly!")

if __name__ == "__main__":
    asyncio.run(main())

