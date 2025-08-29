import os
import subprocess
import json
import shutil
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich import print as rprint
import pyfiglet
import typer

app = typer.Typer(help="VidTally: Tally durations of MP4 videos in a folder.")

console = Console()

def get_video_duration(file_path: str) -> tuple[float, str]:
    """
    Get the duration of a video file using ffprobe.
    Returns duration in seconds as a float and formatted HH:MM:SS string.
    """
    if not shutil.which('ffprobe'):
        raise FileNotFoundError(
            "ffprobe not found in your system PATH. This tool requires ffmpeg to be installed.\n"
            "Installation instructions:\n"
            "- macOS: brew install ffmpeg\n"
            "- Windows: Download from https://ffmpeg.org/download.html and add to PATH\n"
            "- Linux (Ubuntu): sudo apt install ffmpeg\n"
            "See README.md for more details."
        )

    try:
        cmd = [
            'ffprobe', 
            '-v', 'quiet', 
            '-print_format', 'json', 
            '-show_format', 
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        duration_seconds = float(data['format']['duration'])
        
        hours = int(duration_seconds // 3600)
        minutes = int((duration_seconds % 3600) // 60)
        seconds = int(duration_seconds % 60)
        
        formatted_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        return duration_seconds, formatted_duration
    
    except (subprocess.SubprocessError, KeyError, json.JSONDecodeError) as e:
        rprint(f"[red]Error processing {os.path.basename(file_path)}: {str(e)}[/red]")
        return 0, "00:00:00"

def format_total_duration(total_seconds: float) -> str:
    """
    Format total seconds to HH:MM:SS
    """
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@app.command()
def tally(folder_path: str = typer.Argument(..., help="Path to the folder containing MP4 files")):
    # Display banner
    banner = pyfiglet.figlet_format("VidTally", font="slant")
    console.print(banner, style="bold green")

    if not os.path.isdir(folder_path):
        rprint(f"[red]Error: Folder '{folder_path}' does not exist[/red]")
        raise typer.Exit(code=1)
    
    mp4_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')]
    
    if not mp4_files:
        rprint(f"[yellow]No MP4 files found in '{folder_path}'[/yellow]")
        raise typer.Exit(code=0)
    
    rprint(f"[cyan]Found {len(mp4_files)} MP4 files. Tallying durations...[/cyan]")
    
    table = Table(title="Video Durations", show_header=True, header_style="bold magenta")
    table.add_column("File Prefix", style="dim", width=12)
    table.add_column("Duration", justify="right")
    
    total_seconds = 0
    sorted_files = sorted(mp4_files)
    
    for file_name in track(sorted_files, description="Processing..."):
        file_path = os.path.join(folder_path, file_name)
        seconds, formatted_duration = get_video_duration(file_path)
        total_seconds += seconds
        name = file_name[:3]  # Adjust as needed
        table.add_row(name, formatted_duration)
    
    console.print(table)
    
    rprint("[bold green]Total Duration:[/bold green] " + format_total_duration(total_seconds))

if __name__ == "__main__":
    app()