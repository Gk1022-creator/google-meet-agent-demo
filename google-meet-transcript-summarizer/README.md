# Google Meet Bot with Transcription & Notes

This project automates joining Google Meet meetings, recording audio, transcribing, and generating summarized meeting notes.

---

## ⚙️ Setup Instructions

### 1. Install Requirements
- Python 3.9+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### 2. Configure `join_meet.py`
Add the following values inside `join_meet.py`. These will be used to join Google Meet meetings:

```python
MEET_URL = os.environ.get("MEET_URL")  # Google Meet link
USER_DATA_DIR = os.environ.get("USER_DATA_DIR")  # Chrome user data path
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # Path to Chrome executable
PROFILE_NAME = "Profile 6"  # Chrome profile to use
GUEST_NAME = "meeting bot"  # Display name in the meeting
FILE_PATH = "transcript_file_path"  # Where transcripts will be stored
```

Meeting audio and logs will be stored in the **`meeting_logs`** directory.

---

## 🎧 VB-Cable Setup (For Audio Capture)

This project uses **VB-Audio Virtual Cable** to capture meeting audio.

1. Download VB-Cable from: [VB-Audio Official Site](https://vb-audio.com/Cable/)  
2. Install the driver and restart your computer.  
3. Open **Windows Sound Settings**:
   - Set **VB-Cable Input** as the **Default Playback Device**.  
   - Set **VB-Cable Output** as the **Recording Device**.  
4. Test setup:
   - Play any audio → It should be captured by VB-Cable.  
   - Check in `capture_transcribe.py` if audio frames are being received.  

---

## 📂 Project Structure

This module has three parts:

1. **`join_meet.py`** → Automatically joins a Google Meet meeting.  
2. **`capture_transcribe.py`** → Captures meeting audio coming from VB-Cable and generates transcripts.  
3. **`notes_worker.py`** → Processes the transcript and summarizes the meeting.  

---

## ▶️ Running the Project

1. Start Google Meet joiner:
   ```bash
   python join_meet.py
   ```

2. Start audio capture & transcription:
   ```bash
   python capture_transcribe.py
   ```

3. Run notes summarizer:
   ```bash
   python notes_worker.py
   ```

---
