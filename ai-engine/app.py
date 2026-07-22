from flask import Flask, jsonify
from routes.webhook import webhook_bp
from config import Config
from utils.logger import logger

app = Flask(__name__)
app.register_blueprint(webhook_bp)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    logger.info(f"AI Engine baslatiliyor -- port {Config.PORT}, model={Config.OLLAMA_MODEL}")
    app.run(host="0.0.0.0", port=Config.PORT)
