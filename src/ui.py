import io
from urllib.error import URLError
from urllib.request import urlopen, Request

import PyPDF2
import streamlit as st
from bs4 import BeautifulSoup

from job_analyzer import JobAnalyzer
from job_searcher import JobSearcher
from text_processor import TextProcessor


class StreamlitUI:
    """Streamlit UI components."""

    def __init__(self, job_analyzer: JobAnalyzer, job_searcher: JobSearcher):
        self.job_analyzer = job_analyzer
        self.job_searcher = job_searcher

    def run(self):
        self._setup_page()
        self._show_sidebar()
        self._show_main_content()

    @staticmethod
    def _setup_page():
        st.set_page_config(page_title="CareerMatch AI", page_icon="🎯", layout="wide")

    @staticmethod
    def _show_sidebar():
        with st.sidebar:
            st.warning(
                """
            **Disclaimer:**
            - This tool uses AI to analyze resumes and job postings
            - Results are suggestions only and not guaranteed
            - Your data is processed securely but not stored
            - Always review AI-generated content before use
            """
            )

            st.info(
                """
            **How to use:**
            1. Upload/enter your resume
            2. Either:
               - Enter a job URL to analyze match
               - Leave URL blank to get job search recommendations
            3. Click 'Analyze' to get results
            """
            )

    def _show_main_content(self):
        st.title("🎯 CareerMatch AI")
        st.subheader("Intelligent Career Matching Platform")

        resume_text = self._get_resume_input()
        job_url = self._get_job_url_input()

        if st.button("🔎 Analyze", type="primary", use_container_width=True):
            self._process_analysis(resume_text, job_url)

    def _get_resume_input(self):
        st.subheader("Step 1: Provide Your Resume")
        col1, col2 = st.columns(2)

        with col1:
            resume_input_method = st.radio(
                "Choose input method:", ["Upload Resume (PDF)", "Enter Resume Text"]
            )

        with col2:
            if resume_input_method == "Upload Resume (PDF)":
                return self._handle_file_upload()
            return st.text_area(
                "Paste your resume text",
                height=200,
                placeholder="Paste your resume content here...",
            )

    @staticmethod
    def _handle_file_upload():
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf"])
        if uploaded_file:
            file_content = uploaded_file.read()
            resume_text = StreamlitUI._extract_text_from_pdf(file_content)
            st.success("✅ Resume uploaded successfully!")
            with st.expander("Review Extracted Text"):
                st.text(resume_text)
            return resume_text
        return ""

    @staticmethod
    def _extract_text_from_pdf(file_content: bytes) -> str:
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            return " ".join(page.extract_text() for page in pdf_reader.pages)
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"

    @staticmethod
    def _get_job_url_input():
        st.subheader("Step 2: Choose Analysis Type")
        return st.text_input(
            "Enter job posting URL (optional)",
            placeholder="https://example.com/job-posting",
            help="Leave blank to get job search recommendations based on your resume",
        )

    def _process_analysis(self, resume_text: str, job_url: str) -> None:
        """Process the analysis of resume and job posting."""
        if not resume_text:
            st.error("⚠️ Please provide your resume first!")
            return

        if job_url:
            if not TextProcessor.validate_url(job_url):
                st.error("⚠️ Please provide a valid URL!")
                return

            with st.spinner("Scraping job details..."):
                job_details = self._scrape_job_details(job_url)
                if not job_details:
                    st.error("❌ Could not fetch job details. Please check the URL.")
                    return

            with st.spinner("Analyzing match..."):
                score, analysis = self.job_analyzer.calculate_similarity(
                    resume_text, job_details
                )
                self._display_job_match_results(
                    score, analysis, job_details, resume_text
                )

        else:
            with st.spinner("Searching for relevant jobs..."):
                search_results = self.job_searcher.search_jobs(resume_text)
                full_text = "".join(search_results)
                with st.expander("🎯 Job Search Results", expanded=True):
                    st.markdown(full_text)

    def _scrape_job_details(self, url: str) -> str:
        """Scrape job details from URL."""
        try:
            headers = {
                "User-Agent": "*",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            req = Request(url, headers=headers)
            with urlopen(req) as response:
                soup = BeautifulSoup(response.read(), "html.parser")
                return soup.get_text()
        except URLError as e:
            st.error(f"Error fetching job details: {str(e)}")
            return ""

    def _display_job_match_results(
        self, score: float, analysis: str, job_details: str, resume_text: str
    ) -> None:
        """Display job match results in a structured format."""
        st.subheader("Analysis Results")

        col1, col2 = st.columns(2)
        generate_cv = False
        with col1:
            # Use a clean display format for the metric, avoid any string parsing issues
            st.metric("Match Score", f"{int(score * 100)}%")
        with col2:
            if score >= 0.75:
                generate_cv = True
                st.success("Strong Match! 🌟")
            elif score >= 0.5:
                generate_cv = True
                st.warning("Moderate Match 📈")
            else:
                st.error("Low Match 📉")

        st.markdown("### Detailed Analysis")
        st.markdown(analysis)

        # Automatically generate cover letter if the match is strong or moderate
        if generate_cv:
            with st.spinner("Generating your cover letter..."):
                cover_letter = self.job_analyzer.generate_cover_letter(
                    resume_text, job_details, analysis
                )

            if cover_letter:
                st.markdown(
                    "### View and Download Cover Letter relevant to the job posting"
                )
                with st.expander("View Cover Letter", expanded=True):
                    st.markdown(cover_letter)

                st.download_button(
                    label="📥 Download Cover Letter",
                    data=cover_letter,
                    file_name="cover_letter.txt",
                    mime="text/plain",
                    key="download_cover_letter",
                )
