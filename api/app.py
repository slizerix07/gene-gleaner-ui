
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import logging
import re
from typing import Dict, List, Any, Union

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Biology-related keywords for content filtering
BIOLOGY_KEYWORDS = [
    "biology", "cell", "dna", "rna", "protein", "gene", "chromosome", 
    "enzyme", "bacteria", "virus", "organism", "species", "evolution", 
    "ecology", "photosynthesis", "respiration", "metabolism", "mitosis",
    "meiosis", "amino acid", "nucleotide", "mutation", "heredity", "taxonomy",
    "ecosystem", "biodiversity", "genome", "biotechnology", "microorganism",
    "anatomy", "physiology", "botany", "zoology", "molecular", "biosphere",
    "cytology", "genetics", "homeostasis", "membrane", "nucleus", "organelle"
]

def is_biology_related(text: str) -> bool:
    """Check if the text contains biology-related keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in BIOLOGY_KEYWORDS)

def clean_text(text: str) -> str:
    """Clean text by removing extra whitespaces."""
    return re.sub(r'\s+', ' ', text).strip()

def fetch_url_content(url: str) -> str:
    """Fetch the content of the URL."""
    try:
        logger.info(f"Fetching content from URL: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        raise

def parse_html_content(html_content: str) -> Dict[str, Any]:
    """Parse HTML content and extract biology-related information."""
    logger.info("Parsing HTML content")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted tags
    for tag in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe']):
        tag.decompose()
    
    # Extract title and headlines
    title = soup.title.text.strip() if soup.title else ""
    h1_tags = [clean_text(h1.get_text()) for h1 in soup.find_all('h1')]
    h2_tags = [clean_text(h2.get_text()) for h2 in soup.find_all('h2')]
    
    # Extract biology-related paragraphs
    paragraphs = []
    for p in soup.find_all('p'):
        text = clean_text(p.get_text())
        if text and is_biology_related(text):
            paragraphs.append(text)
    
    # Extract tables
    tables = []
    for table in soup.find_all('table'):
        headers = []
        rows = []
        
        # Extract table headers
        for th in table.find_all('th'):
            headers.append(clean_text(th.get_text()))
        
        # Extract table rows
        for tr in table.find_all('tr'):
            row = []
            for td in tr.find_all('td'):
                row.append(clean_text(td.get_text()))
            if row:  # Only add non-empty rows
                rows.append(row)
        
        tables.append({
            "headers": headers,
            "rows": rows
        })
    
    # Build result
    result = {
        "title": title,
        "headlines": {
            "h1": h1_tags,
            "h2": h2_tags
        },
        "biology_paragraphs": paragraphs,
        "tables": tables
    }
    
    return result

@app.route('/extract', methods=['POST'])
def extract():
    """Extract biology information from the provided URL."""
    try:
        # Get the URL from the request
        data = request.get_json()
        
        if not data or 'url' not in data:
            logger.warning("Invalid request: missing URL")
            return jsonify({"error": "URL is required"}), 400
        
        url = data['url']
        logger.info(f"Received extraction request for URL: {url}")
        
        # Fetch and parse the URL content
        html_content = fetch_url_content(url)
        extracted_data = parse_html_content(html_content)
        
        logger.info(f"Successfully extracted biology information from {url}")
        return jsonify(extracted_data)
        
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return jsonify({"error": f"Error fetching URL: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
