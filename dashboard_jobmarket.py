import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# 💼 JOB MARKET INTELLIGENCE DASHBOARD


st.set_page_config(
    page_title="Job Market Intelligence Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LOAD DATA

@st.cache_data
def load_data():
    df = pd.read_csv("job_market_data.csv")
    df["Date_Posted"] = pd.to_datetime(df["Date_Posted"], errors="coerce")

    df["Year"] = df["Date_Posted"].dt.year
    df["Month_Name"] = df["Date_Posted"].dt.strftime("%b")
    df["Month_Number"] = df["Date_Posted"].dt.month

    return df


try:
    data = load_data()
except FileNotFoundError:
    st.error(
        "❌ job_market_data.csv was not found. "
        "Keep the CSV file in the same folder as dashboard_jobmarket.py."
    )
    st.stop()

# SIDEBAR

st.sidebar.title("💼 Job Market Analytics")
st.sidebar.caption("Skills • Salary • Roles • Locations")

years = sorted(data["Year"].dropna().unique())
if len(years) > 1:
    year_range = st.sidebar.slider(
        "📅 Choose Year",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years)))
    )
else:
    year_range = (int(years[0]), int(years[0]))
    st.sidebar.info(f"📅 Year: {years[0]}")

role_options = sorted(data["Job_Title"].dropna().unique())
location_options = sorted(data["Location"].dropna().unique())
industry_options = sorted(data["Industry"].dropna().unique())
experience_options = sorted(data["Experience_Level"].dropna().unique())
remote_options = sorted(data["Remote"].dropna().unique())

role = st.sidebar.multiselect(
    "💼 Job Role",
    role_options
)

location = st.sidebar.multiselect(
    "📍 Location",
    location_options
)

industry = st.sidebar.multiselect(
    "🏭 Industry",
    industry_options
)

experience = st.sidebar.multiselect(
    "🎓 Experience Level",
    experience_options
)

remote = st.sidebar.multiselect(
    "🏠 Remote",
    remote_options
)

# FILTER DATA

filtered_df = data[
    (data["Year"] >= year_range[0]) &
    (data["Year"] <= year_range[1])
].copy()

if role:
    filtered_df = filtered_df[
        filtered_df["Job_Title"].isin(role)
    ]

if location:
    filtered_df = filtered_df[
        filtered_df["Location"].isin(location)
    ]

if industry:
    filtered_df = filtered_df[
        filtered_df["Industry"].isin(industry)
    ]

if experience:
    filtered_df = filtered_df[
        filtered_df["Experience_Level"].isin(experience)
    ]

if remote:
    filtered_df = filtered_df[
        filtered_df["Remote"].isin(remote)
    ]

st.sidebar.divider()
st.sidebar.caption(
    "Job Market Intelligence Project\n"
    "Interactive Streamlit Dashboard"
)

# HEADER

st.title("💼 Job Market Intelligence Dashboard")
st.markdown(
    "### 📊 Skills, Salary & Hiring Trend Intelligence"
)
st.caption(
    "Explore in-demand skills, salary benchmarks, hiring trends, and "
    "regional/industry performance across job postings."
)

# KPI CARDS

