import base64
import httplib2
from exceptions import Exception
from flask import Flask, render_template, request, jsonify
from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

app = Flask(__name__, template_folder=".")
app.secret_key = "\xc3\xad\xb7\xaa\xc2\x82\xa4\xb0\n\xe2"

def get_service(service, version):
  scope = ["https://www.googleapis.com/auth/cloud-platform"]
  credentials = GoogleCredentials.get_application_default().create_scoped(scope)
  http = httplib2.Http(timeout=60)
  credentials.authorize(http)
  return discovery.build(service, version, http=http)

@app.route("/")
def main():
  return render_template("main.html")

@app.route("/speech", methods=["POST"])
def speech():
  audio = request.files["file"].read()

  payload = {
    "initialRequest": {
      "encoding": "LINEAR16",
      "sampleRate": 44100
    },
    "audioRequest": {
      "content": base64.b64encode(audio).decode("UTF-8")
    },
  }

  req = get_service("speech", "v1").speech().recognize(body=payload)
  response = req.execute()
  return jsonify(response)

@app.route("/language", methods=["POST"])
def language():
  string = request.form["string"]

  payload = {
    "document": {
      "type": "PLAIN_TEXT",
      "content": string
    },
    "features": {
      "extract_syntax": True,
      "extract_entities": True,
      "extract_document_sentiment": True
    },
    "encodingType": "UTF32"
  }

  req = get_service("language", "v1alpha1").documents().annotateText(body=payload)
  response = req.execute()
  return jsonify(response)

