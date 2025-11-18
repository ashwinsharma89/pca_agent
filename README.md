# Post Campaign Analysis (PCA) Agentic System

An AI-powered system for automated campaign performance analysis across multiple advertising platforms using Vision Language Models (VLMs), Large Language Models (LLMs), and agentic reasoning.

## Features

### 🎯 Core Capabilities
- **Multi-Platform Support**: Google Ads, CM360, DV360, Meta Ads, Snapchat Ads, LinkedIn Ads
- **Vision-Based Extraction**: Extract metrics, graphs, and tables from dashboard screenshots
- **Agentic Reasoning**: Cross-channel analysis, attribution modeling, achievement detection
- **Automated Report Generation**: PowerPoint reports with data, visuals, and insights
- **API-First Design**: RESTful API for programmatic access

### 🤖 AI Agents
1. **Vision Agent**: Extract data from dashboard screenshots using GPT-4V/Claude Sonnet 4
2. **Data Extraction Agent**: Normalize and validate multi-platform data
3. **Reasoning Agent**: Generate insights, detect achievements, provide recommendations
4. **Visualization Agent**: Create charts, infographics, and comparison visuals
5. **Report Assembly Agent**: Generate branded PowerPoint reports

### 📊 Supported Platforms
- **Google Ads**: Search, Display, Video campaigns
- **Campaign Manager 360 (CM360)**: Display campaign metrics
- **Display & Video 360 (DV360)**: Programmatic buying
- **Meta Ads**: Facebook, Instagram campaigns
- **Snapchat Ads**: Story ads, lens engagement
- **LinkedIn Ads**: B2B lead generation

## Architecture

```
API Gateway (FastAPI)
    ↓
Orchestration Layer (LangGraph)
    ↓
┌─────────┬──────────┬──────────┬──────────┬────────────┐
│ Vision  │ Data     │ Reasoning│ Visual   │ Report Gen │
│ Agent   │ Extract  │ Agent    │ Gen      │ Agent      │
└─────────┴──────────┴──────────┴──────────┴────────────┘
    ↓
Storage (PostgreSQL + Redis + S3)
```

## Tech Stack

- **AI/ML**: OpenAI GPT-4V, Anthropic Claude Sonnet 4, LangGraph, LangChain
- **Backend**: FastAPI, Python 3.11+, Celery, Redis
- **Database**: PostgreSQL, Redis
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Report Generation**: python-pptx, ReportLab
- **Image Processing**: OpenCV, Pillow, Tesseract OCR
- **Frontend**: Streamlit (demo dashboard)

## Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Add your API keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### 3. Run API Server

```bash
# Start FastAPI server
uvicorn src.api.main:app --reload --port 8000
```

### 4. Run Streamlit Dashboard

```bash
# Start demo dashboard
streamlit run streamlit_app.py
```

## Usage

### API Workflow

```python
import requests

# 1. Create campaign analysis job
response = requests.post("http://localhost:8000/api/campaigns", json={
    "campaign_name": "Q4 2024 Holiday Campaign",
    "objectives": ["awareness", "conversion"],
    "date_range": {"start": "2024-10-01", "end": "2024-12-31"}
})
campaign_id = response.json()["campaign_id"]

# 2. Upload dashboard snapshots
files = [
    ("files", open("google_ads_dashboard.png", "rb")),
    ("files", open("meta_ads_dashboard.png", "rb")),
    ("files", open("linkedin_ads_dashboard.png", "rb"))
]
requests.post(f"http://localhost:8000/api/campaigns/{campaign_id}/snapshots", files=files)

# 3. Check status
status = requests.get(f"http://localhost:8000/api/campaigns/{campaign_id}/status")
print(status.json())

# 4. Download report
report = requests.get(f"http://localhost:8000/api/campaigns/{campaign_id}/report")
with open("campaign_report.pptx", "wb") as f:
    f.write(report.content)
```

### Streamlit Dashboard

1. Upload dashboard screenshots (drag & drop)
2. Select campaign objectives and date range
3. Click "Analyze Campaign"
4. View extracted data, insights, and visualizations
5. Download PowerPoint report

## Project Structure

```
PCA_Agent/
├── src/
│   ├── agents/              # AI agents
│   │   ├── vision_agent.py
│   │   ├── extraction_agent.py
│   │   ├── reasoning_agent.py
│   │   ├── visualization_agent.py
│   │   └── report_agent.py
│   ├── api/                 # FastAPI endpoints
│   │   ├── main.py
│   │   └── routes/
│   ├── models/              # Data models
│   │   ├── campaign.py
│   │   ├── platform.py
│   │   └── report.py
│   ├── orchestration/       # LangGraph workflows
│   │   └── workflow.py
│   ├── utils/               # Utilities
│   │   ├── image_processor.py
│   │   ├── chart_generator.py
│   │   └── logger.py
│   └── config/              # Configuration
│       └── settings.py
├── templates/               # Report templates
│   └── ppt_templates/
├── tests/                   # Unit tests
├── data/                    # Sample data
│   └── sample_dashboards/
├── streamlit_app.py         # Demo dashboard
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

### Campaign Management
- `POST /api/campaigns` - Create new campaign analysis
- `GET /api/campaigns/{id}` - Get campaign details
- `DELETE /api/campaigns/{id}` - Delete campaign

### Snapshot Upload
- `POST /api/campaigns/{id}/snapshots` - Upload dashboard screenshots
- `GET /api/campaigns/{id}/snapshots` - List uploaded snapshots

### Analysis & Reports
- `GET /api/campaigns/{id}/status` - Check processing status
- `GET /api/campaigns/{id}/data` - Get extracted data (JSON)
- `GET /api/campaigns/{id}/insights` - Get AI-generated insights
- `GET /api/campaigns/{id}/report` - Download PowerPoint report
- `POST /api/campaigns/{id}/regenerate` - Regenerate report with new template

## Examples

### Supported Dashboard Formats
- PNG, JPG, JPEG (screenshots)
- PDF (exported reports)
- Multi-page PDFs (automatically split)

### Extracted Metrics
- **Performance**: Impressions, Clicks, CTR, Conversions, CPA, ROAS
- **Engagement**: Likes, Shares, Comments, Video Views, Completion Rate
- **Audience**: Demographics, Interests, Device, Location
- **Creative**: Ad format performance, A/B test results

### Generated Insights
- Channel performance comparison
- Budget efficiency analysis
- Attribution modeling (first-touch, last-touch, multi-touch)
- Audience segment analysis
- Creative performance ranking
- Trend analysis and forecasting
- Actionable recommendations

## Development

### Run Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.
