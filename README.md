# Pronto

An application for clients of shoe repairers, dry cleaners, etc. to be notified when their items are ready to be collected.

## Features

- **Vendor Management**: Local shops can register, manage their items, and update item status
- **Item Registration**: Vendors can register items with unique tags and generate QR codes
- **Client Notifications**: Clients receive push notifications when their items are ready
- **QR Code Scanning**: Clients can scan QR codes to associate themselves with items
- **Status Tracking**: Track the status of items from registration to collection

## Development Requirements

- Python 3.11+
- Uv (Python Package Manager)
- Gotify server (for push notifications)

### M.L Model Environment

```sh
MODEL_PATH=./ml/model/
MODEL_NAME=model.pkl
```

### Update `/predict`

To update your machine learning model, add your `load` and `method` [change here](app/api/routes/predictor.py#L19) at `predictor.py`

## Installation

```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
make install
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
DATABASE_URL=sqlite:///./pronto.db
SECRET_KEY=your-secret-key
GOTIFY_URL=http://your-gotify-server:8080
GOTIFY_APP_TOKEN=your-app-token-here
```

## Setting Up Gotify

Gotify is an open-source push notification server that we use for sending notifications to clients.

1. **Install Gotify Server**:
   - Docker: `docker run -p 80:80 -v /var/gotify/data:/app/data gotify/server`
   - Or follow the installation instructions at [Gotify Documentation](https://gotify.net/docs/)

2. **Create an Application**:
   - Log in to your Gotify server
   - Go to "APPS" and click "CREATE APPLICATION"
   - Name it "Pronto" and create
   - Copy the generated token to your `.env` file as `GOTIFY_APP_TOKEN`

3. **Client Setup**:
   - Install the Gotify app on client devices from [Google Play](https://play.google.com/store/apps/details?id=com.github.gotify) or [F-Droid](https://f-droid.org/packages/com.github.gotify/)
   - Configure the app to connect to your Gotify server
   - Each client will get a unique token that should be stored in your database

## Running Locally

```sh
make run
```

## API Documentation

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/client` - Register a new client
- `POST /api/v1/auth/register/vendor` - Register a new vendor
- `POST /api/v1/auth/token` - Login and get access token

### Users
- `GET /api/v1/users/me` - Get current user information
- `GET /api/v1/users/me/vendor` - Get vendor profile
- `PUT /api/v1/users/me/vendor` - Update vendor profile

### Items
- `POST /api/v1/items/` - Create a new item (vendor only)
- `GET /api/v1/items/` - List all vendor items
- `GET /api/v1/items/{item_id}` - Get item details
- `PUT /api/v1/items/{item_id}` - Update item details
- `PUT /api/v1/items/{item_id}/status` - Update item status
- `POST /api/v1/items/scan/{qr_code}` - Scan QR code to register as client

### Notifications
- `GET /api/v1/notifications/` - Get user notifications
- `PUT /api/v1/notifications/{notification_id}/read` - Mark notification as read

## Mobile App

The mobile app is built with React Native and provides the following features:

- User authentication (login/registration)
- Vendor dashboard for item management
- QR code scanning for clients
- Push notifications via Gotify for item status updates
- Item status tracking

## Running Tests

```sh
make test
```

## Project Structure

```
app
├── api                 - Web routes and API endpoints
├── core                - Application configuration and startup
├── models              - Database models and schemas
├── services            - Business logic and services
└── main.py             - FastAPI application creation
```

## License

This project is licensed under the MIT License.

## GCP

Deploying inference service to Cloud Run

### Authenticate

1. Install `gcloud` cli
2. `gcloud auth login`
3. `gcloud config set project <PROJECT_ID>`

### Enable APIs

1. Cloud Run API
2. Cloud Build API
3. IAM API

### Deploy to Cloud Run

1. Run `gcp-deploy.sh`

### Clean up

1. Delete Cloud Run
2. Delete Docker image in GCR

## AWS

Deploying inference service to AWS Lambda

### Authenticate

1. Install `awscli` and `sam-cli`
2. `aws configure`

### Deploy to Lambda

1. Run `sam build`
2. Run `sam deploy --guiChange this portion for other types of models

## Add the correct type hinting when completed

`aws cloudformation delete-stack --stack-name <STACK_NAME_ON_CREATION>`

Made with ❤️
