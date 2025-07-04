import os
import streamlit as st
import openai
from serpapi import GoogleSearch


import os
import streamlit as st
import openai

# Securely load keys from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]






def ai_score_profile(profile_title, profile_link):
    prompt = f"""
You are a technical recruiter. Rate the following LinkedIn profile on a scale of 1–10 for a Solutions Engineer position. 
The ideal candidate has strong experience in DevOps, CI/CD, cloud infrastructure, and application security. Focus on technical fit.

LinkedIn profile title: {profile_title}
LinkedIn URL: {profile_link}

Give a brief explanation and then the score as "Score: X/10".
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=60,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error scoring profile: {e}"

def build_query(job_title, skills, location):
    parts = []
    if job_title:
        parts.append(f'"{job_title}"')
    if skills:
        parts.append(' '.join([f'"{skill.strip()}"' for skill in skills.split(',') if skill.strip()]))
    if location:
        parts.append(f'"{location}"')
    query = ' '.join(parts)
    return query

def search_linkedin(query, num_results=10):
    params = {
        "engine": "google",
        "q": f"site:linkedin.com/in {query}",
        "num": num_results,
        "api_key": SERPAPI_KEY
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        st.error(f"Error searching LinkedIn profiles: {e}")
        return []

    linkedin_profiles = []
    if "organic_results" in results:
        for result in results["organic_results"]:
            if "linkedin.com/in" in result["link"]:
                linkedin_profiles.append({
                    "title": result.get("title", "No Title"),
                    "link": result["link"]
                })

    return linkedin_profiles

st.title("LinkedIn Profile Finder - Google X-Ray Search")

with st.form("search_form"):
    job_title = st.text_input("Job Title (e.g. Solutions Engineer)")
    skills = st.text_input("Skills (comma separated, e.g. DevOps, Application Security)")
    location = st.text_input("Location (e.g. Israel)")
    submitted = st.form_submit_button("Search LinkedIn Profiles")

if submitted:
    query = build_query(job_title, skills, location)
    st.info(f"Searching Google for: {query}")

    with st.spinner("Searching LinkedIn profiles..."):
        profiles = search_linkedin(query)

    if profiles:
        st.success(f"Found {len(profiles)} LinkedIn profiles:")
        for p in profiles:
            st.markdown(f"### [{p['title']}]({p['link']})")
            with st.spinner('Scoring profile...'):
                score = ai_score_profile(p['title'], p['link'])
                st.write(score)
            st.write("---")
    else:
        st.warning("No results found. Try changing your search terms or try again later.")
