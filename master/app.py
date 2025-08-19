from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from datetime import datetime
import os
import sys

# Make sure parent folder is on sys.path so we can import the sibling `worker` package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Try to import local worker functions. If not available, leave as None and fall back to HTTP calls.
try:
    from worker.test_generator import generate_test_cases
except Exception:
    generate_test_cases = None

try:
    from worker.test_executor import execute_task
except Exception:
    execute_task = None

app = Flask(__name__)
CORS(app)
# Using local worker functions (no HTTP calls).
# Ensure `worker/test_generator.py` exposes `generate_test_cases(feature_description, task_id)`
# and `worker/test_executor.py` exposes `execute_task(data, headless=True)`.


@app.route("/run-tests", methods=["POST"])
def run_tests_from_nlp():
    data = request.get_json()
    feature = data.get("feature_description", "")
    if not feature:
        return jsonify({"error": "Missing feature_description"}), 400

    task_id = data.get("task_id", f"task-{datetime.utcnow().isoformat()}")

    # Debug: confirm we're calling local worker functions
    gen_target = "<local:function:generate_test_cases>" if callable(generate_test_cases) else "<missing>"
    exec_target = "<local:function:execute_task>" if callable(execute_task) else "<missing>"
    print(f"Calling test-generator at {gen_target}")
    print(f"Calling test-executor at {exec_target}")

    # Step 1: Gọi test-generator để tạo test case MCP-style
    try:
        # Require local generate_test_cases function
        if not callable(generate_test_cases):
            return jsonify({"error": "Local test generator function not available"}), 500

        # Call local function which returns MCP-style dict
        gen_data = generate_test_cases(feature, task_id)
        if hasattr(gen_data, "json") and callable(gen_data.json):
            gen_data = gen_data.json()

        test_cases = gen_data.get("output", {}).get("test_cases", [])
    except Exception as e:
        return jsonify({"error": f"Test-generator failed: {str(e)}"}), 500

    if not test_cases:
        return jsonify({"error": "No test cases generated"}), 500

    # Step 2: Gọi test-executor để chạy test
    try:
        if not callable(execute_task):
            return jsonify({"error": "Local test executor function not available"}), 500

        exec_payload = {"task_id": task_id, "input": {"test_cases": test_cases}}
        exec_data = execute_task(exec_payload)
        if hasattr(exec_data, "json") and callable(exec_data.json):
            exec_data = exec_data.json()

        results = exec_data.get("output", {}).get("results", [])
    except Exception as e:
        return jsonify({"error": f"Test-executor failed: {str(e)}"}), 500

    # Step 3: Trả về kết quả tổng hợp
    return jsonify({
        "task_id": task_id,
        "feature_description": feature,
        "generated_cases": test_cases,
        "execution_results": results,
        "status": "completed",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

if __name__ == "__main__":
    # Listen on all interfaces so Docker port mapping works from the host.
    # Disable the auto-reloader to avoid repeated restarts when files are mounted.
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)