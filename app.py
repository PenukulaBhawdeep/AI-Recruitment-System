# app.py
import streamlit as st
import pandas as pd
from main import init_db, process_recruitment

st.set_page_config(page_title="AI Recruitment System", layout="wide")

def main():
    st.title("🤖 AI Recruitment System")
    init_db()

    st.sidebar.header("Job Description Input")
    job_title = st.sidebar.text_input("Job Title", value="Software Engineer")
    jd_option = st.sidebar.radio("Job Description Source", ["Use Sample", "Custom Input"])

    if jd_option == "Use Sample":
        job_description = """
        Software Engineer Position
        Requirements:
        - 3+ years experience in Python
        - Knowledge of machine learning frameworks
        - Bachelor's degree in Computer Science
        - Experience with cloud platforms (AWS/Azure)
        - Strong problem-solving skills
        """
    else:
        job_description = st.sidebar.text_area("Enter Job Description", height=200)

    st.sidebar.header("Candidate Entries")
    sample_candidates = [
        ("John Doe", "john@example.com", "Experienced Python developer with 5 years of experience. ML expert with projects using TensorFlow and PyTorch. BS in Computer Science from MIT. AWS certified."),
        ("Sam Wilson", "sam@example.com", "Data scientist with 10 years of Python experience. PhD in Computer Science. Published papers on machine learning. Google Cloud certified. ML expert with projects using TensorFlow and PyTorch"),
        ("Jane Smith", "jane@example.com", "Full-stack developer with 1/2 years of JavaScript experience. AS in Information Technology.")
    ]

    candidate_entries = []
    for i, candidate in enumerate(sample_candidates):
        with st.expander(f"Candidate {i+1}: {candidate[0]}"):
            name = st.text_input(f"Name {i+1}", candidate[0])
            email = st.text_input(f"Email {i+1}", candidate[1])
            resume = st.text_area(f"Resume {i+1}", candidate[2])
            candidate_entries.append((name, email, resume))

    if st.button("Run Recruitment Process"):
        with st.spinner("Processing with AI agents..."):
            progress = st.progress(0)
            progress.progress(10)
            
            results = process_recruitment(job_title, job_description, candidate_entries)
            progress.progress(100)

        st.success("Processing Complete!")

        # Convert list of dicts to DataFrame
        results_df = pd.DataFrame(results)

        st.header("📝 Results Table")
        st.dataframe(results_df[["name", "email", "score", "interview_scheduled"]])

        st.header("📧 Generated Interview Emails")
        for result in results:
            if result["interview_scheduled"]:
                with st.expander(f"Email to {result['name']}"):
                    st.write(result["email_content"])

if __name__ == "__main__":
    main()
