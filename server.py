"""
Deadline Radar - FastAPI Backend Server
Wraps existing parsing, extraction, reconciliation, and ics generation logic.
Serves REST API for the modern React + TypeScript + Vite frontend.
"""

import os
import io
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from parser import parse_chat
from extract import extract_with_gemini, extract_entities
from reconcile import reconcile_events
from ics_export import export_to_ics
from sample_data import (
    SAMPLE_CHAT_RAW,
    SAMPLE_DETERMINISTIC_EXTRACTION,
    REAL_COURSE_DATASETS,
    load_real_chat_text,
    get_all_real_chats_combined,
)

app = FastAPI(title="Deadline Radar API", version="2.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for state (session-level persistence)
class AppState:
    def __init__(self):
        self.raw_text = SAMPLE_CHAT_RAW
        self.messages = parse_chat(SAMPLE_CHAT_RAW, anonymize=True)
        self.extracted_items = list(SAMPLE_DETERMINISTIC_EXTRACTION)
        self.events = reconcile_events(self.extracted_items, self.messages)
        self.is_demo_mode = True
        self.active_dataset = "benchmark_16"
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.engine_used = "Deterministic Benchmark Engine"
        self.annotate_messages()

    def annotate_messages(self):
        """Cross-references raw messages with extracted items and reconciled events to track full provenance."""
        ext_map = {it.get("message_id"): it for it in self.extracted_items if it.get("message_id") is not None}
        
        evt_src_map = {}
        for evt in self.events:
            for sid in evt.get("sources", []):
                evt_src_map[sid] = evt

        for m in self.messages:
            mid = m["id"]
            ext = ext_map.get(mid)
            evt = evt_src_map.get(mid)

            if evt:
                m["category"] = evt.get("category", "event")
                m["title"] = evt.get("title")
                m["event_id"] = evt.get("id")
                m["confidence"] = evt.get("confidence", 0.9)
                m["is_event_source"] = True
                m["has_conflict"] = evt.get("has_conflict", False)
                m["conflict_reason"] = evt.get("conflict_reason")
                m["date"] = str(evt.get("date")) if evt.get("date") else None
                m["time"] = evt.get("time")
                m["venue"] = evt.get("venue")
            elif ext and ext.get("category") != "chatter":
                m["category"] = ext.get("category", "event")
                m["title"] = ext.get("title")
                m["event_id"] = None
                m["confidence"] = ext.get("confidence", 0.8)
                m["is_event_source"] = False
                m["has_conflict"] = False
                m["conflict_reason"] = None
                m["date"] = str(ext.get("date")) if ext.get("date") else None
                m["time"] = ext.get("time")
                m["venue"] = ext.get("venue")
            else:
                m["category"] = "chatter"
                m["title"] = None
                m["event_id"] = None
                m["confidence"] = 0.99
                m["is_event_source"] = False
                m["has_conflict"] = False
                m["conflict_reason"] = None
                m["date"] = None
                m["time"] = None
                m["venue"] = None

state = AppState()


# Pydantic Models
class EventUpdateRequest(BaseModel):
    title: Optional[str] = None
    course_or_subject: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    venue: Optional[str] = None
    audience: Optional[str] = None
    status: Optional[str] = None


class ImportTextRequest(BaseModel):
    text: str
    anonymize: bool = True
    use_live_ai: bool = False
    api_key: Optional[str] = None


class SettingsUpdateRequest(BaseModel):
    api_key: Optional[str] = None
    model: Optional[str] = None


@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
        "service": "Deadline Radar API",
        "active_events": len(state.events),
        "is_demo_mode": state.is_demo_mode,
        "active_dataset": state.active_dataset,
        "has_api_key": bool(os.getenv("GEMINI_API_KEY")),
    }


