from flask import Flask, render_template, request
from gplay_scraper import GPlayScraper
import io
import sys
import json

app = Flask(__name__)
scraper = GPlayScraper(http_client="curl_cffi")

REGIONS = {
    'us': {'name': 'United States', 'lang': 'en'},
    'ma': {'name': 'Arabic', 'lang': 'ar'},  # --- ma-ar ==> morocco - dz-ar ==> algeria  - eg-ar ==> egypt - sa-ar ==> saudi arabia - ae-ar ==> united arab emirates    ---
    'fr': {'name': 'France', 'lang': 'fr'},
    'es': {'name': 'Spain', 'lang': 'es'},
    'de': {'name': 'Germany', 'lang': 'de'},
    'it': {'name': 'Italy', 'lang': 'it'},
    'se': {'name': 'Sweden', 'lang': 'sv'},
    'no': {'name': 'Norway', 'lang': 'no'},
    'nl': {'name': 'Netherlands', 'lang': 'nl'},
    'ru': {'name': 'Russia', 'lang': 'ru'},
    'jp': {'name': 'Japan', 'lang': 'ja'},
    'ko': {'name': 'South Korea', 'lang': 'ko'},
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

    # --- NEW: CLICK-TO-SCRAPE HANDLER ---
    # If a package_name is in the URL, we treat it like a form submission
    if request.method == "GET" and 'package_name' in request.args:
        from werkzeug.datastructures import MultiDict
        form_values = MultiDict({
            'package_name': request.args.get('package_name'),
            'submit_app_details': 'Search' # Simulate button press
        })
        active_tab = 'app-details'
        request.method = "POST" # Force the code to enter the POST logic block
    
    selected_region_code = form_values.get('region', 'us')
    selected_lang = REGIONS[selected_region_code]['lang']
    selected_country = selected_region_code
    
    if request.method == "POST":
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer

        try:
            if 'submit_app_details' in form_values:
                last_action, active_tab = 'App Details', 'app-details'
                package_name = form_values.get("package_name", "").strip()
                if not package_name: raise ValueError("Package Name is required.")
                scraper.app_print_all(package_name, lang=selected_lang, country=selected_country)
            
            # --- NEW: COMPARE APPS LOGIC ---
            elif 'submit_compare' in form_values:
                last_action, active_tab = 'Compare Apps', 'compare-apps'
                pkg1 = form_values.get("package1", "").strip()
                pkg2 = form_values.get("package2", "").strip()
                if not pkg1 or not pkg2: raise ValueError("Both package names are required.")
                # Scrape both apps; the output will be captured together
                scraper.app_print_all(pkg1, lang=selected_lang, country=selected_country)
                scraper.app_print_all(pkg2, lang=selected_lang, country=selected_country)

            elif 'submit_search' in form_values:
                last_action, active_tab = 'Search Apps', 'search-apps'
                query = form_values.get("search_query", "").strip()
                count = int(form_values.get("count", 21))
                if not query: raise ValueError("Search Query is required.")
                scraper.search_print_all(query, count=count, lang=selected_lang, country=selected_country)

            elif 'submit_list' in form_values:
                last_action, active_tab = 'Top Charts', 'top-charts'
                chart = form_values.get("chart_type")
                category = form_values.get("category_type")
                count = int(form_values.get("count", 21))
                scraper.list_print_all(chart, category, count=count, lang=selected_lang, country=selected_country)

            elif 'submit_similar' in form_values:
                last_action, active_tab = 'Similar Apps', 'similar-apps'
                package_name = form_values.get("similar_package", "").strip()
                count = int(form_values.get("count", 21))
                if not package_name: raise ValueError("Package Name is required.")
                scraper.similar_print_all(package_name, count=count, lang=selected_lang, country=selected_country)

            elif 'submit_suggest' in form_values:
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
                if (last_action == 'App Details') and captured_text:
                    data = json.loads(captured_text)
                # Compare and Search use the same stream parser
                elif (last_action in ['Search Apps', 'Compare Apps']) and captured_text:
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
        regions=REGIONS, selected_region=selected_region_code
    )

if __name__ == "__main__":
    app.run(debug=True)
