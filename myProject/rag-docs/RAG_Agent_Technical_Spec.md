# 高召回率 RAG Agent 技术规范

## 项目概述

### 目标
构建一个具备**高召回率**（>70%）的上下文感知型 RAG Agent，支持中英混合知识库，能够处理复杂的多轮对话场景。

### 核心价值
- **高召回率**：相比普通RAG提升40%以上的信息召回率
- **上下文感知**：通过查询重写技术处理多轮对话的指代消解
- **中英混合支持**：优化的多语言检索策略
- **可扩展性**：支持中等规模（1万-100万文档）知识库

---

## 技术架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG Agent System                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   用户输入   │ -> │  查询重写   │ -> │  多查询生成  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                           ↓                   ↓             │
│                  ┌─────────────────────────────────┐        │
│                  │        混合检索引擎              │        │
│                  │  ┌─────────┐    ┌─────────┐    │        │
│                  │  │ 向量检索 │ +  │ BM25检索 │   │        │
│                  │  └─────────┘    └─────────┘    │        │
│                  └─────────────────────────────────┘        │
│                           ↓                                  │
│                  ┌─────────────────────────────────┐        │
│                  │         重排序引擎               │        │
│                  └─────────────────────────────────┘        │
│                           ↓                                  │
│                  ┌─────────────────────────────────┐        │
│                  │      上下文组装与生成            │        │
│                  └─────────────────────────────────┘        │
│                           ↓                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   答案输出   │ <- │  答案生成   │ <- │  记忆管理    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈选型

#### 核心组件
| 组件 | 技术选型 | 说明 |
|------|----------|------|
| **LLM** | Claude 3.5 Sonnet / GPT-4o | 主推理模型 |
| **Embedding** | BGE-M3 | 中英混合支持，多语言优化 |
| **向量数据库** | ChromaDB / Milvus | 本地开发用ChromaDB，生产用Milvus |
| **关键词检索** | BM25 (rank_bm25) | 补充向量检索的不足 |
| **重排序** | BGE-Reranker-v2-m3 | 精准排序，提升最终准确率 |
| **框架** | LangChain + LlamaIndex | LangChain用于流程编排，LlamaIndex用于检索优化 |

#### 辅助工具
- **文档处理**: LangChain TextSplitter, Unstructured
- **评估**: RAGAS, TruLens
- **监控**: LangSmith, Weights & Biases

---

## 高召回率策略详解

### 1. 多查询策略 (Multi-Query Strategy)

#### 原理
将用户问题扩展为3-5个语义相同但表述不同的查询，每个查询独立检索，最后合并结果。

#### 实现逻辑
```python
# 示例：用户问"孙悟空的武器"
原始问题: "孙悟空的武器"
↓ LLM生成扩展查询
扩展查询: [
  "孙悟空的兵器是什么",
  "如意金箍棒",
  "美猴王的法宝",
  "孙悟空手持的物品"
]
↓ 并行检索
合并去重 → 重排序 → 返回Top-K结果
```

#### 提升效果
- **召回率提升**: 30-50%
- **适用场景**: 专业术语、同义词、缩写等

### 2. 混合检索 (Hybrid Search)

#### 原理
结合向量检索（语义理解）和BM25检索（关键词匹配），融合两者的优势。

#### 实现逻辑
```python
# 向量检索
vector_results = vector_store.similarity_search(query, k=20)

# BM25检索
bm25_results = bm25_search(query, k=20)

# 结果融合 (RRF - Reciprocal Rank Fusion)
final_results = reciprocal_rank_fusion(vector_results, bm25_results)
```

#### RRF算法
```python
def reciprocal_rank_fusion(results1, results2, k=60):
    scores = {}
    for rank, doc in enumerate(results1):
        scores[doc.id] = scores.get(doc.id, 0) + 1 / (k + rank + 1)
    
    for rank, doc in enumerate(results2):
        scores[doc.id] = scores.get(doc.id, 0) + 1 / (k + rank + 1)
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

#### 提升效果
- **召回率提升**: 20-40%
- **特别适合**: 专业术语、型号编号等精确匹配场景

### 3. 递归检索 (Recursive Retrieval)

#### 原理
使用小文档块进行精准检索，但返回包含该块的父文档，提供更完整的上下文。

#### 实现逻辑
```python
# 文档结构
父文档: 完整章节
  └── 子文档: 200-500字小块

