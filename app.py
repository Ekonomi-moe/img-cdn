from flask import *
from flask_cors import CORS
import requests

storage = Storage()
app = Flask(__name__)
app.secret_key = os.urandom(12)
CORS(app)


@app.route('/<path:path>')
def static_file(path):
    img_id = path.split('.')[0]
    if img_id in requests.get('http://localhost:5000/api/ddr_imglist').json()["data"]:
        return requests.get('http://localhost:5000/api/ddr_img?id=' + img_id).content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
