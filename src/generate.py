import time
import pypandoc
import os
import re
import csv
import string
import copy
from itertools import groupby
import yaml

LEXICON_COLUMN_DEFAULTS = {'word': 0, 'local': 1, 'part_of_speech': 3,
                           'definition': 5, 'pronunciation': 2}

base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(base_directory, 'latexthemes', 'Dictionary.tex')) as f:
    DICTIONARY_TEMPLATE = f.read()

DEFINITION_TEMPLATE = '''
<span class="word">$word
    <span class="definition">$local_word ($part)<br>
        <span class="full-definition">$definition</span>
    </span>
</span>
'''

DICTIONARY_ENTRY_TEMPLATE = '''
\entry{$word}{$pronunciation}{$part_of_speech}{$local_word: $definition}
'''

HTML_DICTIONARY_TEMPLATE = '''
# Lexicon
$definitions
'''

HTML_DICTIONARY_ENTRY_TEMPLATE = '''
<div class="lexicon-entry">
<h3 class="lexicon-word">$word</h5>
<h4 class="lexicon-info">$pronunciation, $part_of_speech</h4>
<p class="lexicon-definition"><span class="lexicon-local">$local_word</span> $definition</p>
</div>
'''

METADATA_TEMPLATE = '''
---
title: $title
subtitle: $subtitle
author: $author
year: $year
papersize: $papersize
geometry: $geometry
fontsize: $fontsize
dictionary: $dictionary
---
'''


def generate(markdown_file_strings, lexicon_file, settings):
    concatenated_markdown = '\n'.join(markdown_file_strings)

    lexicon_columns = read_lexicon_columns(settings)

    if settings['format'] == 'HTML':
        filename = generate_HTML(concatenated_markdown, lexicon_file,
                                 lexicon_columns=lexicon_columns,
                                 theme=settings['theme'],
                                 title=settings['grammarTitle'],
                                 subtitle=settings['grammarSubtitle'],
                                 author=settings['author'])
    elif settings['format'] == 'LaTeX PDF':
        filename = generate_latex(concatenated_markdown, lexicon_file,
                                  lexicon_columns=lexicon_columns,
                                  layout=settings['layout'],
                                  title=settings['grammarTitle'],
                                  subtitle=settings['grammarSubtitle'],
                                  author=settings['author'])

    return filename


def read_lexicon_columns(settings):
    '''Given a settings dictionary, return a lexicon columns dictionary.'''
    equivalents = {'csvColumnWord': 'word',
                   'csvColumnLocal': 'local',
                   'csvColumnDefinition': 'definition',
                   'csvColumnPronunciation': 'pronunciation',
                   'csvColumnPartOfSpeech': 'part_of_speech'}

    columns = {}

    # Add an entry to overrides for each column included in the request.
    for old, new in equivalents.items():
        if old in settings:
            columns[new] = int(settings[old]) - 1

    return columns


def generate_latex(markdown, lexicon, lexicon_columns=LEXICON_COLUMN_DEFAULTS,
                   title='My language', subtitle='A grammar',
                   author='An author', layout='A4'):
    '''Takes a markdown string, a lexicon CSV string, and a number of settings.
    Creates a PDF document and returns the filename.'''

    template_directory = os.path.join(base_directory, 'latexthemes')

    # Create the lexicon as a LaTeX string.
    dictionary_string = create_latex_dictionary(lexicon, lexicon_columns)

    # Create a metadata block and add it to the beginning of the markdown
    # string.
    year = time.strftime('%Y')

    layouts = {'A4': {'papersize': 'a4paper',
                      'geometry':
                      'top=3cm,bottom=3cm,left=3cm,right=3cm,headsep=10pt,',
                      'fontsize': '11pt'},

               'A5': {'papersize': 'a5paper',
                      'geometry':
                      'top=1.5cm,bottom=1.5cm,left=1.75cm,right=1.75cm,headsep=10pt,',
                      'fontsize': '12pt'}}

    paper = layouts[layout]['papersize']
    font = layouts[layout]['fontsize']
    geometry = layouts[layout]['geometry']

    metadata = {'title': title, 'subtitle': subtitle, 'author': author, 'year':
                year, 'fontsize': font, 'papersize': paper, 'geometry':
                geometry, 'dictionary': dictionary_string}

    # Format metadata as YAML and add it before the rest of the file.
    markdown = '---\n' + yaml.dump(metadata) + '\n---\n' + markdown

    # Create list of pandoc settings, including template file
    pandoc_arguments = ['--standalone',
                        '--toc',
                        '--smart',
                        '--latex-engine=xelatex',
                        '--top-level-division=chapter']

    template_name = 'Default.tex'
    template_path = os.path.join(template_directory, template_name)
    pandoc_arguments.append('--template={0}'.format(template_path))

    # Create temporary filename for output
    temp_filename = 'grammar.pdf'
    temp_path = os.path.join(base_directory, 'temp', temp_filename)

    # Define the filters to use
    filter_path = os.path.join(base_directory, 'filters', 'LaTeX.py')

    pypandoc.convert_text(markdown, format='md', to='pdf',
                          outputfile=temp_path,
                          extra_args=pandoc_arguments,
                          filters=[filter_path])

    return temp_filename


