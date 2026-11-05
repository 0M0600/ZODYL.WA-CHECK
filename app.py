import re

import time

from collections import defaultdict, deque



from flask import Flask, request, jsonify



app = Flask(__name__, static_folder="static", static_url_path="/static")



cache = {}                      # en vrai : Redis ou une base de données

hits = defaultdict(deque)       # rate limiting par IP

MAX_REQ, WINDOW = 10, 60        # 10 requêtes par minute





def valid_format(num: str) -> bool:

    return re.fullmatch(r"\+\d{8,15}", num) is not None





def rate_limited(ip: str) -> bool:

    now = time.time()

    q = hits[ip]

    while q and now - q[0] > WINDOW:

        q.popleft()

    if len(q) >= MAX_REQ:

        return True

    q.append(now)

    return False





def check_status(num: str) -> str:

    # Partie 3 : volontairement non implémentée.

    # Retournerait "active", "banned", "spam" ou "unknown".

    raise NotImplementedError





@app.get("/")

def home():

    return app.send_static_file("index.html")





@app.post("/check")

def check():

    if rate_limited(request.remote_addr):

        return jsonify(error="trop de requêtes"), 429

    data = request.get_json(silent=True) or {}

    num = data.get("number", "")

    if not valid_format(num):

        return jsonify(error="format invalide"), 400

    if num not in cache:

        try:

            cache[num] = check_status(num)

        except NotImplementedError:

            return jsonify(error="vérification non implémentée"), 501

    return jsonify(number=num, status=cache[num])





if __name__ == "__main__":

    app.run(port=5000)



