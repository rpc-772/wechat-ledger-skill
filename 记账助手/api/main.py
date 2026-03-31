from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from scripts.wechat_ledger_to_notion import process_message


class LedgerRequest(BaseModel):
    message: str


class LedgerResponse(BaseModel):
    ok: bool
    reply: str
    page_id: str | None = None


app = FastAPI(title="WeChat Ledger API", version="0.1.0")


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/wechat-ledger", response_model=LedgerResponse)
def wechat_ledger(
    body: LedgerRequest,
    authorization: str | None = Header(default=None),
):
    expected_token = __import__("os").getenv("LEDGER_API_TOKEN", "").strip()
    if expected_token:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        provided = authorization.removeprefix("Bearer ").strip()
        if provided != expected_token:
            raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        result = process_message(body.message, write=True)
        return LedgerResponse(ok=True, reply=result["reply"], page_id=result.get("page_id"))
    except RuntimeError as exc:
        return LedgerResponse(ok=False, reply=str(exc), page_id=None)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
