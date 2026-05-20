搭建一个具备“上下文意识”的 RAG Agent，本质上是给传统的搜索流程加上一个**大脑（控制器）**。

这份文档将指导你如何从零开始，使用 **LangChain** 框架和 **Query Rewriting（查询重写）** 技术，实现你所描述的连贯问答功能。

---

## 技术文档：从零构建上下文感知型 RAG Agent

### 1. 核心原理
普通 RAG 失败的原因是向量检索（Vector Search）是**静态**的。Agent 的改进在于引入了**多轮对话改写逻辑**：
1. **输入分析**：接收用户当前问题和历史对话。
2. **问题重写**：LLM 将“那他的棍子叫什么”重写为“孙悟空的武器叫什么”。
3. **检索增强**：使用重写后的完整语义进行 Embedding 检索。
4. **答案生成**：结合上下文和检索到的片段生成回答。



---

### 2. 技术栈建议
* **LLM**: GPT-4o 或 Claude 3.5 Sonnet（逻辑推理能力强，适合改写问题）。
* **向量库**: Pinecone, Milvus 或本地的 ChromaDB。
* **框架**: LangChain 或 LlamaIndex。
* **内存管理**: `ConversationBufferWindowMemory`（保留最近 $K$ 轮对话）。

---

### 3. 核心实现步骤

#### 第一步：环境准备
```python
pip install langchain langchain-openai chromadb
```

#### 第二步：定义“问题重写”提示词
这是 Agent 处理第二句问话的关键。我们需要告诉 LLM：如果是追问，请补全主体。

```python
REWRITE_PROMPT = """
基于以下对话历史和用户提出的新问题，
请生成一个“独立的、语义完整的”检索语句，
确保即使没有上下文，搜索系统也能明白你在搜什么。

对话历史:
{chat_history}

用户新问题: {question}

独立问题:"""
```

#### 第三步：构建 Agent 工作流
这里我们模拟一个简单的逻辑链：

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferWindowMemory

# 1. 初始化模型和记忆
llm = ChatOpenAI(model="gpt-4o")
memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history")

# 2. 查询重写环节
def get_standalone_question(user_input):
    history = memory.load_memory_variables({})["chat_history"]
    if not history:
        return user_input
    
    prompt = REWRITE_PROMPT.format(chat_history=history, question=user_input)
    standalone_question = llm.predict(prompt)
    return standalone_question

# 4. 执行流程展示
# 问：孙悟空的诨名是什么？ -> 重写：孙悟空的诨名是什么？ -> 检索并回答：孙行者
# 问：那他的棍子叫什么？ -> 重写：孙悟空的武器是什么？ -> 检索并回答：如意金箍棒
```

---

### 4. 关键点优化（避坑指南）

#### 1. 阈值控制 (Self-Correction)
并不是所有问题都需要重写。如果用户问的是“今天天气不错”，重写可能会弄巧成拙。建议在 Prompt 中加入：`“如果问题已经是独立的，请原样返回”`。

#### 2. 知识库的粒度
“孙悟空”的资料可能分散在《西游记》全文中。
* **建议**：使用 **RecursiveCharacterTextSplitter** 进行切片，并保持块与块之间有 10%-20% 的重叠（Overlap），确保语义不被切断。

#### 3. 引入 Re-rank（重排序）
检索回来的前 5 个片段，不一定都是最精准的。在检索后加入一个 **Rerank 模型**（如 BGE-Reranker），可以显著提升答案的准确度。

---

### 5. 预期效果对比

#### 目标：
比如问 “孙悟空的诨名是什么”
    答：“孙行者”
    问：“那他的棍子叫什么”
    答：“如意金箍棒”

| 特性 | 普通 RAG | 我们的 RAG Agent |
| :--- | :--- | :--- |
| **首问** (孙悟空是谁) | ✅ 准确 | ✅ 准确 |
| **指代消解** (他的/那个) | ❌ 检索失败，无法回答 | ✅ 自动补全为“孙悟空的” |
| **省略句处理** (那武器呢) | ❌ 语义缺失 | ✅ 自动识别为“查询武器” |

---

### 总结
要实现准确的问答检索，不能只靠增加数据，必须**给 LLM 赋予处理对话状态的能力**。通过“重写问题 + 记忆管理”这两步，你就能解决 90% 以上的多轮检索失效问题。
