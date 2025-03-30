from typing import Any, Dict, List

from google.genai import types

from config import MODEL_NAME, Config


class JobSearcher:
    """Job search functionality."""

    def __init__(self, config: Config):
        self.config = config

    def search_jobs(self, resume_text: str) -> List[Dict[str, Any]]:
        contents = self._create_search_contents(resume_text)
        config = self._create_search_config()

        search_results = []
        for chunk in self.config.genai_client.models.generate_content_stream(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        ):
            if chunk.candidates and chunk.candidates[0].content.parts:
                for part in chunk.candidates[0].content.parts:
                    if hasattr(part, "text"):
                        search_results.append(part.text)

        return search_results

    @staticmethod
    def _create_search_contents(resume_text: str) -> List[types.Content]:
        web_search_prompt = f"""I need help finding job opportunities in Australia for a candidate with the following resume.
        Please provide links to job boards with current listings, suggest relevant search terms to use on those job boards,
        and identify specific companies that might be hiring. Also, please summarize the types of roles that would be a good fit,
        and industries that are actively hiring for these roles in Australia.

        Here is the candidate's resume: {resume_text}

        Please ensure that the links provided are to active job search pages, and focus on Australian opportunities."""

        return [
            types.Content(
                role="user", parts=[types.Part.from_text(text=web_search_prompt)]
            )
        ]

    @staticmethod
    def _create_search_config() -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            temperature=0,
            top_p=1,
            max_output_tokens=8192,
            response_modalities=["TEXT"],
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT", threshold="OFF"
                ),
            ],
            tools=[types.Tool(google_search=types.GoogleSearch())],
        )
