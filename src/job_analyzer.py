from typing import Tuple

import streamlit as st
from vertexai.generative_models import GenerativeModel

from config import Config


class JobAnalyzer:
    """Job analysis and matching functionality using generative AI."""

    def __init__(self, config: Config):
        self.config = config

    def calculate_similarity(
        self, resume_text: str, job_details: str
    ) -> Tuple[float, str]:
        """
        Use generative AI to calculate similarity and provide analysis.
        """
        try:
            model = GenerativeModel("gemini-pro")
            prompt = self._create_similarity_prompt(resume_text, job_details)
            response = model.generate_content(prompt)

            # Extract the similarity score and analysis from the AI's response
            similarity_score, analysis = self._parse_ai_response(response.text)
            return similarity_score, analysis
        except Exception as e:
            st.error(f"Error calculating similarity: {str(e)}")
            return 0.0, f"Error analyzing match: {str(e)}"

    @staticmethod
    def _create_similarity_prompt(resume_text: str, job_details: str) -> str:
        """
        Create a prompt for the AI to analyze the similarity between the resume and job description.
        """
        return f"""
        Analyze the following resume and job description, and provide a similarity score between 0 and 1.
        The score should reflect how well the resume matches the job requirements.
        Also, provide a detailed analysis of the match, including:
        1. Key skills that match.
        2. Missing skills or qualifications.
        3. Suggestions for improving the resume to better match the job.

        Resume:
        {resume_text}

        Job Description:
        {job_details}

        Format your response as follows:
        Similarity Score: [score between 0 and 1]
        Analysis: [detailed analysis]
        """

    @staticmethod
    def _parse_ai_response(response_text: str) -> Tuple[float, str]:
        """
        Parse the AI's response to extract the similarity score and analysis.
        """
        similarity_score = 0.0
        analysis = ""
        if "Similarity Score:" in response_text:
            score_part = response_text.split("Similarity Score:")[1].strip()
            similarity_score = float(score_part.split()[0])
        if "Analysis:" in response_text:
            analysis = response_text.split("Analysis:")[1].strip()
        return similarity_score, analysis
