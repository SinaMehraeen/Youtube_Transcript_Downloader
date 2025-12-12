# YouTube Channel Transcript Downloader

A Python tool to download transcripts from all videos on a YouTube channel and process them into clean, formatted files.

## Features

- 📺 **Download all transcripts** from any YouTube channel
- 📝 **Plain text output** with video metadata
- 🔄 **Post-processing script** to clean and convert to Markdown
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

## Scripts

### 1. Download Transcripts

Downloads transcripts from a YouTube channel as `.txt` files.

```bash
# Download all transcripts from a channel
python download_transcripts.py https://www.youtube.com/@ChannelName

# Or use the short @username format
python download_transcripts.py @ChannelName

# Vanity URLs also work
python download_transcripts.py https://www.youtube.com/minutephysics
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output directory | `transcripts` |
| `-l, --limit` | Max videos to process | All |
| `-d, --delay` | Delay between requests (seconds) | `3` |
| `-c, --cookies` | Path to cookies.txt file | None |
| `--languages` | Preferred transcript languages | `en en-US en-GB` |

#### Examples

```bash
# Save to custom folder
python download_transcripts.py @ChannelName -o my_transcripts

# Download only the 10 most recent videos
python download_transcripts.py @ChannelName --limit 10

# Use longer delay to avoid rate limiting
python download_transcripts.py @ChannelName --delay 5

# Download Spanish transcripts
python download_transcripts.py @ChannelName --languages es es-ES
```

### 2. Process Transcripts

Cleans up transcript files (removes extra whitespace) and converts to formatted Markdown.

```bash
# Default: reads from 'transcripts', outputs to 'processed_transcripts'
python process_transcripts.py

# Specify custom directories
python process_transcripts.py transcripts processed_transcripts
```

#### What it does:
- Removes multiple consecutive spaces
- Normalizes line breaks
- Strips leading/trailing whitespace
- Exports as clean Markdown with proper formatting

## Workflow

1. **Download** transcripts as plain text:
   ```bash
   python download_transcripts.py @ChannelName
   ```

2. **Process** into clean Markdown:
   ```bash
   python process_transcripts.py
   ```

## Output Formats

### Raw transcript (.txt)
```
Video Title
Video ID: abc123xyz
URL: https://www.youtube.com/watch?v=abc123xyz

This is the transcript content...
```

### Processed transcript (.md)
```markdown
# Video Title

**Video ID:** `abc123xyz`

**URL:** [https://www.youtube.com/watch?v=abc123xyz](https://www.youtube.com/watch?v=abc123xyz)

---

## Transcript

This is the cleaned transcript content...
```

## Avoiding Rate Limiting

YouTube may rate limit requests. If you see "429 Too Many Requests" errors:

### Option 1: Increase Delay

```bash
python download_transcripts.py @ChannelName --delay 10
```

### Option 2: Wait and Retry

Wait 1-2 hours before trying again if heavily rate limited.

> **Note:** Cookie authentication is currently broken in the youtube-transcript-api library (v1.2.3). The `--cookies` option is accepted but may not work.

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

## License

MIT License
