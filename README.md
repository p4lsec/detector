# DetecTor

This project provides an API for detecting if an IP address is a Tor exit node, retrieving the list of Tor exit nodes, and deleting specific IP addresses from the list. The application is built using FastAPI, PostgreSQL, and Docker.

## Setup Instructions

### Prerequisites

- Docker
- Docker Compose

### Environment Variables

Create a `.env` file in the root directory with the following content:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=tor_db
```

## Running the Application

	1.	Build and start the application using Docker Compose:

    ```
    docker-compose up --build
    ```

  	2.	The API will be available at http://localhost:8000.

## API Endpoints

- GET /search?ip={ip}: Check if the given IP address is a Tor exit node.
- GET /list: Retrieve the full list of Tor exit nodes.

## Examples

```
curl -X GET "http://localhost:8000/list"
curl -X GET "http://localhost:8000/search?ip=176.9.38.121"

```

