import time
import pypandoc


def generate(markdown_file_strings, lexicon_file, settings):

    concatenated_markdown = '\n'.join(markdown_file_strings)

    if settings['format'] == 'HTML':
        filename = generate_HTML(concatenated_markdown, lexicon_file,
                                 theme=settings['theme'],
                                 title=settings['grammarTitle'],
                                 subtitle=settings['grammarSubtitle'],
                                 author=settings['author'])

    return filename


def generate_HTML(markdown, lexicon, theme='Default', title='My language',
                  subtitle='A grammar', author='An author'):
    '''Takes a markdown string, a lexicon CSV string, and a number of settings.
    Creates a full HTML document and returns the filename.'''

    # temp_filename = 'temp/{0}.html'.format(str(time.time()))
    temp_filename = 'temp/grammar.html'

    pypandoc.convert_text(markdown, format='md', to='html',
                          outputfile=temp_filename)

    return temp_filename
