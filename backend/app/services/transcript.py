# pyrefly: ignore [missing-import]
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable

class TranscriptService:
    @staticmethod
    def get_transcript(video_id: str) -> str:
        """
        Retrieves the transcript for a given YouTube video ID.
        Combines all transcript segments into a single string.
        """
        try:
            # 1. Initialize the API object
            ytt_api = YouTubeTranscriptApi()

            # 2. Use .fetch() instead of .get_transcript()
            transcript_list = ytt_api.fetch(video_id)
            
            # Combine all pieces of transcript into a single text string
            full_text = " ".join(chunk.text for chunk in transcript_list)
            return full_text
        except (NoTranscriptFound, TranscriptsDisabled) as e:
            raise Exception("Transcripts are disabled or not available for this video.")
        except VideoUnavailable:
            raise Exception("The requested YouTube video is unavailable or private.")
        except Exception as e:
            raise Exception(f"Failed to fetch YouTube transcript: {str(e)}")
