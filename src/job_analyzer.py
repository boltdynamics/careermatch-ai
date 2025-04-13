from typing import Tuple, Dict, Any
import re

import streamlit as st
from vertexai.generative_models import GenerativeModel

from config import Config, MODEL_NAME


class JobAnalyzer:
    """Job analysis and matching functionality using generative AI."""

    def __init__(self, config: Config):
        self.config = config
        self.model = GenerativeModel(MODEL_NAME)

    def calculate_similarity(
        self, resume_text: str, job_details: str
    ) -> Tuple[float, str]:
        """
        Use generative AI to calculate similarity and provide analysis.
        Returns both a similarity score and a formatted analysis.
        """
        try:
            result = self._get_structured_analysis(resume_text, job_details)
            return result["score"], result["analysis"]
        except Exception as e:
            st.error(f"Error calculating similarity: {str(e)}")
            return 0.0, f"Error analyzing match: {str(e)}"

    def _get_structured_analysis(
        self, resume_text: str, job_details: str
    ) -> Dict[str, Any]:
        """
        Get a structured analysis with score and text as separate elements.
        This avoids the need to parse text to extract the score.
        """
        try:
            score_prompt = f"""
            Analyze the resume and job description below. Return ONLY a numeric score between 0 and 1
            representing how well the resume matches the job requirements.
            Higher score means better match.

            YOUR RESPONSE MUST BE ONLY A SINGLE NUMBER between 0 and 1 and nothing else.
            Examples of valid responses: 0.75 or 0.3 or 0.9
            DO NOT include any explanations, text, or other information.

            Resume:
            {resume_text}

            Job Description:
            {job_details}
            """

            score_response = self.model.generate_content(score_prompt)
            score_text = score_response.text.strip()

            # Extract numeric value using regex to handle cases where model adds text
            score_match = re.search(r"([0-9]*\.?[0-9]+)", score_text)

            if score_match:
                # Extract the first numeric value found
                score = float(score_match.group(1))
            else:
                # Fallback if no numeric value is found
                score = 0.5
                st.warning(
                    "Could not extract a numeric score from the model response. Using default value of 0.5."
                )

            # Ensure score is properly bounded
            score = max(0.0, min(1.0, score))

            # Second, get detailed analysis
            analysis_prompt = f"""
            Analyze the following resume and job description. Provide a detailed analysis including:
            1. Key skills that match (if any)
            2. Missing skills or qualifications
            3. Suggestions for improving the resume

            Format the analysis with clear sections and bullet points for readability.

            Resume:
            {resume_text}

            Job Description:
            {job_details}
            """

            analysis_response = self.model.generate_content(analysis_prompt)
            analysis_text = analysis_response.text

            return {"score": score, "analysis": analysis_text}
        except Exception as e:
            st.error(f"Error in structured analysis: {str(e)}")
            return {"score": 0.5, "analysis": f"Error performing analysis: {str(e)}"}

    def generate_cover_letter(
        self, resume_text: str, job_details: str, analysis: str = None
    ) -> str:
        """
        Generate a professional cover letter based on resume and job posting details.

        Args:
            resume_text: The candidate's resume text
            job_details: The job posting description
            analysis: Optional job match analysis to further tailor the letter

        Returns:
            A formatted cover letter as a string
        """
        try:
            prompt = f"""
            Create a professional cover letter based on the following resume and job description.

            Resume:
            {resume_text}

            Job Description:
            {job_details}
            """
            if analysis:
                prompt += f"""
                Analysis of Match:
                {analysis}
                """

            prompt += """
            The cover letter should:
            1. Start with a proper, formal letter format including today's date
            2. Begin with a compelling introduction that mentions the specific position
            3. Highlight key skills from the resume that match the job requirements
            4. Address any potential gaps with alternative qualifications or transferable skills
            5. Demonstrate enthusiasm for the role and company
            6. End with a professional closing paragraph and "Sincerely," signature

            Keep the tone professional but engaging. Format the letter properly with paragraphs.
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            st.error(f"Error generating cover letter: {str(e)}")
            return "Error: Unable to generate cover letter. Please try again later."
