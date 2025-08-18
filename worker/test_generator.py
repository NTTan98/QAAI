from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    feature = data.get("feature_description", "")
    task_id = data.get("task_id", "unknown")

    if not feature:
        return jsonify({"error": "Missing feature_description"}), 400

    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""
    Bạn là một hệ thống tạo test case tự động.

    Hãy viết các test case cho tính năng sau dưới dạng JSON theo MCP-style.

    Tính năng: {feature}

    Yêu cầu:
    - Mỗi test case gồm: title, steps (danh sách các hành động), expected_result
    - Mỗi step là một object có các trường: action, selector (nếu cần), value (nếu cần), url (nếu là 'goto')
    - Không thêm giải thích, chỉ trả về JSON hợp lệ

    Ví dụ:
    [
    {{
        "title": "Đăng nhập thành công",
        "steps": [
        {{ "action": "goto", "url": "https://your-login-page.com" }},
        {{ "action": "fill", "selector": "input[name='email']", "value": "user@example.com" }},
        {{ "action": "fill", "selector": "input[name='password']", "value": "Password123" }},
        {{ "action": "click", "selector": "button[type='submit']" }},
        {{ "action": "assert_url_contains", "value": "dashboard" }}
        ],
        "expected_result": "Người dùng được chuyển hướng đến trang chính/dashboard."
    }}
    ]
    """
    response = model.generate_content(prompt)
    # Debug: print raw LLM output
    print("LLM raw output:", response.text)

    # Clean LLM output: remove code block markers and whitespace
    cleaned = response.text.strip()
    if cleaned.startswith('```'):
        cleaned = cleaned.lstrip('`')
        # Remove possible language tag (e.g., json)
        cleaned = cleaned.split('\n', 1)[-1]
        if cleaned.endswith('```'):
            cleaned = cleaned.rsplit('```', 1)[0]
    cleaned = cleaned.strip()

    try:
        test_cases = json.loads(cleaned)
    except Exception:
        return jsonify({"error": "LLM output is not valid JSON", "raw": response.text}), 500

    return jsonify({
        "task_id": task_id,
        "worker": "test-generator",
        "output": {
            "test_cases": test_cases
        },
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

if __name__ == "__main__":
    # Bind to all interfaces so other containers can reach this service.
    app.run(host="0.0.0.0", port=6000, debug=True, use_reloader=False)