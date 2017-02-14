import panflute as pf
import string

EXAMPLE_TEMPLATE = '''
\\exdisplay
\\begingl[aboveglftskip=-2.25pt]
\\gla $target//
\\glc $gloss//
\\glft `$native'//
\\endgl
\\xe
'''

EXAMPLE_BLOCK_TEMPLATE = '''
\\begin{sentence}
$examples
\\end{sentence}
'''

RULE_TEMPLATE = '''
\\begin{definition}[$name]
~\\\\
\\textsc{$definition}
\\end{definition}
'''


def create_example(number, elem):
    '''Create an example LaTeX block.'''
    examples = []

    # For each example in the list, extract each part of the example.
    # Then substitute the parts into the example template.
    for example in elem.content:
        content = [line.strip() for line in
                   pf.stringify(example).split(',')]

        parts = {}
        parts['target'] = content[0]

        # Format the gloss in small caps
        parts['gloss'] = ' '.join(['\\textsc{' + x + '}' for x in
                                   content[1].split(' ')])

        parts['native'] = content[2]

        example_LaTeX = string.Template(EXAMPLE_TEMPLATE).substitute(parts)
        examples.append(example_LaTeX)

    # Substitute examples into the block div.
    block_settings = {'examples': '\n'.join(examples)}
    example_block = string.Template(EXAMPLE_BLOCK_TEMPLATE)

    return pf.RawBlock(example_block.substitute(block_settings),
                       format='latex')


def create_rule(elem):
    '''Create a rule HTML block.'''
    name, definition = pf.stringify(elem)[3:].split(':')

    substitutions = dict(name=name, definition=definition.strip())
    rule_LaTeX = string.Template(RULE_TEMPLATE).substitute(substitutions)
    pf.debug(rule_LaTeX)
    return pf.RawBlock(rule_LaTeX, format='latex')


def create_definition(elem):
    '''Italicise language words.'''
    word = pf.stringify(elem)

    return pf.RawInline('\\textit{' + word + '}', format='latex')


def linguistic_features(elem, doc):
    ''' Detect individual syntax features and delegate to their creation
    functions.'''
    if type(elem) == pf.OrderedList and elem.style == 'Example':
        return create_example(elem.start, elem)
    elif type(elem) == pf.Para and pf.stringify(elem).startswith('(*)'):
        return create_rule(elem)
    elif type(elem) == pf.Code:
        return create_definition(elem)
    else:
        return elem


def main(doc=None):
    return pf.run_filter(linguistic_features, doc=doc)


if __name__ == '__main__':
    main()
