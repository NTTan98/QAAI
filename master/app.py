from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Địa chỉ các worker MCP
TEST_GENERATOR_URL = "http://localhost:6000/generate"
TEST_EXECUTOR_URL = "http://localhost:6001/execute"

@app.route("/run-tests", methods=["POST"])
def run_tests_from_nlp():
    data = request.get_json()
    feature = data.get("feature_description", "")
    if not feature:
        return jsonify({"error": "Missing feature_description"}), 400

    task_id = data.get("task_id", f"task-{datetime.utcnow().isoformat()}")

    # Step 1: Gọi test-generator để tạo test case MCP-style
    try:
        gen_response = requests.post(TEST_GENERATOR_URL, json={
            "feature_description": feature,
            "task_id": task_id
        })
        gen_response.raise_for_status()
        gen_data = gen_response.json()
        test_cases = gen_data.get("output", {}).get("test_cases", [])
    except Exception as e:
        return jsonify({"error": f"Test-generator failed: {str(e)}"}), 500

    if not test_cases:
        return jsonify({"error": "No test cases generated"}), 500

    # Step 2: Gọi test-executor để chạy test
    try:
        exec_response = requests.post(TEST_EXECUTOR_URL, json={
            "task_id": task_id,
            "input": {
                "test_cases": test_cases
            }
        })
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
    app.run(port=5000, debug=True)