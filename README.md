# GPlay Scraper Web UI

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0-orange.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, clean, and user-friendly web interface for the powerful `gplay-scraper` library. This application allows you to scrape data from the Google Play Store through a simple web UI instead of the command line.

![App Screenshot](https://i.imgur.com/2h1t48X.png)

---

## Features

- **Tabbed Interface:** Easily switch between different scraper functions.
- **App Details:** Get a comprehensive, formatted view of any app's details.
- **Search Apps:** Search for apps by keyword and view results in a clean grid.
- **Top Charts:** Fetch Top Free, Top Paid, and Top Grossing apps.
- **Similar Apps:** Find apps similar to a given package name.
- **Search Suggestions:** Get keyword suggestions.
- **Region Control:** Easily select the country and language for your queries using a single dropdown.

---

## Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS
- **Scraping Library:** [gplay-scraper](https://github.com/Mohammedcha/gplay-scraper)

---

## Setup and Installation

Follow these steps to get the project running locally.

### 1. Prerequisites

Make sure you have Python 3.7+ installed on your system.

### 2. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/gplay-scraper-webui.git](https://github.com/YOUR_USERNAME/gplay-scraper-webui.git)
cd gplay-scraper-webui
```

### 3. Create a Virtual Environment (Recommended)

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

You'll need to create a `requirements.txt` file. Create a new file named `requirements.txt` in your project folder and add the following lines:

```
Flask
gplay-scraper
curl_cffi
```

Now, run the installation command:

```bash
pip install -r requirements.txt
```

---

## How to Run

With your virtual environment activated and dependencies installed, run the Flask application:

```bash
python app.py
```

Open your web browser and navigate to **`http://127.0.0.1:5000`**. The web UI should now be running.

---

## Acknowledgements

This project provides a web interface for the excellent **[gplay-scraper](https://github.com/Mohammedcha/gplay-scraper)** library created by Mohammedcha. All scraping functionality is powered by this source library.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
