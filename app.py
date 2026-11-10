"""
Deadline Radar - Premium Academic Productivity SaaS
IIIT Hyderabad AI for Product Management Capstone.
Redesigned with a polished Light Theme (Linear / Notion Calendar / Raycast style).
"""

import os
import io
import json
import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Load local .env if present
load_dotenv()

from parser import parse_chat
from extract import extract_with_gemini
from reconcile import reconcile_events
from dates import resolve_date
from ics_export import export_to_ics
from sample_data import (
    SAMPLE_CHAT_RAW,
    SAMPLE_DETERMINISTIC_EXTRACTION,
    REAL_COURSE_DATASETS,
    load_real_chat_text,
    get_all_real_chats_combined,
)

# Page Configuration
st.set_page_config(
    page_title="Deadline Radar — Academic Schedule Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# LIGHT THEME DESIGN SYSTEM (Linear / Notion Calendar / Raycast)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* CSS Variables & Global Typography */
    :root {
        --bg: #F7F8FA;
        --surface: #FFFFFF;
        --sidebar: #FFFFFF;
        --text-primary: #182230;
        --text-secondary: #667085;
        --accent: #4468F5;
        --accent-hover: #3251D4;
        --border: #EAECF0;
        --border-subtle: #F2F4F7;
        --success: #16865C;
        --success-bg: #ECFDF3;
        --success-border: #A6F4C5;
        --warning: #B54708;
        --warning-bg: #FFFAEB;
        --warning-border: #FEDF89;
        --danger: #B42318;
        --danger-bg: #FEF3F2;
        --danger-border: #FECDCA;
        --info: #175CD3;
        --info-bg: #EFF8FF;
        --info-border: #B2DDFF;
    }

    /* Overall Layout Background */
    .stApp {
        background-color: var(--bg);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, Helvetica, Arial, sans-serif;
        font-size: 15px;
        line-height: 1.5;
    }

    /* Remove Streamlit Default Header Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    /* Clean Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid var(--border);
        box-shadow: none;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    /* Brand Header in Sidebar */
    .brand-container {
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 18px;
        border-bottom: 1px solid var(--border);
        margin-bottom: 16px;
    }
    .brand-icon {
        width: 32px;
        height: 32px;
        background: #4468F5;
        color: #FFFFFF;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 18px;
    }
    .brand-title {
        font-size: 17px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.3px;
        margin: 0;
    }
    .brand-subtitle {
        font-size: 12px;
        color: var(--text-secondary);
        margin: 0;
    }

    /* Page Headings */
    .page-header {
        margin-bottom: 24px;
    }
    .page-title {
        font-size: 26px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.5px;
        margin: 0 0 4px 0;
    }
    .page-subtitle {
        font-size: 14px;
        color: var(--text-secondary);
        margin: 0;
    }

    /* KPI Summary Cards */
    .kpi-card {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.05);
        transition: border-color 0.15s ease;
    }
    .kpi-card:hover {
        border-color: #D0D5DD;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 13px;
        font-weight: 500;
        color: var(--text-secondary);
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Linear-Style Row Container */
    .item-row {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        transition: all 0.15s ease;
    }
    .item-row:hover {
        border-color: #B2DDFF;
        box-shadow: 0 2px 6px rgba(16, 24, 40, 0.08);
    }

    /* Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 9px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.2px;
        white-space: nowrap;
    }
    .badge-upcoming {
        background-color: var(--success-bg);
        color: var(--success);
        border: 1px solid var(--success-border);
    }
    .badge-updated {
        background-color: var(--info-bg);
        color: var(--info);
        border: 1px solid var(--info-border);
    }
    .badge-review {
        background-color: var(--warning-bg);
        color: var(--warning);
        border: 1px solid var(--warning-border);
    }
    .badge-cancelled {
        background-color: var(--danger-bg);
        color: var(--danger);
        border: 1px solid var(--danger-border);
    }
    .badge-neutral {
        background-color: #F2F4F7;
        color: #344054;
        border: 1px solid #EAECF0;
    }

    /* Conflict Alert Box */
    .conflict-callout {
        background-color: #FFFAEB;
        border: 1px solid #FEDF89;
        border-left: 4px solid #F79009;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 12px 0 16px 0;
        color: #7A2E0E;
        font-size: 14px;
    }

    /* Source Quote Box */
    .source-snippet {
        background-color: #F8F9FC;
        border: 1px solid #EAECF0;
        border-left: 3px solid #4468F5;
        border-radius: 6px;
        padding: 10px 14px;
        margin-top: 8px;
        font-size: 13px;
        color: #344054;
        font-family: inherit;
    }

    /* Section White Card */
    .card-panel {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(16, 24, 40, 0.05);
    }

    /* Buttons override */
    button[kind="primary"] {
        background-color: #4468F5 !important;
        border: 1px solid #3251D4 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
    }
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D0D5DD !important;
        color: #344054 !important;
        font-weight: 500 !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "extracted_items" not in st.session_state:
    st.session_state["extracted_items"] = []
if "reconciled_events" not in st.session_state:
    st.session_state["reconciled_events"] = []
if "is_demo_mode" not in st.session_state:
    st.session_state["is_demo_mode"] = False
if "raw_chat_input" not in st.session_state:
    st.session_state["raw_chat_input"] = ""
if "current_nav" not in st.session_state:
    st.session_state["current_nav"] = "Overview"
if "selected_event_for_edit" not in st.session_state:
    st.session_state["selected_event_for_edit"] = None


# Auto-load synthetic demo data if completely fresh session so user gets instant value
if not st.session_state["messages"]:
    st.session_state["raw_chat_input"] = SAMPLE_CHAT_RAW
    st.session_state["messages"] = parse_chat(SAMPLE_CHAT_RAW, anonymize=True)
    st.session_state["extracted_items"] = SAMPLE_DETERMINISTIC_EXTRACTION
    st.session_state["reconciled_events"] = reconcile_events(
        SAMPLE_DETERMINISTIC_EXTRACTION,
        st.session_state["messages"]
    )
    st.session_state["is_demo_mode"] = True


# Helper functions
def get_review_count() -> int:
    return sum(1 for e in st.session_state["reconciled_events"] if e.get("needs_review") or e.get("has_conflict"))

def get_relative_time_label(target_date: Optional[date]) -> str:
    if not target_date:
        return "Date TBA"
    today = date.today()
    # If using test date in 2026, calculate relative to 2026-11-10
    base = date(2026, 11, 10) if target_date.year == 2026 else today
    diff = (target_date - base).days
    if diff == 0:
        return "Today"
    elif diff == 1:
        return "Tomorrow"
    elif diff > 1:
        return f"in {diff} days"
    elif diff == -1:
        return "Yesterday"
    else:
        return f"{abs(diff)} days ago"


# -----------------------------------------------------------------------------
# SINGLE-EVENT EDIT DIALOG (Streamlit Modal Dialog)
# -----------------------------------------------------------------------------
@st.dialog("Edit Event & Audit Provenance", width="large")
def show_edit_event_dialog(event_id: str):
    events = st.session_state["reconciled_events"]
    evt = next((e for e in events if e.get("id") == event_id), None)
    if not evt:
        st.error("Event not found.")
        return

    st.markdown(f"#### Edit: {evt.get('title')}")
    st.caption(f"Event ID: `{evt.get('id')}` • Category: `{evt.get('category')}` • Current Status: `{evt.get('status')}`")

    # Conflict banner inside editor if present
    if evt.get("has_conflict") and evt.get("conflict_reason"):
        st.markdown(f"""
        <div class="conflict-callout" style="margin-top: 4px;">
            <strong>⚠️ Flagged Conflict:</strong> {evt['conflict_reason']}
        </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        new_title = st.text_input("Title", value=evt.get("title", ""))
        new_course = st.text_input("Course / Subject", value=evt.get("course_or_subject", ""))
        new_venue = st.text_input("Venue / Portal", value=evt.get("venue", ""))
    with c2:
        curr_d = evt.get("date")
        if not isinstance(curr_d, (date, datetime)):
            try:
                curr_d = datetime.strptime(str(curr_d), "%Y-%m-%d").date() if curr_d else date.today()
            except Exception:
                curr_d = date.today()
        new_date = st.date_input("Event Date", value=curr_d)
        new_time = st.text_input("Time (HH:MM 24h format)", value=evt.get("time") or "")
        new_audience = st.text_input("Audience", value=evt.get("audience", "All"))

    st.markdown("---")
    st.markdown("##### 📜 Audit Provenance (Original Source Messages)")
    for src in evt.get("source_details", []):
        st.markdown(f"""
        <div class="source-snippet">
            <strong>Msg #{src.get('msg_id')}</strong> • <strong>{src.get('sender')}</strong> ({src.get('sent_at')}):<br>
            "{src.get('text')}"
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3 = st.columns([2, 1.5, 1.5])
    with b_col1:
        if st.button("💾 Save & Mark Confirmed", type="primary", use_container_width=True):
            evt["title"] = new_title
            evt["course_or_subject"] = new_course
            evt["venue"] = new_venue
            evt["date"] = new_date
            evt["time"] = new_time.strip() if new_time.strip() else None
            evt["audience"] = new_audience
            evt["needs_review"] = False
            evt["has_conflict"] = False
            evt["confirmed"] = True
            if evt.get("status") in ("Needs Review", "Cancelled"):
                evt["status"] = "Upcoming"
            st.success("Event updated successfully!")
            st.rerun()
    with b_col2:
        if st.button("❌ Mark Cancelled", use_container_width=True):
            evt["status"] = "Cancelled"
            evt["needs_review"] = False
            st.rerun()
    with b_col3:
        if st.button("Close", use_container_width=True):
            st.rerun()


# -----------------------------------------------------------------------------
# LEFT SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="brand-container">
        <div class="brand-icon">🎯</div>
        <div>
            <div class="brand-title">Deadline Radar</div>
            <div class="brand-subtitle">Academic Schedule Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    review_count = get_review_count()
    review_label = f"Needs Review ({review_count})" if review_count > 0 else "Needs Review"

    nav_options = [
        "Overview",
        "Deadlines",
        "Events",
        review_label,
        "Import Messages",
        "Calendar Export",
        "Settings",
    ]

    # Map current_nav to matching index
    current_index = 0
    if st.session_state["current_nav"] == "Deadlines":
        current_index = 1
    elif st.session_state["current_nav"] == "Events":
        current_index = 2
    elif "Needs Review" in st.session_state["current_nav"]:
        current_index = 3
    elif st.session_state["current_nav"] == "Import Messages":
        current_index = 4
    elif st.session_state["current_nav"] == "Calendar Export":
        current_index = 5
    elif st.session_state["current_nav"] == "Settings":
        current_index = 6

    selected_nav = st.radio(
        "Navigation",
        options=nav_options,
        index=current_index,
        label_visibility="collapsed"
    )

    # Normalize selected_nav back to core page name
    if "Needs Review" in selected_nav:
        st.session_state["current_nav"] = "Needs Review"
    else:
        st.session_state["current_nav"] = selected_nav

    st.markdown("---")
    
    # Sidebar Quick Stats / Status
    events_all = st.session_state.get("reconciled_events", [])
    active_count = sum(1 for e in events_all if e.get("status") in ("Upcoming", "Updated"))
    
    st.markdown(f"""
    <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.8;">
        <div><strong>Status:</strong> <span style="color: #16865C;">● Ready</span></div>
        <div><strong>Active Items:</strong> {active_count} confirmed</div>
        <div><strong>Mode:</strong> {'⚡ Deterministic Demo' if st.session_state.get('is_demo_mode') else 'Live Gemini API'}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📚 Switch Course Chat")
    dataset_choice = st.selectbox(
        "Choose Dataset",
        options=[
            "⚡ Synthetic Benchmark (16 Edge Cases)",
            "📚 M26: Product Management",
            "📚 M26: Design Thinking",
            "📚 M26: Business Fundamentals",
            "📚 M26: AI for Product Managers",
            "🎓 All 4 M26 Courses Combined"
        ],
        index=0,
        label_visibility="collapsed"
    )

    if st.button("Load Dataset", use_container_width=True, type="secondary"):
        if "Synthetic" in dataset_choice:
            st.session_state["raw_chat_input"] = SAMPLE_CHAT_RAW
            st.session_state["messages"] = parse_chat(SAMPLE_CHAT_RAW, anonymize=True)
            st.session_state["extracted_items"] = SAMPLE_DETERMINISTIC_EXTRACTION
            st.session_state["reconciled_events"] = reconcile_events(SAMPLE_DETERMINISTIC_EXTRACTION, st.session_state["messages"])
        elif "Product Management" in dataset_choice:
            raw = load_real_chat_text("M26_Product_Management")
            st.session_state["raw_chat_input"] = raw
            st.session_state["messages"] = parse_chat(raw, anonymize=True)
            st.session_state["extracted_items"] = REAL_COURSE_DATASETS["m26_pm"]["deterministic_extractions"]
            st.session_state["reconciled_events"] = reconcile_events(st.session_state["extracted_items"], st.session_state["messages"])
        elif "Design Thinking" in dataset_choice:
            raw = load_real_chat_text("M26_Design_Thinking")
            st.session_state["raw_chat_input"] = raw
            st.session_state["messages"] = parse_chat(raw, anonymize=True)
            st.session_state["extracted_items"] = REAL_COURSE_DATASETS["m26_dt"]["deterministic_extractions"]
            st.session_state["reconciled_events"] = reconcile_events(st.session_state["extracted_items"], st.session_state["messages"])
        elif "Business Fundamentals" in dataset_choice:
            raw = load_real_chat_text("M26_Business_Fundamentals")
            st.session_state["raw_chat_input"] = raw
            st.session_state["messages"] = parse_chat(raw, anonymize=True)
            st.session_state["extracted_items"] = REAL_COURSE_DATASETS["m26_bf"]["deterministic_extractions"]
            st.session_state["reconciled_events"] = reconcile_events(st.session_state["extracted_items"], st.session_state["messages"])
        elif "AI for Product Managers" in dataset_choice:
            raw = load_real_chat_text("M26_AI_for_Product_Managers")
            st.session_state["raw_chat_input"] = raw
            st.session_state["messages"] = parse_chat(raw, anonymize=True)
            st.session_state["extracted_items"] = REAL_COURSE_DATASETS["m26_ai_pm"]["deterministic_extractions"]
            st.session_state["reconciled_events"] = reconcile_events(st.session_state["extracted_items"], st.session_state["messages"])
        elif "All 4" in dataset_choice:
            raw = get_all_real_chats_combined()
            st.session_state["raw_chat_input"] = raw
            st.session_state["messages"] = parse_chat(raw, anonymize=True)
            # Combine all deterministic extractions
            all_dets = []
            for k in REAL_COURSE_DATASETS:
                all_dets.extend(REAL_COURSE_DATASETS[k]["deterministic_extractions"])
            st.session_state["extracted_items"] = all_dets
            st.session_state["reconciled_events"] = reconcile_events(all_dets, st.session_state["messages"])

        st.session_state["is_demo_mode"] = True
        st.session_state["current_nav"] = "Overview"
        st.rerun()


# -----------------------------------------------------------------------------
# MAIN VIEW ROUTING
# -----------------------------------------------------------------------------
events = st.session_state.get("reconciled_events", [])
page = st.session_state["current_nav"]


# =============================================================================
# PAGE 1: OVERVIEW DASHBOARD
# =============================================================================
if page == "Overview":
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Campus Schedule Overview</h1>
        <p class="page-subtitle">Verified, deduplicated academic deadlines and schedule changes extracted from campus chats.</p>
    </div>
    """, unsafe_allow_html=True)

    # 4 KPI Summary Cards
    deadlines_active = [e for e in events if e.get("category") == "deadline" and e.get("status") != "Cancelled"]
    events_active = [e for e in events if e.get("category") == "event" and e.get("status") != "Cancelled"]
    postponements = [e for e in events if e.get("status") == "Updated"]
    needs_review = [e for e in events if e.get("needs_review") or e.get("has_conflict")]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: #4468F5;">{len(deadlines_active)}</div>
            <div class="kpi-label">Active Deadlines</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: #16865C;">{len(events_active)}</div>
            <div class="kpi-label">Upcoming Events</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: #175CD3;">{len(postponements)}</div>
            <div class="kpi-label">Updated / Postponed</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        rev_color = "#B54708" if len(needs_review) > 0 else "#667085"
        st.markdown(f"""
        <div class="kpi-card" style="border-color: {'#FEDF89' if len(needs_review) > 0 else '#EAECF0'};">
            <div class="kpi-value" style="color: {rev_color};">{len(needs_review)}</div>
            <div class="kpi-label">Needs Review</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Attention Callout if items need review
    if len(needs_review) > 0:
        st.markdown(f"""
        <div class="conflict-callout" style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>⚠️ {len(needs_review)} announcements require human verification:</strong>
                Conflicting student rumors, unverified cancellations, or missing dates detected.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Resolve {len(needs_review)} Flagged Items →", type="secondary"):
            st.session_state["current_nav"] = "Needs Review"
            st.rerun()

    # Two Column Layout: Upcoming Deadlines & Recent Changes
    col_left, col_right = st.columns([1.6, 1.2])

    with col_left:
        st.markdown("#### ⏱️ Imminent Deadlines")
        deadlines_sorted = sorted(deadlines_active, key=lambda e: str(e.get("date") or "9999-99-99"))
        if deadlines_sorted:
            for d in deadlines_sorted[:5]:
                d_id = d.get("id")
                due_badge = get_relative_time_label(d.get("date"))
                date_str = d.get("date").strftime("%d %b %Y") if hasattr(d.get("date"), "strftime") else str(d.get("date") or "Date TBA")
                
                row_c1, row_c2 = st.columns([4, 1])
                with row_c1:
                    st.markdown(f"""
                    <div style="background: #FFFFFF; border: 1px solid #EAECF0; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="badge badge-neutral">{d.get('course_or_subject', 'General')}</span>
                            <span class="badge badge-upcoming">{due_badge}</span>
                        </div>
                        <div style="font-weight: 600; font-size: 15px; color: #182230; margin: 6px 0 2px 0;">{d.get('title')}</div>
                        <div style="font-size: 13px; color: #667085;">
                            Due: <strong>{date_str}</strong> {('• ' + d.get('time')) if d.get('time') else ''} • {d.get('venue') or 'Campus'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with row_c2:
                    if st.button("Edit", key=f"ov_btn_{d_id}", use_container_width=True):
                        show_edit_event_dialog(d_id)
        else:
            st.info("No active deadlines.")

    with col_right:
        st.markdown("#### 🔄 Schedule Changes & Postponements")
        if postponements:
            for p in postponements:
                p_id = p.get("id")
                hist_note = p.get("history", ["Updated"])[-1] if p.get("history") else "Schedule revised"
                row_p1, row_p2 = st.columns([4, 1])
                with row_p1:
                    st.markdown(f"""
                    <div style="background: #FFFFFF; border: 1px solid #B2DDFF; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
                        <span class="badge badge-updated">Postponed / Rescheduled</span>
                        <div style="font-weight: 600; font-size: 14px; color: #182230; margin: 4px 0 2px 0;">{p.get('title')}</div>
                        <div style="font-size: 13px; color: #175CD3;">
                            New Date: <strong>{p.get('date')}</strong> • {p.get('time') or '10:00'} • {p.get('venue') or 'Audi 2'}
                        </div>
                        <div style="font-size: 12px; color: #667085; margin-top: 4px;">
                            <em>{hist_note}</em>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with row_p2:
                    if st.button("Inspect", key=f"ov_btn_p_{p_id}", use_container_width=True):
                        show_edit_event_dialog(p_id)
        else:
            st.caption("No recent schedule changes.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ⚡ Quick Actions")
        if st.button("📥 Import New Chat Export", use_container_width=True):
            st.session_state["current_nav"] = "Import Messages"
            st.rerun()
        if st.button("📆 Download .ics Calendar", use_container_width=True):
            st.session_state["current_nav"] = "Calendar Export"
            st.rerun()


# =============================================================================
# PAGE 2: DEADLINES
# =============================================================================
elif page == "Deadlines":
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Academic Deadlines</h1>
        <p class="page-subtitle">Track, filter, and verify assignments, project submissions, and registrations.</p>
    </div>
    """, unsafe_allow_html=True)

    deadlines_all = [e for e in events if e.get("category") == "deadline"]

    # Filter Bar
    f1, f2 = st.columns([3, 1])
    with f1:
        search_query = st.text_input("Search deadlines...", placeholder="Search by title, subject, or portal...", label_visibility="collapsed")
    with f2:
        status_filter = st.selectbox("Status", ["All Active", "All (Including Cancelled)", "Needs Review"], label_visibility="collapsed")

    filtered_d = deadlines_all
    if search_query.strip():
        q = search_query.lower()
        filtered_d = [d for d in filtered_d if q in d.get("title", "").lower() or q in d.get("course_or_subject", "").lower()]
    if status_filter == "All Active":
        filtered_d = [d for d in filtered_d if d.get("status") != "Cancelled"]
    elif status_filter == "Needs Review":
        filtered_d = [d for d in filtered_d if d.get("needs_review")]

    filtered_d.sort(key=lambda d: str(d.get("date") or "9999-99-99"))

    st.markdown("<br>", unsafe_allow_html=True)
    if not filtered_d:
        st.info("No deadlines matching your filter criteria.")
    else:
        for d in filtered_d:
            d_id = d.get("id")
            status = d.get("status", "Upcoming")
            due_badge = get_relative_time_label(d.get("date"))
            date_str = d.get("date").strftime("%a, %d %b %Y") if hasattr(d.get("date"), "strftime") else str(d.get("date") or "Date TBA")
            src_count = len(d.get("sources", []))

            r_col1, r_col2 = st.columns([5, 1])
            with r_col1:
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #EAECF0; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <span class="badge badge-neutral">{d.get('course_or_subject', 'General')}</span>
                            <span class="badge {'badge-upcoming' if status == 'Upcoming' else 'badge-review'}">{status}</span>
                        </div>
                        <span class="badge badge-upcoming" style="font-size: 13px;">{due_badge}</span>
                    </div>
                    <div style="font-size: 16px; font-weight: 600; color: #182230;">{d.get('title')}</div>
                    <div style="font-size: 13px; color: #667085; margin-top: 4px;">
                        Due: <strong>{date_str}</strong> {('at ' + d.get('time')) if d.get('time') else '23:59'} • Portal: <strong>{d.get('venue') or 'LMS Portal'}</strong> • Merged notices: <strong>{src_count}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with r_col2:
                if st.button("Inspect / Edit", key=f"btn_edit_d_{d_id}", use_container_width=True):
                    show_edit_event_dialog(d_id)


# =============================================================================
# PAGE 3: EVENTS
# =============================================================================
elif page == "Events":
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Scheduled Campus Events</h1>
        <p class="page-subtitle">Quizzes, lectures, lab sessions, seminars, and club meetings in chronological order.</p>
    </div>
    """, unsafe_allow_html=True)

    events_list = [e for e in events if e.get("category") in ("event", "schedule_change", "cancellation")]
    events_list.sort(key=lambda e: str(e.get("date") or "9999-99-99"))

    if not events_list:
        st.info("No events recorded.")
    else:
        for ev in events_list:
            ev_id = ev.get("id")
            status = ev.get("status", "Upcoming")
            
            if status == "Updated":
                badge_html = '<span class="badge badge-updated">Updated / Postponed</span>'
            elif status == "Cancelled":
                badge_html = '<span class="badge badge-cancelled">Cancelled</span>'
            elif ev.get("has_conflict"):
                badge_html = '<span class="badge badge-review">Conflict Detected</span>'
            else:
                badge_html = '<span class="badge badge-upcoming">Upcoming Event</span>'

            date_str = ev.get("date").strftime("%a, %d %b %Y") if hasattr(ev.get("date"), "strftime") else str(ev.get("date") or "Date TBA")
            time_str = ev.get("time") or "Time TBA"

            r_col1, r_col2 = st.columns([5, 1])
            with r_col1:
                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #EAECF0; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span class="badge badge-neutral">{ev.get('course_or_subject', 'General')}</span>
                        {badge_html}
                    </div>
                    <div style="font-size: 16px; font-weight: 600; color: #182230;">{ev.get('title')}</div>
                    <div style="font-size: 13px; color: #667085; margin-top: 4px;">
                        Date & Time: <strong>{date_str}</strong> at <strong>{time_str}</strong> • Venue: <strong>{ev.get('venue') or 'Campus'}</strong> • Audience: {ev.get('audience', 'All')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with r_col2:
                if st.button("Inspect / Edit", key=f"btn_edit_ev_{ev_id}", use_container_width=True):
                    show_edit_event_dialog(ev_id)


# =============================================================================
# PAGE 4: NEEDS REVIEW (FLAGSHIP RECONCILIATION FEATURE)
# =============================================================================
elif page == "Needs Review":
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Human Review & Conflict Resolution</h1>
        <p class="page-subtitle">Announcements requiring manual verification. Conflicting rumors, unverified cancellations, and TBA dates are separated here to prevent silent schedule corruption.</p>
    </div>
    """, unsafe_allow_html=True)

    items_for_review = [e for e in events if e.get("needs_review") or e.get("has_conflict")]

    if not items_for_review:
        st.success("🎉 All announcements verified! No conflicts or unconfirmed items remaining.")
    else:
        st.markdown(f"**{len(items_for_review)} announcements requiring attention:**")
        
        for rev_item in items_for_review:
            r_id = rev_item.get("id")
            title = rev_item.get("title", "Untitled Notice")
            reason = rev_item.get("conflict_reason") or "Notice has low extraction confidence or missing date."
            conf_pct = int((rev_item.get("confidence") or 0.6) * 100)

            # Build source message HTML snippets directly on the card
            src_snippets_html = ""
            for src in rev_item.get("source_details", []):
                src_snippets_html += f"""
                <div class="source-snippet" style="margin-top: 6px;">
                    <strong>Msg #{src.get('msg_id')}</strong> • <strong>{src.get('sender')}</strong> <span style="color:#667085;">({src.get('sent_at')})</span>:<br>
                    "{src.get('text')}"
                </div>
                """

            st.markdown(f"""
            <div class="card-panel" style="border-left: 4px solid #F79009; margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span class="badge badge-review">Requires Verification</span>
                        <span style="font-size: 13px; color: #667085; margin-left: 8px;">Confidence: <strong>{conf_pct}%</strong></span>
                        <h3 style="margin: 6px 0 4px 0; font-size: 18px; color: #182230;">{title}</h3>
                        <div style="font-size: 14px; color: #475467;">
                            Subject: <strong>{rev_item.get('course_or_subject', 'General')}</strong> • Current Date: <strong>{rev_item.get('date') or '⚠️ Missing (TBA)'}</strong> • Venue: <strong>{rev_item.get('venue') or 'Campus'}</strong>
                        </div>
                    </div>
                </div>
                <div class="conflict-callout" style="margin-top: 10px;">
                    <strong>Why flagged?</strong> {reason}
                </div>
                <div style="margin-top: 10px;">
                    <strong style="font-size: 13px; color: #344054;">Contributing WhatsApp Messages:</strong>
                    {src_snippets_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Action Buttons Row
            b1, b2, b3 = st.columns([2, 2, 4])
            with b1:
                if st.button("✅ Confirm Official Notice", key=f"rev_confirm_{r_id}", use_container_width=True, type="primary"):
                    rev_item["needs_review"] = False
                    rev_item["has_conflict"] = False
                    rev_item["confirmed"] = True
                    if rev_item.get("status") == "Needs Review":
                        rev_item["status"] = "Upcoming"
                    st.success(f"Confirmed '{title}'!")
                    st.rerun()
            with b2:
                if st.button("❌ Mark Cancelled / Ignore", key=f"rev_reject_{r_id}", use_container_width=True):
                    rev_item["status"] = "Cancelled"
                    rev_item["needs_review"] = False
                    st.rerun()
            with b3:
                if st.button("⚙️ Edit Date & Resolve Conflict", key=f"rev_edit_{r_id}", use_container_width=True):
                    show_edit_event_dialog(r_id)

            st.markdown("<hr style='border: 0; border-top: 1px dashed #EAECF0; margin: 16px 0;'>", unsafe_allow_html=True)


# =============================================================================
# PAGE 5: IMPORT MESSAGES (DEDICATED WORKFLOW)
# =============================================================================
elif page == "Import Messages":
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Import Campus Chat Export</h1>
        <p class="page-subtitle">Upload exported chat files from WhatsApp or Telegram, or paste raw announcement messages.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div class="card-panel">
            <h3 style="margin-top: 0; font-size: 18px;">1. Select Input Method</h3>
        </div>
        """, unsafe_allow_html=True)

        input_tab1, input_tab2 = st.tabs(["📁 Upload WhatsApp Export (.txt)", "📋 Paste Messages"])

        with input_tab1:
            uploaded_file = st.file_uploader(
                "Upload chat export .txt file",
                type=["txt"],
                help="WhatsApp: Chat > More > Export Chat > Without Media"
            )
            st.caption("Standard Android and iOS WhatsApp chat export formats supported.")

        with input_tab2:
            pasted_text = st.text_area(
                "Paste announcements here",
                value=st.session_state.get("raw_chat_input", ""),
                height=180,
                placeholder="[10/11/26, 09:15] CR: DBMS Assignment 2 due on 14th Nov 11:59 PM..."
            )

        # Content resolution
        active_raw = ""
        if uploaded_file is not None:
            active_raw = uploaded_file.read().decode("utf-8", errors="ignore")
        elif pasted_text.strip():
            active_raw = pasted_text.strip()

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Privacy & Extraction Controls
        p1, p2 = st.columns([2, 1])
        with p1:
            anonymize = st.checkbox("Enable Privacy Anonymization", value=True, help="Scrubs student phone numbers and maps names to Student 1, Student 2 before processing.")
        with p2:
            st.caption("Processing runs in-memory with zero permanent storage.")

        st.markdown("<br>", unsafe_allow_html=True)
        btn1, btn2 = st.columns([2, 2])
        with btn1:
            run_ai = st.button("🚀 Analyse Messages with Gemini AI", type="primary", use_container_width=True)
        with btn2:
            load_sample = st.button("⚡ Load 16 Sample Messages (IIIT-H Demo)", use_container_width=True)

        if run_ai:
            if not active_raw.strip():
                st.warning("Please upload a .txt file or paste chat messages.")
            else:
                api_key = os.getenv("GEMINI_API_KEY", "")
                if not api_key:
                    st.error("🔑 Missing Gemini API Key! Please enter your key in Settings, or click 'Load 16 Sample Messages' for deterministic demo analysis.")
                else:
                    with st.spinner("Extracting structured deadlines and reconciling updates via Gemini..."):
                        try:
                            parsed_msgs = parse_chat(active_raw, anonymize=anonymize)
                            st.session_state["messages"] = parsed_msgs
                            extracted = extract_with_gemini(
                                parsed_msgs,
                                api_key=api_key,
                                model_name="gemini-2.5-flash"
                            )
                            st.session_state["extracted_items"] = extracted
                            st.session_state["reconciled_events"] = reconcile_events(extracted, parsed_msgs)
                            st.session_state["is_demo_mode"] = False
                            st.success(f"Successfully processed {len(parsed_msgs)} messages!")
                            st.session_state["current_nav"] = "Overview"
                            st.rerun()
                        except Exception as e:
                            st.error(f"Extraction failed: {str(e)}")

        if load_sample:
            st.session_state["raw_chat_input"] = SAMPLE_CHAT_RAW
            st.session_state["messages"] = parse_chat(SAMPLE_CHAT_RAW, anonymize=anonymize)
            st.session_state["extracted_items"] = SAMPLE_DETERMINISTIC_EXTRACTION
            st.session_state["reconciled_events"] = reconcile_events(
                SAMPLE_DETERMINISTIC_EXTRACTION,
                st.session_state["messages"]
            )
            st.session_state["is_demo_mode"] = True
            st.session_state["current_nav"] = "Overview"
            st.rerun()

        st.markdown("<br><hr>", unsafe_allow_html=True)
        st.markdown("#### 🎓 Load Authentic M26 Course Chat Exports")
        st.caption("Select any of your 4 actual IIIT Hyderabad courses to load real WhatsApp chats with Moodle submissions, team selection forms, and lecture venue shifts:")

        rc_col1, rc_col2 = st.columns(2)
        with rc_col1:
            if st.button("📚 Load M26: Product Management", use_container_width=True):
                raw = load_real_chat_text("M26_Product_Management")
                st.session_state["raw_chat_input"] = raw
                st.session_state["messages"] = parse_chat(raw, anonymize=anonymize)
                st.session_state["extracted_items"] = REAL_COURSE_DATASETS["m26_pm"]["deterministic_extractions"]
                st.session_state["reconciled_events"] = reconcile_events(st.session_state["extracted_items"], st.session_state["messages"])
                st.session_state["is_demo_mode"] = True
                st.session_state["current_nav"] = "Overview"
                st.rerun()
            if st.button("📚 Load M26: Design Thinking", use_container_width=True):
                raw = load_real_chat_text("M26_Design_Thinking")
                st.session_state["raw_chat_input"] = raw
                st.session_state["messages"] = parse_chat(raw, anonymize=anonymize)
                st.session_state["extracted_items"] = REAL_COURSE_DATASETS["m26_dt"]["deterministic_extractions"]
                st.session_state["reconciled_events"] = reconcile_events(st.session_state["extracted_items"], st.session_state["messages"])
                st.session_state["is_demo_mode"] = True
                st.session_state["current_nav"] = "Overview"
                st.rerun()
        with rc_col2:
            if st.button("📚 Load M26: Business Fundamentals", use_container_width=True):
                raw = load_real_chat_text("M26_Business_Fundamentals")
                st.session_state["raw_chat_input"] = raw
                st.session_state["messages"] = parse_chat(raw, anonymize=anonymize)
                st.session_state["extracted_items"] = REAL_COURSE_DATASETS["m26_bf"]["deterministic_extractions"]
                st.session_state["reconciled_events"] = reconcile_events(st.session_state["extracted_items"], st.session_state["messages"])
                st.session_state["is_demo_mode"] = True
                st.session_state["current_nav"] = "Overview"
                st.rerun()
            if st.button("📚 Load M26: AI for Product Managers", use_container_width=True):
                raw = load_real_chat_text("M26_AI_for_Product_Managers")
                st.session_state["raw_chat_input"] = raw
                st.session_state["messages"] = parse_chat(raw, anonymize=anonymize)
                st.session_state["extracted_items"] = REAL_COURSE_DATASETS["m26_ai_pm"]["deterministic_extractions"]
                st.session_state["reconciled_events"] = reconcile_events(st.session_state["extracted_items"], st.session_state["messages"])
                st.session_state["is_demo_mode"] = True
                st.session_state["current_nav"] = "Overview"
                st.rerun()

        if st.button("🌟 Load All 4 M26 Courses Combined", use_container_width=True, type="secondary"):
            raw = get_all_real_chats_combined()
            st.session_state["raw_chat_input"] = raw
            st.session_state["messages"] = parse_chat(raw, anonymize=anonymize)
            all_dets = []
            for k in REAL_COURSE_DATASETS:
                all_dets.extend(REAL_COURSE_DATASETS[k]["deterministic_extractions"])
            st.session_state["extracted_items"] = all_dets
            st.session_state["reconciled_events"] = reconcile_events(all_dets, st.session_state["messages"])
            st.session_state["is_demo_mode"] = True
            st.session_state["current_nav"] = "Overview"
            st.rerun()


# =============================================================================
# PAGE 6: CALENDAR EXPORT
# =============================================================================
elif page == "Calendar Export":
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Export Calendar & Synchronize</h1>
        <p class="page-subtitle">Generate standard RFC 5545 iCalendar (.ics) files compatible with Google Calendar, Apple Calendar, and Outlook.</p>
    </div>
    """, unsafe_allow_html=True)

    confirmed_active = [e for e in events if e.get("status") != "Cancelled" and e.get("date") is not None and e.get("confirmed", True)]
    cancelled_count = sum(1 for e in events if e.get("status") == "Cancelled")
    unconfirmed_count = sum(1 for e in events if e.get("needs_review") or e.get("has_conflict") or e.get("date") is None)

    # Export Readiness Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="border-color: #A6F4C5;">
            <div class="kpi-value" style="color: #16865C;">{len(confirmed_active)}</div>
            <div class="kpi-label">Ready for Export</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: #B42318;">{cancelled_count}</div>
            <div class="kpi-label">Cancelled (Excluded)</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value" style="color: #B54708;">{unconfirmed_count}</div>
            <div class="kpi-label">Unconfirmed / Missing Dates</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if unconfirmed_count > 0:
        st.warning(f"⚠️ You have {unconfirmed_count} unconfirmed notices or items with missing dates. You can review them before exporting.")

    ics_content = export_to_ics(confirmed_active)

    st.markdown("### 📥 Download Formats")
    d_col1, d_col2, d_col3 = st.columns([2, 1, 1])
    with d_col1:
        st.download_button(
            label=f"📥 Download .ics Calendar File ({len(confirmed_active)} Events)",
            data=ics_content,
            file_name=f"deadline_radar_{datetime.now().strftime('%Y%m%d')}.ics",
            mime="text/calendar",
            type="primary",
            use_container_width=True
        )
    with d_col2:
        df_export = pd.DataFrame([
            {
                "Title": e.get("title"),
                "Category": e.get("category"),
                "Date": str(e.get("date")),
                "Time": e.get("time") or "",
                "Venue": e.get("venue") or "",
                "Course": e.get("course_or_subject") or "",
                "Status": e.get("status")
            }
            for e in confirmed_active
        ])
        st.download_button(
            label="📊 Export CSV",
            data=df_export.to_csv(index=False),
            file_name=f"deadlines_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with d_col3:
        json_export = json.dumps(confirmed_active, default=str, indent=2)
        st.download_button(
            label="📄 Export JSON",
            data=json_export,
            file_name=f"deadlines_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📋 Preview of Events in Calendar Export")
    if confirmed_active:
        preview_df = pd.DataFrame([
            {
                "Title": e.get("title"),
                "Date": str(e.get("date")),
                "Time": e.get("time") or "All Day",
                "Venue": e.get("venue") or "Campus",
                "Course": e.get("course_or_subject") or "General",
                "Status": e.get("status")
            }
            for e in confirmed_active
        ])
        st.dataframe(preview_df, use_container_width=True, hide_index=True)
    else:
        st.info("No active confirmed events ready for export.")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("#### 📱 How to Import into Your Calendar:")
    st.markdown("""
    - **Google Calendar**: Settings ⚙️ > Import & Export > Select file from your computer > Choose target calendar > Click Import.
    - **Apple Calendar (Mac/iOS)**: Double-click the downloaded `.ics` file or drag into Calendar app.
    - **Outlook**: File > Open & Export > Open Calendar (.ics).
    """)


# =============================================================================
# PAGE 7: SETTINGS & MODEL CONFIGURATION
# =============================================================================
elif page == "Settings":
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Settings & Engine Configuration</h1>
        <p class="page-subtitle">Configure Gemini API keys, default models, timezone, and student privacy controls.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("""
        <div class="card-panel">
            <h3 style="margin-top:0; font-size:18px;">🔑 Gemini API Credentials</h3>
        </div>
        """, unsafe_allow_html=True)

        current_key = os.getenv("GEMINI_API_KEY", "")
        new_key = st.text_input("Gemini API Key", value=current_key, type="password", help="Obtain a free API key from https://aistudio.google.com/")
        
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox("Model Selection", ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"], index=0)
        with c2:
            st.text_input("Default Timezone", value="Asia/Kolkata (IST)", disabled=True)

        if st.button("Save Settings", type="primary"):
            if new_key.strip():
                os.environ["GEMINI_API_KEY"] = new_key.strip()
                st.success("API Key updated for this session!")
            else:
                st.info("API Key cleared. Application will operate in Deterministic Demo Mode.")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div class="card-panel">
            <h3 style="margin-top:0; font-size:18px;">ℹ️ About Deadline Radar (IIIT Hyderabad Capstone)</h3>
            <p style="font-size:14px; color:#475467; margin-bottom: 0;">
                Built for the <strong>AI for Product Management</strong> capstone project. 
                Deadline Radar solves communication breakdown in informal college chat groups through 
                zero-hallucination entity extraction, authoritative update reconciliation, and calendar synchronization.
            </p>
        </div>
        """, unsafe_allow_html=True)
