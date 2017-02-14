from flask import Flask, request, send_file, url_for, after_this_request
import os
import pypandoc

from src.generate import generate

app = Flask(__name__)

available_settings = ['grammarTitle', 'grammarSubtitle', 'author', 'format',
                      'theme', 'csvColumnWord', 'csvColumnLocal',
                      'csvColumnDefinition', 'csvColumnPronunciation',
                      'csvColumnPartOfSpeech', 'layout']


@app.route('/', methods=['POST'])
def index():
    # Get all available string settings from posted object
    settings = {}
    for key in available_settings:
        settings[key] = request.form.get(key, None)

    print(settings)

    # Loop through the files posted to the endpoint, reading all
    # files as strings.
    markdown_file_strings = []
    lexicon_file_string = None
    for filename, blob in request.files.items():
        if filename.endswith('.csv'):
            lexicon_file_string = str(blob.read(), 'utf-8')
        else:
            markdown_file_strings.append(str(blob.read(), 'utf-8'))

    try:
        filename = generate(markdown_file_strings, lexicon_file_string,
                            settings)
        return filename
    except Exception as e:
        print(type(e).__name__)
        return 'ERROR' + str(e)


@app.route('/download')
def download():
    filename = request.args.get('filename')
    filepath = os.path.join('temp', filename)

    print('Received request with filename {0}'.format(filename))

    if filename.endswith('.html'):
        mimetype = 'text/html; charset=utf-8'
        attachment_filename = 'Grammar.html'
    elif filename.endswith('.pdf'):
        mimetype = 'application/pdf'
        attachment_filename = 'Grammar.pdf'
    else:
        return 'File not found', 404

    return send_file(filepath, mimetype=mimetype, as_attachment=True,
                     attachment_filename=attachment_filename)


def check_pandoc_on_startup():
    '''On startup, checks if pandoc is installed. If it is, continues to main
    application. Otherwise, pandoc will be installed.'''
    print('Looking for pandoc...')

    try:
        version = pypandoc.get_pandoc_version()
        print('Found version {0}'.format(version))

    except OSError:
        print('Not found! Downloading...')

        pypandoc.pandoc_download.download_pandoc()

        print('Download complete!')


if __name__ == '__main__':
    check_pandoc_on_startup()
    app.run(debug=True)
