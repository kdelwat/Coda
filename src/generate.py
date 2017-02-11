import tempfile


def generate(markdown_file_strings, lexicon_file, settings):
    print('Generating...')
    with open('temp/filename.md', 'w') as f:
        f.write('\n'.join(markdown_file_strings))
    return 'temp/filename.md'
