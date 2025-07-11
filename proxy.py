from flask import Flask, Response, request
import cloudscraper
import base64
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def proxy():
    encoded_url = request.args.get('q')
    if not encoded_url:
        return "Erro: forneça uma URL codificada em Base64 com ?q=", 400

    try:
        url = base64.b64decode(encoded_url).decode('utf-8')
        if not url.startswith(('http://', 'https://')):
            return "Erro: URL inválida", 400

        scraper = cloudscraper.create_scraper()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = scraper.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()

        excluded_headers = ['X-Frame-Options', 'Content-Security-Policy', 'Content-Encoding']
        headers = {k: v for k, v in response.headers.items() if k not in excluded_headers}
        headers['X-Frame-Options'] = 'ALLOWALL'

        return Response(response.content, status=response.status_code, headers=headers)
    except Exception as e:
        return f"Erro: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
