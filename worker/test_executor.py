from playwright.sync_api import sync_playwright
from datetime import datetime
import re
import base64

def sanitize_filename(text):
    """Loại bỏ ký tự không hợp lệ khỏi tên file"""
    return re.sub(r'[^\w\-_.]', '_', text)

def execute_task(data, headless=True):
    """
    data: dict tương tự payload trước đây:
      {
        "task_id": "...",
        "input": {
          "test_cases": [
            {"title": "...", "steps": [...], "expected_result": "..."},
            ...
          ]
        }
      }
    headless: True/False để bật/tắt chế độ headless của Chromium
    Trả về dict kết quả.
    """
    task_id = data.get("task_id", "unknown")
    test_cases = data.get("input", {}).get("test_cases", [])

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            for test in test_cases:
                title = test.get("title", "Unnamed Test")
                steps = test.get("steps", [])
                expected = test.get("expected_result", "")
                actual = ""
                success = False
                logs = []
                screenshot_base64 = None

                try:
                    for step in steps:
                        action = step.get("action")
                        selector = step.get("selector")
                        value = step.get("value")
                        url = step.get("url")

                        logs.append(f"{action.upper()} → {selector or url} → {value or ''}")

                        if action == "goto":
                            page.goto(url)
                        elif action == "fill":
                            page.fill(selector, value)
                        elif action == "click":
                            page.click(selector)
                        elif action == "assert_url_contains":
                            actual = page.url
                            success = value in actual
                        elif action == "assert_element_visible":
                            element = page.locator(selector)
                            success = element.is_visible()
                            actual = f"Element visible: {success}"
                        elif action == "assert_text_contains":
                            text = page.inner_text(selector)
                            actual = text
                            success = value in text
                        else:
                            actual = f"Unknown action: {action}"
                            success = False

                    # Chụp ảnh sau khi test -> base64
                    try:
                        screenshot_bytes = page.screenshot()
                        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                    except Exception as e:
                        logs.append(f"Screenshot failed: {str(e)}")
                        screenshot_base64 = None

                except Exception as e:
                    actual = f"Lỗi: {str(e)}"
                    success = False
                    screenshot_base64 = None

                results.append({
                    "title": title,
                    "expected": expected,
                    "actual": actual,
                    "success": success,
                    "screenshot": screenshot_base64,  # chỉ trả base64
                    "logs": logs
                })
        finally:
            browser.close()

    return {
        "task_id": task_id,
        "worker": "test-executor",
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "output": {
            "results": results
        }
    }
