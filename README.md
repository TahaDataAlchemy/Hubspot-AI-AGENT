## HubSpot AI Agent – Intelligent CRM Co‑Pilot for HubSpot

**HubSpot AI Agent** is a production‑ready FastAPI backend that connects Groq LLMs, vector search, MongoDB, Redis, and HubSpot APIs to power an AI assistant for your HubSpot CRM data.  
It is designed as a reusable, modular boilerplate for:
- **Conversational agents** that can read/update HubSpot contacts
- **Background workflows** using Celery & Redis
- **Search & retrieval** over your data using Qdrant (vector DB)
- **Operational tooling** like centralized logging and health checks

The goal is that a new developer can:
- Understand the full architecture in minutes
- Run the stack locally with minimal setup
- Extend it with new tools, models, and workflows safely

---

## 🧩 High‑Level Architecture

At a glance, the system is made of:

- **FastAPI application (`main.py`, `core/server.py`)**  
  Handles HTTP requests, routes, auth, and middleware.
- **AI Agent module (`modules/ai_agent`)**  
  - `groq_client.py`: low‑level Groq client configuration  
  - `intent.py`: intent classification and routing logic  
  - `schema.py`: Pydantic models for agent requests/responses  
  - `tools/`: JSON tool specs that define what the LLM is allowed to call  
  - `contacts/`: contact‑specific tools and logic for HubSpot
- **HubSpot + Auth (`modules/auth`, `modules/crud_ops/contacts`)**  
  - OAuth / token management and user mapping to HubSpot  
  - CRUD operations for contacts via HubSpot APIs
- **Databases (`modules/database`)**  
  - `mongo_db/`: MongoDB models and ops (metadata, logs, or domain data)  
  - `redis/`: Redis client for caching, sessions, Celery broker/backend  
  - `vector_db/`: Qdrant client and utilities for embeddings & search
- **Background Processing (`modules/celery`)**  
  - `celery_ini.py`: Celery app configuration  
  - `tasks.py`: background jobs like syncs, email sending, enrichment
- **Observability & Ops**  
  - `core/logger/`: file + web‑based log viewer (`log_viewer.html`, `log_viewer_service.py`)  
  - `modules/healthcheck/`: health endpoints  
  - `logs/`: rolling log files for the application

The detailed backend flow is documented here:  
**Backend Flow Diagram**: `https://drive.google.com/file/d/1Unuw3HK6Qlbk6sIVYawtEykcq1ZzzVD-/view?usp=sharing`

And the core architecture diagram is embedded below in the **System Diagram** section.

---

## 📦 Features Overview

- **Modern FastAPI stack**
  - Structured project layout with `modules` and `core` packages
  - Middlewares, logging, health checks, and configuration handling

- **AI Agent for HubSpot**
  - Uses **Groq** LLMs (`GROQ_API_KEY`, `MODEL_NAME`)  
  - Tool‑based design: LLM can only perform allowed actions defined in `modules/ai_agent/tools/*.json`  
  - HubSpot contact tools: create, read, update, delete, search‑by‑identifier

- **HubSpot Integration**
  - OAuth / token handling via `modules/auth`  
  - Contact CRUD routes under `modules/crud_ops/contacts`  
  - Configurable `HUBSPOT_BASE_URL` and app credentials

- **Vector Search with Qdrant**
  - Embeddings generated with `EMBEDING_MODEL` (e.g. `all-MiniLM-L6-v2`)  
  - Qdrant client + helper utilities in `modules/database/vector_db`  
  - Supports semantic search over your HubSpot or domain data

- **MongoDB + Redis**
  - MongoDB for persistent business data (`MONGO_URI`, `MONGO_DB`)  
  - Redis for cache, sessions, and Celery broker/result backend

- **Background Jobs**
  - Celery workers for async tasks (data sync, enrichment, emails)  
  - Flower dashboard for monitoring

- **Logging & Monitoring**
  - File logs in `logs/` folder  
  - Web UI for log viewing via `/api/v1/logs`  
  - Health check endpoints for readiness/liveness

---

## ⚙️ Environment Variables (`.env`)

Create a `.env` file at the project root with the following keys (all are case‑sensitive):

- **HubSpot & API**
  - `HUBSPOT_CLIENT_ID=`  
  - `HUBSPOT_CLIENT_SECRET=`  
  - `HUBSPOT_REDIRECT_URI=`  
  - `HUBSPOT_BASE_URL=https://api.hubapi.com`  
  - `API_BASE_URL=`  (base URL where this backend is exposed, e.g. `http://localhost:8000`)