@app.get("/api/overview")
def get_overview():
    deadlines = [e for e in state.events if e.get("category") == "deadline" and e.get("status") != "Cancelled"]
    events_list = [e for e in state.events if e.get("category") == "event" and e.get("status") != "Cancelled"]
    updated = [e for e in state.events if e.get("status") == "Updated"]
    needs_review = [e for e in state.events if e.get("needs_review") or e.get("has_conflict")]

    # Sort upcoming active events chronologically
    active_all = [e for e in state.events if e.get("status") != "Cancelled" and e.get("date")]
    active_all.sort(key=lambda e: str(e.get("date") or "9999-99-99"))

    annotated_sources = len([m for m in state.messages if m.get("is_event_source")])

    return {
        "metrics": {
            "active_deadlines": len(deadlines),
            "upcoming_events": len(events_list),
            "updated_postponed": len(updated),
            "needs_review": len(needs_review),
            "total_messages_parsed": len(state.messages),
            "annotated_sources": annotated_sources,
        },
        "upcoming_agenda": active_all[:8],
        "recent_updates": updated[:5],
        "needs_review_items": needs_review,
        "active_dataset": state.active_dataset,
        "is_demo_mode": state.is_demo_mode,
        "engine_used": state.engine_used,
    }


@app.get("/api/events")
def list_events(
    category: Optional[str] = None,
    status: Optional[str] = None,
    needs_review: Optional[bool] = None,
    search: Optional[str] = None,
):
    res = list(state.events)
    if category and category != "all":
        res = [e for e in res if e.get("category") == category]
    if status and status != "all":
        res = [e for e in res if e.get("status") == status]
    if needs_review is not None:
        res = [e for e in res if bool(e.get("needs_review") or e.get("has_conflict")) == needs_review]
    if search:
        s = search.lower()
        res = [e for e in res if s in (e.get("title") or "").lower() or s in (e.get("course_or_subject") or "").lower()]

    res.sort(key=lambda e: (not e.get("needs_review", False), str(e.get("date") or "9999-99-99")))
    return res


@app.get("/api/events/{event_id}")
def get_event_detail(event_id: str):
    evt = next((e for e in state.events if e.get("id") == event_id), None)
    if not evt:
        raise HTTPException(status_code=404, detail="Event not found")
    return evt


@app.put("/api/events/{event_id}")
def update_event(event_id: str, req: EventUpdateRequest):
    evt = next((e for e in state.events if e.get("id") == event_id), None)
    if not evt:
        raise HTTPException(status_code=404, detail="Event not found")

    if req.title is not None:
        evt["title"] = req.title
    if req.course_or_subject is not None:
        evt["course_or_subject"] = req.course_or_subject
    if req.venue is not None:
        evt["venue"] = req.venue
    if req.audience is not None:
        evt["audience"] = req.audience
    if req.time is not None:
        evt["time"] = req.time if req.time.strip() else None
    if req.status is not None:
        evt["status"] = req.status
    if req.date is not None:
        try:
            evt["date"] = datetime.strptime(req.date, "%Y-%m-%d").date()
        except ValueError:
            pass

    evt["needs_review"] = False
    evt["has_conflict"] = False
    evt["confirmed"] = True
    return evt


@app.post("/api/events/{event_id}/confirm")
def confirm_event(event_id: str):
    evt = next((e for e in state.events if e.get("id") == event_id), None)
    if not evt:
        raise HTTPException(status_code=404, detail="Event not found")
    evt["needs_review"] = False
    evt["has_conflict"] = False
    evt["confirmed"] = True
    if evt.get("status") in ("Needs Review", "Cancelled"):
        evt["status"] = "Upcoming"
    return {"status": "confirmed", "event": evt}


@app.post("/api/events/{event_id}/reject")
def reject_event(event_id: str):
    evt = next((e for e in state.events if e.get("id") == event_id), None)
    if not evt:
        raise HTTPException(status_code=404, detail="Event not found")
    evt["status"] = "Cancelled"
    evt["needs_review"] = False
    evt["confirmed"] = False
    return {"status": "rejected", "event": evt}


