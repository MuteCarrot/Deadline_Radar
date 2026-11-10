"""
Deadline Radar - Reconciliation & Deduplication Engine
Handles merging repeated notices, detecting schedule changes / postponements,
guarding against speculative overrides, flagging conflicts for human review,
and ensuring full traceability back to source messages.
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional
from rapidfuzz import fuzz
from dates import resolve_date, parse_time_string

# Similarity thresholds
SIMILARITY_DUPLICATE = 75   # Threshold to consider two titles the exact same event
SIMILARITY_REFERS = 60      # Threshold to link a schedule change/cancellation to an earlier event
AUTHORITY_ROLES = {"cr", "rep", "admin", "prof", "professor", "ta", "faculty", "coordinator", "club", "council"}


def is_authoritative_sender(sender: str) -> bool:
    """Checks if sender appears to hold an official position (CR, Prof, TA, Club, Admin)."""
    s_lower = sender.lower()
    return any(role in s_lower for role in AUTHORITY_ROLES)


def calculate_title_similarity(t1: Optional[str], t2: Optional[str]) -> float:
    """Calculates token set ratio similarity between two event titles."""
    if not t1 or not t2:
        return 0.0
    return fuzz.token_set_ratio(t1.lower().strip(), t2.lower().strip())


def find_matching_event(target_title: str, events: List[Dict[str, Any]], threshold: float) -> Optional[Dict[str, Any]]:
    """Finds best matching existing event above the similarity threshold."""
    if not target_title or not events:
        return None
    
    best_event = None
    best_score = 0.0
    
    for event in events:
        # Check against title
        score1 = calculate_title_similarity(target_title, event.get("title"))
        # Check against course/subject
        score2 = calculate_title_similarity(target_title, event.get("course_or_subject"))
        score = max(score1, score2)
        
        if score > best_score:
            best_score = score
            best_event = event
            
    if best_score >= threshold:
        return best_event
    return None


def reconcile_events(
    extracted_items: List[Dict[str, Any]],
    messages: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Takes raw LLM extraction items and source messages, applying intelligent reconciliation.
    
    Rules:
    1. Filter out pure chatter.
    2. Repeated notices are merged, keeping source provenance and highest confidence.
    3. Postponements and venue changes update the target event if authoritative.
    4. Speculative / unverified changes trigger a CONFLICT flag rather than silent overwrite.
    5. Cancellations from unverified sources require human review.
    6. Missing dates or low confidence trigger 'Needs Review'.
    """
    msg_map = {m["id"]: m for m in messages}
    
    # Sort items by message sent timestamp to ensure chronological event progression
    valid_items = [it for it in extracted_items if it.get("message_id") in msg_map]
    valid_items.sort(key=lambda it: msg_map[it["message_id"]]["sent_at"])
    
    reconciled_events: List[Dict[str, Any]] = []

    for item in valid_items:
        category = (item.get("category") or "").lower()
        if category == "chatter":
            continue

        msg_id = item["message_id"]
        source_msg = msg_map[msg_id]
        sender = source_msg["sender"]
        sent_at = source_msg["sent_at"]
        confidence = float(item.get("confidence") or 0.6)
        
        # Resolve date
        event_date = resolve_date(
            item.get("date"),
            item.get("original_date_phrase"),
            sent_at,
            context_text=source_msg["text"]
        )
        
        event_time = parse_time_string(item.get("time"), source_msg["text"])
        title = (item.get("title") or item.get("refers_to") or "Untitled Event").strip()
        refers_to = item.get("refers_to") or title
        venue = item.get("venue")
        course = item.get("course_or_subject")
        audience = item.get("audience") or "All"
        is_auth = is_authoritative_sender(sender)

        # -------------------------------------------------------------
        # Case A: Cancellation
        # -------------------------------------------------------------
        if category == "cancellation":
            target = find_matching_event(refers_to, reconciled_events, SIMILARITY_REFERS)
            if target:
                target["sources"].append(msg_id)
                target["source_details"].append({
                    "msg_id": msg_id,
                    "sender": sender,
                    "sent_at": sent_at.strftime("%d %b %H:%M"),
                    "text": source_msg["text"]
                })
                
                # Rule: Do not blindly accept cancellations from unverified random students
                if not is_auth and confidence < 0.85:
                    target["has_conflict"] = True
                    target["conflict_reason"] = (
                        f"Unconfirmed cancellation reported by {sender} (Message #{msg_id}): '{source_msg['text']}'"
                    )
                    target["status"] = "Needs Review"
                    target["needs_review"] = True
                else:
                    target["status"] = "Cancelled"
                    target["history"].append(f"Cancelled by {sender} at {sent_at.strftime('%d %b %H:%M')}")
            else:
                # Standalone cancellation without prior event record
                reconciled_events.append({
                    "id": f"evt-{len(reconciled_events) + 1}",
                    "title": title,
                    "category": "cancellation",
                    "status": "Cancelled" if is_auth else "Needs Review",
                    "date": event_date,
                    "time": event_time,
                    "venue": venue,
                    "course_or_subject": course,
                    "audience": audience,
                    "confidence": confidence if is_auth else min(confidence, 0.6),
                    "needs_review": not is_auth or event_date is None,
                    "has_conflict": not is_auth,
                    "conflict_reason": "Cancellation without prior announcement record" if not is_auth else None,
                    "sources": [msg_id],
                    "source_details": [{
                        "msg_id": msg_id,
                        "sender": sender,
                        "sent_at": sent_at.strftime("%d %b %H:%M"),
                        "text": source_msg["text"]
                    }],
                    "history": [f"Reported cancelled by {sender}"],
                    "confirmed": False
                })
            continue

        # -------------------------------------------------------------
        # Case B: Schedule Change / Postponement / Venue Change
        # -------------------------------------------------------------
        if category == "schedule_change":
            target = find_matching_event(refers_to, reconciled_events, SIMILARITY_REFERS)
            if target:
                target["sources"].append(msg_id)
                target["source_details"].append({
                    "msg_id": msg_id,
                    "sender": sender,
                    "sent_at": sent_at.strftime("%d %b %H:%M"),
                    "text": source_msg["text"]
                })
                
                # Check for speculation (e.g. low confidence or non-authoritative rumour)
                is_speculative = (confidence < 0.75) or ("check with" in source_msg["text"].lower()) or ("someone in group said" in source_msg["text"].lower())
                
                if is_speculative:
                    target["has_conflict"] = True
                    proposed_date = event_date or "Unknown date"
                    target["conflict_reason"] = (
                        f"Conflicting / speculative update from {sender} (Msg #{msg_id}): "
                        f"claims shifted to {proposed_date}. Original date ({target['date']}) preserved."
                    )
                    target["status"] = "Needs Review"
                    target["needs_review"] = True
                    target["history"].append(f"Speculative change noted from {sender}: {source_msg['text']}")
                else:
                    # Legitimate update from authoritative sender or high confidence
                    old_date = target["date"]
                    old_time = target["time"]
                    old_venue = target["venue"]
                    
                    if event_date:
                        target["date"] = event_date
                    if event_time:
                        target["time"] = event_time
                    if venue:
                        target["venue"] = venue
                        
                    target["status"] = "Updated"
                    changes = []
                    if event_date and event_date != old_date:
                        changes.append(f"date from {old_date} to {event_date}")
                    if event_time and event_time != old_time:
                        changes.append(f"time from {old_time} to {event_time}")
                    if venue and venue != old_venue:
                        changes.append(f"venue to {venue}")
                        
                    change_desc = ", ".join(changes) if changes else "schedule revised"
                    target["history"].append(f"Updated by {sender}: {change_desc}")
            else:
                # Orphan change - no prior event found
                reconciled_events.append({
                    "id": f"evt-{len(reconciled_events) + 1}",
                    "title": title,
                    "category": "schedule_change",
                    "status": "Needs Review",
                    "date": event_date,
                    "time": event_time,
                    "venue": venue,
                    "course_or_subject": course,
                    "audience": audience,
                    "confidence": min(confidence, 0.65),
                    "needs_review": True,
                    "has_conflict": False,
                    "conflict_reason": "Schedule change announcement without prior event record.",
                    "sources": [msg_id],
                    "source_details": [{
                        "msg_id": msg_id,
                        "sender": sender,
                        "sent_at": sent_at.strftime("%d %b %H:%M"),
                        "text": source_msg["text"]
                    }],
                    "history": [f"Announced as change by {sender}"],
                    "confirmed": False
                })
            continue

        # -------------------------------------------------------------
        # Case C: Standard Deadline or Event
        # -------------------------------------------------------------
        existing_dup = find_matching_event(title, reconciled_events, SIMILARITY_DUPLICATE)
        
        # Check if existing duplicate announcement
        if existing_dup and (existing_dup["date"] == event_date or existing_dup["date"] is None or event_date is None):
            # Duplicate / reminder announcement: Merge!
            existing_dup["sources"].append(msg_id)
            existing_dup["source_details"].append({
                "msg_id": msg_id,
                "sender": sender,
                "sent_at": sent_at.strftime("%d %b %H:%M"),
                "text": source_msg["text"]
            })
            existing_dup["confidence"] = max(existing_dup["confidence"], confidence)
            if not existing_dup["venue"] and venue:
                existing_dup["venue"] = venue
            if not existing_dup["time"] and event_time:
                existing_dup["time"] = event_time
            if not existing_dup["date"] and event_date:
                existing_dup["date"] = event_date
            existing_dup["history"].append(f"Reminder repeated by {sender} at {sent_at.strftime('%d %b %H:%M')}")
        else:
            # New distinct event
            needs_review = (
                (confidence < 0.75) or
                (event_date is None) or
                (venue == "TBA") or
                ("TBA" in str(title))
            )
            
            reconciled_events.append({
                "id": f"evt-{len(reconciled_events) + 1}",
                "title": title,
                "category": category,  # "deadline" or "event"
                "status": "Needs Review" if needs_review else "Upcoming",
                "date": event_date,
                "time": event_time,
                "venue": venue or "Campus / Online",
                "course_or_subject": course or "General",
                "audience": audience,
                "confidence": confidence,
                "needs_review": needs_review,
                "has_conflict": False,
                "conflict_reason": "Date missing (TBA) or low extraction confidence" if needs_review else None,
                "sources": [msg_id],
                "source_details": [{
                    "msg_id": msg_id,
                    "sender": sender,
                    "sent_at": sent_at.strftime("%d %b %H:%M"),
                    "text": source_msg["text"]
                }],
                "history": [f"Created from notice by {sender}"],
                "confirmed": not needs_review
            })

    return reconciled_events

