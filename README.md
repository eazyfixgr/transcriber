# FTW Transcriber (Lite)

A lightweight desktop workspace for transcription work: audio playback, bookmarks and timestamps — **without** the heavy speech-to-text engine.

> **Download:** grab the latest `Transcriber.exe` from the [Releases](https://github.com/eazyfixgr/transcriber/releases) page. No installation required.

## Why "Lite"?

The full version bundled Whisper (speech-to-text) which made the app very large (hundreds of MB). This Lite build removes the speech-to-text engine, so the executable is only ~19 MB and starts instantly. It is intended for manual transcription: you listen and type in your own editor while using precise playback control.

## Features

- Audio playback for MP3, WAV, OGG, FLAC, M4A
- Play / Pause / Stop controls
- Variable playback speed (0.5x – 2.0x)
- Skip forward/backward (5 seconds)
- Progress bar and precise time display
- Bookmarks and timestamps
- Global hotkeys (pynput)

## Getting started (run from source)

```bash
python -m pip install -r requirements.txt
python main.py
```

## Build a standalone EXE

```bash
python -m pip install pyinstaller
python -m PyInstaller --onefile --windowed --name Transcriber ^
  --exclude-module whisper --exclude-module torch ^
  --exclude-module torchaudio --exclude-module numpy main.py
```

The executable is created in `dist/Transcriber.exe`.

## License

Released under the [MIT License](LICENSE).

---

# FTW Transcriber (Lite) — Ελληνικά

Ελαφριά εφαρμογή για απομαγνητοφώνηση: αναπαραγωγή ήχου, bookmarks και χρονικές σημάνσεις — **χωρίς** τη βαριά μηχανή speech-to-text.

> **Λήψη:** κατεβάστε το `Transcriber.exe` από τη σελίδα [Releases](https://github.com/eazyfixgr/transcriber/releases).

Η πλήρης έκδοση ενσωμάτωνε το Whisper (ήταν πολύ μεγάλη). Η Lite αφαιρεί τη μετατροπή ομιλίας σε κείμενο, οπότε το εκτελέσιμο είναι μόλις ~19MB.

## Δυνατότητες

- Αναπαραγωγή MP3, WAV, OGG, FLAC, M4A
- Play / Pause / Stop
- Ταχύτητα αναπαραγωγής (0.5x – 2.0x)
- Μετάβαση ±5 δευτερολέπτων
- Bookmarks και χρονικές σημάνσεις
- Καθολικά shortcuts (pynput)
