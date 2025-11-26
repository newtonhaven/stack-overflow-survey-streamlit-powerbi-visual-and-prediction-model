import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx

# =====================================================
#  Helper: Multi-select kolonları düzgün listeye çevirme
# =====================================================
def ensure_list(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return []
    if isinstance(x, list):
        return [v for v in x if v]
    if isinstance(x, str):
        return [v.strip() for v in x.split(";") if v.strip()]
    return []

# =====================================================
# WORLD MAP — Country vs Count
# =====================================================
def plot_glyph_map(df):
    if "Country" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(text="Country column missing", showarrow=False)
        return fig

    counts = df["Country"].value_counts().reset_index()
    counts.columns = ["Country", "Count"]
    if counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="No country data for selection", showarrow=False)
        return fig


    fig = px.choropleth(
        counts,
        locations="Country",
        locationmode="country names",
        color="Count",
        color_continuous_scale="Viridis"
    )

    # Adjust graph size
    fig.update_layout(
        height=700,
        width=1100,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

# =====================================================
# SUNBURST — Education → RemoteWork
# =====================================================
def plot_sunburst_edlevel_remote(df):
    if "EdLevel" not in df.columns or "RemoteWork" not in df.columns:
        return go.Figure()

    tmp = df[["EdLevel", "RemoteWork"]].dropna()
    if tmp.empty:
        return go.Figure()

    counts = tmp.groupby(["EdLevel", "RemoteWork"]).size().reset_index(name="Count")

    # custom color mapping
    color_map = {
        "Remote": "steelblue",
        "Hybrid": "seagreen",
        "In-person": "firebrick"
    }

    fig = px.sunburst(
        counts,
        path=["EdLevel", "RemoteWork"],
        values="Count",
        color="RemoteWork",               # color by category
        color_discrete_map=color_map,
        title=""
    )

    fig.update_layout(
        height=550,
        width=550,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


# =====================================================
# PARALLEL COORDINATES
# =====================================================
def plot_parallel_coordinates(df):
    
    desired_cols = ["Age", "YearsCode", "ConvertedCompYearly", "EdLevel", "Country"]
    available_cols = [c for c in desired_cols if c in df.columns]

    if len(available_cols) < 2:
        return go.Figure().add_annotation(
            text="Not enough columns available",
            showarrow=False,
            font=dict(size=16)
        )

    tmp = df[available_cols].copy()

    # Encode categorical columns as numeric and store mappings
    categorical_mappings = {}
    for col in ["EdLevel", "Country"]:
        if col in tmp.columns:
            # Create numeric encoding
            categories = sorted(tmp[col].astype(str).unique())
            mapping = {cat: idx for idx, cat in enumerate(categories)}
            reverse_mapping = {idx: cat for cat, idx in mapping.items()}

            tmp[col + "_encoded"] = tmp[col].map(mapping)
            categorical_mappings[col] = reverse_mapping

            # Remove original column, keep encoded version
            tmp = tmp.drop(columns=[col])
            tmp = tmp.rename(columns={col + "_encoded": col})

    # removes missing values
    tmp = tmp.dropna()
    if tmp.empty:
        return go.Figure().add_annotation(
            text="No data available after filtering",
            showarrow=False,
            font=dict(size=16)
        )

    if len(tmp) > 600:
        tmp = tmp.sample(600, random_state=42)

    # Build dimensions list with custom tick labels for categorical columns
    dimensions = []
    for col in tmp.columns.tolist():
        dim = dict(label=col, values=tmp[col])

        # Add custom tick labels for categorical columns
        if col in categorical_mappings:
            mapping = categorical_mappings[col]
            # Get unique values present in the filtered data
            unique_vals = sorted(tmp[col].unique())
            dim['tickvals'] = unique_vals
            dim['ticktext'] = [mapping[val] for val in unique_vals]

        dimensions.append(dim)

    # Create parallel coordinates plot using graph_objects for more control
    fig = go.Figure(data=
    go.Parcoords(
        line=dict(
            color=tmp[tmp.columns[0]],
            colorscale='Turbo',
            showscale=True,
            cmin=tmp[tmp.columns[0]].min(),
            cmax=tmp[tmp.columns[0]].max()
        ),
        dimensions=dimensions
    )
    )

    fig.update_layout(
        title=" ",
        height=900,
        margin=dict(l=100, r=100, t=60, b=50)
    )

    return fig


# =====================================================
#  CORRELATION HEATMAP
# =====================================================
def plot_correlation_heatmap(df):
    # Select only numeric columns that exist in the dataframe
    numeric_cols = ["Age", "YearsCode", "YearsCodePro", "ConvertedCompYearly", "CompTotal", "SurveyLength"]
    numeric_cols = [c for c in numeric_cols if c in df.columns]

    if len(numeric_cols) < 2:
        return go.Figure().add_annotation(
            text="Not enough numeric columns for correlation",
            showarrow=False,
            font=dict(size=16)
        )

    # Get only numeric columns and drop any remaining NaN values
    tmp = df[numeric_cols].apply(pd.to_numeric, errors="coerce").dropna()

    if tmp.empty or len(tmp) < 2:
        return go.Figure().add_annotation(
            text="Insufficient data for correlation analysis",
            showarrow=False,
            font=dict(size=16)
        )

    corr = tmp.corr()

    return px.imshow(
        corr,
        text_auto=".2f",  # Show 2 decimal places
        color_continuous_scale="RdBu",
        aspect="auto",
        title=" ",
        labels=dict(color="Correlation")
    )


# =====================================================
# TREEMAP (DevType)
# =====================================================
def plot_treemap_devtype(df):
    if "DevType" not in df.columns:
        return go.Figure()

    series = df["DevType"].apply(ensure_list).explode().dropna()
    if series.empty:
        return go.Figure()

    # Count occurrences
    counts = series.value_counts().reset_index()
    counts.columns = ["DevType", "Count"]

    # Percentage column
    total = counts["Count"].sum()
    counts["Percent"] = (counts["Count"] / total * 100).round(2)

    # Custom vibrant color palette (20+ colors)
    TREEMAP_COLORS = [
        "#4CAF50", "#8BC34A", "#CDDC39", "#FFC107", "#FF9800",
        "#FF5722", "#F44336", "#E91E63", "#9C27B0", "#673AB7",
        "#3F51B5", "#2196F3", "#03A9F4", "#00BCD4", "#009688",
        "#4DB6AC", "#8D6E63", "#795548", "#9E9E9E", "#607D8B"
    ]

    fig = px.treemap(
        counts,
        path=["DevType"],
        values="Count",
        color="DevType",
        color_discrete_sequence=TREEMAP_COLORS,
        hover_data={"Percent": True, "Count": True},
    )

    # Show percentage inside boxes
    fig.data[0].textinfo = "label+text+value"
    fig.data[0].texttemplate = (
        "<b>%{label}</b><br>%{customdata[0]}%<br>(%{value})"
    )

    fig.update_layout(
        title=" ",
        uniformtext=dict(minsize=12, mode='show'),
        margin=dict(t=40, l=0, r=0, b=0)
    )

    return fig

def treemap_devtype_insight(df):
    if "DevType" not in df.columns:
        return "Veri bulunamadı."
    series = df["DevType"].apply(ensure_list).explode().dropna()
    if series.empty:
        return "Hiç geliştirici tipi verisi yok."
    top = series.value_counts().head(3)
    return (
        f"En yaygın geliştirici tipleri: "
        + ", ".join([f"{idx} ({val})" for idx, val in top.items()])
    )



# =====================================================
# 10) NODE-LINK NETWORK GRAPH
# =====================================================
def plot_node_link_filtered_clustered(df, filter_role=None, filter_language=None, max_edges=120):

    # community-louvain paketi kullanımı için
    try:
        import community as community_louvain
    except ImportError:
        fig = go.Figure()
        fig.update_layout(title_text="community-louvain paketi kurulu değil. Lütfen yükleyiniz.")
        return fig

    if not {"DevType", "LanguageHaveWorkedWith", "ConvertedCompYearly"}.issubset(df.columns):
        return go.Figure()

    temp_df = df.copy()
    temp_df = temp_df.explode("DevType")
    temp_df = temp_df.explode("LanguageHaveWorkedWith")
    temp_df = temp_df.dropna(subset=["DevType", "LanguageHaveWorkedWith"])

    if filter_role is not None:
        temp_df = temp_df[temp_df["DevType"] == filter_role]

    if filter_language is not None:
        temp_df = temp_df[temp_df["LanguageHaveWorkedWith"] == filter_language]

    edge_weights = (
        temp_df.groupby(["DevType", "LanguageHaveWorkedWith"])
        .size()
        .reset_index(name="weight")
    )

    nodes_devtype = temp_df.groupby("DevType")["ConvertedCompYearly"].mean()
    nodes_language = temp_df.groupby("LanguageHaveWorkedWith")["ConvertedCompYearly"].mean()

    G = nx.Graph()
    for _, row in edge_weights.iterrows():
        d = row["DevType"]
        l = row["LanguageHaveWorkedWith"]
        w = row["weight"]
        G.add_edge(d, l, weight=w)

    if G.number_of_edges() == 0:
        return go.Figure()

    top_edges = sorted(G.edges(data=True), key=lambda x: x[2]["weight"], reverse=True)[:max_edges]
    H = nx.Graph()
    H.add_edges_from(top_edges)

    # Kümeleme: Louvain algoritması ile community detection
    partition = community_louvain.best_partition(H)

    viridis = px.colors.qualitative.Light24

    pos = nx.spring_layout(H, seed=42)
    edge_x, edge_y = [], []
    for u, v in H.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(width=1, color="#888"),
            hoverinfo="none",
        )
    )

    node_x, node_y, labels, sizes, colors = [], [], [], [], []
    max_comp = max(
        nodes_devtype.max() if not np.isnan(nodes_devtype.max()) else 0,
        nodes_language.max() if not np.isnan(nodes_language.max()) else 0,
    )

    for node in H.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        labels.append(node)

        if node in nodes_devtype.index:
            comp_avg = nodes_devtype[node]
        elif node in nodes_language.index:
            comp_avg = nodes_language[node]
        else:
            comp_avg = 0

        comp_avg = 0 if comp_avg is None or np.isnan(comp_avg) else comp_avg
        size = 10 + 40 * (comp_avg / max_comp if max_comp > 0 else 0)
        sizes.append(size)

        cluster_id = partition.get(node, 0)
        colors.append(viridis[cluster_id % len(viridis)])

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=labels,
            textposition="top center",
            marker=dict(
                size=sizes,
                color=colors,
                showscale=False,
                line_width=2,
            ),
            hoverinfo="text",
        )
    )

    title = " "
    if filter_role:
        title += f" — Rol: {filter_role}"
    if filter_language:
        title += f" — Dil: {filter_language}"

    fig.update_layout(
        title=title,
        showlegend=False,
    )
    
    fig.update_layout(
        height=800,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# =====================================================
# 7) SCATTER
# =====================================================
def plot_scatter_experience_vs_salary(df):
    """Gelişmiş scatter plot: Deneyim vs Maaş"""
    if "YearsCode" not in df.columns or "ConvertedCompYearly" not in df.columns:
        return go.Figure()

    # Veriyi temizle
    tmp = df[["YearsCode", "ConvertedCompYearly", "RemoteWork", "DevType", "Country"]].copy()

    # YearsCode'u sayısal yap
    tmp["YearsCode_Numeric"] = tmp["YearsCode"].apply(lambda x:
                                                      0.5 if x == "Less than 1 year" else
                                                      50 if "More than 50" in str(x) else
                                                      pd.to_numeric(x, errors="coerce")
                                                      )

    # Outlier'ları filtrele (maaş için)
    tmp = tmp[tmp["ConvertedCompYearly"] < 500000]  # 500K üzeri outlier
    tmp = tmp.dropna(subset=["YearsCode_Numeric", "ConvertedCompYearly"])

    # Sampling (performans için)
    if len(tmp) > 1000:
        tmp = tmp.sample(1000, random_state=42)

    return px.scatter(
        tmp,
        x="YearsCode_Numeric",
        y="ConvertedCompYearly",
        color="RemoteWork",
        size="ConvertedCompYearly",
        hover_data=["DevType", "Country"],
        trendline="ols",  # Regresyon çizgisi
        title="Experience vs Salary (with Trend Line)",
        labels={
            "YearsCode_Numeric": "Years of Coding Experience",
            "ConvertedCompYearly": "Annual Salary (USD)",
            "RemoteWork": "Work Type"
        },
        color_discrete_map={
            "Remote": "#2E8B57",
            "Hybrid (some remote, some in-person)": "#FF6347",
            "In-person": "#4169E1"
        }
    )


def plot_scatter_age_vs_salary(df):
    """Yaş vs Maaş scatter plot"""
    if "Age" not in df.columns or "ConvertedCompYearly" not in df.columns:
        return go.Figure()

    tmp = df[["Age", "ConvertedCompYearly", "DevType", "EdLevel"]].copy()
    tmp = tmp[tmp["ConvertedCompYearly"] < 300000]  # Outlier filtrele
    tmp = tmp.dropna()

    if len(tmp) > 800:
        tmp = tmp.sample(800, random_state=42)

    return px.scatter(
        tmp,
        x="Age",
        y="ConvertedCompYearly",
        color="EdLevel",
        hover_data=["DevType"],
        trendline="ols",
        title="Age vs Salary by Education Level",
        labels={
            "Age": "Age (Years)",
            "ConvertedCompYearly": "Annual Salary (USD)",
            "EdLevel": "Education Level"
        },
        opacity=0.7
    )


def plot_scatter_interactive_comparison(df):
    """Interaktif karşılaştırma - kullanıcı seçimi"""
    from plotly.subplots import make_subplots

    # İki farklı scatter plot yan yana
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Experience vs Salary", "Age vs Education Distribution")
    )

    # Sol grafik: Deneyim vs Maaş
    tmp1 = df[["YearsCode", "ConvertedCompYearly", "RemoteWork"]].copy()
    tmp1["YearsCode_Numeric"] = tmp1["YearsCode"].apply(lambda x:
                                                        0.5 if x == "Less than 1 year" else
                                                        50 if "More than 50" in str(x) else
                                                        pd.to_numeric(x, errors="coerce")
                                                        )
    tmp1 = tmp1[tmp1["ConvertedCompYearly"] < 400000].dropna()

    if len(tmp1) > 500:
        tmp1 = tmp1.sample(500, random_state=42)

    # Sağ grafik: Yaş vs Eğitim
    tmp2 = df[["Age", "EdLevel"]].copy().dropna()
    age_ed_counts = tmp2.groupby(["Age", "EdLevel"]).size().reset_index(name="Count")

    # Sol scatter
    fig.add_scatter(
        x=tmp1["YearsCode_Numeric"],
        y=tmp1["ConvertedCompYearly"],
        mode="markers",
        marker=dict(color=tmp1["RemoteWork"].astype("category").cat.codes, colorscale="Viridis"),
        name="Exp vs Salary",
        row=1, col=1
    )

    # Sağ bubble chart
    fig.add_scatter(
        x=age_ed_counts["Age"],
        y=age_ed_counts["EdLevel"].astype("category").cat.codes,
        mode="markers",
        marker=dict(size=age_ed_counts["Count"], sizemode="area", sizeref=2),
        name="Age vs Education",
        row=1, col=2
    )

    fig.update_layout(title="Multi-Dimensional Analysis Dashboard")
    return fig


