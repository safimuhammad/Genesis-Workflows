# Genesis Workflows 🚀

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![Microservices](https://img.shields.io/badge/Microservices-000000?style=for-the-badge)
![REST API](https://img.shields.io/badge/REST%20API-02569B?style=for-the-badge)
![Asynchronous Processing](https://img.shields.io/badge/Async%20Processing-4CAF50?style=for-the-badge)
![Task Queue](https://img.shields.io/badge/Task%20Queue-FF9800?style=for-the-badge)
![Workflow Automation](https://img.shields.io/badge/Workflow%20Automation-007ACC?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

A distributed backend system that powers the Genesis-GPT platform, built with FastAPI, RabbitMQ, Celery, and PostgreSQL for handling complex workflow management and autonomous agent task processing. 🤖

## Architecture Overview 🏗️
![Architecture](./Genesis-backend-final.png)
The backend consists of three main microservices:

1. **FastAPI Service** (`fastapi_service/`) ⚡
   - RESTful API endpoints for client communication 🖥️
   - JWT-based authentication and authorization 🔑
   - PostgreSQL database integration 🗄️
   - Rate limiting and security middleware 🔐
   - API routes:
     - `/auth` - Authentication endpoints 👤
     - `/users` - User management 👥
     - `/messages` - Message chain handling 📩
     - `/components` - System components 🏗️
     - `/background` - Background task management 🏃‍♂️

2. **Dispatcher Service** (`dispatcher_service/`) 📡
   - Message routing and workflow orchestration 🔄
   - RabbitMQ consistent hash exchange implementation 🐇
   - Agent management system:
     - Content Writer Agent ✍️
     - File Read/Write Agents 📄
   - Chain-based message processing ⛓️
   - Real-time message dispatching ⏳

3. **Celery Service** (`celery_service/`) 🌿
   - Asynchronous task processing ⏳
   - Background job execution 🚀
   - Integration with RabbitMQ task queue 📬
   - Worker scaling capabilities 📈

## Prerequisites 🛠️

- Python 3.10+ 🐍
- PostgreSQL 13+ 🗄️
- RabbitMQ 3.8+ 🐇
- Docker & Docker Compose (optional) 🐳

## Local Development Setup 💻

1. **Environment Setup**:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Start RabbitMQ**:
```bash
docker run -d --name rabbitmq \
    -p 5672:5672 -p 15672:15672 \
    rabbitmq:management
```

3. **Configure Environment Variables**:
```bash
# For FastAPI Service
cp fastapi_service/app/.env.example fastapi_service/app/.env
# Edit .env with your configurations
```

4. **Database Setup**:
```bash
# Create PostgreSQL database
createdb genesis_db

# Run migrations
cd fastapi_service/app
alembic upgrade head
```

## Running Services 🚀

### FastAPI Service ⚡
```bash
cd fastapi_service/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Dispatcher Service 📡
```bash
cd dispatcher_service/app
python main.py
```

### Celery Workers 🌿
```bash
cd celery_service/app
celery -A tasks worker --loglevel=info
```

## Docker Deployment 🐳

Build and run all services using Docker Compose:
```bash
docker-compose up -d
```

## Testing 🧪

1. **Unit Tests**:
```bash
pytest fastapi_service/tests/
```

## Service Endpoints 🌎

### FastAPI Service (Default: http://localhost:8000)
- Swagger UI: `/docs` 📜
- ReDoc: `/redoc` 📖
- Health Check: `/health` ✅

### RabbitMQ Management (Default: http://localhost:15672)
- Username: guest 👤
- Password: guest 🔑

## Monitoring & Logging 📊

- Each service maintains its own logs in the `logs/` directory 🗂️

## Security Notes 🔒

- JWT tokens expire after 30 minutes ⏳
- API rate limiting enabled 🚦
- CORS configured for specified origins 🌎
- SSL/TLS required in production 🔐

## Contributing 🤝

1. Fork the repository 🍴
2. Create a feature branch 🌱
3. Make your changes 🛠️
4. Run tests 🧪
5. Submit a pull request 🚀

## License 📜

This project is licensed under the MIT License.


