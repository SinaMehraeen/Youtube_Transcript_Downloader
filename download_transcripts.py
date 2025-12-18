"""
YouTube Transcript Analyzer
===========================

This script analyzes transcript files to provide statistics and visualizations.

Features:
1. Calculate average channel views from all transcript files
2. Calculate word count for every transcript
3. Create a histogram of normalized view counts with quartiles and median

Usage:
    python analyze_transcripts.py [folder]
    python analyze_transcripts.py                  # Uses default: cleaned
    python analyze_transcripts.py cleaned
"""

import re
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class TranscriptData:
    """Data extracted from a single transcript file."""
    filename: str
    title: str
    video_id: str
    view_count: int
    like_count: int
    comment_count: int
    word_count: int
    transcript_text: str


# =============================================================================
# PARSING FUNCTIONS
# =============================================================================

def parse_transcript_file(filepath: Path) -> TranscriptData | None:
    """
    Parse a cleaned transcript file and extract metadata and content.
    
    Expected format:
        Title: Video Title Here
        Video ID: abc123xyz
        URL: https://www.youtube.com/watch?v=abc123xyz
        View Count: 1234567
        Like Count: 12345
        Favorite Count: 0
        Comment Count: 234

        ========================================

        Transcript text here...
    """
    try:
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Initialize values
        title = ""
        video_id = ""
        view_count = 0
        like_count = 0
        comment_count = 0
        transcript_text = ""
        
        separator_found = False
        transcript_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Parse metadata
            if line_stripped.startswith('Title:'):
                title = line_stripped[6:].strip()
            elif line_stripped.startswith('Video ID:'):
                video_id = line_stripped[9:].strip()
            elif line_stripped.startswith('View Count:'):
                match = re.search(r'(\d+)', line_stripped)
                if match:
                    view_count = int(match.group(1))
            elif line_stripped.startswith('Like Count:'):
                match = re.search(r'(\d+)', line_stripped)
                if match:
                    like_count = int(match.group(1))
            elif line_stripped.startswith('Comment Count:'):
                match = re.search(r'(\d+)', line_stripped)
                if match:
                    comment_count = int(match.group(1))
            elif line_stripped.startswith('=' * 10):
                separator_found = True
            elif separator_found:
                transcript_lines.append(line)
        
        transcript_text = '\n'.join(transcript_lines).strip()
        word_count = len(transcript_text.split()) if transcript_text else 0
        
        return TranscriptData(
            filename=filepath.name,
            title=title,
            video_id=video_id,
            view_count=view_count,
            like_count=like_count,
            comment_count=comment_count,
            word_count=word_count,
            transcript_text=transcript_text
        )
        
    except Exception as e:
        print(f"  Error parsing {filepath.name}: {e}")
        return None


def collect_transcript_data(folder: Path) -> list[TranscriptData]:
    """Collect data from all transcript files in the folder."""
    data = []
    
    md_files = list(folder.glob("*.md"))
    print(f"Found {len(md_files)} transcript files\n")
    
    for filepath in md_files:
        result = parse_transcript_file(filepath)
        if result and result.view_count > 0:
            data.append(result)
    
    print(f"Successfully parsed {len(data)} files with valid view counts\n")
    return data


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def calculate_statistics(data: list[TranscriptData]) -> dict:
    """Calculate various statistics from the transcript data."""
    view_counts = [d.view_count for d in data]
    word_counts = [d.word_count for d in data]
    
    stats = {
        'total_videos': len(data),
        'total_views': sum(view_counts),
        'average_views': np.mean(view_counts),
        'median_views': np.median(view_counts),
        'std_views': np.std(view_counts),
        'min_views': min(view_counts),
        'max_views': max(view_counts),
        'q1_views': np.percentile(view_counts, 25),
        'q3_views': np.percentile(view_counts, 75),
        'average_word_count': np.mean(word_counts),
        'median_word_count': np.median(word_counts),
        'min_word_count': min(word_counts),
        'max_word_count': max(word_counts),
        'q1_word_count': np.percentile(word_counts, 25),
        'q3_word_count': np.percentile(word_counts, 75),
    }
    
    return stats


