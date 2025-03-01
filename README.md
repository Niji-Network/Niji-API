<div align="center">
    <h1>Niji - Anime related API</h1>
</div>

## Overview

Niji is an API for managing anime/manga images. It supports downloading images from a source URL, saving them locally, and providing endpoints for image management (search, update, delete, etc). It also includes status endpoints for monitoring resource consumption.

## Features

- **Image Management:** Create, update, search, and delete images.
- **Authentication:** Secure API key creation and verification.
- **Rate Limiting:** Distributed rate limiting using Redis.
- **Status Monitoring:** Retrieve system consumption and usage metrics.
- **Hosting:** Dockerized deployment with environment variable configuration.

## Getting Started

### Prerequisites

- **Docker & Docker Compose:** Ensure you have [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.
- **Git:** For cloning the repository.

### Environment Configuration

Create a `.env` file in the root of the project with your configuration variables. For example:

```dotenv
MONGO_URI=mongodb://localhost:27017
DB_NAME=nijiapi
API_KEYS_COLLECTION=api_keys
IMAGES_COLLECTION=images
RATE_LIMIT_MINUTE=20
RATE_LIMIT_DAY=5000
ALLOWED_POST_USERS=gonzyui
REDIS_URL=redis://localhost:6379
CDN_DOMAIN=https://cdn.nijiapi.xyz
STATIC_IMAGES_DIR=static/images
```
**Note:** Do not commit your `.env` file to your repository. Use your CI/CD system or secrets management to securely inject these values in production.

## Running the API Locally (Auto-Hosting)
1. **Clone the repository:**
```bash
git clone https://github.com/Niji-Network/Niji-API
cd Niji-API
```
2. **Build and RUn with Docker Compose:**
```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGO_URI=${MONGO_URI}
      - DB_NAME=${DB_NAME}
      - API_KEYS_COLLECTION=${API_KEYS_COLLECTION}
      - IMAGES_COLLECTION=${IMAGES_COLLECTION}
      - RATE_LIMIT_MINUTE=${RATE_LIMIT_MINUTE}
      - RATE_LIMIT_DAY=${RATE_LIMIT_DAY}
      - ALLOWED_POST_USERS=${ALLOWED_POST_USERS}
      - REDIS_URL=${REDIS_URL}
      - CDN_DOMAIN=${CDN_DOMAIN}
      - STATIC_IMAGES_DIR=${STATIC_IMAGES_DIR}
    depends_on:
      - mongo
      - redis

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

volumes:
  mongo-data:
```
Then, run:
```bash
docker-compose up --build
```
3. **Access the API Documentation:**

Open your browser and navigate to http://localhost:8000/docs for the custom ReDoc documentation.

## CI/CD & Deployment

For continuous integration and deployment, consider using GitHub Actions (or similar). Here's a briew overview of how to deploy:
1. **Ci/CD Pipeline:**
    - Use GitHub Actions to build your Docker Image.
    - Inject environment variables via GitHub Secrets.
    - Deploy to your VPS using SSH or a container orchestation tool.
2. **Protecting your `.env` file:**
    - Do not commit your `.env` file to GitHub.
    - Store sensitive values in your repository's secrets.
    - Use your CI/CD pipeline to generate the `.env` file during deployment.

## Contributing

We welcome contributions! Here's how you can help:
1. **Fork the repository:**
    - Click the **Fork** button at the top right of the repository page.
2. **Clone your Fork:**
```bash
git clone https://github.com/Niji-Network/Niji-API
cd Niji-API
```
3. **Create a new branch:**
```bash
git checkout -b feature/my-new-feature
```
4. **Make your changes:**
- Follow the coding guidelines.
- Write tests for your changes.
- Update documentation as needed.
5. **Submit a PR**

Push your branch and create a pull request. Please ensure your code follows our coding standards and passes all tests.
