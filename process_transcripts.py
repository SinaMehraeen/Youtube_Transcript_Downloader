"""
Transcript Processor
====================

This script processes transcript text files:
1. Reads .txt files from a directory
2. Removes extra whitespace (multiple spaces, leading/trailing spaces)
3. Exports as formatted Markdown files

Usage:
    python process_transcripts.py [input_dir] [output_dir]
    python process_transcripts.py transcripts processed_transcripts
"""

import argparse
import re
from pathlib import Path


def clean_text(text: str) -> str:
    """
    Clean up transcript text by removing extra whitespace and annotations.
    
    Args:
        text: Raw transcript text
    
    Returns:
        Cleaned text with normalized spacing and annotations removed
    """
    # Remove YouTube auto-generated annotations like [Music], [Applause], etc.
    # This handles various formats: [Music], [ Music ], [MUSIC], etc.
    text = re.sub(r'\[\s*[Mm]usic\s*\]', '', text)
    text = re.sub(r'\[\s*[Aa]pplause\s*\]', '', text)
    text = re.sub(r'\[\s*[Ll]aughter\s*\]', '', text)
    text = re.sub(r'\[\s*[Cc]heering\s*\]', '', text)
    text = re.sub(r'\[\s*[Ii]naudible\s*\]', '', text)
    
    # Replace all types of whitespace (including non-breaking spaces, tabs, etc.)
    # with regular spaces first
    text = re.sub(r'[\t\u00a0\u2000-\u200b\u202f\u205f\u3000]', ' ', text)
    
    # Replace all newlines with spaces to create continuous flowing text
    # (YouTube transcripts have line breaks for each subtitle segment)
    text = text.replace('\n', ' ')
    
    # Replace multiple spaces with single space
    text = re.sub(r'[ ]{2,}', ' ', text)
    
    # Final pass: ensure no double spaces remain
    text = re.sub(r'  +', ' ', text)
    
    # Strip overall leading/trailing whitespace
    return text.strip()


def parse_txt_file(filepath: Path) -> dict:
    """
    Parse a transcript .txt file and extract metadata and content.
    
    Expected format:
        Title
        Video ID: xxxxx
        URL: https://...
        
        [transcript text]
    
    Args:
        filepath: Path to the .txt file
    
    Returns:
        Dictionary with 'title', 'video_id', 'url', and 'transcript' keys
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Parse header lines
    title = lines[0].strip() if len(lines) > 0 else "Unknown Title"
    video_id = ""
    url = ""
    
    # Find Video ID and URL lines
    transcript_start = 0
    for i, line in enumerate(lines[1:], start=1):
        if line.startswith("Video ID:"):
            video_id = line.replace("Video ID:", "").strip()
        elif line.startswith("URL:"):
            url = line.replace("URL:", "").strip()
        elif line.strip() == "" and i > 2:
            # Empty line after headers marks start of transcript
            transcript_start = i + 1
            break
    
    # Extract transcript (everything after the header)
    transcript = '\n'.join(lines[transcript_start:])
    
    return {
        'title': title,
        'video_id': video_id,
        'url': url,
        'transcript': transcript
    }


def export_as_markdown(data: dict, output_path: Path) -> None:
    """
    Export transcript data as a formatted Markdown file.
    
    Args:
        data: Dictionary with title, video_id, url, and transcript
        output_path: Path to save the markdown file
    """
    # Clean the transcript text
    clean_transcript = clean_text(data['transcript'])
    
    # Build markdown content
    md_content = f"# {data['title']}\n\n"
    
    if data['video_id']:
        md_content += f"**Video ID:** `{data['video_id']}`\n\n"
    
    if data['url']:
        md_content += f"**URL:** [{data['url']}]({data['url']})\n\n"
    
    md_content += "---\n\n"
    md_content += "## Transcript\n\n"
    md_content += clean_transcript
    md_content += "\n"
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)


def process_transcripts(input_dir: str, output_dir: str) -> None:
    """
    Process all .txt transcript files in a directory.
    
    Args:
        input_dir: Directory containing .txt files
        output_dir: Directory to save processed .md files
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Validate input directory
    if not input_path.exists():
        print(f"❌ Error: Input directory not found: {input_dir}")
        return
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all .txt files
    txt_files = list(input_path.glob("*.txt"))
    
    if not txt_files:
        print(f"❌ No .txt files found in: {input_dir}")
        return
    
    print(f"📁 Input directory: {input_path.absolute()}")
    print(f"📁 Output directory: {output_path.absolute()}")
    print(f"📊 Found {len(txt_files)} transcript files to process\n")
    
    success_count = 0
    fail_count = 0
    
    for txt_file in txt_files:
        try:
            # Parse the text file
            data = parse_txt_file(txt_file)
            
            # Generate output filename (same name but .md extension)
            output_filename = txt_file.stem + ".md"
            output_filepath = output_path / output_filename
            
            # Export as markdown
            export_as_markdown(data, output_filepath)
            
            print(f"✅ Processed: {txt_file.name} → {output_filename}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed: {txt_file.name} - {str(e)}")
            fail_count += 1
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"✨ Done! Results:")
    print(f"    ✅ Processed: {success_count}")
    print(f"    ❌ Failed: {fail_count}")
    print(f"📁 Output saved to: {output_path.absolute()}")


def main():
    """Command-line interface for the transcript processor."""
    parser = argparse.ArgumentParser(
        description="Process transcript .txt files and export as clean Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_transcripts.py transcripts processed
  python process_transcripts.py ./raw_transcripts ./clean_transcripts
        """
    )
    
    parser.add_argument(
        "input_dir",
        nargs="?",
        default="transcripts",
        help="Directory containing .txt transcript files (default: transcripts)"
    )
    
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="processed_transcripts",
        help="Directory to save processed .md files (default: processed_transcripts)"
    )
    
    args = parser.parse_args()
    
    process_transcripts(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