# 检索流程
1. 在子文档中检索 (精准匹配)
2. 找到相关子文档后，返回其父文档
3. 使用父文档的完整上下文生成答案
```

#### 提升效果
- **召回率提升**: 15-25%
- **上下文完整性**: 显著提升

### 4. 句子窗口检索 (Sentence Window Retrieval)

#### 原理
索引时按句子切分，检索时返回目标句子及其周围的句子。

#### 实现逻辑
```python
# 索引阶段
sentences = split_into_sentences(document)
for sentence in sentences:
    index(sentence)  # 单句索引

# 检索阶段
matched_sentence = search(query)
context_window = get_surrounding_sentences(matched_sentence, window_size=3)
```

#### 提升效果
- **召回率提升**: 10-20%
- **上下文连贯性**: 更好

### 5. 查询重写 (Query Rewriting)

#### 原理
基于对话历史，将当前问题重写为语义完整的独立问题。

#### 实现示例
```
对话历史:
User: 孙悟空的诨名是什么？
AI: 孙行者

User: 那他的棍子叫什么？
↓ LLM重写
重写后问题: "孙悟空的武器是什么？"
↓ 检索并回答
AI: 如意金箍棒
```

#### 提升效果
- **多轮对话召回率提升**: 40-60%
- **指代消解准确率**: 90%+

---

## 实现指南

### 项目结构

```
ragAgent/
├── data/                      # 知识库数据
│   ├── raw/                   # 原始文档
│   └── processed/             # 处理后的文档
├── embeddings/                # 向量存储
├── logs/                      # 日志文件
├── src/
│   ├── core/                  # 核心模块
│   │   ├── agent.py           # Agent控制器
│   │   ├── retriever.py       # 检索器
│   │   └── memory.py          # 记忆管理
│   ├── strategies/            # 检索策略
│   │   ├── multi_query.py     # 多查询策略
│   │   ├── hybrid_search.py   # 混合检索
│   │   ├── recursive.py       # 递归检索
│   │   └── sentence_window.py # 句子窗口检索
│   ├── processing/            # 数据处理
│   │   ├── chunking.py        # 文档分块
│   │   ├── embedding.py       # 向量化
│   │   └── reranking.py       # 重排序
│   ├── evaluation/            # 评估模块
│   │   ├── metrics.py         # 评估指标
│   │   └── test_cases.py      # 测试用例
│   └── utils/                 # 工具函数
│       ├── config.py          # 配置管理
│       └── logger.py          # 日志管理
├── tests/                     # 测试文件
├── config.yaml                # 配置文件
├── requirements.txt           # 依赖包
└── README.md                  # 项目说明
```

### 核心代码示例

#### 1. 配置管理 (config.yaml)
```yaml
# 模型配置
models:
  llm:
    model: "claude-3-5-sonnet-20241022"
    temperature: 0.7
    max_tokens: 2000
  
  embedding:
    model: "BAAI/bge-m3"
    dimension: 1024
  
  reranker:
    model: "BAAI/bge-reranker-v2-m3"

# 检索配置
retrieval:
  chunk_size: 512
  chunk_overlap: 50
  
  hybrid_search:
    vector_weight: 0.7
    bm25_weight: 0.3
    top_k: 20
  
  multi_query:
    num_queries: 4
    expand_threshold: 0.6
  
  reranking:
    top_k: 5

# 向量数据库配置
vector_db:
  type: "chromadb"  # chromadb or milvus
  collection_name: "knowledge_base"
  
# 记忆配置
memory:
  type: "buffer_window"
  window_size: 5
