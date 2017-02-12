import time
import pypandoc
import os
import re
import csv
import string

base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFINITION_TEMPLATE = '''
<span class="word">$word
    <span class="definition">$local_word ($part)<br>
        <span class="full-definition">$definition</span>
    </span>
</span>
'''


def generate(markdown_file_strings, lexicon_file, settings):

    concatenated_markdown = '\n'.join(markdown_file_strings)

    if settings['format'] == 'HTML':
        filename = generate_HTML(concatenated_markdown, lexicon_file,
                                 theme=settings['theme'],
                                 title=settings['grammarTitle'],
                                 subtitle=settings['grammarSubtitle'],
                                 author=settings['author'])
    elif settings['format'] == 'LaTeX PDF':
        filename = generate_latex(concatenated_markdown, lexicon_file,
                                  theme=settings['theme'],
                                  title=settings['grammarTitle'],
                                  subtitle=settings['grammarSubtitle'],
                                  author=settings['author'])

    return filename


def generate_latex(markdown, lexicon, theme='Default', title='My language',
                   subtitle='A grammar', author='An author'):
    '''Takes a markdown string, a lexicon CSV string, and a number of settings.
    Creates a PDF document and returns the filename.'''

    # Create list of pandoc settings, including template file
    pandoc_arguments = ['--standalone',
                        '--toc',
                        '--smart',
                        '--latex-engine=xelatex']

    template_directory = os.path.join(base_directory, 'latexthemes')
    template_name = '{0}.tex'.format(theme)
    template_path = os.path.join(template_directory, template_name)
    pandoc_arguments.append('--template={0}'.format(template_path))

    # Create temporary filename for output
    temp_filename = 'grammar.pdf'
    temp_path = os.path.join(base_directory, 'temp', temp_filename)

    pypandoc.convert_text(markdown, format='md', to='pdf',
                          outputfile=temp_path,
                          extra_args=pandoc_arguments)

    return temp_path


def generate_HTML(markdown, lexicon, theme='Default', title='My language',
                  subtitle='A grammar', author='An author'):
    '''Takes a markdown string, a lexicon CSV string, and a number of settings.
    Creates a full HTML document and returns the filename.'''

    # Create a metadata block and add it to the beginning of the markdown
    # string.
    metadata = '% {0}\n% {1}\n% {2}\n'.format(title, author,
                                              time.strftime('%d/%m/%Y'))

    markdown = metadata + markdown

    # Create list of pandoc settings, including theme files
    pandoc_arguments = ['--standalone',
                        '--toc',
                        '--smart',
                        '--html-q-tags']

    html_name = '{0}.html'.format(theme)
    css_name = '{0}.css'.format(theme)

    theme_directory = os.path.join(base_directory, 'themes')

    header_files = [html_name, 'before.html', css_name, 'after.html']

    for filename in header_files:
        full_path = os.path.join(theme_directory, filename)
        pandoc_arguments.append('--include-in-header={0}'.format(full_path))

    # Define the filters to use
    filter_path = os.path.join(base_directory, 'filters', 'new_HTML.py')

    # Get the generated HTML as a string
    html = pypandoc.convert_text(markdown, format='md', to='html',
                                 extra_args=pandoc_arguments,
                                 filters=[filter_path])

    # Replace dictionary words in the HTML with their definitions
    html = load_words_from_lexicon(html, lexicon)

    # Save the HTML to a temporary file
    # temp_filename = 'temp/{0}.html'.format(str(time.time()))
    temp_filename = 'grammar.html'
    with open(os.path.join(base_directory, 'temp', temp_filename), 'w') as f:
        f.write(html)

    return temp_filename


def load_words_from_lexicon(html, lexicon_string):
    '''Replace all words surrounded by double curly braces in the HTML string
    (created by the filter) with their dictionary definition according to the
    given lexicon.'''

    # Read the lexicon string as a CSV file.
    lexicon = convert_lexicon(lexicon_string)

    match_list = re.findall(r'{{[a-z]*}}', html, re.I)

    for match in match_list:
        word = match[2:-2]
        try:
            local_word = lexicon[word]['local_word']
            definition = lexicon[word]['definition']
            part = lexicon[word]['part_of_speech']

            definition_block = string.Template(DEFINITION_TEMPLATE)
            definition_HTML = definition_block.substitute(word=word,
                                                          local_word=local_word,
                                                          definition=definition,
                                                          part=part)

            html = html.replace(match, definition_HTML)

        except KeyError:
            pass

    return html


def convert_lexicon(lexicon_string):
    '''Convert a lexicon string (CSV) to a dictionary. Each key is a word and
    each value is a dictionary containing information about the word.'''
    word_lines = csv.reader(lexicon_string.split('\n'))

    lexicon = {}
    for line in word_lines:
        try:
            word_data = {'local_word': line[1],
                         'definition': line[4],
                         'part_of_speech': line[2]}
            lexicon[line[0]] = word_data
        except IndexError:
            pass

    return lexicon
