# /d:/test/AutoAITest/worker/test_generator.py
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_test_cases(feature_description: str, task_id: str = "unknown", model_name: str = "gemini-2.5-flash") -> dict:
    """
    Trả về dict giống structure trước đây:
    {
      "task_id": ...,
      "worker": "test-generator",
      "output": {"test_cases": [...]},
      "status": "completed" / "error",
      "timestamp": ...,
      optionally "error" or "raw" on lỗi
    }
    """
    feature = feature_description or ""
    if not feature:
        return {
            "task_id": task_id,
            "worker": "test-generator",
            "status": "error",
            "error": "Missing feature_description",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

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

    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)

    # Debug: raw LLM output
    raw = getattr(response, "text", str(response))
    print("LLM raw output:", raw)

    # Clean LLM output: remove code fences and surrounding whitespace
    cleaned = raw.strip()
    if cleaned.startswith('```'):
        # remove leading backticks and optional language tag
        cleaned = cleaned.lstrip('`')
        cleaned = cleaned.split('\n', 1)[-1]
        if cleaned.endswith('```'):
            cleaned = cleaned.rsplit('```', 1)[0]
    cleaned = cleaned.strip()

    try:
        test_cases = json.loads(cleaned)
    except Exception:
        return {
            "task_id": task_id,
            "worker": "test-generator",
            "status": "error",
            "error": "LLM output is not valid JSON",
            "raw": raw,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    return {
        "task_id": task_id,
        "worker": "test-generator",
        "output": {"test_cases": test_cases},
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }