#!/bin/bash

set -e  # 有錯就中斷
set -o pipefail

WORKDIR="/home/horus/.tim/llm-zoomcamp-2025/dlt-workshop/dlt"
DUCKDB_PATH="$WORKDIR/zoomcamp_pipeline.duckdb"

echo "📁 建立工作目錄：$WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "🚚 執行 DLT pipeline (寫入 DuckDB)..."
python ingest.py

echo "✅ DuckDB pipeline 執行完成"
echo "🔍 DuckDB 檔案位置：$DUCKDB_PATH"
[ -f "$DUCKDB_PATH" ] && echo "📦 DuckDB 檔案存在" || echo "❌ DuckDB 檔案遺失"

echo ""
echo "🐳 啟動 Neo4j（docker-compose）..."
docker compose up -d neo4j

echo "⏳ 等待 Neo4j 啟動完成（約 10 秒）..."
sleep 10

echo ""
echo "🔎 測試 Neo4j 查詢"
python test_neo4j.py

echo ""
echo "🎯 全部流程完成 ✅"
