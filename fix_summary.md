I have resolved the UI layout issues:

1. **Tab Borders and De-selection Fix**: 
   - Addressed the right border disappearing on the active tab by resetting `border-bottom: none !important; margin-bottom: -1px; z-index: 10 !important` and making sure it has standard border color.
   - Added `selection_mode="single"` to `st.segmented_control` so you can no longer deselect an open tab by clicking it a second time.

2. **Dashboard Layout and Stats Pill Fix**:
   - Adjusted the `.dashboard-intro` container. It now properly occupies `width: 100%` and uses a `padding-right` instead of rigid width calculations. This prevents it from getting squeezed when active, putting the stats in the same line without overlapping the filter button space.

3. **Restored Sidebar Reopen Toggle**:
   - The native Streamlit toggle was getting obscured or hidden due to the custom header override. I added explicit `position: fixed`, `left: 16px`, and an ultra-high `z-index` so the `>` expand button is always visible on the top-left when the sidebar is collapsed.
