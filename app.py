
import os
import io
import pandas as pd
import streamlit as st
import urllib.parse as up

CHECK_COL = "check?"
CHECK_VAL = "checked"

st.set_page_config(page_title="Nazdikia – Iranian List Reviewer (Web MVP)", layout="wide")

@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(file_bytes), dtype=str, encoding="utf-8-sig").fillna("")

def build_google_query(name, city, subcat):
    parts = [str(name or "").strip()]
    if city: parts.append(str(city).strip())
    if subcat: parts.append(str(subcat).strip())
    parts.append("Persian Iranian Farsi")
    q = " ".join([p for p in parts if p])
    url = "https://www.google.com/search?q=" + up.quote(q)
    return q, url

def other_subcategories(df_all: pd.DataFrame, name_val: str, current_subcat: str):
    if not isinstance(name_val, str) or not name_val.strip():
        return []
    if "name" not in df_all.columns or "subcategory" not in df_all.columns:
        return []
    series_names = df_all["name"].astype(str).str.strip().str.lower()
    name_norm = name_val.strip().lower()
    matches = df_all.loc[series_names == name_norm, "subcategory"].astype(str).str.strip()
    cur_norm = (current_subcat or "").strip().lower()
    out = sorted({s for s in matches if s and s.lower() != cur_norm})
    return out

def mark_checked_in_all(df_all: pd.DataFrame, row: pd.Series):
    idx_all = None
    # Prefer exact match by place_id
    if "place_id" in df_all.columns and str(row.get("place_id", "")).strip():
        pid = str(row.get("place_id")).strip()
        cand = df_all["place_id"].astype(str).str.strip() == pid
        if cand.any():
            idx_all = cand.idxmax()

    # Fallback composite key on exact equality of selected fields
    if idx_all is None:
        cond = pd.Series([True] * len(df_all))
        for c in ["name", "city", "website", "link"]:
            if c in df_all.columns:
                v = str(row.get(c, "")).strip()
                cond = cond & (df_all[c].astype(str).str.strip() == v)
        if cond.any():
            idx_all = cond.idxmax()

    if idx_all is not None:
        df_all.at[idx_all, CHECK_COL] = CHECK_VAL

def delete_in_all(df_all: pd.DataFrame, row: pd.Series) -> pd.DataFrame:
    cond = pd.Series([True] * len(df_all))
    for c in ["name", "city", "website", "link"]:
        if c in df_all.columns:
            v = str(row.get(c, "")).strip()
            cond = cond & (df_all[c].astype(str).str.strip() == v)
    idxs = df_all[cond].index
    if len(idxs) > 0:
        df_all = df_all.drop(idxs)
    return df_all

def init_state():
    for k, v in {
        "df_all": None,
        "unchecked_idx": 0,
        "filename": None,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

st.title("Nazdikia – Iranian List Reviewer (Web MVP)")

with st.sidebar:
    st.header("1) Upload CSV")
    uploaded = st.file_uploader("iranian_only_fa.csv", type=["csv"])
    autosave = st.toggle("Autosave to memory (download anytime)", value=True)
    st.caption("This MVP stores your changes in memory during the session. Use the Download button to export the updated CSV.")

    st.header("2) Navigation")
    if st.session_state.df_all is not None:
        total_unchecked = (st.session_state.df_all[CHECK_COL] != CHECK_VAL).sum()
        st.write(f"Unchecked rows: **{int(total_unchecked)}**")
        st.session_state.unchecked_idx = st.number_input(
            "Jump to row index", min_value=0, max_value=max(0, int(total_unchecked) - 1),
            value=int(st.session_state.unchecked_idx), step=1
        )

    st.header("3) Download")
    if st.session_state.df_all is not None:
        # Export current df_all
        out = st.session_state.df_all.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("💾 Download reviewed CSV", data=out, file_name="iranian_only_fa_reviewed.csv", mime="text/csv")

if uploaded is not None and st.session_state.df_all is None:
    df_all = load_csv(uploaded.getvalue())
    if CHECK_COL not in df_all.columns:
        df_all[CHECK_COL] = ""
    # Keep CHECK_COL as last column
    cols = [c for c in df_all.columns if c != CHECK_COL] + [CHECK_COL]
    df_all = df_all[cols]
    st.session_state.df_all = df_all
    st.session_state.filename = uploaded.name

if st.session_state.df_all is None:
    st.info("Please upload your input CSV in the sidebar to begin.")
    st.stop()

df_all = st.session_state.df_all
unchecked_mask = df_all[CHECK_COL].astype(str).str.strip().str.lower().ne(CHECK_VAL)
df_unchecked = df_all.loc[unchecked_mask].reset_index(drop=True)

if df_unchecked.empty:
    st.success("🎉 All rows reviewed! You can still download the CSV from the sidebar.")
    st.stop()

idx = int(st.session_state.unchecked_idx)
idx = max(0, min(idx, len(df_unchecked)-1))
row = df_unchecked.iloc[idx]

# Header / progress
left, right = st.columns([3, 2])
with left:
    st.subheader(f"Row {idx+1} of {len(df_unchecked)}")
    st.caption(f"File: {st.session_state.filename or 'uploaded.csv'}")
with right:
    st.metric("Remaining", len(df_unchecked))

# Display fields
name = str(row.get("name", "") or "")
city = str(row.get("city", "") or "")
subcat = str(row.get("subcategory", "") or "")
site = str(row.get("website", "") or "").strip()
maps = str(row.get("link", "") or "").strip()

st.write(f"**Name (EN):** {name}")
st.write(f"**City:** {city}  |  **Subcategory:** {subcat}")

cols = st.columns([2,2,2,1])
with cols[0]:
    if site:
        st.markdown(f"**Website:** [{site}]({site})")
    else:
        st.markdown("**Website:** —")
with cols[1]:
    if maps:
        st.markdown(f"**Google Maps:** [{maps}]({maps})")
    else:
        st.markdown("**Google Maps:** —")
with cols[2]:
    q_text, q_url = build_google_query(name, city, subcat)
    st.markdown(f"**Google query:** `{q_text}`  \n[Open search]({q_url})")
with cols[3]:
    st.write("")

# Other categories
with st.expander("Other categories for this name"):
    others = other_subcategories(df_all, name, subcat)
    if others:
        st.write("\n".join(f"• {s}" for s in others))
    else:
        st.write("(nothing else)")

# Actions
a1, a2, a3, a4 = st.columns(4)
do_rerun = False

if a1.button("⬅️ Back", use_container_width=True):
    st.session_state.unchecked_idx = max(0, idx-1)
    do_rerun = True

if a2.button("✅ Approve & Next", type="primary", use_container_width=True):
    # mark checked in df_all and advance
    mark_checked_in_all(df_all, row)
    st.session_state.df_all = df_all
    st.session_state.unchecked_idx = max(0, min(idx, len(df_unchecked)-2))
    do_rerun = True

if a3.button("🗑️ Delete", use_container_width=True):
    st.session_state.df_all = delete_in_all(df_all, row)
    st.session_state.unchecked_idx = max(0, min(idx, len(df_unchecked)-2))
    do_rerun = True

if a4.button("💾 Save (refresh download)", use_container_width=True):
    # No-op: the download button always serializes current df_all
    st.toast("Saved to memory. Use the Download button in the sidebar.", icon="✅")

if do_rerun:
    st.rerun()
