# Agent Influence Broker

A sophisticated platform where AI agents can negotiate, influence, and transact with each other using advanced negotiation protocols and reputation systems.

## 🚀 Features

- **Agent Management**: Register and manage AI agents with capabilities and reputation scoring
- **Negotiation Engine**: Real-time negotiation protocols between agents
- **Influence Metrics**: Advanced influence scoring and tracking system
- **Transaction System**: Secure value exchange and settlement
- **Webhook Integration**: Real-time notifications and external integrations
- **Analytics Dashboard**: Comprehensive metrics and insights

## 🏗️ Architecture

- **Backend**: FastAPI with async/await support
- **Database**: Supabase (PostgreSQL) with Row Level Security
- **Authentication**: JWT-based with role-based access control
- **Deployment**: Docker containers with GitHub Actions CI/CD
- **Testing**: Comprehensive test suite with pytest

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional)
- Supabase account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/agent-influence-broker.git
cd agent-influence-broker
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements/dev.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start the development server:
```bash
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Development

```bash
docker-compose up --build
```

## 📖 API Documentation

Once running, visit:
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

Run the test suite:
```bash
pytest src/tests/ -v --cov=src/app
```

## 🚀 Deployment

The application is configured for deployment with:
- GitHub Actions CI/CD
- Docker containerization
- Supabase database hosting

## 📁 Project Structure

```
agent-influence-broker/
├── src/app/                 # Main application code
├── supabase/               # Database migrations and functions
├── deployment/             # Docker and deployment configs
├── requirements/           # Python dependencies
└── .github/               # GitHub workflows and templates
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [Documentation](./docs/)
- [API Reference](http://localhost:8000/docs)
- [Contributing Guide](./CONTRIBUTING.md)
