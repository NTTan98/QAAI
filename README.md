QAAI — QA Automation Crew
================================

Mục đích
--------
QAAI là một prototype/khung làm việc dùng `crewai` để phối hợp nhiều agent (Generator, Executor, Multi-purpose) thực hiện luồng QA automation:
- Generator: nhận mô tả feature và sinh ra JSON test case (theo format step-by-step cho Playwright).
- Executor: nhận JSON test case và thực thi bằng Playwright (tool tại `tools/run_playwright.py`).
- MultiAgent: quyết định kết quả (nếu tất cả pass → sinh code Playwright TypeScript; nếu có fail → sinh báo cáo chi tiết).

Entrypoint
---------
File chạy chính: `crew.py`
- Tạo 3 Task: `GeneratorTask`, `ExecutorTask`, `DecisionTask`.
- Tạo Crew với 3 agents: `GENERATOR_AGENT`, `ExecutorAgent`, `MultiAgent`.
- Gọi `crew.kickoff()` để chạy toàn bộ flow.

Yêu cầu
-------
- Python 3.10+
- Docker & Docker Compose (nếu muốn chạy trong container)
- (Tùy chọn) Playwright CLI để cài browser binaries khi chạy local: `playwright install`

Cài đặt và chạy (local - PowerShell)
-----------------------------------
1) Tạo virtualenv và kích hoạt:

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

2) Cài dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
# Nếu chạy Playwright local lần đầu, cài browser binaries:
playwright install
```

3) Thiết lập biến môi trường (ví dụ dùng PowerShell):

```powershell
$env:GEMINI_API_KEY = "your_gemini_api_key"
$env:LLL_MODEL = "your_model_name"
```

4) Chạy orchestration:

```powershell
python crew.py
```

Docker / Docker Compose
-----------------------
- `Dockerfile` sử dụng base image `mcr.microsoft.com/playwright/python:v1.54.0-jammy` và gọi `playwright install --with-deps`.
- `docker-compose.yml` đã được cấu hình để build và mount source (dễ cho phát triển). Entrypoint đã đổi để chạy `python crew.py`.

Build & chạy bằng Docker:

```powershell
docker build -t qaai:latest .
docker run --rm -it -e GEMINI_API_KEY="$env:GEMINI_API_KEY" -e LLL_MODEL="$env:LLL_MODEL" qaai:latest
```

Hoặc dùng docker-compose:

```powershell
docker-compose up --build
docker-compose logs -f
```

Biến môi trường quan trọng
--------------------------
- `GEMINI_API_KEY` — API key cho Google Gemini / Google Generative AI (nếu dùng)
- `LLL_MODEL` — model id/name được truyền vào Agent như biến `llm` (lưu ý trong code tên biến là `LLL_MODEL`)

Cấu trúc thư mục chính
----------------------
- `crew.py` — entrypoint orchestration
- `agents/` — định nghĩa các Agent
  - `generator_agent.py` — generator (sinh JSON test case)
  - `executor_agent.py` — executor (gọi Playwright tool)
  - `multi_agent.py` — decision/codegen/reporter
- `tasks/` — factory tạo `Task` (generator_task, executor_task, decision_task)
- `tools/run_playwright.py` — công cụ thực thi test case bằng Playwright và trả về kết quả JSON
- `Dockerfile`, `docker-compose.yml`, `requirements.txt`, `.env.example`

Chi tiết kỹ thuật quan trọng
---------------------------
- `tools/run_playwright.py`:
  - Nhận input là JSON string chứa `steps` (mảng các action: `goto`, `click`, `type`, `fill`, `wait`, `press`, `waitForSelector`, `getText`, `assert`, `screenshot`, `log`).
  - Trả về JSON chi tiết: `total_steps`, `passed`, `failed`, `results` (mảng object cho từng step với `status` và `message`).
  - Hiện mã chạy Playwright với `headless=False` — đổi sang `True` để chạy headless trong CI/Docker nếu cần.

- Agents đọc environment variable `LLL_MODEL` làm `llm` (để cấu hình LLM/adapter). Kiểm tra biến này khi chạy.

Gợi ý & troubleshooting
------------------------
- Nếu container không khởi động: kiểm tra `docker-compose logs` hoặc `docker logs <id>`.
- Nếu Playwright báo thiếu browser: chạy `playwright install` (hoặc rebuild image nếu chạy trong Docker).
- Để phát triển nhanh, `docker-compose.yml` mount source vào container; nhớ restart container nếu thay đổi cấu trúc import.

Next steps đề xuất (mình có thể làm giúp):
- Thêm `scripts/bootstrap.ps1` để tự động tạo venv + cài deps + playwright install.
- Tạo `README` tiếng Anh.
- Thêm flag/biến env để điều khiển `headless` và `PLAYWRIGHT_TIMEOUT`.
- Viết unit test nhỏ cho parser JSON trong `tools/run_playwright.py`.

License
-------
Chưa có thông tin license trong repo — thêm file `LICENSE` nếu bạn muốn công khai bản quyền.
