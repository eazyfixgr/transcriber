# Changelog

## Version 1.1.0 (2025-12-04)

### ✨ Νέα Χαρακτηριστικά

#### Rewind on Resume
- **Σαν το original FTW Transcriber!**
- Όταν πατάτε pause και μετά play, το audio πηγαίνει αυτόματα πίσω
- Επιλογές: 0, 2, 4, 6, 8, 10 δευτερόλεπτα
- Default: 4 δευτερόλεπτα (recommended)
- Ρυθμίζεται από: **Settings → Rewind on Resume**

**Γιατί είναι χρήσιμο:**
- Βοηθάει να μην χάσετε τον συνειρμό σας κατά τη μεταγραφή
- Δίνει λίγο context πριν συνεχίσετε
- Εξαιρετικά χρήσιμο για γρήγορη μεταγραφή
- Ακριβώς όπως στο original FTW Transcriber!

**Τεχνικές λεπτομέρειες:**
- Αποθηκεύει τη θέση κατά το pause
- Υπολογίζει τη νέα θέση με rewind κατά το resume
- Persistent ρύθμιση στο `transcriber_settings.json`
- Status bar δείχνει το rewind message: "Playing... (rewound Xs)"

---

## Version 1.0.0 (2025-12-04)

### 🎉 Initial Release

#### Core Features
- Audio playback με πολλαπλά formats (MP3, WAV, OGG, FLAC, M4A)
- Play/Pause/Stop controls
- Speed control (0.5x - 2.0x)
- Volume control
- Skip forward/backward (5s)
- Progress bar

#### AI Transcription
- Αυτόματη μεταγραφή με OpenAI Whisper
- Automatic timestamp insertion
- Manual timestamp insertion
- Προσαρμοζόμενα timestamp formats

#### Additional Features
- Bookmarks με ονόματα
- Global hotkeys (F9-F12, Ctrl+T)
- Modern UI με FTW Transcriber colors
- Settings persistence
- Χωρίς χρονικούς περιορισμούς!

#### Documentation
- README.md
- QUICK_START.md
- FEATURES.md
- requirements.txt
- run.bat για εύκολη εκκίνηση
