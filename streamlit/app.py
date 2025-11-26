import streamlit as st
import pandas as pd
from data_processing import get_clean_data
import plots

# -----------------------------------------------------
# HELPER FUNCTION
# -----------------------------------------------------
def encode_category(series):
    """Encode categorical series to numeric"""
    cats = series.astype(str).unique()
    mapping = {c: i for i, c in enumerate(cats)}
    return series.map(mapping), mapping

# -----------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------
st.set_page_config(
    page_title="StackOverflow Developer Survey 2023 Dashboard",
    layout="wide"
)

# -----------------------------------------------------
# LOAD DATA
# -----------------------------------------------------
@st.cache_data
def load_data():
    return get_clean_data()

df = load_data()

# --- Diagnostics: Check if data is loaded ---
st.sidebar.markdown(f"**Data rows:** {len(df)}")
st.sidebar.markdown(f"**Columns:** {', '.join(df.columns)}")
with st.sidebar.expander("Preview Data"):
    st.dataframe(df.head())

st.title("📊 StackOverflow Developers Survey 2023 Dashboard")
st.sidebar.title("🔍 Filters")


# -----------------------------------------------------
# AGE FILTER
# -----------------------------------------------------
if "Age" in df.columns:
    age_col = pd.to_numeric(df["Age"], errors="coerce").dropna()

    if len(age_col) > 0:
        age_min = int(age_col.min())
        age_max = int(age_col.max())
    else:
        age_min, age_max = 18, 65
else:
    age_min, age_max = 18, 65

age_range = st.sidebar.slider(
    "Age Range",
    min_value=age_min,
    max_value=age_max,
    value=(age_min, age_max)
)

# -----------------------------------------------------
# Country filter
# -----------------------------------------------------
if "Country" in df.columns:
    country_values = [c for c in df["Country"].dropna().unique() if str(c).strip() and c != "Unknown"]
    countries = ["All"] + sorted(country_values)
    selected_country = st.sidebar.selectbox("Select Country:", countries)
else:
    selected_country = "All"

# -----------------------------------------------------
# APPLY FILTERS
# -----------------------------------------------------
df_filtered = df.copy()

# Filter by country
if selected_country != "All":
    df_filtered = df_filtered[df_filtered["Country"] == selected_country]

# Filter by age
df_filtered = df_filtered[
    (df_filtered["Age"] >= age_range[0]) &
    (df_filtered["Age"] <= age_range[1])
]

st.sidebar.info(f"Total records: {len(df_filtered)}")

if df_filtered.empty:
    st.warning("No data matches the selected filters. Please broaden your selection.")
    st.stop()

# -----------------------------------------------------
# LOAD DATA
# -----------------------------------------------------
@st.cache_data
def load_data():
    return get_clean_data()

df = load_data()

# -----------------------------------------------------
# NAVIGATION MENU
# -----------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "1) Map Chart",
    "2) Top 10 Languages",
    "3) Education Donut Chart",
    "4) Treemap",
    "5) Correlation Heat-Map",
    "6) Language ↔ DevType Network",
    "7) Scatter Plot",
    "8) Sunburst (EdLevel → RemoteWork)",
    "9) Parallel Coordinates"
])

# -----------------------------------------------------
# TAB 1 Map Chart
# -----------------------------------------------------
with tab1:
    st.subheader("Number of Developers form Countries")
    fig = plots.plot_glyph_map(df_filtered)
    st.plotly_chart(fig, use_container_width=True, key="plot5")

# -----------------------------------------------------
# TAB 2 Top 10 Languages
# -----------------------------------------------------
with tab2:
    st.subheader("Top 10 Programming Languages")
    fig = plots.plot_bar_top_languages(df_filtered)
    st.plotly_chart(fig, use_container_width=True, key="plot9")

# -----------------------------------------------------
# TAB 3 Education Donut Chart
# -----------------------------------------------------
with tab3:
    st.subheader(" Education Level Distribution")
    fig = plots.plot_box_remote_vs_yearspro(df_filtered)
    st.plotly_chart(fig, use_container_width=True, key="plot8")

# -----------------------------------------------------
# TAB 4 Treemap (DevType)
# -----------------------------------------------------
with tab4:
    st.subheader("Distribution of Developer Types")
    fig = plots.plot_treemap_devtype(df_filtered)
    st.plotly_chart(fig, use_container_width=True, key="plot1")


# -----------------------------------------------------
# TAB 5 Correlation Heatmap
# -----------------------------------------------------
with tab5:
    st.subheader("Correlation Between Age, Experience, and Salary")
    fig = plots.plot_correlation_heatmap(df_filtered)
    st.plotly_chart(fig, use_container_width=True, key="plot4")

# -----------------------------------------------------
# TAB 6 Language ↔ DevType Network
# -----------------------------------------------------
with tab6:
    st.subheader("Tech Stack ↔ Developer Field Relation")
    fig = plots.plot_node_link_filtered_clustered(df_filtered)
    st.plotly_chart(fig, use_container_width=True, key="plot6")

# -----------------------------------------------------
# TAB 7
# -----------------------------------------------------
with tab7:
    st.subheader("Scatter Analysis — Multiple Perspectives")

    # Kullanıcı seçimi
    scatter_type = st.selectbox(
        "Choose scatter plot type:",
        ["Experience vs Salary", "Age vs Salary", "Interactive Comparison"]
    )

    if scatter_type == "Experience vs Salary":
        fig = plots.plot_scatter_experience_vs_salary(df_filtered)
    elif scatter_type == "Age vs Salary":
        fig = plots.plot_scatter_age_vs_salary(df_filtered)
    else:
        fig = plots.plot_scatter_interactive_comparison(df_filtered)

    st.plotly_chart(fig, use_container_width=True, key="plot7")

    # İstatistiksel özet
    if "ConvertedCompYearly" in df_filtered.columns:
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_salary = df_filtered['ConvertedCompYearly'].mean()
            st.metric("Avg Salary", f"${avg_salary:,.0f}" if not pd.isna(avg_salary) else "N/A")
        with col2:
            median_salary = df_filtered['ConvertedCompYearly'].median()
            st.metric("Median Salary", f"${median_salary:,.0f}" if not pd.isna(median_salary) else "N/A")
        with col3:
            st.metric("Sample Size", f"{len(df_filtered):,}")


# --------------------------------------------------s---
# TAB 8
# -----------------------------------------------------
with tab8:
    st.subheader("Remote Work Preferences by Different Education Levels")
    fig = plots.plot_sunburst_edlevel_remote(df_filtered)
    st.plotly_chart(fig, use_container_width=True, key="plot2")

# -----------------------------------------------------
# TAB 9
# -----------------------------------------------------
with tab9:
    st.subheader("Age ↔ Experience ↔ Yearly Salary ↔ Education Level ↔ Countries - Relation")
    fig = plots.plot_parallel_coordinates(df_filtered)
    st.plotly_chart(fig, use_container_width=True, key="plot3")
