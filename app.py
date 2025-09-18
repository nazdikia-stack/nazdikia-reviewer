
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

def init_state():
    for k, v in {
        "df_all": None,
        "unchecked_idx": 0,
        "filename": None,
        "history": [],
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

st.title("Nazdikia – Iranian List Reviewer (Web MVP)")

with st.sidebar:
    st.header("1) Upload CSV")
    uploaded = st.file_uploader("iranian_only_fa.csv", type=["csv"])
    st.caption("This MVP stores your changes in memory during the session. Use the Download button to export the updated CSV.")

    st.header("2) Navigation")
    if st.session_state.df_all is not None:
        mask_unchecked = st.session_state.df_all[CHECK_COL].astype(str).str.strip().str.lower().ne(CHECK_VAL)
        total_unchecked = mask_unchecked.sum()
        st.write(f"Unchecked rows: **{int(total_unchecked)}**")
        st.session_state.unchecked_idx = st.number_input(
            "Jump to row index", min_value=0, max_value=max(0, int(total_unchecked) - 1),
            value=int(st.session_state.unchecked_idx), step=1
        )

    st.header("3) Download")
    if st.session_state.df_all is not None:
        out = st.session_state.df_all.to_csv(index=False, encoding="utf-8-sig")
        st.download_button("💾 Download reviewed CSV", data=out, file_name="iranian_only_fa_reviewed.csv", mime="text/csv")

if uploaded is not None and st.session_state.df_all is None:
    df_all = load_csv(uploaded.getvalue())
    # Ensure columns
    if CHECK_COL not in df_all.columns:
        df_all[CHECK_COL] = ""
    if "name_fa" not in df_all.columns:
        df_all["name_fa"] = ""
    # Keep CHECK_COL as last column (optional)
    cols = [c for c in df_all.columns if c != CHECK_COL] + [CHECK_COL]
    df_all = df_all[cols]
    st.session_state.df_all = df_all
    st.session_state.filename = uploaded.name

if st.session_state.df_all is None:
    st.info("Please upload your input CSV in the sidebar to begin.")
    st.stop()

df_all = st.session_state.df_all
if "name_fa" not in df_all.columns:
    df_all["name_fa"] = ""

mask_unchecked = df_all[CHECK_COL].astype(str).str.strip().str.lower().ne(CHECK_VAL)
df_unchecked = df_all.loc[mask_unchecked].reset_index(drop=True)

if df_unchecked.empty:
    st.success("🎉 All rows reviewed! You can still download the CSV from the sidebar.")
    st.stop()

idx = int(st.session_state.unchecked_idx)
idx = max(0, min(idx, len(df_unchecked)-1))
row = df_unchecked.iloc[idx]

# ----- GROUP by English business name -----
current_name_en = str(row.get("name", "") or "")
group_mask = df_all["name"].astype(str).str.strip().str.lower() == current_name_en.strip().lower()
group_rows = df_all.loc[group_mask].reset_index()
group_subcats = group_rows["subcategory"].astype(str).str.strip().tolist()

# Persian name (editable target column)
current_name_fa = str(row.get("name_fa", "") or "")

# Title shows English name
st.markdown(f"## 🏷️ {current_name_en}")

# Editable Persian name
display_name_fa = current_name_fa if current_name_fa else ""
new_name_fa = st.text_input("نام کسب‌وکار (فارسی، قابل ویرایش):", value=display_name_fa, placeholder="نام فارسی را وارد کنید")

# City (use from first row)
city = str(row.get("city", "") or "")

# Category selection with checkboxes
st.markdown("**Select categories to KEEP for this business:**")
selected_subcats = []
for sub in group_subcats:
    checked = st.checkbox(sub, value=True, key=f"sub_{sub}_{idx}")
    if checked:
        selected_subcats.append(sub)

# Other info
site = str(row.get("website", "") or "").strip()
maps = str(row.get("link", "") or "").strip()
subcat = str(row.get("subcategory", "") or "").strip()
q_name = new_name_fa.strip() if new_name_fa.strip() else current_name_en
q_text, q_url = build_google_query(q_name, city, subcat)

cols = st.columns(3)
with cols[0]:
    st.write("**Website:**")
    if site:
        st.link_button("🌐 Visit Website", site)
    else:
        st.text("—")
with cols[1]:
    st.write("**Google Maps:**")
    if maps:
        st.link_button("📍 Open Google Maps", maps)
    else:
        st.text("—")
with cols[2]:
    st.write("**Google query:**")
    st.markdown(f"`{q_text}`  \n[Open search]({q_url})")

# Actions
a1, a2, a3 = st.columns(3)
do_rerun = False

if a1.button("⬅️ Back", use_container_width=True):
    if st.session_state.history:
        last_state = st.session_state.history.pop()
        st.session_state.df_all = last_state["df_all"]
        st.session_state.unchecked_idx = last_state["idx"]
        do_rerun = True

if a2.button("✅ Approve & Next", type="primary", use_container_width=True):
    # Save current snapshot before change
    st.session_state.history.append({
        "df_all": st.session_state.df_all.copy(),
        "idx": idx
    })
    # Update Persian names
    for i in group_rows["index"]:
        st.session_state.df_all.at[i, "name_fa"] = new_name_fa.strip()
    # Keep only selected subcats, mark them checked
    for i, sub in zip(group_rows["index"], group_rows["subcategory"]):
        if sub in selected_subcats:
            st.session_state.df_all.at[i, CHECK_COL] = CHECK_VAL
        else:
            st.session_state.df_all.drop(i, inplace=True)
    st.session_state.df_all = st.session_state.df_all.reset_index(drop=True)
    st.session_state.unchecked_idx = max(0, min(idx, len(df_unchecked)-2))
    do_rerun = True

if a3.button("🗑️ Delete Business", use_container_width=True):
    # Save current snapshot before change
    st.session_state.history.append({
        "df_all": st.session_state.df_all.copy(),
        "idx": idx
    })
    st.session_state.df_all = st.session_state.df_all.drop(group_rows["index"])
    st.session_state.df_all = st.session_state.df_all.reset_index(drop=True)
    st.session_state.unchecked_idx = max(0, min(idx, len(df_unchecked)-2))
    do_rerun = True

if do_rerun:
    st.rerun()
