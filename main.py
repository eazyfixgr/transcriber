import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import threading
import time
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import queue
import tempfile

# Try importing optional dependencies
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("Whisper not installed. Transcription features will be limited.")

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("Pynput not installed. Global hotkeys will not work.")

try:
    from pydub import AudioSegment
    from pydub.utils import which
    PYDUB_AVAILABLE = True

    # Check if FFmpeg is available
    ffmpeg_path = which("ffmpeg")
    if ffmpeg_path:
        print(f"✓ FFmpeg found at: {ffmpeg_path}")
    else:
        print("⚠ WARNING: FFmpeg not found in PATH!")
        print("  M4A/MP4 files may not work properly.")
        print("  Install with: choco install ffmpeg-full")

except ImportError:
    PYDUB_AVAILABLE = False
    print("⚠ Pydub not installed. Live transcription will be slower.")
    print("  M4A/MP4 files will NOT work without pydub.")
    print("  Install with: pip install pydub")


class AudioPlayer:
    """Handles audio playback with speed control"""

    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.current_file = None
        self.is_playing = False
        self.is_paused = False
        self.playback_speed = 1.0
        self.volume = 0.7
        self.position = 0
        self.duration = 0
        self.pause_position = 0  # Store position when paused
        self.temp_converted_file = None  # Store temp file path

    def load_file(self, filepath):
        """Load an audio file (with auto-conversion for unsupported formats)"""
        try:
            # Check if file needs conversion (m4a, mp4, etc)
            file_ext = os.path.splitext(filepath)[1].lower()
            needs_conversion = file_ext in ['.m4a', '.mp4', '.aac', '.flac']

            print(f"Loading file: {filepath}")
            print(f"File extension: {file_ext}")
            print(f"Needs conversion: {needs_conversion}")
            print(f"PYDUB_AVAILABLE: {PYDUB_AVAILABLE}")

            if needs_conversion:
                if not PYDUB_AVAILABLE:
                    print("ERROR: Pydub not available!")
                    raise Exception(f"Format {file_ext} requires pydub. Install with: pip install pydub")

                # Convert to WAV temporarily
                print(f"Converting {file_ext} to WAV for playback...")
                converted_file = self.convert_to_wav(filepath)
                if converted_file:
                    filepath_to_load = converted_file
                    self.temp_converted_file = converted_file
                    print(f"Conversion successful: {converted_file}")
                else:
                    print("ERROR: Conversion failed!")
                    raise Exception("Audio conversion failed. Make sure FFmpeg is installed.")
            else:
                filepath_to_load = filepath
                self.temp_converted_file = None

            # Load the audio file
            print(f"Loading into pygame: {filepath_to_load}")
            pygame.mixer.music.load(filepath_to_load)
            self.current_file = filepath  # Keep original filepath

            # Get duration - use a different method for large files
            try:
                # Try to get duration from Sound (works for smaller files)
                sound = pygame.mixer.Sound(filepath_to_load)
                self.duration = sound.get_length()
            except:
                # Fallback: use pydub to get duration
                if PYDUB_AVAILABLE:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(filepath_to_load)
                    self.duration = len(audio) / 1000.0  # Convert ms to seconds
                else:
                    # Worst case: estimate based on file size (rough estimate)
                    file_size = os.path.getsize(filepath_to_load)
                    # Assume ~1MB per minute for WAV (very rough)
                    self.duration = (file_size / 1024 / 1024) * 60
                    print(f"Warning: Using estimated duration: {self.duration}s")

            pygame.mixer.music.set_volume(self.volume)
            print(f"File loaded successfully! Duration: {self.duration}s")
            return True

        except Exception as e:
            print(f"ERROR loading file: {e}")
            import traceback
            traceback.print_exc()
            # Clean up temp file if exists
            if hasattr(self, 'temp_converted_file') and self.temp_converted_file and os.path.exists(self.temp_converted_file):
                try:
                    os.remove(self.temp_converted_file)
                except:
                    pass
            return False

    def convert_to_wav(self, filepath):
        """Convert audio file to WAV format"""
        try:
            from pydub import AudioSegment
            from pydub.utils import which

            # Check if ffmpeg is available
            ffmpeg_path = which("ffmpeg")
            if not ffmpeg_path:
                print("WARNING: FFmpeg not found in PATH!")
                print("Trying to load anyway...")
            else:
                print(f"FFmpeg found at: {ffmpeg_path}")

            print(f"Loading audio file: {filepath}")
            # Load audio file
            audio = AudioSegment.from_file(filepath)
            print(f"Audio loaded! Duration: {len(audio)/1000.0}s, Channels: {audio.channels}, Sample rate: {audio.frame_rate}")

            # Create temp WAV file
            temp_dir = tempfile.gettempdir()
            temp_filename = f"transcriber_temp_{int(time.time())}.wav"
            temp_path = os.path.join(temp_dir, temp_filename)

            print(f"Exporting to WAV: {temp_path}")
            # Export as WAV with specific parameters
            audio.export(
                temp_path,
                format="wav",
                parameters=["-ar", "44100", "-ac", "2"]  # 44.1kHz, stereo
            )

            if os.path.exists(temp_path):
                file_size = os.path.getsize(temp_path) / (1024 * 1024)  # MB
                print(f"Conversion successful! File size: {file_size:.2f} MB")
                return temp_path
            else:
                print("ERROR: Converted file does not exist!")
                return None

        except Exception as e:
            print(f"Conversion error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def cleanup_temp_file(self):
        """Clean up temporary converted file"""
        if self.temp_converted_file and os.path.exists(self.temp_converted_file):
            try:
                os.remove(self.temp_converted_file)
                self.temp_converted_file = None
            except Exception as e:
                print(f"Error cleaning up temp file: {e}")

    def play(self, rewind_seconds=0):
        """Start or resume playback with optional rewind"""
        if self.is_paused:
            # Resume from position with rewind
            resume_position = max(0, self.pause_position - rewind_seconds)
            pygame.mixer.music.play(start=resume_position)
            self.is_paused = False
        else:
            pygame.mixer.music.play()
        self.is_playing = True

    def pause(self):
        """Pause playback and store current position"""
        if self.is_playing:
            # Store current position before pausing
            self.pause_position = self.get_position()
            pygame.mixer.music.pause()
            self.is_paused = True
            self.is_playing = False

    def stop(self):
        """Stop playback"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        # Clean up temp file if exists
        self.cleanup_temp_file()

    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)

    def get_position(self):
        """Get current playback position in seconds"""
        if self.current_file:
            return pygame.mixer.music.get_pos() / 1000.0
        return 0

    def set_position(self, position):
        """Set playback position in seconds"""
        if self.current_file:
            pygame.mixer.music.play(start=position)
            if not self.is_playing:
                pygame.mixer.music.pause()
                self.is_paused = True


class TranscriberApp:
    """Main FTW Transcriber Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("FTW Transcriber - Full Version")
        self.root.geometry("1200x900")

        # Color scheme matching FTW Transcriber
        self.colors = {
            'primary': '#f6861f',
            'secondary': '#ffd204',
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'button': '#3c3c3c',
            'button_hover': '#4c4c4c'
        }

        self.root.configure(bg=self.colors['bg'])

        # Initialize components
        self.player = AudioPlayer()
        self.current_file = None
        self.bookmarks = []
        self.settings = self.load_settings()
        self.transcription_queue = queue.Queue()

        # Transcription model
        self.whisper_model = None
        if WHISPER_AVAILABLE:
            threading.Thread(target=self.load_whisper_model, daemon=True).start()

        # Create UI
        self.create_menu()
        self.create_widgets()

        # Start position update loop
        self.update_position()

        # Setup hotkeys
        if PYNPUT_AVAILABLE:
            self.setup_hotkeys()

    def load_whisper_model(self):
        """Load Whisper model in background"""
        try:
            print("Loading Whisper model...")
            self.whisper_model = whisper.load_model("base")
            print("Whisper model loaded!")
        except Exception as e:
            print(f"Error loading Whisper model: {e}")

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Audio File", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Playback menu
        playback_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Playback", menu=playback_menu)
        playback_menu.add_command(label="Play/Pause", command=self.toggle_play)
        playback_menu.add_command(label="Stop", command=self.stop_playback)
        playback_menu.add_separator()
        playback_menu.add_command(label="Skip Forward 5s", command=lambda: self.skip(5))
        playback_menu.add_command(label="Skip Backward 5s", command=lambda: self.skip(-5))

        # Transcription menu
        transcribe_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Transcribe", menu=transcribe_menu)
        transcribe_menu.add_command(label="Start Transcription", command=self.start_transcription)
        transcribe_menu.add_command(label="Add Timestamp", command=self.add_timestamp)
        transcribe_menu.add_command(label="Add Bookmark", command=self.add_bookmark)

        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Configure Hotkeys", command=self.configure_hotkeys)
        settings_menu.add_command(label="Timestamp Format", command=self.configure_timestamp_format)
        settings_menu.add_command(label="Rewind on Resume", command=self.configure_rewind_on_resume)

    def create_widgets(self):
        """Create main UI widgets"""
        # Top frame - File info
        top_frame = tk.Frame(self.root, bg=self.colors['bg'])
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top_frame, text="Current File:", bg=self.colors['bg'], fg=self.colors['fg'], font=('Arial', 10, 'bold')).pack(anchor='w')
        self.file_label = tk.Label(top_frame, text="No file loaded", bg=self.colors['bg'], fg=self.colors['secondary'], font=('Arial', 9))
        self.file_label.pack(anchor='w', pady=5)

        # Open file button
        open_btn = tk.Button(top_frame, text="Open Audio File", command=self.open_file,
                            bg=self.colors['primary'], fg=self.colors['fg'],
                            font=('Arial', 10, 'bold'), cursor='hand2')
        open_btn.pack(pady=5)

        # Player controls frame
        player_frame = tk.Frame(self.root, bg=self.colors['button'], relief=tk.RAISED, bd=2)
        player_frame.pack(fill=tk.X, padx=10, pady=10)

        # Time display
        time_frame = tk.Frame(player_frame, bg=self.colors['button'])
        time_frame.pack(fill=tk.X, padx=10, pady=5)

        self.time_label = tk.Label(time_frame, text="00:00 / 00:00", bg=self.colors['button'],
                                   fg=self.colors['fg'], font=('Arial', 12, 'bold'))
        self.time_label.pack()

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(player_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                     variable=self.progress_var, command=self.on_progress_change)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        # Control buttons
        controls_frame = tk.Frame(player_frame, bg=self.colors['button'])
        controls_frame.pack(pady=10)

        # Skip backward button
        btn_skip_back = tk.Button(controls_frame, text="⏪ -5s", command=lambda: self.skip(-5),
                                 bg=self.colors['primary'], fg=self.colors['fg'],
                                 font=('Arial', 10, 'bold'), width=8)
        btn_skip_back.grid(row=0, column=0, padx=5)

        # Play/Pause button
        self.play_btn = tk.Button(controls_frame, text="▶ Play", command=self.toggle_play,
                                 bg=self.colors['primary'], fg=self.colors['fg'],
                                 font=('Arial', 12, 'bold'), width=10)
        self.play_btn.grid(row=0, column=1, padx=5)

        # Skip forward button
        btn_skip_forward = tk.Button(controls_frame, text="+5s ⏩", command=lambda: self.skip(5),
                                    bg=self.colors['primary'], fg=self.colors['fg'],
                                    font=('Arial', 10, 'bold'), width=8)
        btn_skip_forward.grid(row=0, column=2, padx=5)

        # Stop button
        btn_stop = tk.Button(controls_frame, text="⏹ Stop", command=self.stop_playback,
                           bg=self.colors['button_hover'], fg=self.colors['fg'],
                           font=('Arial', 10), width=8)
        btn_stop.grid(row=0, column=3, padx=5)

        # Speed and volume controls
        controls2_frame = tk.Frame(player_frame, bg=self.colors['button'])
        controls2_frame.pack(pady=5)

        # Speed control
        tk.Label(controls2_frame, text="Speed:", bg=self.colors['button'],
                fg=self.colors['fg'], font=('Arial', 9)).grid(row=0, column=0, padx=5)

        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(controls2_frame, from_=0.5, to=2.0, orient=tk.HORIZONTAL,
                               variable=self.speed_var, command=self.on_speed_change, length=150)
        speed_scale.grid(row=0, column=1, padx=5)

        self.speed_label = tk.Label(controls2_frame, text="1.0x", bg=self.colors['button'],
                                   fg=self.colors['secondary'], font=('Arial', 9, 'bold'))
        self.speed_label.grid(row=0, column=2, padx=5)

        # Volume control
        tk.Label(controls2_frame, text="Volume:", bg=self.colors['button'],
                fg=self.colors['fg'], font=('Arial', 9)).grid(row=1, column=0, padx=5, pady=5)

        self.volume_var = tk.DoubleVar(value=70)
        volume_scale = ttk.Scale(controls2_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                variable=self.volume_var, command=self.on_volume_change, length=150)
        volume_scale.grid(row=1, column=1, padx=5, pady=5)

        self.volume_label = tk.Label(controls2_frame, text="70%", bg=self.colors['button'],
                                    fg=self.colors['secondary'], font=('Arial', 9, 'bold'))
        self.volume_label.grid(row=1, column=2, padx=5, pady=5)

        # Transcription controls frame
        transcribe_frame = tk.Frame(self.root, bg=self.colors['bg'])
        transcribe_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(transcribe_frame, text="Transcription:", bg=self.colors['bg'],
                fg=self.colors['fg'], font=('Arial', 10, 'bold')).pack(anchor='w')

        # Transcription buttons
        btn_frame = tk.Frame(transcribe_frame, bg=self.colors['bg'])
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Start Transcription", command=self.start_transcription,
                 bg=self.colors['primary'], fg=self.colors['fg'], font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Add Timestamp", command=self.add_timestamp,
                 bg=self.colors['secondary'], fg=self.colors['bg'], font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Add Bookmark", command=self.add_bookmark,
                 bg=self.colors['button_hover'], fg=self.colors['fg'], font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

        # Transcription text area
        self.transcription_text = tk.Text(transcribe_frame, height=10, wrap=tk.WORD,
                                         bg='#1e1e1e', fg=self.colors['fg'],
                                         font=('Courier', 10), insertbackground=self.colors['secondary'])
        self.transcription_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.transcription_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.transcription_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.transcription_text.yview)

        # Setup context menu for transcription text
        self.setup_transcription_context_menu()

        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready | No time limit - Full Version",
                                  bg=self.colors['button'], fg=self.colors['secondary'],
                                  font=('Arial', 9), anchor='w')
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def open_file(self):
        """Open audio file dialog"""
        filetypes = [
            ("Audio/Video Files", "*.mp3 *.wav *.ogg *.flac *.m4a *.mp4"),
            ("All Files", "*.*")
        ]

        filepath = filedialog.askopenfilename(title="Select Audio File", filetypes=filetypes)

        if filepath:
            # Show loading status
            filename = os.path.basename(filepath)
            self.status_bar.config(text=f"Loading: {filename}...")
            self.root.update()

            if self.player.load_file(filepath):
                self.current_file = filepath
                self.file_label.config(text=filename)
                self.status_bar.config(text=f"Loaded: {filename}")
                messagebox.showinfo("Success", f"File loaded successfully!\n{filename}")
            else:
                file_ext = os.path.splitext(filepath)[1].lower()
                error_msg = f"Failed to load audio file: {filename}"

                if file_ext in ['.m4a', '.mp4', '.aac', '.flac']:
                    if not PYDUB_AVAILABLE:
                        error_msg += f"\n\n❌ Pydub is not installed!"
                        error_msg += f"\n\nFormat {file_ext} requires pydub."
                        error_msg += "\n\nInstall with: pip install pydub"
                    else:
                        error_msg += f"\n\n⚠ Conversion failed!"
                        error_msg += "\n\nMake sure FFmpeg is installed and in your PATH."
                        error_msg += "\n\nYou can install FFmpeg with:"
                        error_msg += "\n  choco install ffmpeg-full"
                        error_msg += "\n\nOr download from: https://ffmpeg.org/download.html"

                    error_msg += f"\n\n💡 Check the console for detailed error messages."

                messagebox.showerror("Error", error_msg)
                self.status_bar.config(text="Failed to load file")

    def toggle_play(self):
        """Toggle play/pause"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please open an audio file first")
            return

        if self.player.is_playing:
            self.player.pause()
            self.play_btn.config(text="▶ Play")
            self.status_bar.config(text="Paused")
        else:
            # Check if we're resuming from pause
            was_paused = self.player.is_paused
            rewind_seconds = self.settings.get('rewind_on_resume', 4)

            # Resume with rewind (if was paused), otherwise start fresh
            self.player.play(rewind_seconds=rewind_seconds if was_paused else 0)
            self.play_btn.config(text="⏸ Pause")

            # Show rewind message if applicable
            if was_paused and rewind_seconds > 0:
                self.status_bar.config(text=f"Playing... (rewound {rewind_seconds}s)")
            else:
                self.status_bar.config(text="Playing...")

    def stop_playback(self):
        """Stop playback"""
        self.player.stop()
        self.play_btn.config(text="▶ Play")
        self.status_bar.config(text="Stopped")

    def skip(self, seconds):
        """Skip forward or backward"""
        if not self.current_file:
            return

        current_pos = self.player.get_position()
        new_pos = max(0, min(self.player.duration, current_pos + seconds))
        self.player.set_position(new_pos)

    def on_speed_change(self, value):
        """Handle speed slider change"""
        speed = float(value)
        self.speed_label.config(text=f"{speed:.1f}x")
        self.player.playback_speed = speed
        # Note: pygame.mixer doesn't support speed change natively
        # This would require additional implementation with pydub or soundstretch

    def on_volume_change(self, value):
        """Handle volume slider change"""
        volume = float(value)
        self.volume_label.config(text=f"{int(volume)}%")
        self.player.set_volume(volume / 100.0)

    def on_progress_change(self, value):
        """Handle progress bar change"""
        if not self.current_file:
            return

        position = (float(value) / 100.0) * self.player.duration
        self.player.set_position(position)

    def update_position(self):
        """Update position display and progress bar"""
        if self.current_file and self.player.is_playing:
            position = self.player.get_position()
            duration = self.player.duration

            # Update time label
            pos_str = self.format_time(position)
            dur_str = self.format_time(duration)
            self.time_label.config(text=f"{pos_str} / {dur_str}")

            # Update progress bar
            if duration > 0:
                progress = (position / duration) * 100
                self.progress_var.set(progress)

        # Schedule next update
        self.root.after(100, self.update_position)

    def format_time(self, seconds):
        """Format seconds to MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def add_timestamp(self):
        """Add timestamp at current position"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please open an audio file first")
            return

        position = self.player.get_position()
        timestamp_format = self.settings.get('timestamp_format', 'MM:SS')

        if timestamp_format == 'MM:SS':
            timestamp = self.format_time(position)
        elif timestamp_format == 'HH:MM:SS':
            hours = int(position // 3600)
            minutes = int((position % 3600) // 60)
            secs = int(position % 60)
            timestamp = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            timestamp = f"{position:.2f}s"

        self.transcription_text.insert(tk.END, f"[{timestamp}] ")
        self.status_bar.config(text=f"Timestamp added: {timestamp}")

    def add_bookmark(self):
        """Add bookmark at current position"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please open an audio file first")
            return

        position = self.player.get_position()
        timestamp = self.format_time(position)

        # Ask for bookmark name
        name = tk.simpledialog.askstring("Bookmark", "Enter bookmark name:",
                                        initialvalue=f"Bookmark {len(self.bookmarks) + 1}")

        if name:
            self.bookmarks.append({'name': name, 'position': position})
            self.transcription_text.insert(tk.END, f"\n*** BOOKMARK: {name} [{timestamp}] ***\n")
            self.status_bar.config(text=f"Bookmark added: {name}")

    def start_transcription(self):
        """Start automatic transcription"""
        if not self.current_file:
            messagebox.showwarning("No File", "Please open an audio file first")
            return

        if not WHISPER_AVAILABLE:
            messagebox.showerror("Error", "Whisper is not installed.\nInstall with: pip install openai-whisper")
            return

        if self.whisper_model is None:
            messagebox.showinfo("Loading", "Whisper model is still loading. Please wait...")
            return

        # Ask user to confirm
        result = messagebox.askyesno("Start Transcription",
                                     "This will transcribe the entire audio file.\nThis may take several minutes.\n\nContinue?")

        if result:
            # Clear existing transcription
            self.transcription_text.delete(1.0, tk.END)
            self.status_bar.config(text="Transcribing... (live updates below)")
            threading.Thread(target=self.transcribe_audio, daemon=True).start()

    def transcribe_audio(self):
        """Transcribe audio file using Whisper with live updates"""
        try:
            # Try chunking for true live updates
            if PYDUB_AVAILABLE:
                self.transcribe_audio_chunked()
            else:
                self.transcribe_audio_simple()

        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Transcription failed:\n{error_msg}"))
            self.root.after(0, lambda: self.status_bar.config(text="Transcription failed"))

    def transcribe_audio_chunked(self):
        """Transcribe audio in chunks for true live updates"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(self.current_file)
            duration_ms = len(audio)
            chunk_size_ms = 30000  # 30 seconds chunks

            total_chunks = (duration_ms + chunk_size_ms - 1) // chunk_size_ms
            temp_dir = tempfile.mkdtemp()

            current_time = 0

            for chunk_idx in range(total_chunks):
                # Extract chunk
                start_ms = chunk_idx * chunk_size_ms
                end_ms = min((chunk_idx + 1) * chunk_size_ms, duration_ms)
                chunk = audio[start_ms:end_ms]

                # Save chunk to temporary file
                chunk_file = os.path.join(temp_dir, f"chunk_{chunk_idx}.wav")
                chunk.export(chunk_file, format="wav")

                # Update status
                progress = f"Transcribing... chunk {chunk_idx + 1}/{total_chunks}"
                self.root.after(0, lambda p=progress: self.status_bar.config(text=p))

                # Transcribe chunk
                result = self.whisper_model.transcribe(chunk_file, verbose=False)

                # Display results immediately
                for segment in result['segments']:
                    # Adjust timestamp to account for chunk offset
                    actual_time = current_time + segment['start']
                    start_time = self.format_time(actual_time)
                    text = segment['text'].strip()
                    line = f"[{start_time}] {text}\n"

                    # Update UI from main thread (live update!)
                    self.root.after(0, lambda l=line: self.append_transcription_line(l))

                # Clean up chunk file
                try:
                    os.remove(chunk_file)
                except:
                    pass

                current_time += (end_ms - start_ms) / 1000.0

            # Clean up temp directory
            try:
                os.rmdir(temp_dir)
            except:
                pass

            # Transcription complete
            self.root.after(0, lambda: self.status_bar.config(text="Transcription complete! ✓"))
            self.root.after(0, lambda: messagebox.showinfo("Success", "Transcription completed successfully!"))

        except Exception as e:
            raise e

    def transcribe_audio_simple(self):
        """Simple transcription (fallback when pydub not available)"""
        try:
            # Transcribe with verbose=False to avoid console spam
            result = self.whisper_model.transcribe(self.current_file, verbose=False)

            # Process segments one by one and update UI
            total_segments = len(result['segments'])
            for idx, segment in enumerate(result['segments'], 1):
                start_time = self.format_time(segment['start'])
                text = segment['text'].strip()
                line = f"[{start_time}] {text}\n"

                # Update UI from main thread
                self.root.after(0, lambda l=line: self.append_transcription_line(l))

                # Update status with progress
                progress = f"Processing... {idx}/{total_segments} segments"
                self.root.after(0, lambda p=progress: self.status_bar.config(text=p))

            # Transcription complete
            self.root.after(0, lambda: self.status_bar.config(text="Transcription complete! ✓"))
            self.root.after(0, lambda: messagebox.showinfo("Success", "Transcription completed successfully!"))

        except Exception as e:
            raise e

    def append_transcription_line(self, line):
        """Append a line to transcription text (called from main thread)"""
        self.transcription_text.insert(tk.END, line)
        # Auto-scroll to bottom to show latest transcription
        self.transcription_text.see(tk.END)
        # Make sure text is editable so user can correct mistakes immediately
        self.transcription_text.config(state=tk.NORMAL)

    def setup_transcription_context_menu(self):
        """Setup right-click context menu for transcription text"""
        # Create context menu
        self.transcription_menu = tk.Menu(self.transcription_text, tearoff=0,
                                         bg=self.colors['button'], fg=self.colors['fg'],
                                         activebackground=self.colors['primary'])

        self.transcription_menu.add_command(label="Cut", accelerator="Ctrl+X",
                                           command=self.transcription_cut)
        self.transcription_menu.add_command(label="Copy", accelerator="Ctrl+C",
                                           command=self.transcription_copy)
        self.transcription_menu.add_command(label="Paste", accelerator="Ctrl+V",
                                           command=self.transcription_paste)
        self.transcription_menu.add_separator()
        self.transcription_menu.add_command(label="Select All", accelerator="Ctrl+A",
                                           command=self.transcription_select_all)
        self.transcription_menu.add_separator()
        self.transcription_menu.add_command(label="Clear All", command=self.transcription_clear)

        # Bind right-click to show menu
        self.transcription_text.bind("<Button-3>", self.show_transcription_menu)

        # Bind keyboard shortcuts
        self.transcription_text.bind("<Control-x>", lambda e: self.transcription_cut())
        self.transcription_text.bind("<Control-c>", lambda e: self.transcription_copy())
        self.transcription_text.bind("<Control-v>", lambda e: self.transcription_paste())
        self.transcription_text.bind("<Control-a>", lambda e: self.transcription_select_all())

    def show_transcription_menu(self, event):
        """Show context menu at cursor position"""
        try:
            self.transcription_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.transcription_menu.grab_release()

    def transcription_cut(self):
        """Cut text from transcription"""
        try:
            self.transcription_text.event_generate("<<Cut>>")
        except:
            pass
        return "break"

    def transcription_copy(self):
        """Copy text from transcription"""
        try:
            self.transcription_text.event_generate("<<Copy>>")
        except:
            pass
        return "break"

    def transcription_paste(self):
        """Paste text to transcription"""
        try:
            self.transcription_text.event_generate("<<Paste>>")
        except:
            pass
        return "break"

    def transcription_select_all(self):
        """Select all text in transcription"""
        try:
            self.transcription_text.tag_add("sel", "1.0", "end")
            self.transcription_text.mark_set("insert", "1.0")
            self.transcription_text.see("insert")
        except:
            pass
        return "break"

    def transcription_clear(self):
        """Clear all transcription text"""
        if messagebox.askyesno("Clear All", "Are you sure you want to clear all transcription text?"):
            self.transcription_text.delete(1.0, tk.END)

    def display_transcription(self, transcription):
        """Display transcription in text area"""
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.insert(1.0, transcription)
        self.status_bar.config(text="Transcription complete!")
        messagebox.showinfo("Success", "Transcription completed successfully!")

    def configure_hotkeys(self):
        """Configure hotkey settings"""
        # Create settings dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Hotkeys")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['bg'])

        tk.Label(dialog, text="Hotkey Settings", bg=self.colors['bg'],
                fg=self.colors['fg'], font=('Arial', 12, 'bold')).pack(pady=10)

        tk.Label(dialog, text="Global hotkeys allow you to control playback\neven when the window is not focused.",
                bg=self.colors['bg'], fg=self.colors['fg']).pack(pady=10)

        if not PYNPUT_AVAILABLE:
            tk.Label(dialog, text="⚠ Pynput not installed\nInstall with: pip install pynput",
                    bg=self.colors['bg'], fg='red', font=('Arial', 10)).pack(pady=10)

        # Default hotkeys info
        hotkeys_frame = tk.Frame(dialog, bg=self.colors['button'], relief=tk.RAISED, bd=2)
        hotkeys_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(hotkeys_frame, text="Default Hotkeys:", bg=self.colors['button'],
                fg=self.colors['secondary'], font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=5)

        hotkeys_info = [
            "F9 - Play/Pause",
            "F10 - Stop",
            "F11 - Skip Backward 5s",
            "F12 - Skip Forward 5s",
            "Ctrl+T - Add Timestamp"
        ]

        for hotkey in hotkeys_info:
            tk.Label(hotkeys_frame, text=hotkey, bg=self.colors['button'],
                    fg=self.colors['fg'], font=('Arial', 9)).pack(anchor='w', padx=20, pady=2)

        tk.Button(dialog, text="Close", command=dialog.destroy,
                 bg=self.colors['primary'], fg=self.colors['fg']).pack(pady=10)

    def configure_timestamp_format(self):
        """Configure timestamp format"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Timestamp Format")
        dialog.geometry("300x200")
        dialog.configure(bg=self.colors['bg'])

        tk.Label(dialog, text="Select Timestamp Format:", bg=self.colors['bg'],
                fg=self.colors['fg'], font=('Arial', 10, 'bold')).pack(pady=10)

        format_var = tk.StringVar(value=self.settings.get('timestamp_format', 'MM:SS'))

        formats = [
            ("MM:SS", "MM:SS"),
            ("HH:MM:SS", "HH:MM:SS"),
            ("Seconds", "seconds")
        ]

        for text, value in formats:
            tk.Radiobutton(dialog, text=text, variable=format_var, value=value,
                          bg=self.colors['bg'], fg=self.colors['fg'],
                          selectcolor=self.colors['button'],
                          font=('Arial', 10)).pack(anchor='w', padx=30, pady=5)

        def save_format():
            self.settings['timestamp_format'] = format_var.get()
            self.save_settings()
            dialog.destroy()
            messagebox.showinfo("Saved", f"Timestamp format set to: {format_var.get()}")

        tk.Button(dialog, text="Save", command=save_format,
                 bg=self.colors['primary'], fg=self.colors['fg']).pack(pady=10)

    def configure_rewind_on_resume(self):
        """Configure rewind on resume feature"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Rewind on Resume")
        dialog.geometry("400x350")
        dialog.configure(bg=self.colors['bg'])

        tk.Label(dialog, text="Rewind on Resume Settings", bg=self.colors['bg'],
                fg=self.colors['fg'], font=('Arial', 12, 'bold')).pack(pady=10)

        tk.Label(dialog, text="When you pause and then resume playback,\nthe audio will rewind by this many seconds.\nThis helps you catch the context you were transcribing.",
                bg=self.colors['bg'], fg=self.colors['fg'],
                font=('Arial', 9), justify='center').pack(pady=10)

        rewind_var = tk.IntVar(value=self.settings.get('rewind_on_resume', 4))

        # Rewind options frame
        options_frame = tk.Frame(dialog, bg=self.colors['button'], relief=tk.RAISED, bd=2)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(options_frame, text="Select rewind time:", bg=self.colors['button'],
                fg=self.colors['secondary'], font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=10)

        rewind_options = [
            (0, "0 seconds (no rewind)"),
            (2, "2 seconds"),
            (4, "4 seconds (recommended)"),
            (6, "6 seconds"),
            (8, "8 seconds"),
            (10, "10 seconds")
        ]

        for value, text in rewind_options:
            tk.Radiobutton(options_frame, text=text, variable=rewind_var, value=value,
                          bg=self.colors['button'], fg=self.colors['fg'],
                          selectcolor=self.colors['bg'],
                          font=('Arial', 10)).pack(anchor='w', padx=30, pady=3)

        def save_rewind():
            self.settings['rewind_on_resume'] = rewind_var.get()
            self.save_settings()
            dialog.destroy()
            messagebox.showinfo("Saved", f"Rewind on resume set to: {rewind_var.get()} seconds")

        tk.Button(dialog, text="Save", command=save_rewind,
                 bg=self.colors['primary'], fg=self.colors['fg'],
                 font=('Arial', 10, 'bold')).pack(pady=10)

    def setup_hotkeys(self):
        """Setup global hotkeys"""
        def on_press(key):
            try:
                if key == keyboard.Key.f9:
                    self.root.after(0, self.toggle_play)
                elif key == keyboard.Key.f10:
                    self.root.after(0, self.stop_playback)
                elif key == keyboard.Key.f11:
                    self.root.after(0, lambda: self.skip(-5))
                elif key == keyboard.Key.f12:
                    self.root.after(0, lambda: self.skip(5))
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def load_settings(self):
        """Load settings from file"""
        settings_file = Path("transcriber_settings.json")
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'timestamp_format': 'MM:SS',
            'rewind_on_resume': 4  # Default 4 seconds rewind on resume
        }

    def save_settings(self):
        """Save settings to file"""
        settings_file = Path("transcriber_settings.json")
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")


def main():
    """Main entry point"""
    root = tk.Tk()

    # Set icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass

    app = TranscriberApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
