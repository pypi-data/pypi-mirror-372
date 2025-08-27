import json
import os
import re
import adalflow as adal
from dataclasses import dataclass, field
from adalflow.core import Generator
from adalflow.components.model_client.openai_client import OpenAIClient
from adalflow.optim.parameter import Parameter, ParameterType
from .llm_config import LLMCatalogueSummary


@dataclass
class DataSummary(adal.DataClass):
    """Data class for structured dataset summary output."""

    title: str = field(
        default="", metadata={"desc": "The title or name of the dataset/package"}
    )
    description: str = field(
        default="",
        metadata={"desc": "A concise description of the dataset in 100 words"},
    )
    key_resources: list[dict] = field(
        default_factory=list,
        metadata={"desc": "List of key resources with name, format, and description"},
    )
    metadata_summary: dict = field(
        default_factory=dict,
        metadata={
            "desc": "Summary of important metadata like when dataset was created, update frequency, license, etc."
        },
    )

    __output_fields__ = ["title", "description", "key_resources", "metadata_summary"]


class CatalogueSummariser(LLMCatalogueSummary):
    """Implementation of the LLMCatalogueSummary protocol for dataset information."""

    def __init__(self, temperature=0.2):
        """
        Initialise the catalogue summariser with AdalFlow components.

        Currently uses GPT-4o-mini.

        Args:
            temperature: The temperature parameter for generation
        """
        self.system_prompt = Parameter(
            data="""
            You are a data catalogue specialist who helps users understand and extract value from open data sources.
            Your task is to analyse and summarise dataset metadata in a clear, structured format that highlights the most important aspects of the dataset.
            Focus on providing information that would help a data analyst or data scientist quickly understand:
            1. What the dataset contains
            2. The key available resources and their formats
            3. Important metadata like when it was created,update frequency, and license
            """,
            role_desc="To provide task instructions to the language model",
            requires_opt=False,
            param_type=ParameterType.PROMPT,
        )

        self.parser = adal.DataClassParser(
            data_class=DataSummary,  # type: ignore
            return_data_class=True,
            format_type="json",
        )

        self.template = r"""<START_OF_SYSTEM_PROMPT>
            {{system_prompt}}
            <OUTPUT_FORMAT>
            {{output_format_str}}
            </OUTPUT_FORMAT>
            <END_OF_SYSTEM_PROMPT>
            <START_OF_USER>
            Please analyse and summarise the following dataset information:

            DATASET METADATA:
            {{package_json}}

            {% if context is not none %}
            ADDITIONAL CONTEXT:
            {{context}}
            {% endif %}

            Please provide a concise, structured summary of this dataset that would help users understand its contents, potential uses, and key characteristics.
            <END_OF_USER>
        """

        self.generator = Generator(
            model_client=OpenAIClient(),
            model_kwargs={
                "model": "gpt-4o-mini",
                "temperature": temperature,  # type: ignore
            },
            template=self.template,
            prompt_kwargs={
                "system_prompt": self.system_prompt,
                "output_format_str": self.parser.get_output_format_str(),
            },
            output_processors=self.parser,
        )

    def _sanitize_error_message(self, error_message: str) -> str:
        """
        Sanitize error messages to prevent API key or other sensitive data leakage.

        Args:
            error_message: The original error message

        Returns:
            Sanitized error message with sensitive data redacted
        """
        sanitized = str(error_message)

        sanitized = re.sub(r'sk-[a-zA-Z0-9]{20,}', '[API_KEY_REDACTED]', sanitized)

        sanitized = re.sub(r'Bearer\s+[a-zA-Z0-9\-_\.]+', 'Bearer [TOKEN_REDACTED]', sanitized)

        sanitized = re.sub(r'Authorization:\s*[^\s,]+', 'Authorization: [REDACTED]', sanitized)

        sanitized = re.sub(r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9\-_]{20,}["\']?',
                          'api_key: [REDACTED]', sanitized, flags=re.IGNORECASE)

        return sanitized

    def summarise_catalogue(self, catalogue_data) -> dict:
        """
        Summarise the provided data source information.

        Args:
            catalogue_data: A dictionary or list of dictionaries containing the data source information

        Returns:
            A dictionary containing the structured summary
        """

        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        package_json = json.dumps(catalogue_data, indent=2)

        response = self.generator(
            prompt_kwargs={"package_json": package_json, "context": None}
        )

        if response.error:
            sanitized_error = self._sanitize_error_message(response.error)
            raise Exception(f"Error generating summary: {sanitized_error}")
        summary = response.data
        if not isinstance(summary, DataSummary):
            raise TypeError(f"Expected DataSummary, got {type(summary)}")

        return {
            "title": summary.title,
            "description": summary.description,
            "key_resources": summary.key_resources,
            "metadata_summary": summary.metadata_summary,
        }
