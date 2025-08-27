from .. import NamedModel, MissingDependencyError
from typing import Optional

try:
    from google import genai
except ImportError as err:
    raise MissingDependencyError("Please install google-genai library") from err


class GeminiModel(NamedModel):
    """
    Model that talks to Google Gemini family of models.

    - **model** (`str`): Name of the Gemini model. Default is `"gemini-2.5-flash"`.
    - **api_key** (`str`): Google API key (see Google Cloud Console https://aistudio.google.com/u/1/apikey). This key is
        required to authenticate with the Gemini API. Alternatively, api key can be speciafied with environment variable
        `GEMINI_API_KEY`.
    - **vertexai** (`bool`): Set this to `True` if using Vertex AI. Alternative way to force use of Vertex AI is to set
        environment variable `GOOGLE_GEMINI_USE_VERTEXAI=true`.
    - **project**: (`str`): Only required for Vertex AI. The name of your Google Cloud project.
        Can alternatively be set as environment variable `GOOGLE_CLOUD_PROJECT`.
    - **location**: (`str`): Only required for Vertex AI. The location of the Vertex AI instance.
        Can alternatively be set as environment variable `GOOGLE_CLOUD_LOCATION`.
    """

    def __init__(
        self,
        *,
        model: str = "gemini-1.5-pro",
        api_key: Optional[str] = None,
        vertexai: Optional[bool] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
    ):
        self._model = model

        self._client = genai.Client(
            api_key=api_key,
            vertexai=vertexai,
            project=project,
            location=location,
        )

        super().__init__(f"google-{model}", self.__chat)

    def __chat(self, messages: list) -> str:
        contents = [
            genai.types.Content(role=x["role"], parts=[genai.types.Part.from_text(text=x["content"])]) for x in messages
        ]
        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
        )
        return response.text
