import base64
import httplib2
from flask import Flask, jsonify, render_template, request
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

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

@app.route("/", methods=['POST'])
def upload():
  file = request.files['file']
  if file and file.content_type == "text/plain":
    string = file.read()
    response = language_api(string)
    return jsonify(response)

@app.route("/speech", methods=["POST"])
def speech():
  audio = request.files["file"].read()

  payload = {
    "config": {
      "encoding": "LINEAR16",
      "sampleRate": 44100
    },
    "audio": {
      "content": base64.b64encode(audio).decode("UTF-8")
    },
  }

  req = get_service("speech", "v1beta1").speech().syncrecognize(body=payload)
  response = req.execute()
  return jsonify(response)

@app.route("/language", methods=["POST"])
def language():
  string = request.form["string"]
  response = language_api(string)
  return jsonify(response)

def language_api(string):
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

  req = get_service("language", "v1beta1").documents().annotateText(body=payload)
  return req.execute()

