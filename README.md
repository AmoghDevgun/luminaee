# Leads MERN Stack

Backend: Node/Express, MongoDB, JWT Auth
Frontend: React (Vite)
Pipeline: Python scripts in project root (unchanged logic)

## Prerequisites
- Python 3 available as `python3`
- MongoDB running locally or set `MONGO_URI`

## Backend
```bash
cd server
npm install
npm run dev
```
- Env (optional): create `server/.env` with `MONGO_URI` and `JWT_SECRET`.
- Default port: 4000

## Frontend
```bash
cd client
npm install
npm run dev
```
- Set `VITE_API_BASE` in `client/.env` if backend not on http://localhost:4000

## API
- POST /api/auth/register { email, password }
- POST /api/auth/login { email, password } -> { token }
- GET /api/auth/me (Bearer token)
- POST /api/leads (Bearer token) { username } -> { username, leads_ranked }

This endpoint invokes the Python pipeline and returns ranked leads when complete.

## Python Pipeline Outputs
- Written to `output/` directory as before (e.g., `{username}_leads_ranked.json`).

## Project Structure
```
final2/
  output/                      # Python pipeline outputs
  server/
    src/
      config/
        db.js                  # Mongo connection
        env.js                 # Environment variables
      controllers/
        authController.js
        leadsController.js
      middleware/
        auth.js
      models/
        User.js
        LeadsResult.js
      routes/
        auth.js
        leads.js
      services/
        pipeline.js            # Spawns Python, reads ranked output
      server.js                # Express bootstrap
    package.json
  client/
    src/
      pages/
        Login.jsx
        Register.jsx
        Dashboard.jsx
      App.jsx
      main.jsx
    index.html
    package.json
  # Python scripts remain in project root (used by pipeline)
  main.py
  followers.py
  likes.py
  comments.py
  profile.py
  getMediaId.py
  leads_data.py
  cookies_headers.py
```


