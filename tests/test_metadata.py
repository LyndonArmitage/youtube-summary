from datetime import date
from typing import Self, cast

import pytest
import yt_dlp

from youtube_summary.metadata import YTDLPMetadataFetcher


class _FakeYoutubeDL:
    def __init__(self, _options: dict[str, object]) -> None:
        pass

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def extract_info(self, _url: str, *, download: bool) -> dict[str, object]:
        assert download is False
        return {
            "title": "A useful title",
            "channel": "A useful channel",
            "duration": 125,
            "upload_date": "20260102",
            "chapters": [
                {"title": "Introduction"},
                {"title": "Conclusion"},
                {"start_time": 30},
            ],
        }


def test_get_video_details_parses_metadata_and_chapters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(yt_dlp, "YoutubeDL", cast(object, _FakeYoutubeDL))

    details = YTDLPMetadataFetcher().get_video_details("A5l5GDwjymE")

    assert details.id == "A5l5GDwjymE"
    assert details.video_url == "https://www.youtube.com/watch?v=A5l5GDwjymE"
    assert details.title == "A useful title"
    assert details.channel == "A useful channel"
    assert details.duration_seconds == 125
    assert details.upload_date == date(2026, 1, 2)
    assert details.chapters == ["Introduction", "Conclusion"]
