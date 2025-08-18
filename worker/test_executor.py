from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import re

app = Flask(__name__)

# Tạo thư mục lưu ảnh nếu chưa có
os.makedirs("screenshots", exist_ok=True)

def sanitize_filename(text):
    """Loại bỏ ký tự không hợp lệ khỏi tên file"""
    return re.sub(r'[^\w\-_.]', '_', text)

@app.route("/execute", methods=["POST"])
def execute():
    data = request.get_json()
    task_id = data.get("task_id", "unknown")
    test_cases = data.get("input", {}).get("test_cases", [])

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for test in test_cases:
            title = test.get("title", "Unnamed Test")
            steps = test.get("steps", [])
            expected = test.get("expected_result", "")
            actual = ""
            success = False
            logs = []
            screenshot_path = None

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

                # Chụp ảnh sau khi test
                safe_task_id = sanitize_filename(task_id)
                safe_title = sanitize_filename(title)
                screenshot_path = f"screenshots/{safe_task_id}_{safe_title}.png"
                try:
                    page.screenshot(path=screenshot_path)
                except Exception as e:
                    logs.append(f"Screenshot failed: {str(e)}")
                    screenshot_path = None

            except Exception as e:
                actual = f"Lỗi: {str(e)}"
                success = False
                screenshot_path = None

            results.append({
                "title": title,
                "expected": expected,
                "actual": actual,
                "success": success,
                "screenshot": screenshot_path,
                "logs": logs
            })

        browser.close()

    return jsonify({
        "task_id": task_id,
        "worker": "test-executor",
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "output": {
            "results": results
        }
    })

if __name__ == "__main__":
    # Bind to all interfaces so other containers can reach this service.
    app.run(host="0.0.0.0", port=6001, debug=True, use_reloader=False)