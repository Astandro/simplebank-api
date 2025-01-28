
# Simple Bank API with Docker and SQL Server

This is a simple API service built with FastAPI, Python, and Docker that interacts with a SQL Server database using `pyodbc` and SQL Authentication. The API supports the basic operations of deposit, withdrawal, transfer, and getting activity histories of an account id, and it is dockerized for easy deployment.

## Features
- **Dockerized**: The project runs in Docker using Docker Compose for both the API and the SQL Server (or SQL Edge).
- **SQL Server Integration**: Uses SQL Server (or SQL Edge) for database management, with the connection handled via `pyodbc`.
- **Transaction Handling**: Uses `snapshot` isolation level to prevent deadlocks during `SELECT` queries.
- **Seeding Script**: A seeding script is included to populate the database with initial data.
- **Postman Collection**: The project is designed to be easily imported into Postman for API testing.

## Prerequisites
- Docker and Docker Compose installed.
- Python 3.9+ (if running locally without Docker).
- A SQL Server or SQL Edge instance (Dockerized or local).

## Project Structure
```
/my-project
    /app
        main.py         # FastAPI application entry point
        routes.py       # API route definitions
        config.py       # for database configurations
        models.py       # Models for the service
        seed.py         # Seeding script for initialization
    Dockerfile           # Dockerfile for building the API container
    docker-compose.yml   # Docker Compose configuration
    requirements.txt     # Python dependencies
    .env                 # Environment variables (credentials)
    Makefile             # Makefile for easy development setup
    README.md            # Project documentation
    init.sql             # Init SQL script for allowing SNAPSHOT isolation
    Simplebank.postman_collection.json # Postman collection for testing the API
```

## Setup Instructions

### 1. Clone the repository
Clone the project repository to your local machine:

```bash
git clone https://github.com/Astandro/simplebank-api.git
cd simplebank-api
```

### 2. Configure Environment Variables
Create a `.env` file at the root of your project and add your database credentials. Example:

```
SQL_PASSWORD=StrongPassword123
DATABASE_URL=DRIVER={ODBC Driver 17 for SQL Server};SERVER=sqlserver,1433;DATABASE=bank;UID=sa;PWD=StrongPassword123
```

Make sure that you have the correct ODBC driver installed (e.g., `ODBC Driver 17 for SQL Server`).

### 3. Build and Run the Application using Docker Compose

The project uses Docker Compose to run both the API and the database. Run the following command to build and start the containers:

```bash
docker-compose up --build -d
```

This will start the FastAPI application and the SQL Server container in detached mode.

### 4. Accessing the API

Once the containers are running, you can access the FastAPI application at `http://localhost:3000`.

You can test the following endpoints:

- `GET /bank/histories` — Get all bank activity hsitory of an account id.
- `PUT /bank/deposits` — Deposit (SETOR) some amount of money from an account id in a specific currency.
- `PUT /bank/withdrawals` — Withdraw (TARIK) some amount of money from an account id in a specific currency.
- `PUT /bank/transfers` — Transfer some money from an account id to other account id(s) - Support multiple transfer in a single transaction.

### 5. SQL Server Initial Configuration

You can run the SQL statement in `init.sql` to ensure your SQL server allows SNAPSHOT isolation level

### 6. Seeding the Database

Seed the database for initial table and data:

```bash
make seed
```

### 6. Stop the Containers

To stop and remove the containers, run:

```bash
docker-compose down
```

## Development Setup

To set up the development environment without Docker, follow these steps:

1. **Create a virtual environment**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the FastAPI app locally**:

    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 3000
    ```

## Postman Collection

You can import the Postman collection for testing the API directly from this repository.

- Import the `SimpleBank.postman_collection.json` file into Postman.

## Makefile Commands

For convenience, the following commands are available in the Makefile:

- `make build`: Build the Docker containers.
- `make up`: Start the Docker containers in detached mode.
- `make down`: Stop and remove the Docker containers.
- `make install`: Install Python dependencies.

## Troubleshooting

If you encounter any issues, here are some common solutions:

1. **`ImportError: libodbc.so.2`**:
   - Ensure that `unixODBC` is installed in the Docker container by following the instructions to modify the `Dockerfile`.

2. **`Error loading ASGI app. Could not import module "main"`**:
   - Ensure that your `main.py` file is located in the correct directory and that the `CMD` in the `Dockerfile` points to the correct path (`app.main:app`).

3. **SQL Server Docker Container Fails to Start**:
   - For Mac M1 users, consider using Azure SQL Edge as a lightweight alternative to SQL Server.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
