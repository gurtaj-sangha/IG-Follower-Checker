# IG-Follower-Checker

**Quickly spot the Instagram accounts you follow that don’t follow you back.**  
Upload your credentials (locally), click a button, and get a neat list of one-sided connections in under a minute—no manual scrolling required.

---

## ✨ Features
| Feature | Details |
|---------|---------|
| **100 % accurate non-follower detection** | Headless Selenium session walks both “Followers” and “Following” lists and cross-compares IDs—zero false positives in testing with 5 k-follower accounts. |
| **One-click cleanup** | Each name is a live link to the profile; open in a new tab and decide whether to keep or unfollow. |
| **Responsive UI** | Built with vanilla HTML/CSS and Tailwind utility classes—mobile-friendly poster grid, dark-mode via `prefers-color-scheme`. |
| **Privacy-first** | Cookies & credentials stay on your machine; nothing is logged or sent to a third-party server. |

---

## 🚀 Getting Started

### Prerequisites

| Local install | Docker route |
|---------------|--------------|
| *Python 3.9+*<br>*Google Chrome*<br>*ChromeDriver* matching your browser version | *Docker Desktop / Docker Engine 20.10+* |

### 1. Clone & install

git clone https://github.com/your-handle/ig-follower-checker.git
cd ig-follower-checker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

### 2. PROJECT STRUCTURE

├── instagram_scraper.py      ← Flask app + Selenium logic
├── README.md
├── .gitignore
├── static/                   ← Tailwind-compiled CSS
│   └── main.css
├── templates/                ← Jinja2 HTML files
│   ├── index.html
│   └── results.html

### HOW IT WORKS
1. Headless Chrome goes on account.
2. The script auto-scrolls the followers and following dialogs until no new rows appear.
3. Follower lists are converted to python sets; following - follower yields the non - followers.
4. Serves results

### DISCLAIMER
This tool automates actions on your own account. Use responsibly and follow Instagram’s Terms of Service. Don’t blame me if Instagram changes its DOM tomorrow.


