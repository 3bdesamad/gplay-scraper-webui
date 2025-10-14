from flask import Flask, render_template, request
from gplay_scraper import GPlayScraper
import io
import sys
import json

app = Flask(__name__)
scraper = GPlayScraper(http_client="curl_cffi")

# --- NEW: Combined REGIONS dictionary ---
# Maps a country code to its name and default language code
REGIONS = {
    'us': {'name': 'United States', 'lang': 'en'},
    'ar': {'name': 'Arabic', 'lang': 'ar'},
    'fr': {'name': 'France', 'lang': 'fr'},
    'es': {'name': 'Spain', 'lang': 'es'},
    'de': {'name': 'Germany', 'lang': 'de'},
    'it': {'name': 'Italy', 'lang': 'it'},
    'se': {'name': 'Sweden', 'lang': 'sv'},
    'no': {'name': 'Norway', 'lang': 'no'},
    'nl': {'name': 'Netherlands', 'lang': 'nl'},
    'ru': {'name': 'Russia', 'lang': 'ru'},
    'jp': {'name': 'Japan', 'lang': 'ja'},
    'kr': {'name': 'South Korea', 'lang': 'ko'},
    'br': {'name': 'Brazil', 'lang': 'pt'},
    'cn': {'name': 'China', 'lang': 'zh-CN'},
    'th': {'name': 'Thailand', 'lang': 'th'},
    'tr': {'name': 'Turkey', 'lang': 'tr'},
    'in': {'name': 'India', 'lang': 'hi'}
}

def parse_json_stream(text):
    decoder = json.JSONDecoder()
    results, pos = [], 0
    text = text.strip()
    while pos < len(text):
        while pos < len(text) and text[pos].isspace(): pos += 1
        if pos == len(text): break
        obj, pos = decoder.raw_decode(text, pos)
        results.append(obj)
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    data, data_output, error, last_action = None, None, None, None
    active_tab = 'app-details'
    form_values = request.form

    # --- UPDATED: Logic to use a single region selector ---
    selected_region_code = request.form.get('region', 'us')
    selected_lang = REGIONS[selected_region_code]['lang']
    selected_country = selected_region_code

    if request.method == "POST":
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer

        try:
            # All scraper methods now use the lang/country from the selected region
            if 'submit_app_details' in request.form:
                last_action, active_tab = 'App Details', 'app-details'
                package_name = form_values.get("package_name", "").strip()
                if not package_name: raise ValueError("Package Name is required.")
                scraper.app_print_all(package_name, lang=selected_lang, country=selected_country)

            elif 'submit_search' in request.form:
                last_action, active_tab = 'Search Apps', 'search-apps'
                query = form_values.get("search_query", "").strip()
                count = int(form_values.get("count", 10))
                if not query: raise ValueError("Search Query is required.")
                scraper.search_print_all(query, count=count, lang=selected_lang, country=selected_country)

            elif 'submit_list' in request.form:
                last_action, active_tab = 'Top Charts', 'top-charts'
                chart = form_values.get("chart_type")
                category = form_values.get("category_type")
                count = int(form_values.get("count", 20))
                scraper.list_print_all(chart, category, count=count, lang=selected_lang, country=selected_country)

            elif 'submit_similar' in request.form:
                last_action, active_tab = 'Similar Apps', 'similar-apps'
                package_name = form_values.get("similar_package", "").strip()
                count = int(form_values.get("count", 20))
                if not package_name: raise ValueError("Package Name is required.")
                scraper.similar_print_all(package_name, count=count, lang=selected_lang, country=selected_country)

            elif 'submit_suggest' in request.form:
                last_action, active_tab = 'Suggestions', 'suggestions'
                query = form_values.get("suggest_query", "").strip()
                count = int(form_values.get("count", 5))
                if not query: raise ValueError("Suggestion Query is required.")
                scraper.suggest_print_all(query, count=count, lang=selected_lang, country=selected_country)
        
        except Exception as e:
            error = f"An error occurred: {str(e)}"
        
        finally:
            sys.stdout = old_stdout
            captured_text = buffer.getvalue()
            
            try:
                if last_action == 'App Details' and captured_text:
                    data = json.loads(captured_text)
                elif last_action == 'Search Apps' and captured_text:
                    data = parse_json_stream(captured_text)
                elif (last_action in ['Top Charts', 'Similar Apps', 'Suggestions']) and captured_text:
                    data = json.loads(captured_text)
                else:
                    data_output = captured_text
            except json.JSONDecodeError:
                error = f"Failed to parse results for {last_action}."
                data_output = captured_text

    return render_template(
        "index.html", data=data, data_output=data_output, error=error, 
        last_action=last_action, form=form_values, active_tab=active_tab,
        regions=REGIONS, # Pass the new REGIONS dictionary
        selected_region=selected_region_code
    )

if __name__ == "__main__":
    app.run(debug=True)