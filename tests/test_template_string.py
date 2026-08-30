from datetime import date

import pytest

from youtube_summary import template_string
from youtube_summary.model import VideoDetails


@pytest.fixture
def video_details() -> VideoDetails:
    return VideoDetails(
        id="A5l5GDwjymE",
        title="A useful title",
        channel="A useful channel",
        chapters=[],
        duration_seconds=120,
        upload_date=date(2026, 1, 1),
    )


@pytest.mark.parametrize(
    ("template", "expected"),
    [
        ("$id", "A5l5GDwjymE"),
        ("$youtube_id", "A5l5GDwjymE"),
        ("$channel", "A useful channel"),
        ("$title", "A useful title"),
        (
            "$channel/$title-$id-$youtube_id.md",
            "A useful channel/A useful title-A5l5GDwjymE-A5l5GDwjymE.md",
        ),
    ],
)
def test_template_string_substitutes_metadata(
    template: str, expected: str, video_details: VideoDetails
) -> None:
    assert template_string(template, video_details) == expected


def test_template_string_leaves_unknown_placeholders_unchanged(
    video_details: VideoDetails,
) -> None:
    assert (
        template_string("$title-$unknown", video_details) == "A useful title-$unknown"
    )


def test_template_string_preserves_escaped_dollar_sign(
    video_details: VideoDetails,
) -> None:
    assert template_string("$$-$id", video_details) == "$-A5l5GDwjymE"