- **LLM / AI**
  - `GROQ_API_KEY=`  
  - `MODEL_NAME=openai/gpt-oss-20b`  
  - `EMBEDING_MODEL=all-MiniLM-L6-v2`

- **Email / Notifications**
  - `EMAIL_SMTP_SERVER=`  
  - `EMAIL_SMTP_PORT=`  
  - `EMAIL_USERNAME=`  
  - `EMAIL_PASSWORD=`

- **MongoDB**
  - `MONGO_URI=`  
  - `MONGO_DB=`

- **Redis / Celery**
  - `REDIS_HOST=`  
  - `REDIS_PORT=`  
  - `REDIS_USERNAME=`  
  - `REDIS_PASSWORD=`  
  - `REDIS_URL=`  (e.g. `redis://:<password>@host:port/0`)  
  - `CELERY_BROKER_URL=${REDIS_URL}`  
  - `CELERY_RESULT_BACKEND=${REDIS_URL}`

- **Vector DB (Qdrant)**
  - `VECTOR_DB_URL=`  
  - `VECTOR_DB_API=`  
  - `QDRANT_COLLECTION=`

> **Tip**: Keep your `.env` file out of version control (use `.gitignore`).

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/mubashirsidiki/FastCrate.git
cd FastCrate/Hubspot-AI-AGENT
```

> Adjust the `cd` path if your project structure differs.

### 2. Install `uv` (Python package manager)

```bash
pip install uv
```

### 3. Install Dependencies

```bash
uv sync
```

To add a new package:

```bash
uv add <package_name>
```

Example:

```bash
uv add pandas
```

### 4. Run the Application

```bash
uv run python main.py
```

By default, FastAPI usually binds to `http://localhost:8000` (check your logs or config).

> **OneDrive users**: If you have issues with symlinks or file locking, use:
>
> ```bash
> uv sync --link-mode=copy
> ```

---

## 🧪 Testing the Application

### Interactive API Documentation

Once the server is running, open:

- **URL**: `http://localhost:8000/docs`  
  This is the auto‑generated Swagger UI where you can explore and test all available endpoints.

### Health Check

Basic liveness check to verify the backend is up and wired correctly:

- **Method**: `GET`  
- **Endpoint**: `/api/v1/healthcheck`  
- **Description**: Returns health status of the service.

If this passes, your core app, routers, and DB connections are likely working.

---

## 🌐 Main API Endpoints (Cheat Sheet)

### Public / Health

- **Healthcheck**
  - **Method**: `GET`
  - **Path**: `/api/v1/healthcheck`
  - **Description**: Basic liveness/readiness indicator.

### AI Agent

> **Note**: Exact paths can be confirmed in `modules/ai_agent/ai_routes.py`. Below is the typical pattern:

- **Chat with AI Agent**
  - **Method**: `POST`
  - **Path**: `/api/v1/ai/chat`
  - **Body (example)**:
    ```json
    {
      "user_id": "hubspot_user_123",
      "message": "Find the contact with email john@acme.com and update their lifecycle stage to customer",
      "context": {}
    }
    ```
  - **Response (example)**:
    ```json
    {
      "reply": "I found John Doe at ACME with email john@acme.com and updated their lifecycle stage to Customer.",
      "steps": [
        "search_by_identifier(email=john@acme.com)",
        "update_contact(contact_id=12345, lifecycle_stage=customer)"
      ]
    }
    ```

### Contacts (Direct CRUD)

> **Note**: Confirm exact routes in `modules/crud_ops/contacts/routes.py` and `contacts_routes.py`, but a typical structure is:

- **List contacts**
  - **Method**: `GET`
  - **Path**: `/api/v1/contacts`
- **Get contact by ID**
  - **Method**: `GET`
  - **Path**: `/api/v1/contacts/{contact_id}`
- **Create contact**
  - **Method**: `POST`
  - **Path**: `/api/v1/contacts`
- **Update contact**
  - **Method**: `PUT` or `PATCH`
  - **Path**: `/api/v1/contacts/{contact_id}`
- **Delete contact**
  - **Method**: `DELETE`
  - **Path**: `/api/v1/contacts/{contact_id}`

Use the interactive docs at `/docs` to see the exact request/response schemas pulled directly from `schema.py` files.

---

## 🤖 How the HubSpot AI Agent Works

1. **User Request**  
   A user sends a natural‑language request (e.g. “Find all contacts from ACME and update their lifecycle stage to Customer”).  

