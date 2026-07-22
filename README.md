# 🏦 AI Banking Agents

A comprehensive multi-agent system built for banking operations, featuring specialized agents for task management, CRM, and reporting with both API and interactive UI interfaces.

## 📋 Project Overview

This project implements an AI-powered banking system with multiple specialized agents that work together to streamline banking operations. The system provides both a FastAPI backend and a Streamlit web interface for interactive banking workflows.

## 🎯 Key Features

- **Multi-Agent Architecture**: Three specialized agents for different banking operations
  - **Task Agent**: Manages and tracks banking tasks
  - **CRM Agent**: Handles customer relationship management
  - **Reporting Agent**: Generates banking reports and analytics
  
- **Dual Interface**:
  - 🔌 FastAPI backend for programmatic access
  - 🎨 Streamlit frontend for interactive dashboards

- **RAG Integration**: Retrieval-Augmented Generation support with FAISS indexing

- **Database Support**: SQLite-based persistence for test and production data

## 📁 Project Structure

```
AI_Agents/
├── CRM_Agent/              # Customer Relationship Management Agent
├── Task_Agent/             # Task Management Agent
├── Reporting_Agent/        # Reporting and Analytics Agent
├── pages/                  # Streamlit UI pages
├── shared/                 # Shared utilities and database initialization
├── tests/                  # Unit and integration tests
├── main.py                 # FastAPI application entry point
├── streamlit_app.py        # Streamlit UI entry point
├── requirements.txt        # Python dependencies
├── faiss_index.bin         # FAISS vector index for RAG
├── test.db                 # Test database
├── pytest_test.db          # Pytest testing database
└── app.log                 # Application logs
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ayeshazaf/AI_Agents.git
   cd AI_Agents
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   python -c "import shared.init_db"
   ```

### Running the Application

#### Option 1: FastAPI Backend

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

#### Option 2: Streamlit UI

```bash
streamlit run streamlit_app.py
```

The UI will be available at `http://localhost:8501`

#### Option 3: Run as Script

```bash
python main.py
```

## 📊 Agent Descriptions

### Task Agent
Manages banking tasks including:
- Task creation and assignment
- Task status tracking
- Task scheduling and reminders

**API Endpoint**: `/task/`

### CRM Agent
Handles customer relationships:
- Customer data management
- Interaction tracking
- Customer segmentation

**API Endpoint**: `/crm/`

### Reporting Agent
Generates banking reports:
- Sales reports
- Performance analytics
- Compliance reporting

**API Endpoint**: `/reporting/`

## 🧠 RAG System

The project includes a Retrieval-Augmented Generation (RAG) system powered by FAISS for intelligent document retrieval and question-answering capabilities.

- **Vector Index**: `faiss_index.bin`
- **RAG Page**: Available in Streamlit UI

## 🧪 Testing

Run tests using pytest:

```bash
pytest tests/
```

Tests use a dedicated database (`pytest_test.db`) to ensure isolation from production data.

## 📦 API Endpoints

The FastAPI application exposes the following routers:

- **Task Agent Router**: `/task/*` - Task-related operations
- **CRM Agent Router**: `/crm/*` - CRM-related operations  
- **Reporting Agent Router**: `/reporting/*` - Reporting operations

## 🛠️ Technology Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Database**: SQLite
- **Vector Search**: FAISS
- **Language**: Python

## 📝 Logging

Application logs are written to `app.log` for debugging and monitoring purposes.

## 🤝 Contributing

1. Create a new branch for your feature
2. Make your changes
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**Ayeshazaf**

- GitHub: [@Ayeshazaf](https://github.com/Ayeshazaf)
- Repository: [AI_Agents](https://github.com/Ayeshazaf/AI_Agents)

## 🔗 Related Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FAISS Documentation](https://faiss.ai/)

---

**Last Updated**: July 2026

For more information or issues, please visit the [GitHub Issues](https://github.com/Ayeshazaf/AI_Agents/issues) page.
