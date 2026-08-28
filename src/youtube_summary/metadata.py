from datetime import date, datetime
from typing import cast

import yt_dlp

from youtube_summary.model import VideoDetails, YouTubeID


class YTDLPMetadataFetcher:

    def get_video_details(self, id: YouTubeID) -> VideoDetails:
        """Parse a given URL into a YouTube ID"""

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
            channel: str = (
                cast(str, info["channel"]) if "channel" in info else "Unknown"
            )
            duration: int = cast(int, info["duration"]) if "duration" in info else 0
            upload_date: date | None = None
            if "upload_date" in info and info["upload_date"]:
                upload_date = _parse_date(cast(str, info["upload_date"]))
            return VideoDetails(
                id=id,
                title=title,
                channel=channel,
                chapters=chapters,
                duration_seconds=duration,
                upload_date=upload_date,
            )


def _parse_date(date_string: str) -> date:
    found_date = datetime.strptime(date_string, "%Y%m%d").date()
    return found_date
