"""
sample_web_app.py
-------------------------
This script creates a simple Flask web application that demonstrates 
vector search capabilities using Azure AI Search.

"""

import os
from flask import Flask, render_template, request, jsonify
from vector_search_client import VectorSearchClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize vector search client
search_client = VectorSearchClient()

@app.route('/')
def index():
    """Render the main search page"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    """
    API endpoint for searching documents.
    
    Expects JSON with:
        - query: the search query
        - search_type: "vector", "hybrid", or "semantic"
        - top: number of results to return (optional)
    """
    try:
        # Get request data
        data = request.json
        query = data.get('query', '')
        search_type = data.get('search_type', 'vector')
        top = int(data.get('top', 5))
        
        # Validate input
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Perform appropriate search based on type
        if search_type == 'vector':
            results = search_client.vector_search(query, top)
        elif search_type == 'hybrid':
            results = search_client.hybrid_search(query, top)
        elif search_type == 'semantic':
            results = search_client.semantic_search(query, top)
        else:
            return jsonify({'error': 'Invalid search type'}), 400
        
        # Process results for display
        processed_results = []
        for result in results:
            # Truncate content if too long
            content = result.get('content', '')
            if len(content) > 500:
                content = content[:500] + '...'
            
            processed_results.append({
                'id': result.get('id', ''),
                'title': result.get('title', ''),
                'content': content,
                'category': result.get('category', ''),
                'sourceUrl': result.get('sourceUrl', ''),
                'sourceName': result.get('sourceName', '')
            })
        
        # Return results
        return jsonify({
            'results': processed_results,
            'count': len(processed_results),
            'query': query,
            'search_type': search_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Required HTML templates directory structure
"""
templates/
    index.html
static/
    css/
        styles.css
    js/
        main.js
