# NFC Writer

Desktop NFC reader/writer built with Python, pywebview, and a Vue frontend.

## Architecture

- `src/nfc_writer/main.py` starts the desktop app.
- `src/nfc_writer/app.py` owns pywebview window creation and frontend resolution.
- `src/nfc_writer/bridge.py` exposes a small JSON-safe API to the Vue app.
- `src/nfc_writer/nfc/service.py` contains application-level NFC workflows.
- `src/nfc_writer/nfc/adapters/` isolates hardware-specific NFC implementations (mock / pyscard).
- `frontend/` contains the Vue 3 + TypeScript interface.

The default adapter is `mock`, so the project can run before real NFC hardware is connected.

## Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [pnpm](https://pnpm.io/) (Node.js package manager)

### Setup

Install Python dependencies with uv:

```powershell
uv sync
```

Install frontend dependencies with pnpm:

```powershell
Set-Location ".\frontend"
pnpm install
Set-Location ".."
```

### Run the Vue dev server

```powershell
Set-Location ".\frontend"
pnpm dev
```

### Run the desktop shell against the dev server

```powershell
uv run nfc-writer --dev-server "http://localhost:5173" --debug
```

### Build and run locally

```powershell
Set-Location ".\frontend"
pnpm build
Set-Location ".."
uv run nfc-writer
```

### NFC adapters

Set the adapter via environment variable or `.env` file:

| Value | Description |
|---|---|
| `mock` | Default. In-memory fake reader for development. |
| `pyscard` | Real PC/SC hardware via pyscard (requires `uv sync --extra nfc`). |

```powershell
# Install with real NFC support
uv sync --extra nfc

# Use the pyscard adapter
$env:NFC_WRITER_ADAPTER = "pyscard"
uv run nfc-writer
```

## Testing

```powershell
uv run pytest
```
