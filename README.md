# AutoAITest

## Mô tả
Dự án này gồm 2 service Flask và 1 module thực thi test:
- `master/app.py`: Service chính quản lý các task.
- `worker/test_generator.py`: Service sinh test case tự động bằng Gemini AI.
- `worker/test_executor.py`: Module thực thi test case tự động (ví dụ: kiểm thử giao diện, kiểm thử chức năng, lưu ảnh kết quả vào thư mục screenshots).

## Cách cài đặt
1. Clone repo về máy:
   ```
   git clone <repo-url>
   ```
2. Cài Python 3.x và tạo môi trường ảo (nếu muốn):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Cài các thư viện:
   ```
   pip install -r requirements.txt
   ```
4. Tạo file `.env` và điền GEMINI_API_KEY:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Chạy các service và module
- Vào thư mục `worker`:
  ```
  python test_generator.py
  ```
  Service sinh test case chạy tại http://localhost:6000

- Để thực thi test case tự động:
  ```
  python test_executor.py
  ```
  Kết quả test (ví dụ: ảnh chụp màn hình) sẽ được lưu vào thư mục `worker/screenshots/` (đã được loại trừ khỏi git).

## Lưu ý
- Không commit file `.env`, `venv/`, ảnh test, screenshots lên git.
- Đã có file `.gitignore` để loại trừ các file này.

## Troubleshooting / Known issues
Below are the issues encountered during development, their root causes, and the concrete fixes that worked in this project. Keep this section for quick debugging when running with Docker Compose.

- LLM output not valid JSON
   - Symptom: `{"error":"LLM output is not valid JSON"}` returned by `test_generator` or `master` when parsing the model output.
   - Root cause: the LLM returned text with extra surrounding markdown code fences or explanatory text, so `json.loads()` failed.
   - Fixes applied:
      - Log the raw LLM response in `worker/test_generator.py` for debugging.
      - Strip common code fences (```json, ```), leading/trailing text and try a robust JSON extraction before parsing.

- Playwright executor fails with 500 / missing executable
   - Symptom: `playwright._impl._errors.Error: BrowserType.launch: Executable doesn't exist at /ms-playwright/.../headless_shell` and a banner saying the Playwright image version is out of sync.
   - Root cause: mismatch between the installed `playwright` Python package and the Playwright base Docker image (browser binaries weren't present for the installed package version).
   - Fixes applied:
      - Pin `playwright` in `requirements.txt` to match the base image version used in the `Dockerfile` (example: `playwright==1.54.0`).
      - Use the matching Playwright base image in `Dockerfile`, e.g. `mcr.microsoft.com/playwright/python:v1.54.0-jammy`.
      - Ensure the Dockerfile runs `playwright install --with-deps` so the browser binaries are installed inside the image.
      - Rebuild the executor image and recreate the containers: see commands below.

- Development server reloader and repeated restarts
   - Symptom: logs show many `Detected change ... reloading` and the container repeatedly restarts or prints both `127.0.0.1` and `0.0.0.0` addresses.
   - Root cause: running Flask with `debug=True` and the auto-reloader inside a container with mounted source triggers file change detection and repeated reloads.
   - Recommended practice: in Docker containers set `debug=False` and `use_reloader=False` when starting Flask, or use a production WSGI server (gunicorn/waitress) for stability.

- Connection refused / socket hang up when calling master from host
   - Symptom: `connect ECONNREFUSED 127.0.0.1:5000` or Postman shows `socket hang up` while containers appear to run.
   - Common causes & checks:
      - Confirm `docker-compose ps` shows `0.0.0.0:5000->5000/tcp` mapping for the master service.
      - If master is restarting due to an internal exception it may refuse connections; tail `docker-compose logs --tail=200 master` to see stack traces.
      - Ensure firewall or corporate proxy is not blocking Docker Desktop loopback ports.
   - Quick verification & rebuild commands (run from project root):
      ```powershell
      docker-compose build executor
      docker-compose up -d --force-recreate
      docker-compose ps
      docker-compose logs --tail=200 master
      docker-compose logs --tail=200 executor
      ```

## Quick end-to-end test
After containers are up, you can trigger a run (master expects a JSON body with `feature_description`):

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/run-tests -Body '{"feature_description":"Login flow for web app"}' -ContentType 'application/json' -TimeoutSec 120
```

If the request fails, collect logs from the three services for diagnosis:

```powershell
docker-compose logs --tail=200 master
docker-compose logs --tail=200 generator
docker-compose logs --tail=200 executor
```

## License
MIT