```

#### 2. Agent控制器 (src/core/agent.py)
```python
class RAGAgent:
    def __init__(self, config):
        self.config = config
        self.llm = ChatOpenAI(model=config.models.llm.model)
        self.memory = ConversationBufferWindowMemory(k=config.memory.window_size)
        self.retriever = HybridRetriever(config)
        self.reranker = Reranker(config)
        
    async def query(self, user_input: str) -> str:
        # 1. 获取对话历史
        history = self.memory.load_memory_variables({})["chat_history"]
        
        # 2. 查询重写
        rewritten_query = await self._rewrite_query(user_input, history)
        
        # 3. 多查询生成
        expanded_queries = await self._generate_multi_query(rewritten_query)
        
        # 4. 混合检索
        results = await self.retriever.retrieve(expanded_queries)
        
        # 5. 重排序
        reranked_results = await self.reranker.rerank(rewritten_query, results)
        
        # 6. 答案生成
        context = self._assemble_context(reranked_results)
        answer = await self._generate_answer(user_input, context, history)
        
        # 7. 更新记忆
        self.memory.save_context({"input": user_input}, {"output": answer})
        
        return answer
    
    async def _rewrite_query(self, query: str, history: str) -> str:
        """查询重写"""
        rewrite_prompt = ChatPromptTemplate.from_messages([
            ("system", "基于对话历史，将用户问题重写为语义完整的独立问题。"),
            ("human", "对话历史: {history}\n\n问题: {query}\n\n重写后的问题:")
        ])
        
        chain = rewrite_prompt | self.llm | StrOutputParser()
        return await chain.ainvoke({"history": history, "query": query})
    
    async def _generate_multi_query(self, query: str) -> List[str]:
        """多查询生成"""
        multi_query_prompt = ChatPromptTemplate.from_messages([
            ("system", "生成3-5个语义相同但表述不同的查询，用换行符分隔。"),
            ("human", "原始问题: {query}\n\n生成的查询:")
        ])
        
        chain = multi_query_prompt | self.llm | StrOutputParser()
        result = await chain.ainvoke({"query": query})
        return [q.strip() for q in result.split('\n') if q.strip()]
```

#### 3. 混合检索器 (src/strategies/hybrid_search.py)
```python
class HybridRetriever:
    def __init__(self, config):
        self.config = config
        self.vector_store = ChromaDB(
            embedding_function=embedding_function,
            collection_name=config.vector_db.collection_name
        )
        self.bm25 = BM25Retriever()
        
    async def retrieve(self, queries: List[str]) -> List[Document]:
        all_results = []
        
        for query in queries:
            # 向量检索
            vector_results = self.vector_store.similarity_search(
                query, 
                k=self.config.retrieval.hybrid_search.top_k
            )
            
            # BM25检索
            bm25_results = self.bm25.search(
                query,
                k=self.config.retrieval.hybrid_search.top_k
            )
            
            # 结果融合
            fused_results = self._reciprocal_rank_fusion(
                vector_results, 
                bm25_results
            )
            all_results.extend(fused_results)
        
        # 去重
        unique_results = self._deduplicate(all_results)
        return unique_results[:self.config.retrieval.hybrid_search.top_k]
    
    def _reciprocal_rank_fusion(self, results1, results2, k=60):
        """RRF融合算法"""
        scores = {}
        
        for rank, doc in enumerate(results1):
            doc_id = doc.metadata.get('id', id(doc))
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        
        for rank, doc in enumerate(results2):
            doc_id = doc.metadata.get('id', id(doc))
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
        
        # 按分数排序
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # 返回排序后的文档
        doc_map = {doc.metadata.get('id', id(doc)): doc for doc in results1 + results2}
        return [doc_map[doc_id] for doc_id, _ in sorted_docs]
```

---

## 评估指标体系

### 召回率指标

#### 1. 检索召回率 (Retrieval Recall)
```python
# 计算公式
检索召回率 = (检索到的相关文档数 / 总相关文档数) × 100%