2. **Intent & Tool Planning (`modules/ai_agent`)**  
   - `intent.py` classifies what the user wants (search, update, create, delete, explain, etc.).  
   - Tool definitions in `modules/ai_agent/tools/*.json` describe what actions the model can take (e.g. `create_contact`, `update_contact`, `search_by_identifier`).  
   - The LLM (via `groq_client.py`) decides which tools to call and in what order.

3. **Tool Execution (HubSpot + Databases)**  
   - Contact tools call into `modules/crud_ops/contacts` and `modules/auth` to actually perform HubSpot API operations.  
   - For contextual or historical data, the agent can query MongoDB or vector DB (Qdrant) through `modules/database`.

4. **Response Generation**  
   - The LLM combines the raw tool results into a human‑readable final message.  
   - The API then returns a structured JSON response plus natural‑language explanation.

5. **Background Tasks (Optional)**  
   - Heavier work (bulk sync, enrichment, complex reporting) can be offloaded as Celery tasks defined in `modules/celery/tasks.py`.

---

## 💬 Example Questions & Use Cases

Here are **real-world examples** of questions you can ask the AI agent. Copy and paste these into your API requests or use them as inspiration for your own queries.

### 📋 **Viewing & Listing Contacts**

**Get all contacts:**
```
"Show me all contacts"
"List all contacts in the CRM"
"Display everyone in my contact list"
"Who's in the CRM?"
```

**Search for a specific contact (requires email or phone):**
```
"Find the contact with email john.doe@acme.com"
"Search for contact using phone number +1-555-123-4567"
"Get details for sarah.smith@example.com"
"Look up the contact with email marketing@company.com"
```

### ➕ **Creating New Contacts**

**Basic contact creation:**
```
"Create a new contact for Sarah Johnson with email sarah.johnson@techcorp.com"
"Add John Smith to the CRM - his email is john.smith@startup.io and phone is +1-555-987-6543"
"Create a contact: Name is Mike Davis, email mike.davis@enterprise.com, company is Enterprise Inc"
```

**The AI will ask for missing information:**
- If you say: `"Create a contact for Alice"`
- The AI responds: `"I'd be happy to create a contact for Alice. What is her email address?"`
- Then provide: `"alice.brown@company.com"`
- The AI will check for duplicates and create the contact

### ✏️ **Updating Existing Contacts**

**Update contact information:**
```
"Update John Doe's phone number to +1-555-111-2222"
"Change Sarah's email to sarah.new@company.com"
"Update the contact with email john@acme.com - set their company to Acme Corporation"
"Modify Mike's job title to Senior Developer"
```

**Update multiple fields:**
```
"Update contact john.doe@acme.com: change phone to +1-555-999-8888 and company to Acme Industries"
"Modify Sarah's contact - update her job title to VP of Sales and company to TechCorp"
```

### 🔍 **Searching & Finding Contacts**

**Search by email:**
```
"Find contact with email john.doe@acme.com"
"Search for sarah.smith@example.com"
"Get information about the contact with email marketing@company.com"
```

**Search by phone:**
```
"Find the contact with phone number +1-555-123-4567"
"Search using phone +923001234567"
"Look up contact by phone 555-987-6543"
```

**Note**: The AI requires an email or phone number to search. If you only provide a name, it will ask for an identifier.

### 🗑️ **Deleting Contacts**

**Delete a contact:**
```
"Delete the contact with email john.doe@acme.com"
"Remove Sarah Smith from the CRM - her email is sarah@example.com"
"Delete contact using phone +1-555-123-4567"
```

**The AI will confirm before deletion:**
- If you say: `"Delete John Doe"`
- The AI responds: `"Are you sure you want to delete John Doe (john.doe@acme.com)? Please confirm."`
- After confirmation, the contact is deleted

### 📊 **Conversational Queries (Using Context)**

**Ask about past conversations:**
```
"What contact did we create?"
"Which contact did we mark as important?"
"What did we discuss about John?"
"Show me what we talked about regarding Sarah"
"Which contacts did we update today?"
```

**The AI uses conversation history from Redis (recent) or vector search (past) to answer these questions contextually.**

### 🔄 **Multi-Step Workflows**

**Complex operations:**
```
"Find all contacts from ACME company and update their lifecycle stage to Customer"
"Search for contacts with email domain @startup.io and update their company name"
"Find John Doe, update his phone number, then show me his updated details"
```

**Note**: The AI processes one tool call at a time, so complex workflows may require multiple interactions.

### ❓ **General Questions**

**Ask about capabilities:**
```
"What can you help me with?"
"How do I create a contact?"
"What information do you need to search for a contact?"
"Can you update multiple contacts at once?"
```

