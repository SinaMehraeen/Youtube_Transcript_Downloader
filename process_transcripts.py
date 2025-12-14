"""
Transcript Cleaner
===================

This script cleans and reformats YouTube transcript markdown files.
It removes formatting issues, YouTube annotations, and organizes the content.

Usage:
    python process_transcripts.py [input_folder] [output_folder]
    python process_transcripts.py                    # Uses defaults: transcripts -> cleaned
    python process_transcripts.py transcripts cleaned
"""

import re
import sys
from pathlib import Path


# Common YouTube annotations to remove (case-insensitive)
ANNOTATIONS_TO_REMOVE = [
    r'\[music\]',
    r'\[applause\]', 
    r'\[laughter\]',
    r'\[cheering\]',
    r'\[audience\]',
    r'\[inaudible\]',
    r'\[silence\]',
    r'\[background music\]',
    r'\[background noise\]',
    r'\[intro music\]',
    r'\[outro music\]',
    r'\[theme music\]',
    r'\[upbeat music\]',
    r'\[soft music\]',
    r'\[dramatic music\]',
    r'\[foreign\]',
    r'\[speaking foreign language\]',
    r'\[♪\]',
    r'\[♪♪\]',
    r'\[♪♪♪\]',
    r'♪',
]


def clean_transcript_text(text: str) -> str:
    """
    Clean transcript text by removing annotations and fixing formatting.
    Returns a single continuous paragraph of text.
    
    Args:
        text: Raw transcript text
        
    Returns:
        Cleaned transcript text as a single paragraph
    """
    cleaned = text
    
    # Remove YouTube annotations (case-insensitive)
    for annotation in ANNOTATIONS_TO_REMOVE:
        cleaned = re.sub(annotation, '', cleaned, flags=re.IGNORECASE)
    
    # Remove any other bracketed annotations like [Music], [Applause], etc.
    cleaned = re.sub(r'\[[^\]]*\]', '', cleaned)
    
    # Replace all newlines and carriage returns with spaces
    cleaned = re.sub(r'[\r\n]+', ' ', cleaned)
    
    # Fix multiple spaces (replace 2+ spaces with single space)
    cleaned = re.sub(r'  +', ' ', cleaned)
    
    # Remove spaces before punctuation
    cleaned = re.sub(r'\s+([.,!?;:])', r'\1', cleaned)
    
    # Ensure space after punctuation (if followed by letter)
    cleaned = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', cleaned)
    
    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()
    
    return cleaned


def extract_metadata(content: str) -> tuple[dict, str]:
    """
    Extract metadata from the original markdown file.
    
    Args:
        content: Full file content
        
    Returns:
        Tuple of (metadata_dict, transcript_text)
    """
    metadata = {
        'title': '',
        'video_id': '',
        'url': ''
    }
    
    lines = content.split('\n')
    transcript_start = 0
    
    for i, line in enumerate(lines):
        # Extract title (first H1)
        if line.startswith('# ') and not metadata['title']:
            metadata['title'] = line[2:].strip()
        
        # Extract video ID
        if '**Video ID:**' in line:
            match = re.search(r'`([^`]+)`', line)
            if match:
                metadata['video_id'] = match.group(1)
        
        # Extract URL
        if '**URL:**' in line:
            match = re.search(r'\((https://[^)]+)\)', line)
            if match:
                metadata['url'] = match.group(1)
        
        # Find where transcript starts
        if '## Transcript' in line:
            transcript_start = i + 1
            break
    
    # Get transcript text (everything after "## Transcript")
    transcript_text = '\n'.join(lines[transcript_start:]).strip()
    
    return metadata, transcript_text


def format_cleaned_file(metadata: dict, cleaned_text: str) -> str:
    """
    Format the cleaned transcript with metadata header.
    
    Args:
        metadata: Dictionary with title, video_id, url
        cleaned_text: Cleaned transcript text
        
    Returns:
        Formatted file content
    """
    output = []
    
    # Add metadata section
    if metadata['title']:
        output.append(f"Title: {metadata['title']}")
    if metadata['video_id']:
        output.append(f"Video ID: {metadata['video_id']}")
    if metadata['url']:
        output.append(f"URL: {metadata['url']}")
    
    # Add separator
    output.append('')
    output.append('=' * 40)
    output.append('')
    
    # Add cleaned transcript
    output.append(cleaned_text)
    
    return '\n'.join(output)


def process_transcripts(input_dir: str = "transcripts", output_dir: str = "cleaned"):
    """
    Process all transcript files in a directory.
    
    Args:
        input_dir: Folder containing original transcripts
        output_dir: Folder to save cleaned transcripts
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Check input directory exists
    if not input_path.exists():
        print(f"[X] Input directory not found: {input_path.absolute()}")
        return
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all markdown files
    md_files = list(input_path.glob("*.md"))
    
    if not md_files:
        print(f"[X] No .md files found in: {input_path.absolute()}")
        return
    
    print(f"[>] Input: {input_path.absolute()}")
    print(f"[>] Output: {output_path.absolute()}")
    print(f"[#] Found {len(md_files)} transcript(s) to process\n")
    
    success_count = 0
    fail_count = 0
    
    for md_file in md_files:
        try:
            # Read original file
            content = md_file.read_text(encoding='utf-8')
            
            # Extract metadata and transcript
            metadata, transcript_text = extract_metadata(content)
            
            # Clean the transcript
            cleaned_text = clean_transcript_text(transcript_text)
            
            # Format output
            output_content = format_cleaned_file(metadata, cleaned_text)
            
            # Save to output directory
            output_file = output_path / md_file.name
            output_file.write_text(output_content, encoding='utf-8')
            
            print(f"[+] Cleaned: {md_file.name}")
            success_count += 1
            
        except Exception as e:
            print(f"[X] Failed: {md_file.name} - {e}")
            fail_count += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"[*] Done! Results:")
    print(f"    [+] Cleaned: {success_count}")
    print(f"    [X] Failed: {fail_count}")
    print(f"[>] Cleaned files saved to: {output_path.absolute()}")


def main():
    """Command-line interface."""
    # Default directories
    input_dir = "transcripts"
    output_dir = "cleaned"
    
    # Parse command-line arguments
    if len(sys.argv) >= 2:
        input_dir = sys.argv[1]
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    
    print("[*] Transcript Cleaner")
    print("=" * 50)
    print()
    
    process_transcripts(input_dir, output_dir)


if __name__ == "__main__":
    main()