"""

@app.route('/generate_templates', methods=['GET'])
def generate_templates():
    """
    Generate the required HTML templates and static files
    Note: This is for demonstration purposes only and should be removed in production.
    """
    try:
        # Create directories if they don't exist
        os.makedirs('templates', exist_ok=True)
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
        
        # Create index.html
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Azure AI Search Demo</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h1>Azure AI Search Vector Demo</h1>
            <p>Try out different search methods to explore your data</p>
        </header>
        
        <div class="search-container">
            <div class="search-box">
                <input type="text" id="search-input" placeholder="Enter your search query...">
                <button id="search-button">Search</button>
            </div>
            
            <div class="search-options">
                <label>
                    <input type="radio" name="search-type" value="vector" checked> Vector Search
                </label>
                <label>
                    <input type="radio" name="search-type" value="hybrid"> Hybrid Search
                </label>
                <label>
                    <input type="radio" name="search-type" value="semantic"> Semantic Search
                </label>
                
                <div class="results-count">
                    <label for="results-count">Results:</label>
                    <select id="results-count">
                        <option value="5">5</option>
                        <option value="10">10</option>
                        <option value="20">20</option>
                    </select>
                </div>
            </div>
        </div>
        
        <div class="results-container">
            <div class="results-header">
                <h2>Search Results</h2>
                <p id="results-summary"></p>
            </div>
            <div id="results-list"></div>
        </div>
    </div>
    
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
"""
        
        # Create styles.css
        styles_css = """body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
}

header h1 {
    color: #0078d4;
    margin-bottom: 10px;
}

.search-container {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}

.search-box {
    display: flex;
    margin-bottom: 20px;
}

.search-box input {
    flex: 1;
    padding: 12px;
    font-size: 16px;
    border: 1px solid #ddd;
    border-radius: 4px 0 0 4px;
}

.search-box button {
    padding: 12px 24px;
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
    font-size: 16px;
}

.search-box button:hover {
    background-color: #106ebe;
}

.search-options {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
}

.search-options label {
    display: flex;
    align-items: center;
    cursor: pointer;
}

.results-count {
    margin-left: auto;
}

.results-count select {
    padding: 5px 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.results-container {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.results-header h2 {
    margin: 0;
    color: #0078d4;
}

.result-item {
    margin-bottom: 25px;
    padding-bottom: 25px;
    border-bottom: 1px solid #eee;
}

.result-item:last-child {
    border-bottom: none;
}

.result-title {
    margin: 0 0 10px;
    font-size: 18px;
    color: #0078d4;
}

.result-title a {
    color: inherit;
    text-decoration: none;
}

.result-title a:hover {
    text-decoration: underline;
}

.result-source {
    font-size: 14px;
    color: #666;
    margin-bottom: 10px;
}

.result-content {
    line-height: 1.6;
    color: #333;
}

.result-category {
    display: inline-block;
    background-color: #f0f0f0;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
    color: #666;
    margin-top: 10px;
}

.loading {
    text-align: center;
    padding: 20px;
}

.error {
    background-color: #fde8e8;
    color: #e53e3e;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 20px;
}
"""
        
        # Create main.js
        main_js = """document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const resultsList = document.getElementById('results-list');
    const resultsSummary = document.getElementById('results-summary');
    
    // Add event listener for search button click
    searchButton.addEventListener('click', performSearch);
    
    // Add event listener for Enter key in search input
    searchInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            performSearch();
        }
    });
    
    // Function to perform search
    async function performSearch() {
        const query = searchInput.value.trim();
        
        if (!query) {
            showError('Please enter a search query');
            return;
        }
        
        // Get selected search type
        const searchTypeElements = document.getElementsByName('search-type');
        let searchType = 'vector';
        for (const element of searchTypeElements) {
            if (element.checked) {
                searchType = element.value;
                break;
            }
        }
        
        // Get selected number of results
        const topResults = document.getElementById('results-count').value;
        
        // Show loading state
        resultsList.innerHTML = '<div class="loading">Searching...</div>';
        resultsSummary.textContent = '';
        
        try {
            // Send search request to API
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query,
                    search_type: searchType,
                    top: topResults
                })
            });
            
            if (!response.ok) {
                throw new Error('Search request failed');
            }
            
            const data = await response.json();
            
            // Display search results
            displayResults(data);
        } catch (error) {
            showError(error.message);
        }
    }
    
    // Function to display search results
    function displayResults(data) {
        // Clear previous results
        resultsList.innerHTML = '';
        
        // Show results summary
        const searchTypeName = getSearchTypeName(data.search_type);
        resultsSummary.textContent = `Found ${data.count} results for "${data.query}" using ${searchTypeName}`;
        
        // If no results found
        if (data.count === 0) {
            resultsList.innerHTML = '<div class="no-results">No results found. Try a different query or search method.</div>';
            return;
        }
        
        // Display each result
        data.results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';
            
            const sourceUrl = result.sourceUrl || '#';
            
            resultItem.innerHTML = `
                <h3 class="result-title">
                    <a href="${sourceUrl}" target="_blank">${result.title || 'Untitled'}</a>
                </h3>
                <div class="result-source">
                    Source: ${result.sourceName || 'Unknown'}
                </div>
                <div class="result-content">
                    ${result.content || 'No content available'}
                </div>
                ${result.category ? `<div class="result-category">${result.category}</div>` : ''}
            `;
            
            resultsList.appendChild(resultItem);
        });
    }
    
    // Function to show error message
    function showError(message) {
        resultsList.innerHTML = `<div class="error">${message}</div>`;
        resultsSummary.textContent = '';
    }
    
    // Function to get display name for search type
    function getSearchTypeName(searchType) {
        switch (searchType) {
            case 'vector':
                return 'Vector Search';
            case 'hybrid':
                return 'Hybrid Search';
            case 'semantic':
                return 'Semantic Search';
            default:
                return 'Search';
        }
    }
});
"""
        
        # Write files
        with open('templates/index.html', 'w') as f:
            f.write(index_html)
        
        with open('static/css/styles.css', 'w') as f:
            f.write(styles_css)
        
        with open('static/js/main.js', 'w') as f:
            f.write(main_js)
        
        return jsonify({'message': 'Templates generated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Generate templates if they don't exist
    if not os.path.exists('templates/index.html'):
        os.makedirs('templates', exist_ok=True)
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/js', exist_ok=True)
        app.test_client().get('/generate_templates')
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