def print_statistics(stats: dict, data: list[TranscriptData]):
    """Print the statistics summary."""
    print("=" * 60)
    print("CHANNEL STATISTICS")
    print("=" * 60)
    print()
    
    print("[*] VIEW STATISTICS")
    print("-" * 40)
    print(f"  Total Videos:     {stats['total_videos']:,}")
    print(f"  Total Views:      {stats['total_views']:,}")
    print(f"  Average Views:    {stats['average_views']:,.0f}")
    print(f"  Median Views:     {stats['median_views']:,.0f}")
    print(f"  Std Deviation:    {stats['std_views']:,.0f}")
    print(f"  Min Views:        {stats['min_views']:,}")
    print(f"  Max Views:        {stats['max_views']:,}")
    print(f"  Q1 (25th %ile):   {stats['q1_views']:,.0f}")
    print(f"  Q3 (75th %ile):   {stats['q3_views']:,.0f}")
    print()
    
    print("[*] WORD COUNT STATISTICS")
    print("-" * 40)
    print(f"  Average Words:    {stats['average_word_count']:,.0f}")
    print(f"  Median Words:     {stats['median_word_count']:,.0f}")

    
# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_like_view_ratio_histogram_norm(data: list[TranscriptData], output_path: Path):
    """
    Create a histogram of normalized like-to-view ratios.
    Shows Q1, median, Q3, and Q4 as dashed lines.
    """
    # Calculate like-to-view ratios (only for videos with views > 0)
    ratios = []
    for d in data:
        if d.view_count > 0:
            ratio = d.like_count / d.view_count
            ratios.append(ratio)
    
    if not ratios:
        print("  No valid like-to-view ratios to plot.")
        return None
    
    # Calculate average ratio for normalization
    avg_ratio = np.mean(ratios)
    normalized_ratios = [r / avg_ratio if avg_ratio > 0 else 0 for r in ratios]
    
    # Calculate quartiles on normalized data
    q1_normalized = np.percentile(normalized_ratios, 25)
    median_normalized = np.percentile(normalized_ratios, 50)
    q3_normalized = np.percentile(normalized_ratios, 75)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create histogram
    n, bins, patches = ax.hist(
        normalized_ratios, 
        bins=50, 
        edgecolor='white', 
        linewidth=0.5,
        color='#2ecc71',
        alpha=0.7
    )
    
    # Add quartile lines
    ax.axvline(
        q1_normalized, 
        color='orange', 
        linestyle='--', 
        linewidth=2, 
        label=f'Q1 (25th %ile): {q1_normalized:.2f}x'
    )
    ax.axvline(
        q3_normalized, 
        color='gray', 
        linestyle='--', 
        linewidth=2, 
        label=f'Q3 (75th %ile): {q3_normalized:.2f}x'
    )
    
    # Add median line (red dashed)
    ax.axvline(
        median_normalized, 
        color='red', 
        linestyle='--', 
        linewidth=2, 
        label=f'Median: {median_normalized:.2f}x'
    )
    
    # Labels and title
    ax.set_xlabel('Normalized Like-to-View Ratio (Ratio / Average Ratio)', fontsize=12)
    ax.set_ylabel('Number of Videos', fontsize=12)
    ax.set_title(
        f'Distribution of Normalized Like-to-View Ratios\n'
        f'(n={len(ratios):,} videos, avg ratio={avg_ratio:.4f})',
        fontsize=14,
        fontweight='bold'
    )
    
    # Add legend
    ax.legend(loc='upper right', fontsize=10)
    
    # Add grid
    ax.grid(axis='y', alpha=0.3)
    
    # Set x-axis limit to focus on the main distribution
    max_display = min(max(normalized_ratios), 5.0)
    ax.set_xlim(0, max_display + 0.5)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    output_file = output_path / "like_view_ratio_histogram.svg"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"[+] Like-to-View Ratio Histogram saved to: {output_file.absolute()}")
    
    # Show the plot
    plt.show()
    
    return output_file


def create_word_count_histogram(data: list[TranscriptData], stats: dict, output_path: Path):
    """
    Create a histogram of word counts.
    Shows Q1, median, and Q3 as dashed lines.
    """
    # Get word counts
    word_counts = [d.word_count for d in data]
    avg_words = stats['average_word_count']
    
    # Calculate quartiles on raw data
    q1 = np.percentile(word_counts, 25)
    median = np.percentile(word_counts, 50)
    q3 = np.percentile(word_counts, 75)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create histogram
    n, bins, patches = ax.hist(
        word_counts, 
        bins=50, 
        edgecolor='white', 
        linewidth=0.5,
        color='#e74c3c',
        alpha=0.7
    )
    
    # Add quartile lines
    ax.axvline(
        q1, 
        color='orange', 
        linestyle='--', 
        linewidth=2, 
        label=f'Q1 (25th %ile): {q1:,.0f}'
    )
    ax.axvline(
        q3, 
        color='gray', 
        linestyle='--', 
        linewidth=2, 
        label=f'Q3 (75th %ile): {q3:,.0f}'
    )
    
    # Add median line (red dashed)
    ax.axvline(
        median, 
        color='red', 
        linestyle='--', 
        linewidth=2, 
        label=f'Median: {median:,.0f}'
    )
    
    # Labels and title
    ax.set_xlabel('Word Count', fontsize=12)
    ax.set_ylabel('Number of Videos', fontsize=12)
    ax.set_title(
        f'Distribution of Word Counts'
        f'(n={len(data):,} videos, avg words={avg_words:,.0f})',
        fontsize=14,
        fontweight='bold'
    )
    
    # Add legend
    ax.legend(loc='upper right', fontsize=10)
    
    # Add grid
    ax.grid(axis='y', alpha=0.3)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure
    output_file = output_path / "word_count_histogram.svg"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"[+] Word Count Histogram saved to: {output_file.absolute()}")
    
    # Show the plot
    plt.show()
    
    return output_file

