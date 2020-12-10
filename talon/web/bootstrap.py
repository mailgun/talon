from flask import Flask, request, jsonify, json
from werkzeug.exceptions import HTTPException, BadRequest
import talon

talon.init()

from talon import signature

app = Flask(__name__)


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.errorhandler(BadRequest)
def handle_bad_request(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.route('/talon/signature', methods=['GET', 'POST'])
def get_signature():
    email_content = request.form.get('email_content')
    email_sender = request.form.get('email_sender')
    if email_content and email_sender:
        print('email content: ' + email_content)
        print('email sender: ' + email_sender)
        text, s = signature.extract(email_content, sender=email_sender)
        print('text: ' + text)
        print('signature: ' + str(s))
        json_response = {'email_content': email_content, 'email_sender': email_sender, 'email_signature': str(s)}
    else:
        raise BadRequest("Required parameter 'email_content' or 'email_sender' is missing.")
    return jsonify(json_response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')