def generate_HTML(markdown, lexicon, lexicon_columns=LEXICON_COLUMN_DEFAULTS,
                  theme='Default', title='My language', subtitle='A grammar',
                  author='An author'):
    '''Takes a markdown string, a lexicon CSV string, and a number of settings.
    Creates a full HTML document and returns the filename.'''

    # Create a metadata block and add it to the beginning of the markdown
    # string.
    metadata = {'title': title,
                'author': author,
                'date': time.strftime('%d/%m/%Y')}

    # Format metadata as YAML and add it before the rest of the file.
    markdown = '---\n' + yaml.dump(metadata) + '\n---\n' + markdown

    # Create the lexicon as a Markdown string and add it to the end of the
    # file.
    dictionary_string = create_html_dictionary(lexicon, lexicon_columns)
    markdown = markdown + dictionary_string

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
    html = load_words_from_lexicon(html, lexicon, lexicon_columns)

    # Save the HTML to a temporary file
    # temp_filename = 'temp/{0}.html'.format(str(time.time()))
    temp_filename = 'grammar.html'
    with open(os.path.join(base_directory, 'temp', temp_filename), 'w') as f:
        f.write(html)

    return temp_filename


def create_html_dictionary(lexicon_string, lexicon_columns):
    '''Convert the given lexicon string to a Markdown dictionary string for use in
    HTML.'''
    definitions = ''

    # Group words by letter
    groups = get_lexicon_groups(lexicon_string, lexicon_columns)

    entry_template = string.Template(HTML_DICTIONARY_ENTRY_TEMPLATE)

    for group in groups:
        for word in group[1]:
            entry = entry_template.substitute(word)
            definitions += entry

    # Substitute the created string into the template.
    return string.Template(HTML_DICTIONARY_TEMPLATE).substitute(definitions=definitions)


def create_latex_dictionary(lexicon_string, lexicon_columns):
    '''Convert the given lexicon string to a LaTeX dictionary string.'''
    definitions = ''

    # Group words by letter
    groups = get_lexicon_groups(lexicon_string, lexicon_columns)

    entry_template = string.Template(DICTIONARY_ENTRY_TEMPLATE)

    for group in groups:
        # Add letter label
        definitions += '\\section*{' + group[0].upper() + '}'

        definitions += '\\begin{multicols*}{2}'

        for word in group[1]:
            entry = entry_template.substitute(word)
            definitions += entry

        definitions += '\\end{multicols*}'

    # Substitute the created string into the template.
    return string.Template(DICTIONARY_TEMPLATE).substitute(definitions=definitions)


def get_lexicon_groups(lexicon_string, lexicon_columns):
    '''Given a lexicon string, return a list. Each item is a tuple, where the first
    item is a letter and the second is a list of word dictionaries that begin with
    that letter.'''
    groups = []

    # Read the lexicon string as a CSV file, deleting the header row.
    lexicon_dicts = convert_lexicon(lexicon_string, lexicon_columns)

    # Convert to a list.
    lexicon = list(zip(lexicon_dicts.keys(), lexicon_dicts.values()))

    # Sort alphabetically
    lexicon = sorted(lexicon, key=lambda x: x[0])

    # Group by first letter
    for first_letter, words in groupby(lexicon, lambda x: x[0][0]):
        # Add the conlang word to each word dictionary
        modified_words = []
        for word in words:
            modified_word = word[1]
            modified_word['word'] = word[0]
            modified_words.append(modified_word)

        groups.append((first_letter, modified_words))

    return groups


def load_words_from_lexicon(html, lexicon_string, lexicon_columns):
    '''Replace all words surrounded by double curly braces in the HTML string
    (created by the filter) with their dictionary definition according to the
    given lexicon.'''

    # Read the lexicon string as a CSV file.
    lexicon = convert_lexicon(lexicon_string, lexicon_columns)

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


def convert_lexicon(lexicon_string, lexicon_columns):
    '''Convert a lexicon string (CSV) to a dictionary. Each key is a word and
    each value is a dictionary containing information about the word.'''
    word_lines = list(csv.reader(lexicon_string.split('\n')))[1:]

    lexicon = {}
    for line in word_lines:
        try:
            word_data = {'local_word': line[lexicon_columns['local']],
                         'definition': line[lexicon_columns['definition']],
                         'pronunciation': line[lexicon_columns['pronunciation']],
                         'part_of_speech': line[lexicon_columns['part_of_speech']]}
            lexicon[line[lexicon_columns['word']]] = word_data

        except IndexError:
            # Ignore empty lines
            if len(line) != 0:
                error = ('Could not correctly read CSV file! '
                         'Check that your column numbers are correct. '
                         'The error appears in the line: ' + ','.join(line))
                raise Exception(error)

    return lexicon
