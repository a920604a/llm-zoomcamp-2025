
# 🎓 向量搜尋教學：用 FastEmbed + Qdrant 建構智能問答系統

---

## 💡 教學目標

1. 學會將文字轉成「語意向量」
2. 使用 Qdrant 建立可搜尋的向量資料庫
3. 建立語意查詢功能（使用者輸入問題 → 找出最接近的問答資料）

---

## 🧰 環境需求

* Python 3.9+

* 套件：

  ```txt
  fastembed
  qdrant-client
  numpy
  requests
  ```

* 本地啟動 Qdrant（用 Docker 最方便）：

  ```bash
  docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
  ```

---

## 步驟說明

---

### ✅ Q1：將一段文字轉成向量

```python
query = "I just discovered the course. Can I join now?"
embedding = list(embed_model_jina.embed([query]))[0]
print(min(embedding))
```

📘 說明：

* 我們用 `FastEmbed` 的模型，把人類的句子轉成向量（數字陣列）。
* 這個向量代表語意意義，給機器比對用。
* `min(embedding)` 只是取出最小值當作示範，你也可以看 `len(embedding)` 檢查維度（512 維）。

---

### ✅ Q2：比對兩段文字的相似度

```python
similarity = np.dot(q_vector, doc_vector)
```

📘 說明：

* 向量內積（dot product）可以快速計算「兩段話的語意有多像」。
* 如果結果接近 `1`，代表語意幾乎一樣。
* 記得這裡的向量必須是已經正規化（FastEmbed 自動處理）。

---

### ✅ Q3：上傳一批 FAQ 文件到 Qdrant

```python
client.create_collection(...)  # 建立資料庫
client.upsert(...)             # 上傳向量與內容
client.query_points(...)       # 查詢最相近的資料
```

📘 說明：

* 每一筆文件（包含 text + question）都轉成向量後儲存進 Qdrant。
* 查詢時 Qdrant 幫你算語意距離，回傳最接近的資料。

💡 初學者小知識：

> 你可以想像 Qdrant 是一個超大型的「語意字典」，它不是用關鍵字比對，而是用「意思」找答案。

---

### ✅ Q4：改良向量品質，把 `question + text` 結合後上傳

```python
full_text = doc['question'] + ' ' + doc['text']
```

📘 說明：

* 使用者輸入的問題可能不只對應文件的 `question`，所以把上下文也一起放進向量裡會更準。
* 這就像讓模型讀更多資訊來「理解這筆資料」。

---

### ✅ Q5：選擇嵌入模型

```python
models_list = TextEmbedding.list_supported_models()
min_model = min(models_list, key=lambda x: x['dim'])
```

📘 說明：

* 這段會列出所有可用的 FastEmbed 模型，並選出「最小維度」的模型。
* 小模型好處：速度快、記憶體省。
* 常用模型說明：

  | 模型名稱                                 | 維度  | 說明           |
  | ------------------------------------ | --- | ------------ |
  | `jinaai/jina-embeddings-v2-small-en` | 512 | 精準但稍大        |
  | `BAAI/bge-small-en`                  | 384 | 快速，適合資源有限的專案 |

---

### ✅ Q6：使用真實課程 FAQ 建立向量資料庫

```python
docs_url = 'https://github.com/.../documents.json'
```

📘 說明：

* 專案中內建了一批來自 DataTalks.Club 的課程 FAQ 資料。
* 我們用 `requests.get()` 下載後只篩選某課程，例如 `machine-learning-zoomcamp`。
* 每一筆資料一樣轉成向量、加上 `text/section/course` 等 metadata。

---

## 🧪 查詢範例說明（同 Q3/Q4/Q6 通用）

```python
res = search("I just discovered the course. Can I join now?")
point = res.points[0]
print(f"最相似問句: {point.payload['question']}")
print(f"內容摘要: {point.payload['text'][:100]}")
```

---

## 🔧 小工具建議：封裝查詢函式

```python
def pretty_print(res):
    for point in res.points:
        print("🧠 相似問題:", point.payload.get("question"))
        print("📌 課程:", point.payload.get("course"))
        print("📄 回答摘要:", point.payload.get("text")[:200])
        print("📊 相似度:", f"{point.score:.4f}")
        print("="*50)
```

---

## 🎯 延伸任務與練習（可以出作業）

1. **用中文資料做一樣的流程**（改用 bge-m3 多語模型）
2. **加入 Streamlit 前端**，讓使用者能輸入查詢語句
3. **用 sklearn 做向量聚類分析**（KMeans + PCA）
4. **支援 Top-K 相似問句回傳**（`limit=5`）
5. **比較不同模型查詢結果差異**

---

## 🧱 進階說明（講給工程師聽）

* FastEmbed 透過 Rust 編寫、效能非常好，內建多模型（無需 HuggingFace Token）
* `Qdrant` 支援 Remote Embedding，只要你指定 model 名稱，它會自動嵌入（伺服器有支援才行）
* 本地部署 Qdrant 時建議搭配 persistent volume 避免資料丟失
* 可改用 Milvus / Weaviate / Chroma 做類似功能（但語法不同）

當然可以！這裡用簡單易懂的方式說明：

---

## FastEmbed 和 Qdrant 各自負責什麼？

### 1. FastEmbed：負責「文字轉成向量」

* **工作內容**：把一段文字（像是句子、問題、文件）轉換成「向量（Vector）」。
* **為什麼要轉向量？**
  因為機器只能理解數字，要讓機器知道「文字的意思」，就需要用一組有意義的數字（向量）來表示。
* **怎麼做？**
  FastEmbed 是一個輕量級的文字嵌入工具，它內建了多個預訓練模型，可以快速且有效率地產生高品質的文字向量。
* **比喻**：
  就像把一段文章「翻譯」成一組坐標點，方便機器在「語意空間」裡比較兩段文字的距離（意思是否相近）。

---

### 2. Qdrant：負責「向量儲存與搜尋」

* **工作內容**：把 FastEmbed 做好的「向量」存起來，並提供快速的「相似度搜尋」。
* **為什麼要用它？**
  當你有成千上萬的向量，要快速找到跟查詢向量最接近的向量，純靠傳統資料庫查詢非常慢。Qdrant 專門針對這種高維度向量搜尋優化，可以秒級找到最相似的結果。
* **怎麼做？**
  Qdrant 建立一個叫做「向量資料庫」的空間，把向量按照某種距離（例如餘弦距離 Cosine Distance）做索引，當你給它一個查詢向量，它會快速回傳「最接近」的向量和對應的原始資料。
* **比喻**：
  就像一個巨大的「語意字典」，你給它一句話，它幫你找到字典裡意思最接近的那幾條目。

---

### 整合起來看：

* **FastEmbed** 是「翻譯官」：把文字翻譯成機器能懂的語意向量。
* **Qdrant** 是「圖書館管理員」：把這些向量整齊收納，當有人要找跟某句話意思相似的資料時，幫忙快速找出來。

---

如果要更簡短一句話：

> **FastEmbed 是把文字變成數字；Qdrant 是用數字幫你找最像的答案。**
