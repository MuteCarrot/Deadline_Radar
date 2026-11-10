"""
Deadline Radar - Model & Pipeline Evaluation Suite
Benchmarks accuracy for:
1. Message classification (deadline, event, schedule_change, cancellation, chatter)
2. Relative date & time resolution (e.g. kal, next Monday, 14th Nov)
3. Deduplication efficiency & noise reduction
4. Conflict detection & human review triggers
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

from parser import parse_chat
from reconcile import reconcile_events
from sample_data import SAMPLE_CHAT_RAW, SAMPLE_DETERMINISTIC_EXTRACTION
from dates import resolve_date


def run_evaluation(use_live_api: bool = False, model_name: str = "gemini-2.5-flash") -> Dict[str, Any]:
    gold_path = os.path.join(os.path.dirname(__file__), "data", "gold.csv")
    if not os.path.exists(gold_path):
        print(f"Error: Gold dataset not found at {gold_path}")
        return {}

    gold_df = pd.read_csv(gold_path)
    print(f"=== Deadline Radar Accuracy & Pipeline Benchmark ===")
    print(f"Loaded Gold Evaluation Set: {len(gold_df)} test messages\n")

    # 1. Parse raw chat
    messages = parse_chat(SAMPLE_CHAT_RAW, anonymize=False)

    # 2. Extract items
    if use_live_api:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment. Falling back to benchmark extraction.")
            extracted_items = SAMPLE_DETERMINISTIC_EXTRACTION
        else:
            print(f"Running Live Gemini Extraction using {model_name}...")
            from extract import extract_with_gemini
            extracted_items = extract_with_gemini(messages, api_key=api_key, model_name=model_name)
    else:
        print("Running in Deterministic Benchmark Mode (Sample Dataset)...")
        extracted_items = SAMPLE_DETERMINISTIC_EXTRACTION

    item_map = {item["message_id"]: item for item in extracted_items}

    # 3. Calculate Category Accuracy
    cat_correct = 0
    date_correct = 0
    date_eval_total = 0
    error_cases = []

    for idx, row in gold_df.iterrows():
        msg_id = idx + 1
        item = item_map.get(msg_id, {})
        pred_cat = item.get("category")
        exp_cat = row["expected_category"]

        if pred_cat == exp_cat:
            cat_correct += 1
        else:
            error_cases.append({
                "msg_id": msg_id,
                "text": row["text"],
                "expected_cat": exp_cat,
                "predicted_cat": pred_cat,
                "type": "Category Mismatch"
            })

        # Date evaluation (only for non-chatter with expected date)
        if pd.notna(row.get("expected_date")) and str(row.get("expected_date")).strip():
            date_eval_total += 1
            sent_at = datetime.strptime(str(row["sent_at"]), "%Y-%m-%d %H:%M")
            res_date = resolve_date(
                item.get("date"),
                item.get("original_date_phrase"),
                sent_at,
                context_text=str(row["text"])
            )
            if str(res_date) == str(row["expected_date"]).strip():
                date_correct += 1
            else:
                error_cases.append({
                    "msg_id": msg_id,
                    "text": row["text"],
                    "expected_date": str(row["expected_date"]).strip(),
                    "predicted_date": str(res_date),
                    "type": "Date Mismatch"
                })

    cat_acc = (cat_correct / len(gold_df)) * 100
    date_acc = (date_correct / max(date_eval_total, 1)) * 100

    # 4. Reconcile events
    events = reconcile_events(extracted_items, messages)
    active_events = [e for e in events if e.get("status") in ("Upcoming", "Updated")]
    needs_review = [e for e in events if e.get("needs_review") or e.get("has_conflict")]
    cancelled = [e for e in events if e.get("status") == "Cancelled"]

    print("--------------------------------------------------")
    print(f"🎯 Category Classification Accuracy: {cat_correct}/{len(gold_df)} ({cat_acc:.1f}%)")
    print(f"📅 Date Resolution Accuracy:        {date_correct}/{date_eval_total} ({date_acc:.1f}%)")
    print("--------------------------------------------------")
    print(f"📥 Input Messages Processed:        {len(messages)}")
    print(f"🔄 Reconciled Clean Events:         {len(events)} (De-duplicated & Merged)")
    print(f"   • Active / Upcoming Events:      {len(active_events)}")
    print(f"   • Postponed / Rescheduled:       {len([e for e in events if e.get('status') == 'Updated'])}")
    print(f"   • Cancelled Notices:             {len(cancelled)}")
    print(f"   • Flagged for Human Review:      {len(needs_review)}")
    print("--------------------------------------------------")

    # Conflict detection check
    conflict_detected = any("202" in e.get("title", "") and e.get("has_conflict") for e in events)
    missing_date_flagged = any("GSoC" in e.get("title", "") and e.get("needs_review") for e in events)
    dbms_merged = any("DBMS" in e.get("title", "") and len(e.get("sources", [])) >= 3 for e in events)

    print("Reconciliation Integrity Checks:")
    print(f"  [✓] Repeated notices merged (DBMS Assignment x3 merged): {'PASS' if dbms_merged else 'FAIL'}")
    print(f"  [✓] Speculative conflict detected (ECE 202 unverified rumor): {'PASS' if conflict_detected else 'FAIL'}")
    print(f"  [✓] Missing date flagged for review (GSoC session TBA): {'PASS' if missing_date_flagged else 'FAIL'}")

    if error_cases:
        print("\nDiscrepancies / Error Analysis:")
        for err in error_cases:
            print(f"  Msg #{err['msg_id']}: {err['type']} -> {err}")
    else:
        print("\nAll benchmark assertions passed with 100% precision on the gold dataset.")

    return {
        "category_accuracy": cat_acc,
        "date_accuracy": date_acc,
        "total_messages": len(messages),
        "reconciled_events": len(events),
        "needs_review_count": len(needs_review),
        "error_count": len(error_cases)
    }


if __name__ == "__main__":
    live_flag = "--live" in sys.argv
    run_evaluation(use_live_api=live_flag)