total_postings = filtered_df["Job_ID"].nunique()
avg_salary = filtered_df["Salary_LPA"].mean()
median_salary = filtered_df["Salary_LPA"].median()
total_companies = filtered_df["Company"].nunique()
avg_applicants = filtered_df["Applicants"].mean()
top_role = (
    filtered_df["Job_Title"].value_counts().idxmax()
    if not filtered_df.empty else "N/A"
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("🧾 Total Postings", f"{total_postings:,}")
c2.metric("💰 Avg. Salary", f"{avg_salary:,.1f} LPA")
c3.metric("📊 Median Salary", f"{median_salary:,.1f} LPA")
c4.metric("🏢 Companies Hiring", f"{total_companies:,}")
c5.metric("👥 Avg. Applicants/Posting", f"{avg_applicants:,.0f}")

st.divider()

# TABS

tab1, tab2, tab3 = st.tabs(
    ["🏠 Dashboard", "💡 Insights", "📋 Raw Data"]
)

# TAB 1 — DASHBOARD
with tab1:

    # Monthly Hiring Trend

    st.subheader("📈 Monthly Hiring Trend")

    monthly_postings = (
        filtered_df
        .groupby(["Year", "Month_Number", "Month_Name"])["Job_ID"]
        .count()
        .reset_index()
        .sort_values(["Year", "Month_Number"])
    )

    monthly_postings["Period"] = (
        monthly_postings["Month_Name"] + " " +
        monthly_postings["Year"].astype(str)
    )

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(
        monthly_postings["Period"],
        monthly_postings["Job_ID"],
        marker="o",
        color="#2E5EAA"
    )
    ax.fill_between(
        range(len(monthly_postings)),
        monthly_postings["Job_ID"],
        color="#2E5EAA", alpha=0.08
    )
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Postings")
    ax.set_title("Monthly Job Postings Volume")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    col1, col2 = st.columns(2)

    # Top In-Demand Skills
    with col1:
        st.subheader("🧠 Top In-Demand Skills")

        all_skills = (
            filtered_df["Required_Skills"].str.split(", ").explode().str.strip()
        )
        top_skills = all_skills.value_counts().head(10)

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(top_skills.index[::-1], top_skills.values[::-1], color="#2E5EAA")
        ax.set_xlabel("Number of Postings")
        ax.set_ylabel("Skill")
        ax.set_title("Top 10 In-Demand Skills")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # Average Salary by Job Role
    with col2:
        st.subheader("💰 Average Salary by Job Role")
        colors = ["#2E5EAA", "#3C8DBC", "#5CB85C", "#F2A93B", "#E4572E",
                  "#8E44AD", "#16A085", "#C0392B"]
        salary_by_role = (
            filtered_df
            .groupby("Job_Title")["Salary_LPA"]
            .mean()
            .sort_values(ascending=False)
            .head(8)
        )

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(salary_by_role.index, salary_by_role.values, color=colors)
        ax.set_xlabel("Job Role")
        ax.set_ylabel("Avg. Salary (LPA)")
        ax.set_title("Highest Paying Roles (Avg LPA)")
        plt.xticks(rotation=35, ha="right")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.divider()

    col1, col2 = st.columns(2)

    # Experience Level Salary Distribution
    with col1:
        st.subheader("🎓 Salary by Experience Level")
        exp_order = ["Fresher", "Junior (1-3 yrs)", "Mid (3-6 yrs)",
                     "Senior (6-10 yrs)", "Lead (10+ yrs)"]
        present_levels = [e for e in exp_order if e in filtered_df["Experience_Level"].unique()]
        data_by_exp = [
            filtered_df.loc[filtered_df["Experience_Level"] == lvl, "Salary_LPA"].values
            for lvl in present_levels
        ]

        fig, ax = plt.subplots(figsize=(7, 4))
        if any(len(d) > 0 for d in data_by_exp):
            bp = ax.boxplot(data_by_exp, patch_artist=True, tick_labels=present_levels)
            colors = ["#2E5EAA", "#3C8DBC", "#5CB85C", "#F2A93B", "#E4572E"]
            for patch, color in zip(bp["boxes"], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.75)
        ax.set_ylabel("Salary (LPA)")
        ax.set_title("Salary Distribution by Experience Level")
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # Top 10 Locations by Postings
    with col2:
        st.subheader("📍 Top 10 Locations by Postings")
        colors = ["#60241E", "#95271D", "#E73F1E", "#FB6C00", "#F9B637",
                  "#FED24F", "#FFF449", "#FFDE4E", "#E1DCC9", "#2E5EAA"]
        location_counts = (
            filtered_df["Location"].value_counts().head(10)
        )

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.barh(location_counts.index, location_counts.values, color=colors)
        ax.set_xlabel("Number of Postings")
        ax.set_ylabel("Location")
        ax.set_title("Top 10 Locations by Job Postings")
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.divider()

    col1, col2 = st.columns(2)

    # Remote vs On-site
    with col1:
        st.subheader("🏠 Remote vs On-site Postings")
        colors = ["#2BBBD7", "#F599C6"]
        remote_counts = filtered_df["Remote"].value_counts()

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.pie(
            remote_counts.values,
            labels=remote_counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors
        )
        ax.set_title("Remote vs On-site Postings")
        st.pyplot(fig)
        plt.close(fig)

    # Industry Distribution
    with col2:
        st.subheader("🏭 Postings by Industry")
        colors = ["#5D3140", "#CF4173", "#F39399", "#F5CBCB", "#F6D8BD",
                  "#901E3E", "#D6336C", "#FFB6C1", "#412D15", "#715A5A"]
        industry_counts = filtered_df["Industry"].value_counts()

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.pie(
            industry_counts.values,
            labels=industry_counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors
        )
        ax.set_title("Postings by Industry")
        st.pyplot(fig)
        plt.close(fig)

    st.divider()

    # Salary vs Applicants
    st.subheader("🔵 Salary vs. Applicant Competition")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.scatter(
        filtered_df["Applicants"],
        filtered_df["Salary_LPA"],
        alpha=0.5,
        color="#6A1E55"
    )
    ax.set_xlabel("Applicants per Posting")
    ax.set_ylabel("Salary (LPA)")
    ax.set_title("Applicant Competition vs. Salary")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# TAB 2 — INSIGHTS

with tab2:

    st.subheader("💡 Key Business Insights")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:
        top_role_insight = (
            filtered_df["Job_Title"].value_counts().idxmax()
        )

        top_paying_role = (
            filtered_df.groupby("Job_Title")["Salary_LPA"]
            .mean()
            .idxmax()
        )

        top_skill = (
            filtered_df["Required_Skills"]
            .str.split(", ").explode().str.strip()
            .value_counts().idxmax()
        )

        top_location = (
            filtered_df["Location"].value_counts().idxmax()
        )

        top_industry = (
            filtered_df["Industry"].value_counts().idxmax()
        )

        best_month = (
            filtered_df.groupby("Month_Name")["Job_ID"]
            .count()
            .sort_values(ascending=False)
            .index[0]
        )

        highest_avg_salary = filtered_df.groupby("Job_Title")["Salary_LPA"].mean().max()

        avg_experience_salary_gap = (
            filtered_df.groupby("Experience_Level")["Salary_LPA"].mean().max()
            - filtered_df.groupby("Experience_Level")["Salary_LPA"].mean().min()
        )

        st.success(
            f"🏆 **Most Posted Role:** {top_role_insight} has the highest "
            f"number of job postings."
        )

        st.info(
            f"💰 **Highest Paying Role:** {top_paying_role} offers the "
            f"highest average salary ({highest_avg_salary:.1f} LPA)."
        )

        st.info(
            f"🧠 **Most In-Demand Skill:** {top_skill} appears most "
            f"frequently across postings."
        )

        st.info(
            f"📍 **Top Hiring Location:** {top_location} recorded the "
            f"highest number of postings."
        )

        st.info(
            f"🏭 **Leading Industry:** {top_industry} posted the most jobs."
        )

        st.info(
            f"📅 **Peak Hiring Month:** {best_month}."
        )

        st.metric(
            "📊 Experience-Level Salary Gap (Lead − Fresher)",
            f"{avg_experience_salary_gap:.1f} LPA"
        )

        st.divider()

        st.subheader("📌 Project Summary")

        st.write(
            "This dashboard presents the major findings from the Job "
            "Market Intelligence project. It brings together in-demand "
            "skills, salary benchmarks, hiring trends, industries, and "
            "regional performance into one interactive view."
        )

        st.write(
            "The dashboard is designed to make the analysis easier to "
            "explore by allowing users to filter results by year, job "
            "role, location, industry, experience level and remote status."
        )


# TAB 3 — RAW DATA

with tab3:

    st.subheader("📋 Filtered Raw Data")

    st.write(
        f"Showing **{len(filtered_df):,}** records after applying filters."
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        label="⬇️ Download Filtered Data",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="job_market_filtered_data.csv",
        mime="text/csv"
    )
