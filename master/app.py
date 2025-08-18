from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)

# Địa chỉ các worker MCP.
# Khi chạy trong docker-compose, sử dụng service name (generator, executor).
# Cho phép override bằng biến môi trường TEST_GENERATOR_URL/TEST_EXECUTOR_URL để thuận tiện cho dev local.
TEST_GENERATOR_URL = os.getenv("TEST_GENERATOR_URL", "http://generator:6000/generate")
TEST_EXECUTOR_URL = os.getenv("TEST_EXECUTOR_URL", "http://executor:6001/execute")

@app.route("/run-tests", methods=["POST"])
def run_tests_from_nlp():
    data = request.get_json()
    feature = data.get("feature_description", "")
    if not feature:
        return jsonify({"error": "Missing feature_description"}), 400

    task_id = data.get("task_id", f"task-{datetime.utcnow().isoformat()}")

    # Debug: log target worker URLs
    print(f"Calling test-generator at {TEST_GENERATOR_URL}")
    print(f"Calling test-executor at {TEST_EXECUTOR_URL}")

    # Step 1: Gọi test-generator để tạo test case MCP-style
    try:
        gen_response = requests.post(
            TEST_GENERATOR_URL,
            json={"feature_description": feature, "task_id": task_id},
            timeout=30,
        )
        gen_response.raise_for_status()
        gen_data = gen_response.json()
        test_cases = gen_data.get("output", {}).get("test_cases", [])
    except Exception as e:
        return jsonify({"error": f"Test-generator failed: {str(e)}"}), 500

    if not test_cases:
        return jsonify({"error": "No test cases generated"}), 500

    # Step 2: Gọi test-executor để chạy test
    try:
        exec_response = requests.post(
            TEST_EXECUTOR_URL,
            json={"task_id": task_id, "input": {"test_cases": test_cases}},
            timeout=60,
        )
        exec_response.raise_for_status()
        exec_data = exec_response.json()
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