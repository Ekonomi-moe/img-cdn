from flask import *
from flask_cors import CORS
from pathlib import Path
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(12)
CORS(app)

@app.route('/<path:path>')
def static_file(path):
    if path == "favicon.ico": return {"status": 404}, 404
    os.chdir(Path(__file__).parent)
    img_id = path.split('.')[0]
    cache_folder = Path('cache')
    if not cache_folder.exists(): cache_folder.mkdir()
    cache_file = cache_folder / f'{img_id}.png'
    try:
        if img_id in requests.get('http://localhost:5000/api/ddr_imglist').json()["data"]:
            if cache_file.exists(): return send_file(cache_file)
            img = requests.get('http://localhost:5000/api/ddr_img?id=' + img_id).content
            cache_file.write_bytes(img)
            return send_file(cache_file)
        else:
            if cache_file.exists(): cache_file.unlink()
            return {"status": 404, "message": "Image not found"}
    except:
        return {"status": 500, "message": "Internal Server Error"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
