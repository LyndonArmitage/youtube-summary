import re
from dataclasses import dataclass
from typing import cast

import tyro
from youtube_transcript_api import YouTubeTranscriptApi


@dataclass
class Args:

    youtube_url: str
    """The YouTube URL or ID to summarise"""

    lang: str = "en"
    """The language to use, default to en"""

    extra_prompt: str | None = None
    """
    An extra prompt to provide the summariser.
    Helpful if you want to give extra details to help it out.
    """

    ignore_generated_captions: bool = False
    """
    Whether to ignore generated captions or not.
    If you ignore such, and no other captions are available, summary will fail.
    """


def main() -> None:
    args: Args = tyro.cli(Args)  # pyright: ignore[reportAny]
    print(args)
    extracted_id = parse_to_id(args.youtube_url)
    print(f"Extracted ID: {extracted_id}")
    if extracted_id is None:
        return
    api = YouTubeTranscriptApi()
    transcript_list = api.list(extracted_id)
    transcript = transcript_list.find_transcript([args.lang])
    if transcript.is_generated and args.ignore_generated_captions:
        return
    fetched = transcript.fetch()
    for snip in fetched:
        print(snip.text)
    # TODO: Take the fetched transcript and turn it into plain text
    # TODO: Send the transcript for parsing to AI model


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


def parse_to_id(url: str, unescape: bool = False) -> str | None:
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
    main()
