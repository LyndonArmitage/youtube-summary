import sys

from youtube_transcript_api import (
    FetchedTranscript,
    NoTranscriptFound,
    YouTubeTranscriptApi,
)

from youtube_summary.model import YouTubeID


class SimpleTranscriptProvider:

    def __init__(self) -> None:
        self.api: YouTubeTranscriptApi = YouTubeTranscriptApi()

    def get_transcript(
        self, id: YouTubeID, language: str, ignore_generated: bool
    ) -> str | None:

        transcript_list = self.api.list(id)
        try:
            transcript = transcript_list.find_transcript([language])
        except NoTranscriptFound:
            print(f"No transcripts for {id} lang={language}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Failed to get transcript list for {id}: {e}", file=sys.stderr)
            return None

        if transcript.is_generated and ignore_generated:
            print(f"No none-generated captions found for {id}", file=sys.stderr)
            return None

        try:
            fetched = transcript.fetch()
        except Exception as e:
            print(f"Failed to fetch transcript for {id}: {e}", file=sys.stderr)
            return None

        # Take the fetched transcript and turn it into plain text
        raw_text = _convert_transcript(fetched)

        if not raw_text:
            print(f"No transcript text for {id} lang={language}", file=sys.stderr)
            return None

        return raw_text


def _convert_transcript(transcript: FetchedTranscript) -> str:
    joined = "\n".join(snip.text for snip in transcript)
    joined = joined.strip()
    return joined
