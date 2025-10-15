# Google Play Scraper Web UI

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
- **Compare Two Apps**: Instantly compare two apps side-by-side, including their ratings, installs, reviews, developer details, release dates, and more — all displayed in a clean, responsive comparison table.
- **Search Suggestions:** Get keyword suggestions.
- **Region Control:** Easily select the country and language for your queries using a single dropdown.


---

## Tech Stack

- **Backend:** Python, Flask (`pip install Flask`)
- **Frontend:** HTML, CSS
- **Scraping Library:** [gplay-scraper](https://github.com/Mohammedcha/gplay-scraper) (`pip install gplay-scraper`)
- **HTTP Client:** curl_cffi (`pip install curl_cffi`)

---

## How to Run

With your virtual environment activated and dependencies installed, run the Flask application:

```bash
python gplay.py
```

Open your web browser and navigate to **`http://127.0.0.1:5000`**. The web UI should now be running.

---

## Acknowledgements

This project provides a web interface for the excellent **[gplay-scraper](https://github.com/Mohammedcha/gplay-scraper)** library created by Mohammed Cha. All scraping functionality is powered by this source library.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
