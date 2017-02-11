import time
import pypandoc
import os

base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(base_directory)


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

    # Get the generated HTML as a string
    html = pypandoc.convert_text(markdown, format='md', to='html',
                                 extra_args=pandoc_arguments)

    # Save the HTML to a temporary file
    # temp_filename = 'temp/{0}.html'.format(str(time.time()))
    temp_filename = 'grammar.html'
    with open(os.path.join(base_directory, 'temp', temp_filename), 'w') as f:
        f.write(html)

    return temp_filename
