# airflow
test


### 1. Clone the repository
```
git clone https://github.com/your-username/amazon-books-etl.git
cd amazon-books-etl
```
### 2. Initialize Airflow

```
docker compose up airflow-init
```

### 3. Start all services

```
docker compose up -d
```

### 4. Open Airflow UI

- URL: http://localhost:8080



### 5. Open PGAdmin UI

- URL: http://localhost:5050

### 6. Stop services

```
docker compose down
```