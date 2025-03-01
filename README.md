<div align="center">
    <h1>Niji - Anime Related API</h1>
</div>

## Overview

Niji is an API for managing anime/manga images. It supports downloading images from a source URL, saving them locally, and providing endpoints for image management (create, update, search, delete, etc.). It also includes status endpoints for monitoring resource consumption.

## Features

- **Image Management:** Create, update, search, and delete images.
- **Authentication:** Secure API key creation and verification.
- **Rate Limiting:** Distributed rate limiting using Redis.
- **Status Monitoring:** Endpoints to monitor system resource usage.
- **Environment Configuration:** Easily configurable via environment variables (no Docker required).

## Getting Started

### Prerequisites

- **Python 3.9+**: Ensure you have Python installed.
- **MongoDB & Redis:** The API uses MongoDB for data storage and Redis for rate limiting. Install these or ensure they’re accessible on your network.
- **Git:** For cloning the repository.

### Environment Setup

1. **Clone the repository:**

```bash
   git clone https://github.com/Niji-Network/Niji-API
   cd Niji-API
```
2. **Create and activate virtual environment:**
```bash
  python3 -m venv env
  source env/bin/activate
```
3. **Install dependencies:**
```bash
  pip install -r requirements.txt
```
4. **Configure environment variables:**

Create a `.env` file at the root of the project.
```bash
   MONGO_URI=mongodb://localhost:27017
   DB_NAME=nijiapi
   API_KEYS_COLLECTION=api_keys
   IMAGES_COLLECTION=images
   RATE_LIMIT_MINUTE=20
   RATE_LIMIT_DAY=5000
   ALLOWED_POST_USERS=your_username
   REDIS_URL=redis://localhost:6379
   CDN_DOMAIN=https://cdn.nijiapi.xyz
   STATIC_IMAGES_DIR=/var/www/static
```

## Running the API locally
To run the API locally, use Uvicorn (or your preferred process manager):

```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```
The API will be available on http://localhost:8000

See docs to http://localhost:8000/docs

## Contributing

We welcome contributions! To contribute:

1. **Fork this repository**
2. **Clone your fork:**
```bash
git clone https://github.com/Niji-Network/Niji-API
cd Niji-API
```
3. **Create a new branch:**
```bash
git checkout -b feature/my-new-feature
```
4. **Make your changes**
   - Follow coding guidelines
   - Add tests for your changes
   - Update documentation as needed
5. **Submit Pull Request**
Push your branch and then create a PR.
Please ensure your code follows our standards and passes all tests.