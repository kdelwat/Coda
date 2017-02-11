from flask import Flask, request, send_file, url_for, after_this_request
import os

from src.generate import generate

app = Flask(__name__)

available_settings = ['grammarTitle', 'grammarSubtitle', 'author', 'format',
                      'theme']

@app.route('/', methods=['POST'])
def index():

    # Get all available string settings from posted object
    settings = {}
    for key in available_settings:
        settings[key] = request.form.get(key, None)

    # Loop through the files posted to the endpoint, reading all
    # files as strings.
    markdown_file_strings = []
    lexicon_file_string = None
    for filename, blob in request.files.items():
        if filename.endswith('.csv'):
            lexicon_file_string = str(blob.read(), 'utf-8')
        else:
            markdown_file_strings.append(str(blob.read(), 'utf-8'))

    filename = generate(markdown_file_strings, lexicon_file_string, settings)

    return filename


@app.route('/download')
def download():
    filename = request.args.get('filename')
    print('Received request with filename {0}'.format(filename))

    if filename.endswith('.md'):
        mimetype = 'text/markdown; charset=utf-8'

    return send_file(filename, mimetype=mimetype, as_attachment=True,
                     attachment_filename='grammar.md')


if __name__ == '__main__':
    app.run(debug=True)
