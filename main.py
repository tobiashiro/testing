from fastapi import FastAPI, Request, Depends, HTTPException
from contextlib import asynccontextmanager
import httpx

EXTERNAL_SERVICE_URL = "https://api.external-service.com/session"

class SessionManager:
    def __init__(self):
        self.session_id = None

    async def connect(self):
        # Przykładowe połączenie z serwisem zewnętrznym i pobranie session_id
        async with httpx.AsyncClient() as client:
            response = await client.post(EXTERNAL_SERVICE_URL)
            response.raise_for_status()
            self.session_id = response.json()["session_id"]

    def is_connected(self):
        return self.session_id is not None

    async def make_request(self, endpoint: str, data: dict):
        if not self.is_connected():
            raise RuntimeError("Brak aktywnej sesji")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{EXTERNAL_SERVICE_URL}/{endpoint}",
                headers={"Authorization": f"Bearer {self.session_id}"},
                json=data
            )
            resp.raise_for_status()
            return resp.json()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.session_manager = SessionManager()
    await app.state.session_manager.connect()
    yield
    # Tu można dodać cleanup, jeśli potrzeba


app = FastAPI(lifespan=lifespan)

def get_session_manager(request: Request) -> SessionManager:
    manager = request.app.state.session_manager
    if not manager.is_connected():
        raise HTTPException(status_code=503, detail="Brak połączenia z serwisem zewnętrznym")
    return manager


@app.post("/do-something")
async def do_something(
    payload: dict,
    session_manager: SessionManager = Depends(get_session_manager)
):
    # Sprawdzenie, czy sesja jest aktywna i wykonanie requestu do serwisu zewnętrznego
    result = await session_manager.make_request("some-endpoint", payload)
    return {"result": result}