# =====================================================
# DONUT CHART - Education Level Distribution
# =====================================================
def plot_box_remote_vs_yearspro(df):
    if "EdLevel" not in df.columns:
        return go.Figure().add_annotation(
            text="EdLevel column not found",
            showarrow=False,
            font=dict(size=16)
        )

    # Count education levels
    edu_counts = df["EdLevel"].value_counts().reset_index()
    edu_counts.columns = ["EdLevel", "Count"]

    if edu_counts.empty:
        return go.Figure().add_annotation(
            text="No education level data available",
            showarrow=False,
            font=dict(size=16)
        )

    # Calculate percentages
    total = edu_counts["Count"].sum()
    edu_counts["Percent"] = (edu_counts["Count"] / total * 100).round(1)

    # Create donut chart
    fig = px.pie(
        edu_counts,
        names="EdLevel",
        values="Count",
        hole=0.4,  # Creates the donut effect
        title=" ",
        hover_data=["Percent"],
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    # Customize layout
    fig.update_traces(
        textposition='outside',
        textinfo='label+percent',
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{customdata[0]}%<extra></extra>"
    )

    fig.update_layout(
        height=600,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig


# =====================================================
# TOP LANGUAGES
# =====================================================
def plot_bar_top_languages(df):
    if "LanguageHaveWorkedWith" not in df.columns:
        return go.Figure()

    series = df["LanguageHaveWorkedWith"].apply(ensure_list).explode()
    counts = series.value_counts().head(10).reset_index()
    counts.columns = ["Language", "Count"]

    return px.bar(
        counts,
        x="Language",
        y="Count",
        title=" "
    )