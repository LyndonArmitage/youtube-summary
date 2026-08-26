import re
import sys
from dataclasses import dataclass
from typing import cast

import mdformat
import tyro
import yt_dlp
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses import ResponseInputParam
from youtube_transcript_api import (
    FetchedTranscript,
    NoTranscriptFound,
    YouTubeTranscriptApi,
)


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

    save_transcript: str | None = None
    """
    Optional path to save transcript to
    """

    save_markdown: str | None = None
    """
    Optional path to save summary to as a markdown
    """

    openai_api_key: str | None = None
    """
    Optional OpenAI API Key that will be used instead of the environment key
    """


@dataclass
class VideoDetails:
    title: str
    channel: str
    chapters: list[str]


def main() -> int:
    args: Args = tyro.cli(Args)  # pyright: ignore[reportAny]
    _ = load_dotenv()
    extracted_id = parse_to_id(args.youtube_url)
    if extracted_id is None:
        print("No ID was extracted", file=sys.stderr)
        return 2

    api = YouTubeTranscriptApi()
    transcript_list = api.list(extracted_id)
    try:
        transcript = transcript_list.find_transcript([args.lang])
    except NoTranscriptFound:
        print(f"No transcripts for {extracted_id} lang={args.lang}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Failed to get transcript list for {extracted_id}: {e}", file=sys.stderr)
        return 1

    if transcript.is_generated and args.ignore_generated_captions:
        print(f"No none-generated captions found for {extracted_id}", file=sys.stderr)
        return 1

    try:
        fetched = transcript.fetch()
    except Exception as e:
        print(f"Failed to fetch transcript for {extracted_id}: {e}", file=sys.stderr)
        return 1

    # Take the fetched transcript and turn it into plain text
    raw_text = convert_transcript(fetched)

    if args.save_transcript is not None:
        save_transcript(args.save_transcript, raw_text)

    if not raw_text:
        print("No transcript text.")
        return 1

    details = get_info(extracted_id)

    # Send the transcript for parsing to AI model
    try:
        client = (
            OpenAI(api_key=args.openai_api_key)
            if args.openai_api_key is not None
            else OpenAI()
        )
        summary = get_summary(client, raw_text, args.extra_prompt, details)
    except Exception as e:
        print(f"Failed to get summary for {extracted_id}: {e}", file=sys.stderr)
        return 1

    print(summary)
    if args.save_markdown is not None:
        save_markdown(args.save_markdown, summary)
    return 0


def get_info(id: str) -> VideoDetails:
    constructed_url = f"https://www.youtube.com/watch?v={id}"
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # pyright: ignore[reportArgumentType]
        info = ydl.extract_info(constructed_url, download=False)
        chapters: list[str] = []
        if "chapters" in info and info["chapters"]:
            raw_chapters = cast(list[dict[str, str | int]], info["chapters"])
            for chapter in raw_chapters:
                if "title" in chapter:
                    chapter_title: str = cast(str, chapter["title"])
                    chapters.append(chapter_title)
        title: str = cast(str, info["title"]) if "title" in info else "Unknown"
        channel: str = cast(str, info["channel"]) if "channel" in info else "Unknown"
        return VideoDetails(title=title, channel=channel, chapters=chapters)


def save_transcript(path: str, transcript_text: str) -> None:
    with open(path, "w", encoding="utf-8") as w:
        _ = w.write(transcript_text)


def save_markdown(path: str, summary: str) -> None:
    with open(path, "w", encoding="utf-8") as w:
        _ = w.write(summary)


def format_text(text: str) -> str:
    formatted: str = mdformat.text(  # pyright: ignore[reportUnknownMemberType]
        text, options={"wrap": 79, "number": True}
    )
    return formatted


def convert_transcript(transcript: FetchedTranscript) -> str:
    joined = "\n".join(snip.text for snip in transcript)
    joined = joined.strip()
    return joined


def get_summary(
    client: OpenAI, raw_text: str, extra_prompt: str | None, details: VideoDetails
) -> str:
    summary_instructions = get_summary_instructions(raw_text, extra_prompt, details)
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
        {"role": "user", "content": [{"type": "input_text", "text": raw_text}]}
    )

    response = client.responses.create(
        model="gpt-5.6-luna",
        instructions=summary_instructions,
        input=inputs,
    )
    summary = response.output_text.strip()
    summary = format_text(summary)
    return summary


def get_summary_instructions(
    _raw_text: str, extra_prompt: str | None, details: VideoDetails
) -> str:
    instructions = (
        "Summarise the following transcript from a YouTube video "
        f'with the title: "{details.title}" from the channel "{details.channel}"'
    )
    if len(details.chapters) > 1:
        instructions += "\nIt has the following chapter titles:\n"
        for title in details.chapters:
            instructions += f"- {title}\n"
    if extra_prompt is not None and len(extra_prompt) > 0:
        instructions += "\n\nYou will be provided some extra context/instructions."
    return instructions


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
    try:
        return_code = main()
    except Exception as e:
        print(f"Unhandled exception: {e}", file=sys.stderr)
        return_code = 1
    sys.exit(return_code)