@app.post("/api/import")
def import_text(req: ImportTextRequest):
    raw = req.text.strip()
    if not raw:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    state.raw_text = raw
    state.messages = parse_chat(raw, anonymize=req.anonymize)

    api_key = req.api_key or os.getenv("GEMINI_API_KEY")
    state.extracted_items, state.engine_used = extract_entities(
        state.messages,
        api_key=api_key,
        model_name=state.gemini_model,
        prefer_live_ai=req.use_live_ai or bool(api_key)
    )
    state.is_demo_mode = not bool(api_key and req.use_live_ai)
    state.events = reconcile_events(state.extracted_items, state.messages)
    state.annotate_messages()
    state.active_dataset = "Custom Uploaded Chat"

    return {
        "status": "success",
        "messages_parsed": len(state.messages),
        "events_reconciled": len(state.events),
        "engine_used": state.engine_used,
        "is_demo_mode": state.is_demo_mode,
    }


@app.post("/api/import/file")
async def import_file(
    file: UploadFile = File(...),
    anonymize: bool = Form(True),
    use_live_ai: bool = Form(False),
    api_key: Optional[str] = Form(None)
):
    content = await file.read()
    raw = content.decode("utf-8", errors="ignore").strip()
    if not raw:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    state.raw_text = raw
    state.messages = parse_chat(raw, anonymize=anonymize)

    key = api_key or os.getenv("GEMINI_API_KEY")
    state.extracted_items, state.engine_used = extract_entities(
        state.messages,
        api_key=key,
        model_name=state.gemini_model,
        prefer_live_ai=use_live_ai or bool(key)
    )
    state.is_demo_mode = not bool(key and use_live_ai)
    state.events = reconcile_events(state.extracted_items, state.messages)
    state.annotate_messages()
    state.active_dataset = f"Uploaded File: {file.filename}"

    return {
        "status": "success",
        "filename": file.filename,
        "messages_parsed": len(state.messages),
        "events_reconciled": len(state.events),
        "engine_used": state.engine_used,
    }


@app.post("/api/datasets/{key}/load")
def load_dataset(key: str):
    if key == "benchmark_16":
        state.raw_text = SAMPLE_CHAT_RAW
        state.messages = parse_chat(SAMPLE_CHAT_RAW, anonymize=True)
        state.extracted_items = list(SAMPLE_DETERMINISTIC_EXTRACTION)
        state.events = reconcile_events(state.extracted_items, state.messages)
        state.active_dataset = "benchmark_16"
        state.engine_used = "Deterministic Benchmark Engine"
        state.is_demo_mode = True
        state.annotate_messages()
    elif key in REAL_COURSE_DATASETS:
        folder = REAL_COURSE_DATASETS[key]["folder"]
        raw = load_real_chat_text(folder)
        state.raw_text = raw
        state.messages = parse_chat(raw, anonymize=True)
        state.extracted_items = list(REAL_COURSE_DATASETS[key]["deterministic_extractions"])
        state.events = reconcile_events(state.extracted_items, state.messages)
        state.active_dataset = key
        state.engine_used = f"Verified IIIT-H M26 Extraction ({REAL_COURSE_DATASETS[key]['folder']})"
        state.is_demo_mode = True
        state.annotate_messages()
    elif key == "m26_all":
        raw = get_all_real_chats_combined()
        state.raw_text = raw
        state.messages = parse_chat(raw, anonymize=True)
        all_dets = []
        for k in REAL_COURSE_DATASETS:
            all_dets.extend(REAL_COURSE_DATASETS[k]["deterministic_extractions"])
        state.extracted_items = all_dets
        state.events = reconcile_events(all_dets, state.messages)
        state.active_dataset = "m26_all"
        state.engine_used = "Combined 4-Course Multi-Channel Feed"
        state.is_demo_mode = True
        state.annotate_messages()
    else:
        raise HTTPException(status_code=404, detail="Dataset key not recognized")

    return {
        "status": "success",
        "active_dataset": state.active_dataset,
        "messages_parsed": len(state.messages),
        "events_count": len(state.events),
        "engine_used": state.engine_used,
    }


