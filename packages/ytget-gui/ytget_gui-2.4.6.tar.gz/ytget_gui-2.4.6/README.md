# 🎬 YTGet GUI — YouTube Downloader

**YTGet GUI** is a sleek, user-friendly desktop application built with Python and PySide6 to help you download YouTube videos, playlists, and music effortlessly using **yt-dlp**. This Windows `.exe` version is portable and standalone — no Python installation required.

---

## 📊 Repository Stats

#### 🌟 Community
![GitHub repo stars](https://img.shields.io/github/stars/ErfanNamira/ytget?style=for-the-badge&logo=github)
![GitHub forks](https://img.shields.io/github/forks/ErfanNamira/ytget?style=for-the-badge&logo=github)
![GitHub watchers](https://img.shields.io/github/watchers/ErfanNamira/ytget?style=for-the-badge&logo=github)

#### 🐛 Issues & 🔀 Pull Requests
![GitHub issues](https://img.shields.io/github/issues/ErfanNamira/ytget?style=for-the-badge)
![GitHub closed issues](https://img.shields.io/github/issues-closed/ErfanNamira/ytget?style=for-the-badge)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ErfanNamira/ytget?style=for-the-badge)
![GitHub closed PRs](https://img.shields.io/github/issues-pr-closed/ErfanNamira/ytget?style=for-the-badge)

#### 📥 Downloads
![GitHub all releases](https://img.shields.io/github/downloads/ErfanNamira/ytget/total?label=Total%20Downloads&style=for-the-badge)
![GitHub release (latest by date)](https://img.shields.io/github/downloads/ErfanNamira/ytget/latest/total?label=Latest%20Release&style=for-the-badge)

#### 💻 Codebase
![GitHub repo size](https://img.shields.io/github/repo-size/ErfanNamira/ytget?style=for-the-badge)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/ErfanNamira/ytget?style=for-the-badge)
![GitHub language count](https://img.shields.io/github/languages/count/ErfanNamira/ytget?style=for-the-badge)
![GitHub top language](https://img.shields.io/github/languages/top/ErfanNamira/ytget?style=for-the-badge)

#### ⏱️ Activity
![GitHub last commit](https://img.shields.io/github/last-commit/ErfanNamira/ytget?style=for-the-badge)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/ErfanNamira/ytget?style=for-the-badge)

---

## ☄️ How to Run?

1. 📦 Download the latest `.zip` release  
2. 🗂️ Extract the contents  
3. ▶️ Run `YTGet.exe`  

---

## ✨ Features

### 🖥️ Interface
- 🎯 **Clean Qt GUI** — Intuitive layout with dark-friendly visuals
- 🛑 **Cancel Anytime** — Gracefully stop downloads at any moment
- 🔒 **Offline Capable** — No need for Python or external installations

### 📥 Download Options
- 📹 **Multiple Formats** — Download in resolutions from 480p to 8K
- 🎵 **MP3 Mode** — High-quality audio extraction with embedded thumbnails and metadata
- 📄 **Subtitles** — Auto-fetch subtitles (multiple languages supported)
- 📂 **Playlist Support** — Download entire playlists in audio or video mode

### 🔧 Advanced Features
- ⚙️ **Persistent Settings** — All settings saved to `config.json` between sessions
- 🚀 **Improved Playlist Support** — Reverse order, select items, track with archive
- ✂️ **Clip Extraction** — Download video portions by start/end time
- ⏭️ **SponsorBlock** — Skip sponsored content, intros, and outros
- 🧩 **Chapters Handling** — Embed or split videos based on chapters
- 🎼 **YouTube Music Metadata** — Accurate music info and album data

### 🛠 Functionality
- 🌐 **Proxy Support** — Configure proxies for downloading
- 📅 **Date Filter** — Download videos uploaded after a certain date
- 🧪 **Custom FFmpeg Args** — Add advanced arguments for power users
- 🔊 **Audio Normalization** — Uniform audio volume for all downloads
- 🗃 **Channel Organization** — Auto-sort videos into uploader folders
- ⚡ **Performance Enhancements** — Smart rate limiting and retry logic

---

## 🖼 Screenshot

<p align="center">
  <a href="https://raw.githubusercontent.com/ErfanNamira/YTGet/refs/heads/main/Images/YTGet2.4%20(1).JPG">
    <img src="https://raw.githubusercontent.com/ErfanNamira/YTGet/refs/heads/main/Images/YTGet2.4%20(1).JPG" width="220" />
  </a>
  <a href="https://raw.githubusercontent.com/ErfanNamira/YTGet/refs/heads/main/Images/YTGet2.4%20(2).JPG">
    <img src="https://raw.githubusercontent.com/ErfanNamira/YTGet/refs/heads/main/Images/YTGet2.4%20(2).JPG" width="220" />
  </a>
  <a href="https://raw.githubusercontent.com/ErfanNamira/YTGet/refs/heads/main/Images/YTGet2.4%20(3).JPG">
    <img src="https://raw.githubusercontent.com/ErfanNamira/YTGet/refs/heads/main/Images/YTGet2.4%20(3).JPG" width="220" />
  </a>
  <a href="https://raw.githubusercontent.com/ErfanNamira/ytget/refs/heads/main/Images/YTGet2.4.3.JPG">
    <img src="https://raw.githubusercontent.com/ErfanNamira/ytget/refs/heads/main/Images/YTGet2.4.3.JPG" width="220" />
  </a>
</p>

---

## 🧰 How to Use

1. 📦 Extract the downloaded `.zip` file  
2. ▶️ Launch `YTGet.exe`  
3. 🔗 Paste a YouTube URL  
4. 🎚️ Select format (e.g., 1080p MKV or MP3)  
5. ⬇️ Click **➕ Add to Queue**
6. ⬇️ Click **▶️ Start Queue**

---

## 📁 Output

- ✅ Clean filenames: `%(title)s.ext`  
- 🎵 Audio downloads include:
  - Embedded album art (from thumbnail)
  - Metadata tags (artist, title, etc.)
  - Subtitles (if available)

---

## 🧩 Format Options

| Format           | Description                                     |
|------------------|-------------------------------------------------|
| 🎞️ 480p–2160p     | MKV video with merged best audio                |
| 🎵 MP3 Audio      | High-quality audio with tags and thumbnails     |
| 📃 MP3 Playlist   | Batch audio extraction from playlists           |

---

## 🔒 Cookies Support

To download **age-restricted** or **private** content:

1. Export cookies using a browser extension like [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/lgmpjfekhdgcmpcpnmlhkfkfjdkpmoec)  
2. Place the file at:

_internal/cookies.txt


---

## ⚙️ Requirements

- ✅ No installation needed — just unzip and run  
- 🪟 Windows 10 or later (64-bit)

---

## 🔧 Development Setup 

### Prerequisites

- [Python](https://www.python.org/downloads/)
- [FFmpeg and FFprobe](https://www.ffmpeg.org/download.html) (Add to path or source folder)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ErfanNamira/ytget.git
   ```

2. **Create & activate virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate   # on Linux/Mac
    venv\Scripts\activate      # on Windows
    ```

2. **Install dependencies**
   ```bash
    pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python -m ytget
   ```

---

## 🤝 Contribution Guide

1. Fork & clone the repo

2. Create a feature branch: git checkout -b my-feature

3. Commit & push: git commit -m "msg" && git push origin my-feature

4. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for full details.

---

## 📦 Download

👉 [Latest Release (.zip)](https://github.com/ErfanNamira/YTGet/releases/latest)
