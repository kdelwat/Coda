import time


def generate(markdown_file_strings, lexicon_file, settings):
    print('Generating...')

    temp_filename = str(time.time()) + '.md'

    with open('temp/' + temp_filename, 'w') as f:
        f.write('\n'.join(markdown_file_strings))

    return 'temp/' + temp_filename
