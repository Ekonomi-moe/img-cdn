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
    img_id = path.split('.')[0]
    cache_folder = Path('cache')
    if not cache_folder.exists(): cache_folder.mkdir()
    cache_file = cache_folder / f'{img_id}.png'
    if cache_file.exists(): return cache_file.read_bytes()
    try:
        if img_id in requests.get('http://localhost:5000/api/ddr_imglist').json()["data"]:
            img = requests.get('http://localhost:5000/api/ddr_img?id=' + img_id).content
            cache_file.write_bytes(img)
            return img
        else:
            return {"status": 404, "message": "Image not found"}
    except:
        return {"status": 500, "message": "Internal Server Error"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
