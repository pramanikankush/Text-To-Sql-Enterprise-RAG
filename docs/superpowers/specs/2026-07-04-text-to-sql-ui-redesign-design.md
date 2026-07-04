# Design Spec: Text-to-SQL Enterprise UI Redesign (Cohere 2026 Theme)

## Goal & Overview
Redesign the Streamlit frontend for the Text-to-SQL Enterprise application to strictly align with the **Cohere 2026 Web System** design guidelines. The existing UI is broken: Streamlit's default dark theme conflicts with our custom white background, causing invisible labels (white-on-white text), misaligned inputs, and unstyled radio controls. We will fix this by creating a global Streamlit configuration file and writing high-specificity CSS overrides to achieve a clean, premium, editorial AI command center aesthetic.

---

## Design System Mapping (from DESIGN.md)

### Colors
- **Canvas/Page Background**: `#ffffff` (Canvas White)
- **Primary Text**: `#212121` (Ink)
- **Muted Text / Metadata**: `#93939f` (Muted Slate) or `#75758a` (Slate)
- **Secondary Surfaces (Cards/Sidebars)**: `#eeece7` (Soft Stone)
- **Primary CTA Buttons**: `#17171c` (Near-Black Primary) with `#ffffff` text
- **Secondary CTA/Outline Buttons**: Transparent fill with `#17171c` border and text
- **Form/Input Borders**: `#d9d9dd` (Hairline) or `#e5e7eb` (Border Light)
- **Accent/Highlights**:
  - **Coral**: `#ff7759` (category highlights, primary status accent)
  - **Deep Green**: `#003c33` (SQL explanation highlights)
  - **Pale Green Wash**: `#edfce9` (explanation box background)
  - **Focus Ring**: `#4c6ee6` (Focus Blue)

### Typography
- **Display/Headers**: `Space Grotesk`, `Inter`, sans-serif (tight letter spacing, weight 500)
- **UI & Body**: `Inter`, `Arial`, sans-serif
- **Technical/Code**: `JetBrains Mono`, `SF Mono`, `Courier New`, monospace

### Radii & Spacing
- **Pill Radius**: `32px` (used for main search bar, primary buttons, filters)
- **Card/Element Radius**: `8px` (used for dataframes, SQL blocks, metric cards)
- **Input Radius**: `8px` (used for utility inputs like DB path)

---

## Architectural & Styling Changes

### 1. Global Streamlit Theme Configuration
We will create a `.streamlit/config.toml` file to force a light-theme backdrop and color palette globally across the application. This ensures Streamlit's built-in components (dataframes, selectboxes, spinners) render with appropriate background and text colors.

```toml
[theme]
primaryColor = "#17171c"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#eeece7"
textColor = "#212121"
font = "sans serif"

[server]
headless = true
```

### 2. High-Specificity CSS Overrides
We will rewrite the `<style>` block in `frontend/streamlit_app.py` to:
- Reset default list/radio styles so no stray bullet points are visible.
- Force all header and body text to inherit `--ink` (`#212121`) with `!important` to override Streamlit internal dark-theme overrides.
- Style `st.text_input` and `st.text_area` with correct borders, padding, and font families.
- Style Streamlit buttons (`st.button`) to match the primary pill CTA (`button-primary`) or outlined secondary style (`button-secondary`).
- Enhance visual cards:
  - **Metric Cards**: Stark borders (`#d9d9dd`), soft stone/canvas background, Space Grotesk labels.
  - **SQL Code Blocks**: Soft stone (`#eeece7`) background, mono fonts, subtle padding.
  - **Explanation Boxes**: Pale green (`#edfce9`) background with a deep green left border.

### 3. Component Fixes
- **Sidebar**: Adjust text styling of `st.radio` label containers to ensure they are visible. Remove default bullets.
- **SQL Execution**: Ensure the connection string and DB Path input fit naturally into the Cohere layout.

---

## Verification Plan

### Automated Tests
- Run backend tests using:
  ```bash
  pytest tests/ -v
  ```

### Manual Verification
- Start the FastAPI backend and Streamlit frontend.
- Verify the layout matches the Cohere design:
  - Clear readability (no white-on-white or dark-on-dark text).
  - Correct fonts, rounded borders (32px pills for query and primary buttons, 8px for cards).
  - Toggle all pages ("Query", "History", "Schema Explorer", "Database Explorer") to ensure they load and render correctly.