---

## 🎯 **API Request Examples**

### Example 1: Simple Search Query

**Request:**
```bash
POST http://localhost:8000/api/v1/ai_agent/chat
Content-Type: application/json

{
  "query": "Find the contact with email john.doe@acme.com"
}
```

**Expected Response:**
```json
{
  "response": "I found John Doe in your CRM. Here are the details:\n- Name: John Doe\n- Email: john.doe@acme.com\n- Phone: +1-555-123-4567\n- Company: Acme Corporation\n- Contact ID: 12345"
}
```

### Example 2: Create Contact

**Request:**
```bash
POST http://localhost:8000/api/v1/ai_agent/chat
Content-Type: application/json

{
  "query": "Create a new contact for Sarah Johnson with email sarah.johnson@techcorp.com and phone +1-555-987-6543"
}
```

**Expected Response:**
```json
{
  "response": "✅ Created contact: Sarah Johnson (sarah.johnson@techcorp.com)\n- Phone: +1-555-987-6543\n- Contact ID: 67890"
}
```

### Example 3: Update Contact

**Request:**
```bash
POST http://localhost:8000/api/v1/ai_agent/chat
Content-Type: application/json

{
  "query": "Update John Doe's phone number to +1-555-999-8888. His email is john.doe@acme.com"
}
```

**Expected Response:**
```json
{
  "response": "✅ Updated John Doe: phone changed to +1-555-999-8888"
}
```

### Example 4: List All Contacts

**Request:**
```bash
POST http://localhost:8000/api/v1/ai_agent/chat
Content-Type: application/json

{
  "query": "Show me all contacts"
}
```

**Expected Response:**
```json
{
  "response": "Here are all contacts in your CRM:\n\n1. John Doe (john.doe@acme.com) - Acme Corporation\n2. Sarah Johnson (sarah.johnson@techcorp.com) - TechCorp\n3. Mike Davis (mike.davis@enterprise.com) - Enterprise Inc\n\nTotal: 3 contacts"
}
```

### Example 5: Conversational Query

**Request:**
```bash
POST http://localhost:8000/api/v1/ai_agent/chat
Content-Type: application/json

{
  "query": "What contact did we create?"
}
```

**Expected Response:**
```json
{
  "response": "Based on our previous conversation, we created a contact for Sarah Johnson (sarah.johnson@techcorp.com)"
}
```

### Example 6: Delete Contact (with confirmation)

**Request:**
```bash
POST http://localhost:8000/api/v1/ai_agent/chat
Content-Type: application/json

{
  "query": "Delete the contact with email john.doe@acme.com"
}
```

**Expected Response:**
```json
{
  "response": "Are you sure you want to delete John Doe (john.doe@acme.com)? Please confirm."
}
```

**Follow-up Request (after confirmation):**
```bash
POST http://localhost:8000/api/v1/ai_agent/chat
Content-Type: application/json

{
  "query": "Yes, delete John Doe"
}
```

**Expected Response:**
```json
{
  "response": "✅ Deleted contact: John Doe"
}
```

---

## 🔐 HubSpot App & Auth Setup (High‑Level)

To connect this backend to your HubSpot portal, you typically need to:

1. **Create a HubSpot Private App (or Public App)**  
   - Go to your HubSpot portal → **Settings → Integrations → Private Apps**.  
   - Create a new app, give it a name like **“HubSpot AI Agent”**.  
   - Enable the required scopes (e.g. `crm.objects.contacts.read`, `crm.objects.contacts.write`, and any others you need).  
   - Copy the **Client ID**, **Client Secret**, and set/copy a **Redirect URI**.

2. **Configure `.env` for HubSpot**  
   - Set `HUBSPOT_CLIENT_ID`, `HUBSPOT_CLIENT_SECRET`, `HUBSPOT_REDIRECT_URI`, `HUBSPOT_BASE_URL`.  
   - Restart the backend so changes take effect.

3. **Complete OAuth / Token Flow**  
   - The routes under `modules/auth/auth_routes.py` and `modules/auth/routes.py` handle token retrieval and refresh.  
   - On first run, you’ll be redirected to HubSpot to authorize the app; the backend stores tokens (usually in `token.json` and/or DB via `token_manager.py`).

4. **Verify with a Simple Call**  
   - Hit a contact endpoint (e.g. list contacts) via `/docs`.  
   - If you get valid data from HubSpot, your app + backend wiring is correctly configured.

> **Security Note**: Treat your `CLIENT_SECRET` and tokens as highly sensitive; never commit them to version control or share publicly.

---