def create_like_view_ratio_histogram_raw(data: list[TranscriptData], output_path: Path):
    """
    Create a histogram of raw like-to-view ratios. Not normalized
    Shows Q1, median, and Q3 as dashed lines.
    """
    # Calculate like-to-view ratios
    ratios = [
        d.like_count / d.view_count
        for d in data
        if d.view_count > 0
    ]

    if not ratios:
        print("  No valid like-to-view ratios to plot.")
        return None

    # Calculate statistics
    avg_ratio = np.mean(ratios)
    q1 = np.percentile(ratios, 25)
    median = np.percentile(ratios, 50)
    q3 = np.percentile(ratios, 75)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 7))

    # Histogram
    ax.hist(
        ratios,
        bins=50,
        edgecolor="white",
        linewidth=0.5,
        color="#2ecc71",
        alpha=0.7
    )

    # Quartile & median lines
    ax.axvline(q1, color="orange", linestyle="--", linewidth=2,
               label=f"Q1 (25th %ile): {q1:.4f}")
    ax.axvline(median, color="red", linestyle="--", linewidth=2,
               label=f"Median: {median:.4f}")
    ax.axvline(q3, color="gray", linestyle="--", linewidth=2,
               label=f"Q3 (75th %ile): {q3:.4f}")

    # Labels & title
    ax.set_xlabel("Like-to-View Ratio", fontsize=12)
    ax.set_ylabel("Number of Videos", fontsize=12)
    ax.set_title(
        f"Distribution of Like-to-View Ratios\n"
        f"(n={len(ratios):,} videos, avg ratio={avg_ratio:.4f})",
        fontsize=14,
        fontweight="bold"
    )

    ax.legend(loc="upper right", fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    # Save
    output_file = output_path / "like_view_ratio_histogram_raw.svg"
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"[+] Raw Like-to-View Ratio Histogram saved to: {output_file.absolute()}")

    plt.show()

    return output_file

# =============================================================================
# MAIN FUNCTION
# =============================================================================

def analyze_transcripts(folder: str = "cleaned", output_dir: str = None):
    """Main function to analyze transcripts."""
    folder_path = Path(folder)
    
    if not folder_path.exists():
        print(f"Error: Folder not found: {folder_path.absolute()}")
        sys.exit(1)
    
    # Set output directory (default: current working directory / main folder)
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path(".")  # Main folder instead of input folder
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"[>] Analyzing transcripts in: {folder_path.absolute()}")
    print()
    
    # Collect data
    data = collect_transcript_data(folder_path)
    
    if not data:
        print("No valid transcript files found with view counts.")
        return
    
    # Calculate statistics
    stats = calculate_statistics(data)
    
    # Print statistics
    print_statistics(stats, data)
    

    # Create histogram
    print("[>] Creating histograms...")
    create_like_view_ratio_histogram_norm(data, output_path)
    create_word_count_histogram(data, stats, output_path)
    create_like_view_ratio_histogram_raw(data, output_path)


# =============================================================================
# COMMAND-LINE INTERFACE
# =============================================================================

def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Analyze YouTube transcript files for statistics and visualizations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_transcripts.py
  python analyze_transcripts.py cleaned
  python analyze_transcripts.py transcripts --output reports
        """
    )
    
    parser.add_argument(
        "folder",
        nargs="?",
        default="cleaned",
        help="Folder containing transcript files (default: cleaned)"
    )
    
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output directory for generated files (default: same as input folder)"
    )
    
    args = parser.parse_args()
    
    analyze_transcripts(folder=args.folder, output_dir=args.output)


if __name__ == "__main__":
    main()
