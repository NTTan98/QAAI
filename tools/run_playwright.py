from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime
from typing import Type

class PlaywrightToolInput(BaseModel):
    """Input schema for Playwright Test Execution Tool."""
    test_case_json: str = Field(..., description="JSON string containing test case with steps to execute")

class PlaywrightTestTool(BaseTool):
    name: str = "playwright_test_executor"
    description: str = "Executes automated browser tests using Playwright. Takes a JSON test case with steps and returns execution results."
    args_schema: Type[BaseModel] = PlaywrightToolInput

    def _run(self, test_case_json: str) -> str:
        # Parse JSON string → dict
        try:
            test_case = json.loads(test_case_json)
        except Exception as e:
            return json.dumps({
                "status": "error",
                "message": f"Không thể parse JSON input: {str(e)}"
            })

        results = []
        variables = {}
        total_steps = len(test_case.get("steps", []))
        passed = 0
        failed = 0

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # True nếu muốn chạy ẩn
            context = browser.new_context()
            page = context.new_page()

            for index, step in enumerate(test_case.get("steps", []), start=1):
                action = step.get("action")
                target = step.get("target")
                value = step.get("value")
                timeout = step.get("timeout", 5000)
                status = "pass"
                message = ""
                timestamp = datetime.now().isoformat()

                try:
                    # --- GOTO ---
                    if action == "goto":
                        page.goto(target, timeout=timeout)
                        message = f"Điều hướng đến {target} thành công"

                    # --- CLICK ---
                    elif action == "click":
                        page.wait_for_selector(target, timeout=timeout)
                        page.click(target)
                        message = f"Click vào {target} thành công"

                    # --- TYPE ---
                    elif action == "type":
                        page.wait_for_selector(target, timeout=timeout)
                        page.fill(target, value)
                        message = f"Gõ '{value}' vào {target} thành công"

                    # --- FILL ---
                    elif action == "fill":
                        page.wait_for_selector(target, timeout=timeout)
                        page.fill(target, value)
                        message = f"Điền '{value}' vào {target} thành công"

                    # --- WAIT ---
                    elif action == "wait":
                        time.sleep(int(value))
                        message = f"Chờ {value} giây thành công"

                    # --- PRESS ---
                    elif action == "press":
                        page.wait_for_selector(target, timeout=timeout)
                        page.press(target, value)
                        message = f"Nhấn phím '{value}' trên {target} thành công"

                    # --- WAIT FOR SELECTOR ---
                    elif action.lower() == "waitforselector":
                        page.wait_for_selector(target, timeout=timeout)
                        message = f"Đợi selector {target} xuất hiện thành công"

                    # --- GET TEXT ---
                    elif action.lower() == "gettext":
                        element = page.wait_for_selector(target, timeout=timeout)
                        text = element.inner_text()
                        var_name = step.get("variable")
                        if var_name:
                            variables[var_name] = text
                            message = f"Lưu biến {var_name} = {text}"
                        else:
                            message = f"Lấy text: {text}"

                    # --- LOG ---
                    elif action.lower() == "log":
                        msg = step.get("message", "")
                        for k, v in variables.items():
                            msg = msg.replace(f"{{{{{k}}}}}", str(v))
                        print("📝 Log:", msg)
                        message = f"Log: {msg}"

                    # --- ASSERT ---
                    elif action.lower() == "assert":
                        condition = step.get("condition")
                        if condition == "isVisible":
                            element = page.locator(target)
                            assert element.is_visible(), f"{target} không hiển thị"
                            message = f"Assert: {target} hiển thị"
                        elif condition and ".includes(" in condition:
                            var_name, expected = condition.replace(")", "").split(".includes(")
                            var_name = var_name.strip()
                            expected = expected.strip("'\"")
                            actual = variables.get(var_name)
                            assert expected in str(actual), f"'{expected}' không có trong '{actual}'"
                            message = f"Assert: '{expected}' nằm trong {var_name} = {actual}"
                        else:
                            raise ValueError(f"Condition '{condition}' không được hỗ trợ")

                    # --- SCREENSHOT ---
                    elif action.lower() == "screenshot":
                        file_path = step.get("path", f"screenshot_{index}.png")
                        page.screenshot(path=file_path)
                        message = f"Chụp màn hình lưu tại {file_path}"

                    else:
                        status = "fail"
                        message = f"Action '{action}' không được hỗ trợ"

                except Exception as e:
                    status = "fail"
                    message = str(e)

                if status == "pass":
                    passed += 1
                else:
                    failed += 1

                results.append({
                    "step_index": index,
                    "step": step,
                    "status": status,
                    "message": message,
                    "timestamp": timestamp
                })

            browser.close()

        return json.dumps({
            "status": "completed",
            "total_steps": total_steps,
            "passed": passed,
            "failed": failed,
            "results": results
        }, ensure_ascii=False, indent=2)
