import os
import urllib.request

from google.cloud import aiplatform
from google.genai import Client

MODEL_NAME = "gemini-2.0-flash-lite-001"


def get_gcp_project():
    """Get GCP project ID from metadata server."""
    url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
    req = urllib.request.Request(url)
    req.add_header("Metadata-Flavor", "Google")
    return urllib.request.urlopen(req).read().decode()


class Config:
    """Application configuration."""

    def __init__(self):
        aiplatform.init()
        self.genai_client = Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT") or get_gcp_project(),
            location="us-central1",
        )
