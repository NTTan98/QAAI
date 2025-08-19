FROM mcr.microsoft.com/playwright/python:v1.54.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Ensure Playwright browser binaries are installed in the image
RUN playwright install --with-deps

COPY . .

# Expose cổng mặc định cho Flask
EXPOSE 5000

# Lệnh mặc định (sẽ override bằng docker-compose)
CMD ["python", "master/app.py"]
