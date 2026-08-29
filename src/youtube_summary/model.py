from dataclasses import dataclass
from datetime import date
from typing import Protocol

YouTubeID = str


@dataclass
class Args:
    """
    YouTube Summary creator.

    This uses Large Language Model powered AI to summarise the transcript of a
    YouTube video.
    """

    youtube_url: str
    """The YouTube URL or ID to summarise"""

    lang: str = "en"
    """The language to use for transcripts, default to en"""

    extra_prompt: str | None = None
    """
    An extra prompt to provide the summariser.
    Helpful if you want to give extra details to help it out.
    """

    ignore_generated_captions: bool = False
    """
    Whether to ignore generated captions or not.
    If you ignore such, and no other captions are available, summary will fail.
    Normally provided captions are used over generated ones.
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

    model: str = "gpt-5.6-luna"
    """
    The LLM model to use for summaries
    """

    extra_tags: list[str] | None = None
    """
    Extra tags to add to the output
    """


@dataclass
class VideoDetails:
    """
    Metadata related to the video
    """

    id: YouTubeID
    """YouTube ID"""
    title: str
    """Title of the video"""
    channel: str
    """Name of the channel the video came from"""
    chapters: list[str]
    """A list of chapter names, empty if none are present"""
    duration_seconds: int
    """Duration of the video in seconds"""
    upload_date: date | None
    """The date the video was uploaded"""

    @property
    def video_url(self) -> str:
        """The video ID embedded in a URL"""
        return f"https://www.youtube.com/watch?v={self.id}"


class ProvidesVideoDetails(Protocol):

    def get_video_details(self, id: YouTubeID) -> VideoDetails:
        """Get video details from a YouTube ID"""
        ...


class TranscriptProvider(Protocol):

    def get_transcript(
        self, id: YouTubeID, language: str, ignore_generated: bool
    ) -> str | None:
        """Get a transcript for the given ID"""
        ...


class SummaryProvider(Protocol):

    def generate_summary(
        self, metadata: VideoDetails, transcript: str, extra_prompt: str | None
    ) -> str:
        """Generate a summary using the metadata and transcript"""
        ...
