from datetime import timedelta

import mdformat
from openai import OpenAI
from openai.types.responses import ResponseInputParam

from youtube_summary.model import VideoDetails


class OpenAISummariser:

    def __init__(self, model: str, api_key: str | None = None) -> None:
        self.model: str = model
        self.client: OpenAI = (
            OpenAI(api_key=api_key) if api_key is not None else OpenAI()
        )

    def generate_summary(
        self, metadata: VideoDetails, transcript: str, extra_prompt: str | None
    ) -> str:
        """Generate a summary using the metadata and transcript"""
        summary_instructions = _get_summary_instructions(
            transcript, extra_prompt, metadata
        )
        inputs: ResponseInputParam = []

        if extra_prompt:
            inputs.append(
                {
                    "role": "developer",
                    "content": [
                        {
                            "type": "input_text",
                            "text": f"The following extra context has been provided:\n\n{extra_prompt}",
                        }
                    ],
                }
            )

        inputs.append(
            {"role": "user", "content": [{"type": "input_text", "text": transcript}]}
        )

        response = self.client.responses.create(
            model=self.model,
            instructions=summary_instructions,
            input=inputs,
        )
        summary = response.output_text.strip()
        summary = _format_text(summary)
        return _get_header(metadata) + summary


def _get_summary_instructions(
    _transcript: str, extra_prompt: str | None, metadata: VideoDetails
) -> str:
    instructions = (
        "Summarise the following transcript from a YouTube video "
        f'with the title: "{metadata.title}" from the channel "{metadata.channel}".'
        f" It is {metadata.duration_seconds} seconds long."
    )
    if metadata.upload_date is not None:
        formatted = metadata.upload_date.strftime("%d %b %Y")
        instructions += f" It was uploaded on {formatted}."
    if len(metadata.chapters) > 1:
        instructions += "\nIt has the following chapter titles:\n"
        for title in metadata.chapters:
            instructions += f"- {title}\n"
    if extra_prompt is not None and len(extra_prompt) > 0:
        instructions += "\n\nYou will be provided some extra context/instructions."
    return instructions


def _get_header(metadata: VideoDetails) -> str:
    duration = str(timedelta(seconds=metadata.duration_seconds))
    return f"""---
url: {metadata.video_url}
title: {metadata.title}
channel: {metadata.channel}
duration: "{duration}"
---\n
"""


def _format_text(text: str) -> str:
    formatted: str = mdformat.text(  # pyright: ignore[reportUnknownMemberType]
        text, options={"wrap": 79, "number": True}
    )
    return formatted
