import streamlit as st
from service.recommendation_service import recommend_assessments

st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 SHL Assessment Recommender")
st.caption("Describe a role or hiring requirement to get relevant SHL assessments.")

query = st.text_area(
    "Enter job description or requirement",
    placeholder="e.g. Looking for entry-level Java developers with strong collaboration skills",
    height=120
)

top_k = st.slider("Number of results", min_value=3, max_value=10, value=5)

if st.button("Find Assessments"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("Searching assessments..."):
            results = recommend_assessments(query, top_k=top_k)

        if not results:
            st.info("No relevant assessments found.")
        else:
            st.subheader("Recommended Assessments")

            for r in results:
                st.markdown(
                    f"""
                    **{r.get('name','')}**
                    🔗 [View assessment]({r.get('url','')})

                    - Test type: `{', '.join(r.get('test_type', []))}`
                    - Duration: `{r.get('duration_minutes', r.get('duration',''))}`
                    - Remote: `{r.get('remote_support','')}`
                    - Adaptive: `{r.get('adaptive_support','')}`
                    ---
                    """
                )