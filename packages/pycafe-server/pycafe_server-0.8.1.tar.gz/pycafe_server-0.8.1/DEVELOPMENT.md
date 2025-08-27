# Development setup

## Installation

```bash
(cd pycafe-private && npm install)
pip install -e .
```

## Running the development server

Run nextjs in 1 terminal:

```
$ (cd pycafe-private && npm run dev)
```

Run the Python server in another terminal:

```
$ ENV=dev uvicorn pycafe_server.asgi:app --port 8004
```

Navigate to http://localhost:3002 to use the app with the development server (hot reloading).

If you run with `ENV=dev` it will set the CORS headers to allow requests from `http://localhost:3002` to reach the Python server.

## Testing the production build

```
$ (cd pycafe-private && npm run build)
```

Now navigate to the Python server only: http://localhost:8004