## 📊 Logger & Log Viewer

The project ships with a simple web‑based log viewer.

- **URL**: `http://localhost:8000/api/v1/logs`  
  This serves `core/logger/log_viewer.html` which allows you to fetch and inspect logs in `logs/`.

> **Tip**: If clicking **“Fetch Logs”** shows nothing, try an **incognito/private window** to bypass cached credentials and extensions.

Log configuration and handlers live in `core/logger/`:
- `logger.py`: config and logger factory
- `log_handler.py`: file/stream handlers
- `log_viewer_service.py`: backend logic for the web viewer

---

## 🧵 Background Workers (Celery)

### Running Celery Worker

From the project root (where `modules/` lives), run:

```bash
uv run celery -A modules.celery.celery_ini worker --loglevel=info --concurrency=1 --pool=solo
```

- **`celery_ini.py`**: defines the Celery application and broker/backend configuration (using `REDIS_URL`).  
- **`tasks.py`**: define your async jobs here (e.g. sync HubSpot data, send emails, run periodic AI workflows).

### Running Flower (Celery Dashboard)

```bash
uv run celery -A modules.celery.celery_ini flower
```

Then open the URL printed in the terminal (commonly `http://localhost:5555`) to see task status, workers, and queues.

---

## 🗂️ Important Modules & Folders

- **`main.py`**  
  FastAPI app entrypoint; mounts routers, middleware, logging, and startup/shutdown events.

- **`config.py`**  
  Central configuration, environment variable loading, and settings management.

- **`modules/ai_agent/`**
  - `ai_routes.py`: HTTP routes for interacting with the AI agent.  
  - `system_Prompt.py`: system prompts and behaviour definitions for the agent.  
  - `tools/`: JSON specs describing tool names, input schemas, and descriptions.  
  - `contacts/`: logic specific to HubSpot contacts.

- **`modules/auth/`**
  - `auth_routes.py`: routes for auth and token handling.  
  - `token_manager.py`, `token.json`: store and manage access/refresh tokens.  
  - `user_id.py`, `constant.py`: helper constants and user mapping.

- **`modules/crud_ops/contacts/`**
  - `contacts_routes.py`: raw CRUD endpoints for contacts.  
  - `schema.py`: Pydantic models for contacts.  
  - `routes.py`: top‑level router for contact module.

- **`modules/database/`**
  - `mongo_db/`: `mongo_client.py`, `mongo_ops.py`, `models.py`.  
  - `redis/`: `redis_client.py`.  
  - `vector_db/`: `Qdrant.py`, `vector_search.py`, `vector_utility.py`.

- **`core/middlewares/`**
  - `middleware.py`: cross‑cutting concerns (e.g. logging, request IDs, CORS).

- **`modules/healthcheck/`**
  - `healthcheck_routes.py`: implementation of readiness/liveness checks.  
  - `routes.py`: router grouping for healthcheck.

- **`modules/logviewer/`**
  - `log_viewer_routes.py`, `routes.py`: API endpoints for log viewer frontend.

---

## 🧱 System Diagram

Below is the core architecture/flow diagram for the HubSpot AI Agent backend (already included in the repository):

![HubSpot AI Agent Architecture](<Hubspot AI Agent-1.png>)

If you prefer a separate high‑resolution version, open `Hubspot AI Agent-1.png` directly in your file explorer or IDE.

---

## 🛠️ Local Development Tips

- **Use virtual environments**: `uv` automatically manages environments; avoid mixing with global `pip` installs.  
- **Check logs early**: on any error, inspect the latest file in `logs/` and the `/api/v1/logs` UI.  
- **Keep tools small**: when adding new AI tools, keep each JSON file focused on a single business action.  
- **Use healthchecks**: wire your container/orchestrator to check `/api/v1/healthcheck` for readiness.

---

## 📜 License

This project is licensed under the terms specified in `LICENSE`. Please review it before using this code in production.

---

## 🙋 FAQ (Short)

- **Q: Can I change the LLM provider or model?**  
  **A:** Yes. Update `GROQ_API_KEY`, `MODEL_NAME`, and the Groq client logic; or adapt `groq_client.py` to another provider while keeping the tool abstraction.

- **Q: Can this manage objects other than contacts?**  
  **A:** Yes. Add new tools, schemas, and CRUD routes for deals, tickets, etc., and expose them to the AI agent via new tool JSON definitions.

- **Q: Is this production‑ready?**  
  **A:** It ships with strong foundations (logging, healthchecks, background jobs, config handling), but you should review security, rate limits, and observability for your own environment before going to production.