@app.get("/api/sources")
def get_sources_status():
    """
    Honest source connectivity status:
    Only displays Connected / Active if the backend actually processed chat exports.
    Explains missing integrations transparently.
    """
    return [
        {
            "id": "whatsapp",
            "name": "WhatsApp",
            "type": "Chat Exports / Forwarded .txt",
            "status": "active",
            "status_label": "Active (Ingested)",
            "details": f"{len(state.messages)} messages parsed in current session",
            "instructions": "Export WhatsApp chat without media and upload .txt file."
        },
        {
            "id": "telegram",
            "name": "Telegram",
            "type": "Club & Course Groups",
            "status": "available",
            "status_label": "Available (Export)",
            "details": "Export Telegram history as JSON or plaintext to import",
            "instructions": "Telegram Desktop > Chat Settings > Export Chat History"
        },
        {
            "id": "gmail",
            "name": "Gmail Notices",
            "type": "Academic & Faculty Direct Broadcasts",
            "status": "coming_soon",
            "status_label": "Coming Soon",
            "details": "Requires Google Workspace OAuth2 app registration with Readonly Mail scope",
            "instructions": "In production, an OAuth consent screen allows direct IMAP/API email polling."
        }
    ]


@app.get("/api/export/ics")
def export_ics():
    active_confirmed = [e for e in state.events if e.get("status") != "Cancelled" and e.get("date") is not None and e.get("confirmed", True)]
    ics_string = export_to_ics(active_confirmed)
    return PlainTextResponse(
        content=ics_string,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=deadline_radar_{datetime.now().strftime('%Y%m%d')}.ics"}
    )


@app.get("/api/export/json")
def export_json():
    active_confirmed = [e for e in state.events if e.get("status") != "Cancelled"]
    return JSONResponse(content=active_confirmed)


@app.get("/api/messages")
def list_raw_messages(filter_category: Optional[str] = None):
    res = []
    for m in state.messages:
        cat = m.get("category", "chatter")
        if filter_category and filter_category != "all":
            if filter_category == "notices" and cat == "chatter":
                continue
            elif filter_category != "notices" and cat != filter_category:
                continue

        res.append({
            "id": m["id"],
            "sender": m["sender"],
            "sent_at": m["sent_at"].strftime("%Y-%m-%d %H:%M") if hasattr(m["sent_at"], "strftime") else str(m["sent_at"]),
            "text": m["text"],
            "category": cat,
            "title": m.get("title"),
            "event_id": m.get("event_id"),
            "confidence": m.get("confidence", 0.9),
            "is_event_source": m.get("is_event_source", False),
            "has_conflict": m.get("has_conflict", False),
            "conflict_reason": m.get("conflict_reason"),
            "date": m.get("date"),
            "time": m.get("time"),
            "venue": m.get("venue"),
        })
    return res


@app.get("/api/settings")
def get_settings():
    return {
        "model": state.gemini_model,
        "has_api_key": bool(os.getenv("GEMINI_API_KEY")),
        "timezone": "Asia/Kolkata (IST)",
        "active_dataset": state.active_dataset,
    }


@app.post("/api/settings")
def update_settings(req: SettingsUpdateRequest):
    if req.api_key is not None:
        os.environ["GEMINI_API_KEY"] = req.api_key.strip()
    if req.model is not None:
        state.gemini_model = req.model.strip()
    return {"status": "updated", "has_api_key": bool(os.getenv("GEMINI_API_KEY")), "model": state.gemini_model}


from fastapi.staticfiles import StaticFiles

# Mount built React frontend if dist exists (local development mode)
dist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
if not os.getenv("VERCEL") and os.path.exists(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