# 目标值
- 首轮查询: > 70%
- 多轮对话: > 60%
```

#### 2. 上下文精确度 (Context Precision)
```python
# 计算公式
上下文精确度 = (检索到的文档中有多少是相关的) / 总检索文档数

# 目标值
- 目标: > 0.75
```

#### 3. 答案相关性 (Answer Relevancy)
```python
# 计算方法
使用LLM判断生成答案与用户问题的相关程度

# 目标值
- 目标: > 0.80
```

### 评估工具

#### 使用RAGAS进行评估
```python
from ragas import evaluate
from ragas.metrics import (
    context_recall,
    context_precision,
    answer_relevancy
)

# 准备测试数据
test_data = {
    "question": ["问题1", "问题2", ...],
    "answer": ["答案1", "答案2", ...],
    "contexts": [["上下文1", "上下文2"], ...],
    "ground_truth": ["标准答案1", "标准答案2", ...]
}

# 运行评估
result = evaluate(
    test_data,
    metrics=[
        context_recall,
        context_precision,
        answer_relevancy
    ]
)

print(result)
```

### 性能指标

#### 响应时间
- 简单查询: < 3秒
- 复杂查询: < 8秒
- 多轮对话: < 5秒

#### 并发支持
- 单实例: 10+ QPS
- 水平扩展: 支持

---

## 部署建议

### 开发环境

#### 本地部署
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export OPENAI_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"

# 启动服务
python src/main.py
```

### 生产环境

#### Docker部署
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
```

#### Kubernetes配置
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-agent
  template:
    metadata:
      labels:
        app: rag-agent
    spec:
      containers:
      - name: rag-agent
        image: rag-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
```

### 监控与日志

#### 监控指标
- 检索延迟
- 生成延迟
- 端到端延迟
- 召回率趋势
- 错误率

#### 日志记录
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/rag_agent.log'),
        logging.StreamHandler()
    ]
)

# 使用示例
logger = logging.getLogger(__name__)
logger.info(f"Query: {query}, Recall: {recall_score}, Latency: {latency}ms")
```

---

## 优化路线图

### 阶段1：基础实现 (2-3周)
- [ ] 基础RAG系统
- [ ] 查询重写功能
- [ ] 混合检索
- [ ] 基础评估体系

### 阶段2：召回率优化 (3-4周)
- [ ] 多查询策略
- [ ] 递归检索
- [ ] 句子窗口检索
- [ ] 重排序优化

### 阶段3：性能优化 (2-3周)
- [ ] 缓存机制
- [ ] 并行处理
- [ ] 批量检索
- [ ] 查询优化

### 阶段4：生产部署 (1-2周)
- [ ] 容器化
- [ ] 负载均衡
- [ ] 监控告警
- [ ] 安全加固

---

## 成本预估

### 开发成本
- 开发人员：2-3人
- 开发周期：8-12周
- 人力成本：根据地区标准

### 运营成本

#### API调用成本
- Embedding: 每100万token约$0.1
- LLM生成: 每100万token约$3-10
- 重排序: 每100万token约$0.5

#### 存储成本
- 向量数据库: 每100万文档约2-4GB
- 存储成本: 约$0.02-0.05/GB/月

#### 总成本预估 (月活10万用户)
- API调用: $500-2000/月
- 存储成本: $100-500/月
- 总计: $600-2500/月

---

## 总结

本技术规范构建了一个**高召回率、上下文感知**的RAG Agent系统，通过以下核心策略实现：

1. **多查询策略**：从多个角度检索，提升召回率30-50%
2. **混合检索**：结合语义和关键词检索，提升召回率20-40%
3. **递归检索**：平衡精准度和上下文完整性，提升召回率15-25%
4. **句子窗口检索**：提供连贯上下文，提升召回率10-20%
5. **查询重写**：处理多轮对话，提升召回率40-60%

**预期综合效果**：
- 检索召回率: **70-90%**
- 多轮对话准确率: **85%+**
- 响应时间: **3-8秒**

该系统特别适合**中英混合知识库、中等规模、高召回率要求**的应用场景。