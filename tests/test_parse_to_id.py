import pytest

from youtube_summary import parse_to_id


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        (
            "https://www.youtube.com/watch?v=A5l5GDwjymE",
            "A5l5GDwjymE",
        ),
        (
            "https://www.youtube.com/watch?v=zAahrUwjKSE&t=42s",
            "zAahrUwjKSE",
        ),
        (
            "https://youtu.be/zAahrUwjKSE?si=sq1nHuVkk0c7Z1-B",
            "zAahrUwjKSE",
        ),
        (
            "youtu.be/A5l5GDwjymE#comments",
            "A5l5GDwjymE",
        ),
        (
            "https://www.youtube.com/watch?v=9KaXK8HUqTw&pp=ugUEEgJlbg%3D%3D",
            "9KaXK8HUqTw",
        ),
        (
            "https://m.youtube.com/watch?v=A5l5GDwjymE",
            "A5l5GDwjymE",
        ),
    ],
)
def test_parse_to_id_returns_video_id(url: str, expected: str) -> None:
    assert parse_to_id(url) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "https://www.youtube.com/watch?v=too-short",
        "https://youtu.be/too-long-video-id",
        "https://youtu.be/invalid.id",
        "A5l5GDwjymE",
    ],
)
def test_parse_to_id_returns_none_for_invalid_input(value: str) -> None:
    assert parse_to_id(value) is None
