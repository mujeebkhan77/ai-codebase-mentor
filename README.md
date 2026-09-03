# AI Codebase Mentor

> **Understand any codebase by asking it questions.**

AI Codebase Mentor is an AI-powered developer tool that investigates real repositories and explains how the code works.

Instead of manually searching through files, functions, and call chains, you can connect a Git repository and ask questions in natural language. The system combines code indexing, semantic retrieval, symbol search, relationship analysis, evidence management, and an AI investigation loop to produce grounded technical explanations.

🌐 Live Demo
👉 https://ai-codebase-mentor-production.up.railway.app/

## Why I Built This

Understanding an unfamiliar codebase can take hours.

You have to find the right files, trace functions across modules, understand how pieces connect, and then build the bigger picture yourself.

AI Codebase Mentor is designed to reduce that process to a conversation with the codebase itself.

The goal is not just to generate an AI answer, but to make the answer **traceable to the actual code**.

---

## Features

### 🤖 AI Mentor

Ask natural-language questions about a repository.

The AI can investigate the codebase through multiple tools before generating its answer.

Responses can include:

* Direct explanation
* Execution flow
* Implementation details
* Supporting code evidence
* Iterations and tool calls
* Uncertainty and boundaries when the available evidence is insufficient

### 🔎 Multi-Strategy Code Search

The retrieval system combines multiple approaches:

* Semantic search
* Symbol search
* Literal/keyword search
* Relationship search

This allows questions to be answered even when the user does not know the exact function or file name.

### 🧩 Symbol Explorer

Search for functions, classes, and methods and jump directly to their source location.

### 🔗 Call Graph & Relationships

Explore how parts of the codebase connect through:

* Incoming callers
* Outgoing calls
* Class methods
* File symbols
* Multi-hop call chains

### 📂 Code Explorer

Browse the indexed repository and inspect source files with line-level navigation.

### 📌 Grounded Evidence

AI responses are backed by retrieved repository evidence.

The system tracks file paths and line ranges so developers can move from an explanation directly to the relevant source code.

### 🛡️ Repository Isolation

Each investigation is scoped to its active repository.

Retrieval, symbol search, relationship analysis, graph queries, manifests, and evidence handling respect repository boundaries to prevent cross-repository evidence leakage.

### ⚡ Persistent Investigation State

Moving between sections does not destroy the current investigation.

You can move from:

`AI Mentor → Code Explorer → Symbols → Call Graph`

and return without losing the active context.

Explicit **Jump to Code** actions can also override the current explorer selection and open the requested file and line range.

---

## How It Works

```text
Git Repository
      │
      ▼
   Clone / Fetch
      │
      ▼
     Index
      │
      ├── AST Code Chunks
      ├── Symbols
      ├── Relationships
      └── Repository Manifest
      │
      ▼
ChromaDB + Local Embeddings
      │
      ▼
 Retrieval Engine
      │
      ├── Semantic Search
      ├── Symbol Search
      ├── Literal Search
      └── Relationship Search
      │
      ▼
 Deterministic Ranking
      │
      ▼
 Evidence Manager
      │
      ▼
 Agent Investigation Loop
      │
      ▼
 Gemini
      │
      ▼
Grounded Technical Explanation
```

The backend uses a deterministic code-intelligence layer to retrieve and organize evidence before the LLM generates the final explanation. This keeps the system focused on the actual repository rather than relying only on the model's prior knowledge.

---

## AI Agent Architecture

The AI Mentor uses a manual investigation loop rather than a simple single-shot LLM call.

The agent maintains investigation state and can:

1. Understand the question
2. Retrieve relevant code
3. Search symbols and relationships
4. Inspect additional files when required
5. Collect and normalize evidence
6. Avoid unnecessary duplicate tool calls
7. Stop within bounded investigation limits
8. Generate a final evidence-grounded explanation

This makes the system closer to an **AI codebase investigator** than a conventional chatbot.

---

## Code Intelligence

The indexing pipeline extracts structure from the repository before questions are asked.

