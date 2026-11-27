# Signova backend

Signova runs one FastAPI app in one Uvicorn worker. The app keeps active sessions and transcripts in memory. It exposes REST for session and transcript actions and an authenticated WebSocket for live recognition. [REST API](../docs/contracts/rest-api.md) · [WebSocket protocol](../docs/contracts/websocket-protocol.md)

## Start the server

Run these commands from the repository root with the backend virtual environment active. The alphabet runtime was verified on Linux with Python 3.14 and CPU PyTorch.

```bash
python -m pip install -r backend/requirements.lock.txt
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 torchvision==0.29.2
python -m pip install -r backend/requirements-alphabet.in

python -m uvicorn --app-dir backend app.main:app --host 127.0.0.1 --port 8000 \
  --workers 1 --ws-max-size 262144 --ws-max-queue 1 --ws-per-message-deflate false
```

Startup loads and warms the local `ml/alphabet/checkpoints/aasl31_best.pth` checkpoint and `ml/alphabet/checkpoints/hand_landmarker.task` detector. Put those assets in the local checkpoint directory or set `SIGNOVA_ALPHABET_CHECKPOINT` and `SIGNOVA_ALPHABET_HAND_MODEL` to their trusted file paths. The known local asset paths have built-in SHA-256 verification. For other files, configure the corresponding `SIGNOVA_ALPHABET_CHECKPOINT_SHA256` and `SIGNOVA_ALPHABET_HAND_MODEL_SHA256` from the package. The server uses environment variables or a repo-root `.env`. [Example settings](.env.example)

Open Swagger UI for REST. For existing-session routes, use **Authorize** and paste the `session_token` returned by Create Session. [Swagger UI](http://127.0.0.1:8000/docs)

Liveness confirms startup. Readiness reports alphabet as ready after model warmup. The word model is currently unavailable, so word creation and switching to word return `503 MODEL_UNAVAILABLE`. Missing dependencies or model files also leave alphabet unready. [Liveness](http://127.0.0.1:8000/api/v1/health/live) · [Readiness](http://127.0.0.1:8000/api/v1/health/ready) · [Model catalogue](http://127.0.0.1:8000/api/v1/models)

## Live recognition and mode switching

1. Create an alphabet session with `POST /api/v1/sessions` and keep the returned token. Open `/api/v1/ws/sessions/{sid}` from an allowed browser origin and send the v1 authentication message.
2. Send the REST capture Start command and use the returned stream ID for unmirrored JPEG frames. Wait for each matching frame acknowledgement. A stable, eligible candidate can be confirmed through REST using its candidate ID and stream ID. The current alphabet model uses manual confirmation. After confirming, Pause then Start to begin a new signing segment.
3. To switch, send `POST /api/v1/sessions/{sid}/mode` with the desired `mode`, the current `expected_revision` and `expected_state_version`, the bearer token, and a fresh `Idempotency-Key`. The session ID, token, and transcript carry through. If capture is active, restart frame numbering at 1 using the returned fresh stream ID. An unavailable target leaves the current session and stream intact.

Opening a second terminal to run backend tests avoids interrupting any server session. Run the suite from the repository root.

```bash
python -m pytest backend
```

The tests cover the REST and WebSocket flows with deterministic adapters. Native alphabet tests also use the local checkpoint and detector when present. Model accuracy and camera usability still require real signers and a frontend.
