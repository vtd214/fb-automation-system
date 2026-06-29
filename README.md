
# 📊 Facebook Automation System (FAS)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/selenium-4.0%2B-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Facebook Automation System (FAS)** is an open-source automation tool built with **Python** and **Selenium WebDriver**. It is designed to automate group searching, post interactions, and account warming by precisely mimicking human browsing behavior. This tool helps optimize workflow efficiency and cuts down manual interaction time.


## 🔥 Core Features

* 🔑 **Smart Login:** Automatically restores sessions via `Cookies` or logs in using account `UID/Password` paired with real-time `2FA (OTP)` decoding.
* 📜 **Human Behavior Simulation:** Emulates realistic mouse scrolling (Scroll Pixels) to browse content, introducing randomized delay intervals to simulate article reading time.
* ⌨️ **Human-like Typing Speed:** Types comments character by character with dynamic, variable delays rather than copying and pasting, effectively bypassing spam filters.
* 👍 **Randomized Interaction:** Automatically likes posts and picks comment templates randomly from a pre-configured list to avoid repetitive patterns.
* 🛡️ **Absolute Security:** Completely separates sensitive personal account data from the core source code using an external environment configuration file (`.env`).


🚀 Step-by-Step Installation & Setup

📋 Prerequisites
* Make sure **Python 3.8 or higher** is installed on your computer.
* Ensure you have the latest version of the **Google Chrome** browser installed.


🔹 Step 1: Clone the Repository
Open your **CMD** or **Terminal**, navigate to the directory where you want to save the project, and run:
```bash
git clone [https://github.com/vtd214/fb-automation-system.git](https://github.com/vtd214/fb-automation-system.git)
cd fb-automation-system

```

*(Alternatively, you can click the green **Code** button -> select **Download ZIP** on the GitHub interface and extract it).*

🔹 Step 2: Install Required Dependencies

Run the following command in your terminal to install all necessary Python packages:

```bash
pip install selenium pyotp python-dotenv

```

🔹 Step 3: Configure Security Credentials

The system reads credentials from an external `.env` file to ensure your account details are never exposed online.

1. Create a new file named exactly `.env` in the root directory of the project (at the same level as `main.py`).
2. Open the `.env` file with Notepad or any text editor and paste the following structure, replacing the values with your actual data:

```text
FB_UID=your_facebook_uid
FB_PASS=your_facebook_password
FB_2FA=YOUR_2FA_SECRET_KEY_WITHOUT_SPACES
COOKIE_RAW=your_raw_facebook_cookie_string

```

> ⚠️ **IMPORTANT NOTE:** Do NOT use double quotes `""` or single quotes `''` around the text values inside the `.env` file. This file is already ignored by `.gitignore` and will safely stay on your local machine.

🔹 Step 4: Run the Program

Open CMD in the project folder and execute the script:

```bash
python main.py

```

---

## ⚙️ Scenario Configuration Tuning

You can easily adjust the interaction delays and safe operational intervals at the very beginning of the `main.py` file to fit your specific account-warming strategy:

| Config Variable | Function | Recommended Value |
| --- | --- | --- |
| `DELAY_LOAD_PAGE` | Waiting time for pages to fully load (Seconds) | Leave at `(8, 12)` |
| `DELAY_READ_POST` | Time the robot stops to "read" a post | Keep randomized between `(5, 15)` |
| `DELAY_TYPING_SPEED` | Delay between typing individual characters | Set to `(0.08, 0.25)` for realistic typing |
| `DELAY_BETWEEN_GROUPS` | Cooldown period between different groups | **Set to `(180, 300)` (3-5 mins)** for live accounts to avoid spam blocks. |
| `COMMENT_TEMPLATES` | List of randomized text variations for comments | Customize freely based on your marketing campaigns. |

---

## 🤝 Contributing

Contributions to optimize interaction algorithms or enhance anti-bot bypass mechanisms are highly welcome! Feel free to Fork the project, create a new feature branch, and submit a Pull Request anytime.

---

## 📄 License

This project is open-source and distributed under the **MIT License**. You are free to copy, modify for commercial use, or redistribute it.

