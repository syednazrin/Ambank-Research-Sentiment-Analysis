import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# ================================
# 🎨 STREAMLIT CONFIG
# ================================
st.set_page_config(page_title="Nestle Sentiment Dashboard", layout="wide")

# Theme colors
RED = "#E53534"
YELLOW = "#FFE60B"
ORANGE = "#F49C1C"
GRAY = "#F9F9F9"

# ================================
# 📊 DUMMY DATA (replace with real scraped data later)
# ================================
data = {
    "created_at": pd.date_range("2023-05-01", periods=500, freq="D"),
    "sentiment": ["Negative"] * 180 + ["Neutral"] * 140 + ["Positive"] * 180,
    "confidence": [round(x, 2) for x in list(pd.Series(range(500)) / 500)],
    "likes": pd.Series(range(500)).apply(lambda x: x % 50),
    "reshares": pd.Series(range(500)).apply(lambda x: x % 30),
    "comments": pd.Series(range(500)).apply(lambda x: x % 20),
}
df = pd.DataFrame(data)

# Add dummy boycott classification
df["boycott"] = df["sentiment"].apply(lambda x: "Pro-Boycott" if x == "Negative" else "Not Pro-Boycott")

# Split pre vs post Gaza-Israel tension
cutoff_date = pd.to_datetime("2023-10-07")
df["period"] = df["created_at"].apply(lambda x: "Pre-Gaza Tension" if x < cutoff_date else "Post-Gaza Tension")

# ================================
# 🏷️ HEADER WITH LOGO
# ================================
logo_url = "https://upload.wikimedia.org/wikipedia/en/thumb/1/15/Nestle_textlogo.svg/2560px-Nestle_textlogo.svg.png"

col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image(logo_url, width=120)
with col_title:
    st.markdown(f"""
        <h1 style="margin-bottom:0; color:{RED};">Nestlé Social Media Sentiment Dashboard</h1>
        <p style="margin-top:0; font-size:18px; color:#555;">Tracking boycott trends, engagement, and sentiment shifts</p>
    """, unsafe_allow_html=True)

st.markdown("---")

# ================================
# 📌 SENTIMENT SUMMARY CARDS
# ================================
total_posts = len(df)
neg_posts = len(df[df["sentiment"] == "Negative"])
neu_posts = len(df[df["sentiment"] == "Neutral"])
pos_posts = len(df[df["sentiment"] == "Positive"])
avg_conf = df["confidence"].mean()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Posts", f"{total_posts}")
col2.metric("Negative toward Nestle", f"{neg_posts}", delta=f"{round(neg_posts/total_posts*100,1)}%")
col3.metric("Neutral", f"{neu_posts}", delta=f"{round(neu_posts/total_posts*100,1)}%")
col4.metric("Positive toward Nestle", f"{pos_posts}", delta=f"{round(pos_posts/total_posts*100,1)}%")
col5.metric("Avg Confidence Score", f"{avg_conf:.2f}")

st.markdown("---")

# ================================
# 📊 SENTIMENT OVER TIME (SIDE-BY-SIDE)
# ================================
st.subheader("Sentiment Trends: Pre vs Post Gaza Tension")

# Pre (last 5 months before Oct 2023)
pre_df = df[(df["created_at"] < cutoff_date) & (df["created_at"] >= (cutoff_date - pd.DateOffset(months=5)))]
pre_sent = pre_df.groupby([pd.Grouper(key="created_at", freq="M"), "sentiment"]).size().reset_index(name="count")

# Post (5 months after Oct 2023)
post_df = df[(df["created_at"] >= cutoff_date) & (df["created_at"] <= cutoff_date + pd.DateOffset(months=5))]
post_sent = post_df.groupby([pd.Grouper(key="created_at", freq="M"), "sentiment"]).size().reset_index(name="count")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"<div style='background:{GRAY}; padding:10px; border-radius:12px;'>", unsafe_allow_html=True)
    fig_pre = px.line(pre_sent, x="created_at", y="count", color="sentiment", markers=True,
                      title="Pre-Tension Sentiment (5 months)")
    st.plotly_chart(fig_pre, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div style='background:{GRAY}; padding:10px; border-radius:12px;'>", unsafe_allow_html=True)
    fig_post = px.line(post_sent, x="created_at", y="count", color="sentiment", markers=True,
                       title="Post-Tension Sentiment (5 months)")
    st.plotly_chart(fig_post, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# ================================
# ☁️ WORD CLOUD (ASSOCIATED WORDS)
# ================================
st.subheader("Word Association Cloud")

dummy_texts = "Nestle boycott Gaza Israel Malaysia Milo Maggi support reject protest buy brand consumer freedom Palestine"
wordcloud = WordCloud(width=500, height=250, background_color="white",
                      colormap="Reds").generate(dummy_texts)

fig_wc, ax = plt.subplots(figsize=(6,3))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
fig_wc.tight_layout()
st.pyplot(fig_wc)

st.markdown("---")

# ================================
# 📊 ENGAGEMENT METRICS
# ================================
st.subheader("Engagement Metrics (Likes, Reshares, Comments)")

engagement = df.groupby([pd.Grouper(key="created_at", freq="M")]).agg({
    "likes": "sum", "reshares": "sum", "comments": "sum"
}).reset_index()

fig_eng = px.line(engagement, x="created_at", y=["likes", "reshares", "comments"],
                  markers=True, title="Engagement Trends Over Time")
st.plotly_chart(fig_eng, use_container_width=True)

st.markdown("---")

# ================================
# 📊 EXTRA: BOYCOTT TREND
# ================================
st.subheader("Pro-Boycott Mentions Over Time")

boycott_time = df.groupby([pd.Grouper(key="created_at", freq="W"), "boycott"]).size().reset_index(name="count")
fig_boycott = px.bar(
    boycott_time[boycott_time["boycott"] == "Pro-Boycott"],
    x="created_at", y="count", color_discrete_sequence=[RED]
)
st.plotly_chart(fig_boycott, use_container_width=True)
