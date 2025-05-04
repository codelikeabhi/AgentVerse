# AgentVerse

![AgentVerse Logo](https://github.com/Kunj1/AgentVerse/blob/main/AGENTVERSE.png)

## AI-Powered Project Risk Management System

AgentVerse is an advanced project risk management platform that leverages AI to identify, assess, and mitigate project risks in real-time. The system uses multiple intelligent agents to analyze data from various sources and provide actionable insights for project managers and leadership teams.

## 🌟 Features

- **Real-time Risk Analysis**: Continuously monitors internal and external factors affecting project health
- **Multi-Agent System**: Uses specialized AI agents for different aspects of risk assessment
- **Interactive Chat Interface**: Talk directly with the system to get risk insights
- **Rich Visualizations**: Comprehensive dashboards showing risk trends, health scores, and timelines
- **File-Based Analysis**: Upload project data for detailed risk evaluation

## 📊 Dashboard & Visualization

AgentVerse provides rich visual analytics including:
- Project Health Score gauge
- Risk breakdown by category
- Risk evaluation charts (Probability vs. Impact)
- Risk trend analysis over time
- Project timeline visualization
- Risk mitigation recommendations

## 🤖 Agent Framework

The system employs multiple specialized agents:
- **Project Risk Manager**: Overall owner of risk analysis and mitigation
- **Market Analysis Agent**: Analyzes financial trends and external market factors
- **Risk Scoring Agent**: Assesses and quantifies project risks
- **Project Status Tracking Agent**: Monitors internal project metrics and milestones
- **Reporting Agent**: Generates insights and alerts for stakeholders

## 🛠️ Tech Stack

### Frontend
- **Streamlit**: Interactive web application framework
- **Plotly**: Advanced data visualization
- **Pandas**: Data manipulation and analysis

### Backend
- **FastAPI**: High-performance API framework
- **MongoDB**: Document database for storing project data and chat history
- **Google Gemini API**: AI models for intelligent analysis and conversation

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- pip
- Access to MongoDB
- Google Gemini API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/agentverse.git
cd agentverse
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

### Running Locally

#### Frontend
```bash
cd frontend
streamlit run app.py
```

## 🔄 API Endpoints

- `GET /projects/`: List all projects
- `POST /projects/`: Create a new project
- `POST /chat/init/{project_id}`: Initialize chat with project data files
- `POST /chat/continue/{project_id}`: Continue conversation with the AI
- `GET /chats/{project_id}`: Get chat history for a project

## 📁 File Uploads

The system requires the following CSV files for comprehensive risk analysis:
- **Employee Data**: Resource allocation and availability
- **Project Data**: Timeline, milestones, and deliverables
- **Financial Data**: Budget, expenses, and financial risks

## 📱 Deployment

- Frontend: [https://agentversebycorpusbound.streamlit.app/](https://agentversebycorpusbound.streamlit.app/)
- Backend API: [https://agentverse-uz89.onrender.com](https://agentverse-uz89.onrender.com)

## Github Repositories

- **Frontend**: [https://github.com/Kunj1/AgentVerse](https://github.com/Kunj1/AgentVerse)
- **Backend**: [https://github.com/Kunj1/risk_management](https://github.com/Kunj1/risk_management)

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please open an issue or contact the repository owner.

---

Made with ❤️ by CorpusBound Team
