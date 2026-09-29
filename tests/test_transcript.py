from types import SimpleNamespace
from typing import cast, final

from youtube_transcript_api import FetchedTranscript, YouTubeTranscriptApi

from youtube_summary.transcript import SimpleTranscriptProvider


@final
class _FakeTranscript:
    def __init__(self, *, generated: bool, fetched: FetchedTranscript) -> None:
        self.is_generated = generated
        self._fetched = fetched
        self.fetch_called = False

    def fetch(self) -> FetchedTranscript:
        self.fetch_called = True
        return self._fetched


@final
class _FakeTranscriptList:
    def __init__(self, transcript: _FakeTranscript) -> None:
        self.transcript = transcript
        self.requested_languages: list[str] | None = None

    def find_transcript(self, languages: list[str]) -> _FakeTranscript:
        self.requested_languages = languages
        return self.transcript


@final
class _FakeApi:
    def __init__(self, transcripts: _FakeTranscriptList) -> None:
        self.transcripts = transcripts

    def list(self, _video_id: str) -> _FakeTranscriptList:
        return self.transcripts


def _fetched_transcript() -> FetchedTranscript:
    return cast(
        FetchedTranscript,
        cast(
            object,
            [
                SimpleNamespace(text="  First sentence. "),
                SimpleNamespace(text="Second sentence.  "),
            ],
        ),
    )


def test_get_transcript_joins_fetched_snippets() -> None:
    transcript = _FakeTranscript(generated=False, fetched=_fetched_transcript())
    transcript_list = _FakeTranscriptList(transcript)
    provider = SimpleTranscriptProvider()
    provider.api = cast(YouTubeTranscriptApi, cast(object, _FakeApi(transcript_list)))

    result = provider.get_transcript("A5l5GDwjymE", "en", False)

    assert result == "First sentence. \nSecond sentence."
    assert transcript_list.requested_languages == ["en"]
    assert transcript.fetch_called


def test_get_transcript_skips_generated_captions_when_requested() -> None:
    transcript = _FakeTranscript(generated=True, fetched=_fetched_transcript())
    transcript_list = _FakeTranscriptList(transcript)
    provider = SimpleTranscriptProvider()
    provider.api = cast(YouTubeTranscriptApi, cast(object, _FakeApi(transcript_list)))

    assert provider.get_transcript("A5l5GDwjymE", "en", True) is None
    assert not transcript.fetch_called