### AST-Based Chunking

Python source files are divided into meaningful code units such as:

* Functions
* Classes
* Methods

### Symbol Index

The system records symbol metadata including:

* Name
* Type
* File path
* Line range
* Class relationship where applicable

### Relationship Graph

The system extracts and resolves caller-callee relationships and supports graph queries such as:

```text
get_outgoing_calls()
get_incoming_callers()
get_class_methods()
get_file_symbols()
get_call_chain()
```

### Repository Manifest

A deterministic repository manifest stores information such as:

* Languages
* Entry points
* Configuration files
* Source/test directories
* Symbol statistics
* Relationship statistics

---

## Tech Stack

### Backend

* Python
* FastAPI
* ChromaDB
* Sentence Transformers
* `BAAI/bge-small-en-v1.5`
* Gemini
* GitPython
* Pydantic

### Frontend

* React 19
* TypeScript
* Vite
* Tailwind CSS
* Lucide React

### Deployment

* GitHub
* Railway

---

## Project Structure

```text
ai-codebase-mentor/
│
├── backend/
│   ├── agent/
│   ├── api/
│   ├── embeddings/
│   ├── evidence/
│   ├── graph/
│   ├── indexing/
│   ├── retrieval/
│   ├── tests/
│   ├── tools/
│   ├── utils/
│   ├── vectorstore/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── lib/
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

---

## Example

Suppose a repository contains an e-commerce product flow.

You can ask:

> How does the product move from the shop page to the cart?

The system can trace a flow such as:

```text
shop.html
   ↓
viewDetails(id)
   ↓
localStorage
   ↓
product.html
   ↓
addToCart(id)
   ↓
cart state
   ↓
localStorage
```

It can then provide the explanation together with the source files and relevant line ranges.

---

## Testing

The backend includes a deterministic test suite covering core functionality such as:

* AST chunking
* Repository indexing
* Embeddings
* Retrieval
* Ranking
* Symbol extraction
* Relationship extraction
* Evidence management
* Agent state and limits
* Repository manifests
* Code graph traversal
* Caching
* Tool execution
* Error handling

The deterministic backend tests are designed to run without consuming Gemini API quota.

### Backend

```bash
cd backend

python -m pytest tests/
```

### Frontend

```bash
cd frontend

npm install
npm run build
```

---

## Environment Variables

The backend requires a Gemini API key for AI-generated explanations:

For the frontend, the production API endpoint can be configured with:

Do not commit API keys or other secrets to the repository.

---

## Running Locally

### Backend

```bash
cd backend

python -m venv .venv
```

Activate the virtual environment, install dependencies, configure the environment variables, then start FastAPI:

```bash
uvicorn api.app:app --reload
```

### Frontend

```bash
cd frontend

npm install
npm run dev
```

---

## What I Learned Building This

This project was built as a practical way to explore modern AI engineering concepts rather than only experimenting with LLM APIs.

The project involved working with:

* RAG and semantic retrieval
* Vector databases
* Code embeddings
* AI agent loops
* Tool calling
* Code graphs
* Evidence-grounded generation
* Repository isolation
* Deterministic ranking
* Production deployment
* Memory optimization
* Frontend state management

One of the next areas for the project is exposing the existing code-intelligence tools through **MCP (Model Context Protocol)**.

---

## Current Status

AI Codebase Mentor is currently deployed with a working frontend and backend.

The production system has been tested against real repositories, including a Universal RAG application and an e-commerce project, to verify cross-file reasoning, symbol lookup, relationships, evidence grounding, and source navigation.

---

## Future Direction

The project can evolve toward a more complete AI software engineering environment with capabilities such as:

* MCP-based tool integration
* More advanced code graphs
* Deeper cross-language support
* Persistent repository storage
* Improved repository indexing
* More specialized developer workflows
* Code review and debugging assistance

---

## Author

**Majeeb**

Software Engineering student building practical AI systems and developer tools.

[GitHub](https://github.com/mujeebkhan77)
