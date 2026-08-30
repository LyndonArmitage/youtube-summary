import re
import sys
from string import Template
from typing import cast

import tyro
from dotenv import load_dotenv
from pathvalidate import sanitize_filepath

from youtube_summary.metadata import YTDLPMetadataFetcher
from youtube_summary.model import (
    Args,
    ProvidesVideoDetails,
    SummaryProvider,
    TranscriptProvider,
    VideoDetails,
    YouTubeID,
)
from youtube_summary.summariser import OpenAISummariser
from youtube_summary.transcript import SimpleTranscriptProvider


def main() -> int:
    args: Args = tyro.cli(Args)  # pyright: ignore[reportAny]
    _ = load_dotenv()
    extracted_id = parse_to_id(args.youtube_url)
    if extracted_id is None:
        print("No ID was extracted", file=sys.stderr)
        return 2

    transcript_provider: TranscriptProvider = SimpleTranscriptProvider()
    raw_text = transcript_provider.get_transcript(
        extracted_id, args.lang, args.ignore_generated_captions
    )

    if raw_text is None:
        return 1

    provider: ProvidesVideoDetails = YTDLPMetadataFetcher()
    details: VideoDetails = provider.get_video_details(extracted_id)

    if args.save_transcript is not None:
        transcript_path = sanitize_filepath(
            template_string(args.save_transcript, details)
        )
        save_transcript(transcript_path, raw_text)

    # Send the transcript for parsing to AI model
    try:
        summariser: SummaryProvider = OpenAISummariser(
            args.model, args.openai_api_key, args.extra_tags
        )
        summary = summariser.generate_summary(details, raw_text, args.extra_prompt)
    except Exception as e:
        print(f"Failed to get summary for {extracted_id}: {e}", file=sys.stderr)
        return 1

    print(summary)
    if args.save_markdown is not None:
        markdown_path = sanitize_filepath(template_string(args.save_markdown, details))
        save_markdown(markdown_path, summary)
    return 0


def save_transcript(path: str, transcript_text: str) -> None:
    with open(path, "w", encoding="utf-8") as w:
        _ = w.write(transcript_text)


def save_markdown(path: str, summary: str) -> None:
    with open(path, "w", encoding="utf-8") as w:
        _ = w.write(summary)


def template_string(string: str, metadata: VideoDetails) -> str:
    template = Template(string)
    mapping: dict[str, str] = {
        "id": metadata.id,
        "youtube_id": metadata.id,
        "channel": metadata.channel,
        "title": metadata.title,
    }
    return template.safe_substitute(mapping)


VIDEO_ID = r"[A-Za-z0-9_-]{11}"

BASIC_PATTERN = re.compile(rf"[?&]v=({VIDEO_ID})(?=[&#\s]|$)")

SHORT_PATTERN = re.compile(
    rf"(?:https?://)?(?:www\.)?youtu\.be/({VIDEO_ID})(?=[?#\s]|$)"
)


def unescape_url(value: str) -> str:
    """Remove backslash escaping from URL punctuation."""
    return (
        value.replace(r"\/", "/")
        .replace(r"\?", "?")
        .replace(r"\=", "=")
        .replace(r"\&", "&")
    )


def parse_to_id(url: str, unescape: bool = False) -> YouTubeID | None:
    """Parse a URL or other string to a possible video ID"""

    if unescape:
        url = unescape_url(url)

    # Matches URL like:
    # https://www.youtube.com/watch?v=A5l5GDwjymE
    # https://www.youtube.com/watch?v=zAahrUwjKSE
    basic_match = BASIC_PATTERN.search(url)
    if basic_match is not None:
        found_id = cast(str, basic_match.group(1))
        return found_id

    # Short link matching
    # https://youtu.be/zAahrUwjKSE?si=sq1nHuVkk0c7Z1-B
    short_match = SHORT_PATTERN.search(url)
    if short_match is not None:
        found_id = cast(str, short_match.group(1))
        return found_id

    # Try to unescape
    if not unescape:
        return parse_to_id(url, unescape=True)

    return None


if __name__ == "__main__":
    try:
        return_code = main()
    except Exception as e:
        print(f"Unhandled exception: {e}", file=sys.stderr)
        return_code = 1
    sys.exit(return_code)
