from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from youtube_summary.model import VideoDetails
from youtube_summary.summariser import OpenAISummariser


def test_generate_summary_sends_transcript_and_returns_formatted_header() -> None:
    metadata = VideoDetails(
        id="A5l5GDwjymE",
        title="A useful title",
        channel="A useful channel",
        chapters=["Introduction", "Conclusion"],
        duration_seconds=125,
        upload_date=date(2026, 1, 2),
    )
    summariser = OpenAISummariser(
        "test-model", api_key="test-key", extra_tags=["research", "science"]
    )

    with patch.object(
        summariser.client.responses,
        "create",
        return_value=SimpleNamespace(output_text="  **Useful summary**  "),
    ):
        summary = summariser.generate_summary(
            metadata, "Transcript text", "Focus on the key findings."
        )

    expected_header = "---\nurl: https://www.youtube.com/watch?v=A5l5GDwjymE\ntitle: A useful title\nchannel: A useful channel\nduration: 0:02:05\ntags: [research, science]\n---\n"
    assert summary.startswith(expected_header)
    assert "Useful summary" in summary
    assert summary.endswith("\n")
