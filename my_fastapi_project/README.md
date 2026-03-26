# Pricing App

FastAPI application for pricing products from idealo links with automatic price updates.

## Setup

```bash
cd my_fastapi_project
pip install -r requirements.txt
```

## Run

```bash
./run.sh
```

## API Endpoints

- `POST /products` - Add product
- `GET /products` - List all products
- `POST /products/{id}/update-price` - Update price
- `GET /products/{id}/history` - Price history
- `DELETE /products/{id}` - Delete product
- `PUT /products/{id}` - Update product
- `POST /auth/register` - Register user
- `POST /auth/login` - Login
- `GET /scheduler/status` - Scheduler status
- `POST /scheduler/run` - Run scheduler manually