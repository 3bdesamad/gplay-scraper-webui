from flask import Flask, render_template, request
from gplay_scraper import GPlayScraper
import io
import sys
import json
import re
import time

app = Flask(__name__)

# --- Cache dictionary to store results and a timestamp ---
cache = {}
# Set cache duration to 1 hour (3600 seconds)
CACHE_DURATION = 3600

scraper = GPlayScraper(http_client="curl_cffi")

REGIONS = {
    'us': {'name': 'United States', 'lang': 'en'},
    'ma': {'name': 'Arabic', 'lang': 'ar'},  # --- ma-ar ==> morocco - dz-ar ==> algeria  - eg-ar ==> egypt - sa-ar ==> saudi arabia - ae-ar united arab emirates    ---
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

    if request.method == "GET" and 'package_name' in request.args:
        from werkzeug.datastructures import MultiDict
        form_values = MultiDict({
            'package_name': request.args.get('package_name'),
            'submit_app_details': 'Search'
        })
        active_tab = 'app-details'
        request.method = "POST"
    
    selected_region_code = form_values.get('region', 'us')
    selected_lang = REGIONS[selected_region_code]['lang']
    selected_country = selected_region_code
    
    if request.method == "POST":
        
        # --- CACHE LOGIC ---
        # Create a unique key for the cache based on the form submission
        cache_key = str(sorted(form_values.items()))
        
        # Check if a valid, non-expired result is in the cache
        if cache_key in cache and time.time() - cache[cache_key]['timestamp'] < CACHE_DURATION:
            print("Serving from cache!")
            # Load all data directly from the cache
            cached_data = cache[cache_key]
            captured_text = cached_data.get('captured_text')
            last_action = cached_data.get('last_action')
            active_tab = cached_data.get('active_tab')
            error = cached_data.get('error')
        
        else:
            print("Performing new scrape!")
            buffer = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = buffer

            try:
                if 'submit_app_details' in form_values:
                    last_action, active_tab = 'App Details', 'app-details'
                    package_name = form_values.get("package_name", "").strip()
                    if not package_name: raise ValueError("Package Name is required.")
                    scraper.app_print_all(package_name, lang=selected_lang, country=selected_country)
                
                elif 'submit_compare' in form_values:
                    last_action, active_tab = 'Compare', 'compare-apps'
                    pkg1 = form_values.get("package1", "").strip()
                    pkg2 = form_values.get("package2", "").strip()
                    if not pkg1 or not pkg2: raise ValueError("Both package names are required.")
                    scraper.app_print_all(pkg1, lang=selected_lang, country=selected_country)
                    scraper.app_print_all(pkg2, lang=selected_lang, country=selected_country)

                elif 'submit_search' in form_values:
                    last_action, active_tab = 'Search', 'search-apps'
                    query = form_values.get("search_query", "").strip()
                    count = int(form_values.get("count", 20))
                    if not query: raise ValueError("Search Query is required.")
                    scraper.search_print_all(query, count=count, lang=selected_lang, country=selected_country)

                elif 'submit_list' in form_values:
                    last_action, active_tab = 'Top Charts', 'top-charts'
                    chart = form_values.get("chart_type")
                    category = form_values.get("category_type")
                    count = int(form_values.get("count", 20))
                    scraper.list_print_all(chart, category, count=count, lang=selected_lang, country=selected_country)

                elif 'submit_similar' in form_values:
                    last_action, active_tab = 'Similar', 'similar-apps'
                    package_name = form_values.get("similar_package", "").strip()
                    count = int(form_values.get("count", 20))
                    if not package_name: raise ValueError("Package Name is required.")
                    scraper.similar_print_all(package_name, count=count, lang=selected_lang, country=selected_country)

                elif 'submit_suggest' in form_values:
                    last_action, active_tab = 'Suggestions', 'suggestions'
                    query = form_values.get("suggest_query", "").strip()
                    count = int(form_values.get("count", 5))
                    if not query: raise ValueError("Suggestion Query is required.")
                    scraper.suggest_print_nested(query, count=count)
            
            except Exception as e:
                error = f"An error occurred: {str(e)}"
            
            finally:
                sys.stdout = old_stdout
                captured_text = buffer.getvalue()
                
                # --- CACHE LOGIC ---
                # Store the result in the cache
                cache[cache_key] = {
                    'captured_text': captured_text,
                    'last_action': last_action,
                    'active_tab': active_tab,
                    'error': error,
                    'timestamp': time.time()
                }

        # This part for parsing the JSON runs for both cached and new results
        try:
            if not error and captured_text:
                if (last_action == 'App Details'):
                    data = json.loads(captured_text)
                    # Create a URL-friendly slug for the APKPure link
                    if data and 'title' in data:
                        slug = data['title'].lower()
                        slug = re.sub(r'[^a-z0-9\s-]', '', slug) # Remove special characters except spaces/hyphens
                        slug = re.sub(r'\s+', '-', slug).strip('-') # Replace spaces with hyphens
                        data['apkpureSlug'] = slug
                
                elif (last_action in ['Search', 'Compare']):
                    data = parse_json_stream(captured_text)
                elif (last_action in ['Top Charts', 'Similar', 'Suggestions']):
                    data = json.loads(captured_text)
                else:
                    data_output = captured_text
        except json.JSONDecodeError:
            error = f"Failed to parse results for {last_action}."
            data_output = captured_text
            # --- CACHE LOGIC ---
            # Update cache if there was a parsing error
            if cache_key in cache:
                cache[cache_key]['error'] = error

    return render_template(
        "index.html", data=data, data_output=data_output, error=error, 
        last_action=last_action, form=form_values, active_tab=active_tab,
        regions=REGIONS, selected_region=selected_region_code
    )

if __name__ == "__main__":
    app.run(debug=True)
