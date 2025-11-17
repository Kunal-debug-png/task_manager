# Task Manager API

A FastAPI-based task management system with event-driven architecture using Redpanda and AI-powered task analysis via Gemini 2.5 Flash.

## Features

- RESTful API for task CRUD operations
- Event publishing to Redpanda (Kafka-compatible)
- AI-powered task analysis using Google Gemini 2.5 Flash
- Production-grade health checks
- Docker containerization

## Tech Stack

- **Framework**: FastAPI
- **Message Queue**: Redpanda Cloud
- **AI Integration**: Google Gemini 2.5 Flash API
- **Deployment**: Render
- **Language**: Python 3.11

## API Endpoints

### Tasks
- `POST /tasks` - Create a new task
- `GET /tasks` - List all tasks (supports filtering by priority and status)
- `GET /tasks/{task_id}` - Get specific task
- `PUT /tasks/{task_id}` - Update task status
- `DELETE /tasks/{task_id}` - Delete task



### Health
- `GET /health` - Service health check with dependency status

## Setup

### Prerequisites
- Python 3.11+
- Redpanda Cloud account
- Google Gemini API key

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env`:
   ```
   KAFKA_BOOTSTRAP_SERVERS=your-redpanda-url
   KAFKA_SASL_USERNAME=your-username
   KAFKA_SASL_PASSWORD=your-password
   KAFKA_TOPIC=tasks-topic
   KAFKA_SECURITY_PROTOCOL=SASL_SSL
   KAFKA_SASL_MECHANISM=SCRAM-SHA-256
   GEMINI_API_KEY=your-gemini-key
   ```

4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

5. Access API documentation at `http://localhost:8000/docs`

## Docker Deployment

Build and run using Docker:

```bash
docker build -t task-manager-api .
docker run -p 8080:8080 --env-file .env task-manager-api
```

## Event Flow

1. User creates a task via POST /tasks
2. Task is stored in memory local list
3. Gemini API analyzes the task synchronously (summary, sub-tasks, category)
4. Analysis is logged to console
5. Event is published to Redpanda topic 

## Gemini Integration

For each task creation, Gemini 2.5 Flash provides:
- One-sentence task summary
- 3-5 suggested sub-tasks
- Task categorization (Bug Fix, Feature, DevOps, Documentation, Research, Testing)

