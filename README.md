
# Nazdikia – Iranian List Reviewer (Web MVP v2)

Improved Streamlit version with:
- ✅ Handle businesses with multiple subcategories at once (checkboxes to keep/delete categories).
- ✏️ Editable business name (can change or translate to Persian).
- Approve/Delete logic updated accordingly.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
Then open the URL shown in the terminal (default: http://localhost:8501).

## How to use
1. Upload your `iranian_only_fa.csv` in the left sidebar.
2. Review rows:
   - Edit business name if needed.
   - Select categories to keep (others will be deleted).
   - **Approve & Next** will mark kept rows as checked and delete unselected rows.
   - **Delete Business** will delete all rows for this business.
   - **Back** moves to the previous unchecked row.
3. Click **Download reviewed CSV** (sidebar) to save your updated file.

## Deploy

Same as before: upload these files to GitHub and deploy on Streamlit Cloud.
