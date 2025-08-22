from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from playwright.sync_api import sync_playwright
import time
import base64
import json
from datetime import datetime
from typing import Type, List, Dict, Any

class PlaywrightToolInput(BaseModel):
    """Input schema for Playwright Test Execution Tool."""
    test_case_json: str = Field(..., description="JSON string containing test case with steps to execute")

class PlaywrightTestTool(BaseTool):
    name: str = "playwright_test_executor"
    description: str = "Executes automated browser tests using Playwright. Takes a JSON test case with steps and returns execution results."
    args_schema: Type[BaseModel] = PlaywrightToolInput

    def _run(self, test_case_json: str) -> str:
        try:
            test_case = json.loads(test_case_json)
        except json.JSONDecodeError as e:
            return json.dumps({
                "status": "error",
                "message": f"Invalid JSON input: {str(e)}",
                "results": []
            }, ensure_ascii=False, indent=2)

        results = []
        suggestions = []
        print("🚀 Bắt đầu thực thi test case...")
        print("test case json:", test_case_json)

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            page.set_default_timeout(30000)

            for i, step in enumerate(test_case.get("steps", [])):
                step_result = {
                    "step_index": i + 1,
                    "step": step,
                    "status": "fail",
                    "message": "",
                    "timestamp": datetime.now().isoformat()
                }

                try:
                    action = step.get("action", "").lower()
                    target = step.get("target")  # Sử dụng target thống nhất
                    value = step.get("value")  # Giữ value cho fill hoặc type
                    timeout = step.get("timeout", 10000)

                    if action == "goto":
                        if not target:
                            raise ValueError("Target không được để trống cho action 'goto'")
                        page.goto(target, wait_until='domcontentloaded', timeout=timeout)
                        step_result["message"] = f"Điều hướng đến {target} thành công"
                        step_result["status"] = "pass"

                    elif action == "click":
                        if not target:
                            raise ValueError("Target không được để trống cho action 'click'")
                        page.wait_for_selector(target, timeout=timeout)
                        page.click(target, timeout=timeout)
                        step_result["message"] = f"Click vào element {target} thành công"
                        step_result["status"] = "pass"

                    elif action == "fill":
                        if not target or value is None:
                            raise ValueError("Target và value không được để trống cho action 'fill'")
                        page.wait_for_selector(target, timeout=timeout)
                        page.fill(target, str(value), timeout=timeout)
                        step_result["message"] = f"Điền '{value}' vào {target} thành công"
                        step_result["status"] = "pass"

                    elif action == "type":
                        if not target or value is None:
                            raise ValueError("Target và value không được để trống cho action 'type'")
                        page.wait_for_selector(target, timeout=timeout)
                        page.type(target, str(value), delay=100)
                        step_result["message"] = f"Gõ '{value}' vào {target} thành công"
                        step_result["status"] = "pass"

                    elif action == "wait":
                        wait_time = float(value) if value else 1.0
                        time.sleep(wait_time)
                        step_result["message"] = f"Chờ {wait_time} giây thành công"
                        step_result["status"] = "pass"

                    elif action == "wait_for_selector":
                        if not target:
                            raise ValueError("Target không được để trống cho action 'wait_for_selector'")
                        page.wait_for_selector(target, timeout=timeout)
                        step_result["message"] = f"Chờ element {target} xuất hiện thành công"
                        step_result["status"] = "pass"

                    elif action == "assert_text_contains":
                        if not target or not value:
                            raise ValueError("Target và value không được để trống cho action 'assert_text_contains'")
                        page.wait_for_selector(target, timeout=timeout)
                        actual_text = page.inner_text(target)
                        if str(value).lower() in actual_text.lower():
                            step_result["message"] = f"Text '{value}' được tìm thấy trong {target}"
                            step_result["status"] = "pass"
                        else:
                            step_result["message"] = f"Text '{value}' không được tìm thấy. Actual: '{actual_text}'"
                            step_result["status"] = "fail"
                            suggestions.append(f"Step {i+1}: Kiểm tra target '{target}' hoặc nội dung text '{value}' có đúng không.")

                    elif action == "assert_url_contains":
                        if not value:
                            raise ValueError("Value không được để trống cho action 'assert_url_contains'")
                        current_url = page.url
                        if str(value).lower() in current_url.lower():
                            step_result["message"] = f"URL chứa '{value}'. Current URL: {current_url}"
                            step_result["status"] = "pass"
                        else:
                            step_result["message"] = f"URL không chứa '{value}'. Current URL: {current_url}"
                            step_result["status"] = "fail"
                            suggestions.append(f"Step {i+1}: Kiểm tra giá trị URL '{value}' hoặc đảm bảo điều hướng đúng.")

                    elif action == "assert_element_visible":
                        if not target:
                            raise ValueError("Target không được để trống cho action 'assert_element_visible'")
                        element = page.locator(target)
                        if element.is_visible():
                            step_result["message"] = f"Element {target} hiển thị"
                            step_result["status"] = "pass"
                        else:
                            step_result["message"] = f"Element {target} không hiển thị"
                            step_result["status"] = "fail"
                            suggestions.append(f"Step {i+1}: Kiểm tra target '{target}' hoặc đảm bảo element hiển thị trên trang.")

                    elif action == "select_option":
                        if not target or not value:
                            raise ValueError("Target và value không được để trống cho action 'select_option'")
                        page.wait_for_selector(target, timeout=timeout)
                        page.select_option(target, value)
                        step_result["message"] = f"Chọn option '{value}' trong {target} thành công"
                        step_result["status"] = "pass"

                    elif action == "hover":
                        if not target:
                            raise ValueError("Target không được để trống cho action 'hover'")
                        page.wait_for_selector(target, timeout=timeout)
                        page.hover(target)
                        step_result["message"] = f"Hover vào {target} thành công"
                        step_result["status"] = "pass"

                    elif action == "double_click":
                        if not target:
                            raise ValueError("Target không được để trống cho action 'double_click'")
                        page.wait_for_selector(target, timeout=timeout)
                        page.dblclick(target)
                        step_result["message"] = f"Double click vào {target} thành công"
                        step_result["status"] = "pass"

                    elif action == "press_key":
                        key = value or "Enter"
                        page.keyboard.press(key)
                        step_result["message"] = f"Nhấn phím '{key}' thành công"
                        step_result["status"] = "pass"

                    elif action == "screenshot":
                        screenshot_bytes = page.screenshot(full_page=True)
                        screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                        step_result["screenshot"] = screenshot_base64
                        step_result["message"] = "Chụp ảnh màn hình thành công"
                        step_result["status"] = "pass"

                    else:
                        step_result["message"] = f"Action '{action}' không được hỗ trợ"
                        step_result["status"] = "fail"
                        suggestions.append(f"Step {i+1}: Action '{action}' không được hỗ trợ. Kiểm tra tên action.")

                except Exception as e:
                    step_result["message"] = f"Lỗi khi thực thi step: {str(e)}"
                    step_result["status"] = "fail"
                    suggestions.append(f"Step {i+1}: Lỗi '{str(e)}'. Kiểm tra target, value, hoặc kết nối mạng.")
                    try:
                        screenshot_bytes = page.screenshot(full_page=True)
                        step_result["screenshot"] = base64.b64encode(screenshot_bytes).decode("utf-8")
                    except:
                        pass

                results.append(step_result)
                if step_result["status"] == "fail" and step.get("critical", False):
                    step_result["message"] += " - Dừng test do step critical fail"
                    suggestions.append(f"Step {i+1}: Step critical thất bại. Xem lại cấu hình step hoặc trạng thái ứng dụng.")
                    break

            browser.close()

        return json.dumps({
            "status": "completed",
            "total_steps": len(results),
            "passed": len([r for r in results if r["status"] == "pass"]),
            "failed": len([r for r in results if r["status"] == "fail"]),
            "results": results,
            "suggestions": suggestions if suggestions else ["Không có lỗi, tất cả steps đều pass."]
        }, ensure_ascii=False, indent=2)