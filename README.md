<div align="center">
    <h1>Niji - Anime Related API</h1>
    <img src="https://nijii.xyz/logo.png" alt="Logo" width="150">
</div>

## Overview

Niji is an API for managing anime/manga images. It supports downloading images from a source URL, saving them locally, and providing endpoints for full image management (create, update, search, delete, etc.). It also includes authentication, rate limiting using Redis, and status endpoints for monitoring system resource consumption.

## Features

- **Image Management:** Create, update, search, and delete images.
- **Authentication:** Secure API key creation and verification.
- **Role-Based Permissions:** Users with different roles ("user", "team", "admin") have varying privileges.
- **Rate Limiting:** Distributed rate limiting per API key.
- **Status Monitoring:** Retrieve global system statistics (CPU, memory, disk, processes, etc.).
- **Easy Configuration:** Environment variables make configuration straightforward.

## Getting Started

### Prerequisites

- **Python 3.9+**: Ensure Python is installed.
- **MongoDB & Redis:** The API uses MongoDB for data storage and Redis for rate limiting. Either install these locally or ensure they are accessible on your network.
- **Git:** Required for cloning the repository.

### Environment Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Niji-Network/Niji-API
    cd Niji-API
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python3 -m venv env
    source env/bin/activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables:**

    Create a `.env` file at the root of the project with the following content (modify as needed):

    ```bash
    MONGO_URI=mongodb://localhost:27017
    DB_NAME=nijiapi
    API_KEYS_COLLECTION=api_keys
    IMAGES_COLLECTION=images
    RATE_LIMIT_MINUTE=20
    RATE_LIMIT_DAY=5000
    REDIS_URL=redis://localhost:6379
    CDN_DOMAIN=https://cdn.nijiapi.xyz
    STATIC_IMAGES_DIR=/static
    ```

    > **Note:** Do not commit your `.env` file to version control. It should be kept secret and configured directly on your server (VPS).

## Running the API Locally

To run the API locally, use Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

Interactive API documentation will be available at `http://localhost:8000/docs`

## API Documentation

The API documentation is automatically generated using FastAPI’s OpenAPI support. The OpenAPI schema is written to docs/openapi.yaml upon startup. You can update the documentation by editing inline docstrings in the code and then re-running the application.

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
