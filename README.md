# DetecTor

DetecTor provides an API for determining if one or more IP addresses are known Tor exit nodes. 

This application is built using FastAPI, PostgreSQL, and Docker. It refreshes the list of IPs on a configurable basis and persists through reboots and service interruptions.

## Setup Instructions

### Prerequisites

- Docker
- Docker Compose

### Installation and Configuration

1. Clone the repository:

    ```sh
    git clone https://github.com/p4lsec/detector.git
    ```

2. Copy the example `.env` file to the root directory:

    ```sh
    cp .env.example .env
    ```

3. Update the database values in your `.env` file.

4. Build and start the application using Docker Compose:

    ```sh
    docker-compose up --build
    ```

5. The API will be available at [http://localhost:8000](http://localhost:8000).

## API Endpoints

- `GET /search?ip={ip}`: Check if the given IP address is a Tor exit node.
- `GET /list`: Retrieve the full list of Tor exit nodes.
- `DELETE /delete?ip={ip}`: Delete an IP address from the list.

## Examples

```sh
curl -X GET "http://localhost:8000/list"
curl -X GET "http://localhost:8000/search?ip=176.9.38.121"
curl -X DELETE "http://localhost:8000/delete?ip=185.100.87.141"
```

## Usage

A server is deployed at `http://44.197.181.191` for testing purposes. 

## Testing

These commands should allow you to verify an IP address is a Tor exit node, delete it, then verify the IP is no longer on the list. 

```
curl -X GET "http://44.197.181.191/search?ip=185.100.87.141"
curl -X DELETE "http://44.197.181.191/delete?ip=185.100.87.141"
curl -X GET "http://44.197.181.191/search?ip=185.100.87.141"
```