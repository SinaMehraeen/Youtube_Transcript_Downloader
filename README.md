# YouTube Channel Transcript Downloader

A Python tool to download transcripts from all videos on a YouTube channel, fetch video statistics, clean the content, and save as formatted files - all in one step.

## Features

- 📺 **Download all transcripts** from any YouTube channel
- 📊 **Fetch video statistics** (views, likes, comments) automatically
- 🧹 **Clean transcript text** (removes [Music], [Applause], etc.)
- 📝 **Clean formatted output** ready to use
- 🎯 **Prioritizes manual transcripts** over auto-generated ones
- ⏱️ **Rate limiting protection** with automatic retries
- 📁 **Skip existing files** - resume interrupted downloads

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/youtube_transcript_downloader.git
cd youtube_transcript_downloader

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Download all transcripts from a channel
python download_transcripts.py https://www.youtube.com/@ChannelName

# Or use the short @username format
python download_transcripts.py @ChannelName

# Vanity URLs also work
python download_transcripts.py https://www.youtube.com/minutephysics
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output directory | `transcripts` |
| `-l, --limit` | Max videos to process | All |
| `-d, --delay` | Delay between requests (seconds) | `3` |
| `-p, --proxies` | Path to proxy list file | None |
| `--languages` | Preferred transcript languages | `en en-US en-GB` |
| `--skip-stats` | Skip fetching video statistics | False |

## Examples

```bash
# Save to custom folder
python download_transcripts.py @ChannelName -o my_transcripts

# Download only the 10 most recent videos
python download_transcripts.py @ChannelName --limit 10

# Use longer delay to avoid rate limiting
python download_transcripts.py @ChannelName --delay 5

# Download Spanish transcripts
python download_transcripts.py @ChannelName --languages es es-ES

# Skip video statistics (faster download)
python download_transcripts.py @ChannelName --skip-stats
```

## Output Format

Each transcript is saved as a clean, formatted `.md` file:

```
Title: Video Title Here
Video ID: abc123xyz
URL: https://www.youtube.com/watch?v=abc123xyz
View Count: 1234567
Like Count: 12345
Favorite Count: 0
Comment Count: 234

========================================

This is the cleaned transcript content. All YouTube annotations like 
music and applause tags have been removed. The text is formatted as 
a single clean paragraph ready to use.
```

## What Gets Cleaned

The script automatically removes common YouTube annotations:
- `[Music]`, `[Applause]`, `[Laughter]`
- `[Cheering]`, `[Audience]`, `[Silence]`
- `[Background music]`, `[Background noise]`
- `[Intro music]`, `[Outro music]`, `[Theme music]`
- `[Foreign]`, `[Inaudible]`
- Musical note symbols (♪)
- Any other bracketed annotations

## Avoiding Rate Limiting

YouTube may rate limit requests. If you see "429 Too Many Requests" errors:

### Option 1: Increase Delay

```bash
python download_transcripts.py @ChannelName --delay 10
```

### Option 2: Use Proxies

```bash
python download_transcripts.py @ChannelName --proxies proxies.txt
```

### Option 3: Wait and Retry

Wait 1-2 hours before trying again if heavily rate limited.


## Supported URL Formats

- `https://www.youtube.com/@ChannelName`
- `https://www.youtube.com/channel/UCxxxxxx`
- `https://www.youtube.com/c/CustomName`
- `https://www.youtube.com/user/Username`
- `https://www.youtube.com/ChannelName` (vanity URLs)
- `@ChannelName` (shorthand)

## Requirements

- Python 3.10+
- youtube-transcript-api >= 1.0.0
- scrapetube >= 2.5.0
- yt-dlp (optional, for video statistics)

## Legacy Scripts

The repository also includes standalone scripts for existing transcripts:

- `analyze_transcripts.py` - Descriptive statistics of transcripts and engagement analysis of channel videos (e.g. like/view ratio, word count, etc.)


## License

MIT License
