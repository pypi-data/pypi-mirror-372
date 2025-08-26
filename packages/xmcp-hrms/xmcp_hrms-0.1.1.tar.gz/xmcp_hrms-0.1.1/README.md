# XMCP

XMCP is a [Model Context Protocol (MCP)] server exposing selected HRMS portal APIs over HTTP so they can be safely consumed by LLM and chatbot applications.

## Features

- **Health check** endpoint at `/health`.
- **Holiday data** proxy at `/holidays?year=YYYY` forwarding to the HRMS `app/employees/holidays` API.
- **Leave records** proxy at `/leaves?fyId=<financial_year_id>` forwarding to the HRMS `attendance/leaves/my-leaves` API.
- **Apply leave** proxy at `/leaves/apply` forwarding POST requests to the HRMS `attendance/leaves/apply` API.
- **Attendance** proxy at `/attendance/my-attendance`.
- **Feedback** endpoints for adding feedback, viewing RM feedbacks and listing levels.
- **Ticket management** endpoints for viewing, drafting and submitting tickets.
- **Team management** ledger endpoint at `/team-management/ledger`.
- All HRMS calls transparently forward the incoming `Authorization: Bearer <token>` header.
- Built with [FastAPI](https://fastapi.tiangolo.com/) and packaged using Docker.

## Configuration

Create a `.env` file (see `.env.example`) or set environment variables:

- `HRMS_API_BASE_URL` – base URL of the HRMS portal APIs (e.g. `https://devxnet2api.cubastion.net/api/v2`).

Every request to the MCP server **must** include a valid `Authorization` header containing the user's bearer token, which is forwarded unchanged to the HRMS APIs.

## Development

Install dependencies:

```bash
pip install -e .[dev]
```

Run the application locally:

```bash
uvicorn xmcp.main:app --reload
```

Example requests (replace `$TOKEN` with the user's bearer token):

```bash
curl 'http://localhost:8000/holidays?year=2025' -H "Authorization: Bearer $TOKEN"
curl 'http://localhost:8000/leaves?fyId=roxq0g78pis7ia9' -H "Authorization: Bearer $TOKEN"
curl -X POST 'http://localhost:8000/leaves/apply' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"type":"Debit","category":"Leave","leaveCount":2,"leaveDate":"2025-08-24","comments":"Not feeling well","status":"Pending Approval"}'
```

## Testing

The repository includes unit tests under `tests/`:

- `test_health.py`
- `test_holidays.py`
- `test_leaves.py`
- `test_apply_leave.py`

Run all tests with:

```bash
pytest
```

## Docker

Build the container image:

```bash
docker build -t xmcp .
```

Run the server in Docker:

```bash
docker run -p 8000:8000 xmcp
```

The service will be available at `http://localhost:8000`.

## Packaging and Distribution

The project includes a `pyproject.toml` that declares the MCP server as a
standard Python package using the Hatchling build backend. All runtime
dependencies and optional development tools are listed there, which allows the
application to be installed or built in a consistent way.

### Benefits

- Unified metadata and dependency management make the project installable via
  `pip` and buildable into wheel or source distributions.
- Optional `dev` dependencies keep development tooling separate from runtime
  requirements.

### Build and publish

You can now build distributable artifacts and publish them to an index such as
PyPI:

```bash
python -m build   # or: hatch build
```

Install the package in other environments:

```bash
pip install .               # from the project root
# or, after publishing
pip install xmcp
```

These packages can be used in CI/CD pipelines, Docker images, or any other
environment where the MCP server needs to be reused or integrated.

## Code Structure and Adding new APIs

Endpoints and tools are organized by domain under `xmcp/`:

- `leaves/`
- `feedback/`
- `tickets/`
- `attendance/`
- `miscellaneous/`
- `team_management/`

To add a new API within a group:

1. **Define Pydantic models** in the group's `models.py` describing the request and response bodies.
2. **Add a client method** in the group's `client.py` that calls the HRMS endpoint, accepts an `auth_header` argument, and returns the typed models.
3. **Create a route** in the group's `router.py` that accepts the necessary parameters, requires the `Authorization` header, and calls the client method.
4. **Document the endpoint** in this README and add a corresponding test under `tests/` that patches the new client method.
5. **Run `pytest`** before committing to verify everything works.

Following this pattern allows the MCP server to expand as additional HRMS APIs are exposed.

## Using from LangChain

The module `xmcp.tools` exposes helpers to register the MCP endpoints as
tools.  Framework-agnostic specifications can be adapted to LangChain,
LangGraph or any other agentic runtime. StructuredTool from LangChain is being
deprecated, but we still provide helpers for backward compatibility.

```python
# Framework-agnostic definitions
from xmcp.tools import create_tool_specs

specs = create_tool_specs(
    base_url="http://localhost:8000",
    auth_header_getter=lambda: "Bearer <token>",
)

# Convert to LangChain StructuredTool instances (deprecated but supported)
from xmcp.tools import create_langchain_tools

tools = create_langchain_tools(
    base_url="http://localhost:8000",
    auth_header_getter=lambda: "Bearer <token>",
)

# tools now contains StructuredTool instances for all available endpoints
# (e.g. get_holidays, get_leaves, apply_leave, get_attendance, add_feedback, get_tickets, ...)
```

Each specification returns the JSON response from the corresponding MCP
endpoint and can be supplied to any agent framework that supports structured
tool calling.
