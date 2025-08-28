from typing import Optional, Tuple, cast
import logging

from langchain_core.language_models import BaseLanguageModel

log = logging.getLogger(__name__)


class Summarizer:
    def __init__(
        self,
        model: BaseLanguageModel,
        summarize: bool,
        tags: Optional[dict[str, str]] = None,
        character_limit: int = 50000,
    ):
        """Initialize the summarizer.

        Args:
            model: The summarization model.
            summarize: Whether to summarize the document.
            tags: Dictionary of tags and their descriptions used for automatic tagging.
        """
        if not summarize and not tags:
            raise ValueError("Either summarize or tags must be provided.")
        self.model = model
        self.schema = self.create_tag_schema_class(summarize, tags)
        self.character_limit = character_limit

    def create_tag_schema_class(
        self, summarize: bool, tags: Optional[dict[str, str]]
    ) -> dict:
        schema = {
            "title": "SummarizeTagSchema",
            "type": "object",
            "properties": {},
        }
        description = ""
        required = []
        if summarize:
            description = "Summarize and describe what the following document is about in a formal and concise style, in one paragraph. "
            required.append("summary")
            schema["properties"]["summary"] = {
                "type": "string",
                "description": "A concise summary of the given content.",
            }
        if tags:
            description = f"{description} Provide a list of relevant tags for categorization. If the user already provided tags, don't use those tags (or mutually exclusive tags). "
            required.append("tags")
            schema["properties"]["tags"] = {
                "type": "array",
                "items": {"type": "string"},
            }
            schema["properties"]["tags"]["description"] = (
                "A list of relevant tags associated with the content, the following tags are available, DON'T USE ANY OTHER TAGS THAN THESE: "
            )
            for k, v in tags.items():
                schema["properties"]["tags"]["description"] += f"|{k}: {v}|"
        schema["description"] = description
        schema["required"] = required
        return schema

    def __call__(
        self, text: str, max_retries: int = 2
    ) -> Tuple[Optional[str], Optional[list[str]]]:
        structured_llm = self.model.with_structured_output(self.schema)
        truncated_text = text[: self.character_limit]
        for _ in range(max_retries + 1):
            try:
                result = cast(dict, structured_llm.invoke(truncated_text))
                return result["summary"], result["tags"] if "tags" in result else None
            except Exception as e:
                log.error(f"Failed to summarize document: {e}")
        return text[:100], []
