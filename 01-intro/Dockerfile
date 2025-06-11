# 使用官方 Python 映像
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 複製必要檔案到容器中
COPY requirements.txt .
COPY . .

# 安裝依賴套件
RUN pip install --no-cache-dir -r requirements.txt

# 開放 Streamlit 的預設 port
EXPOSE 8501

# 啟動 Streamlit App
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
