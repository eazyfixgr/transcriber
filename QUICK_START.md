# 🚀 Quick Start Guide

## Εγκατάσταση (Πρώτη φορά)

### 1. Εγκατάσταση Dependencies
Ανοίξτε Command Prompt στον φάκελο του project και τρέξτε:
```bash
pip install -r requirements.txt
```

**Προσοχή**: Η εγκατάσταση μπορεί να πάρει αρκετά λεπτά λόγω του PyTorch (~100MB+)

### 2. Εγκατάσταση FFmpeg (Για transcription)
- Κατεβάστε από: https://www.gyan.dev/ffmpeg/builds/
- Επιλέξτε: "ffmpeg-release-essentials.zip"
- Αποσυμπιέστε σε έναν φάκελο (π.χ. C:\ffmpeg)
- Προσθέστε το `C:\ffmpeg\bin` στο PATH:
  1. Search "Environment Variables" στα Windows
  2. Edit "Path" variable
  3. Προσθέστε το path του FFmpeg bin folder
  4. Restart Command Prompt

## Εκκίνηση Application

### Μέθοδος 1: Με το Batch File (Εύκολο)
Κάντε διπλό κλικ στο **`run.bat`**

### Μέθοδος 2: Από Command Line
```bash
cd "C:\Users\George\Desktop\python projects\transcriber"
python main.py
```

## Πρώτη Χρήση

### 1. Φόρτωση Audio File
- Κάντε κλικ στο **"Open Audio File"**
- Επιλέξτε ένα audio/video file (MP3, WAV, etc.)
- Το file θα φορτωθεί και θα είστε έτοιμοι για playback

### 2. Playback Controls
- **Play/Pause**: Κλικ στο κουμπί ή πατήστε **F9**
- **Skip**: Χρησιμοποιήστε τα ⏪/⏩ κουμπιά ή **F11/F12**
- **Volume**: Ρυθμίστε το slider
- **Speed**: Ρυθμίστε το slider (0.5x - 2.0x)

### 3. Transcription

#### Αυτόματη Μεταγραφή (AI)
1. Κάντε κλικ **"Start Transcription"**
2. Περιμένετε (μπορεί να πάρει λίγα λεπτά)
3. Η μεταγραφή θα εμφανιστεί αυτόματα με timestamps

**Σημείωση**: Η πρώτη φορά το Whisper model θα κατεβεί (~140MB)

#### Χειροκίνητη Μεταγραφή
1. Play το audio
2. Γράψτε στο text box
3. Πατήστε **"Add Timestamp"** ή **Ctrl+T** για timestamps
4. Πατήστε **"Add Bookmark"** για σημεία αναφοράς

### 4. Rewind on Resume (Σαν το FTW Transcriber!)
- Πηγαίνετε στο **Settings → Rewind on Resume**
- Επιλέξτε πόσα δευτερόλεπτα θέλετε να πηγαίνει πίσω (0-10s)
- Όταν πατάτε pause και μετά play, το audio πηγαίνει αυτόματα πίσω!
- Αυτό σας βοηθάει να μην χάσετε τον συνειρμό σας

### 5. Αποθήκευση
- Επιλέξτε όλο το κείμενο (Ctrl+A)
- Copy (Ctrl+C)
- Paste σε Word/Notepad (Ctrl+V)
- Αποθηκεύστε το αρχείο

## Hotkeys Αναφοράς

| Hotkey | Λειτουργία |
|--------|-----------|
| **F9** | Play/Pause |
| **F10** | Stop |
| **F11** | Skip Backward 5s |
| **F12** | Skip Forward 5s |
| **Ctrl+T** | Add Timestamp |

**Tip**: Τα hotkeys λειτουργούν globally - δουλεύουν ακόμα και αν δουλεύετε σε άλλο πρόγραμμα!

## Tips & Tricks

### 💡 Για Γρήγορη Μεταγραφή
- Χρησιμοποιήστε speed 1.5x-2.0x για γρήγορο audio
- Χρησιμοποιήστε speed 0.5x-0.8x για δύσκολα σημεία
- Χρησιμοποιήστε F11/F12 για replay
- **ΝΕΟ:** Το "Rewind on Resume" πηγαίνει αυτόματα πίσω όταν συνεχίζετε μετά από pause!

### 💡 Για Ακρίβεια
- Ξεκινήστε με auto transcription
- Κάντε corrections καθώς ακούτε το audio
- Χρησιμοποιήστε bookmarks για σημαντικά σημεία

### 💡 Για Productivity
- Μάθετε τα hotkeys - θα γίνετε 3x πιο γρήγοροι!
- Ρυθμίστε το timestamp format που σας βολεύει
- Χρησιμοποιήστε δύο οθόνες (ένα για player, ένα για editor)

## Troubleshooting

### ❌ "Failed to load audio file"
- Ελέγξτε αν το file είναι σωστό format (MP3, WAV, etc.)
- Δοκιμάστε να μετατρέψετε το file σε MP3

### ❌ "Whisper not installed"
```bash
pip install openai-whisper
```

### ❌ "FFmpeg not found" (κατά το transcription)
- Εγκαταστήστε το FFmpeg (βλέπε παραπάνω)
- Προσθέστε το στο PATH
- Κάντε restart το Command Prompt

### ❌ "Transcription failed"
- Ελέγξτε αν το FFmpeg είναι εγκατεστημένο
- Ελέγξτε αν έχετε αρκετό RAM (> 4GB recommended)
- Δοκιμάστε με μικρότερο audio file πρώτα

### ❌ Hotkeys δεν λειτουργούν
```bash
pip install pynput
```

## Απαιτήσεις Συστήματος

### Minimum
- Windows 7/10/11
- Python 3.8+
- 4GB RAM
- 500MB ελεύθερος χώρος

### Recommended
- Windows 10/11
- Python 3.9+
- 8GB+ RAM (για transcription)
- 2GB ελεύθερος χώρος
- SSD για καλύτερη απόδοση

## Υποστήριξη

### Για ερωτήσεις:
- Διαβάστε το **FEATURES.md** για λεπτομέρειες
- Διαβάστε το **README.md** για γενικές πληροφορίες

### Γνωστά Issues:
- Το speed control δεν αλλάζει πραγματικά την ταχύτητα (pygame limitation)
  - Workaround: Χρησιμοποιήστε external tool να αλλάξετε το speed του audio
- Μερικά video formats μπορεί να μην υποστηρίζονται
  - Workaround: Εξάγετε το audio σε MP3 πρώτα

## Καλή Μεταγραφή! 🎉
