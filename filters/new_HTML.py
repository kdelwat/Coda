import panflute as pf
import string

EXAMPLE_TEMPLATE = '''
<div class="example-target">$target</div>
<div class="example-target-expanded">$expanded_target</div>
<div class="example-gloss">$gloss</div>
<div class="example-native">$native</div>
'''

EXAMPLE_BLOCK_TEMPLATE = '''
<div class="example" id="example-$number">
    <span class="example-tag">($number)</span>
    $examples
</div>
'''

RULE_TEMPLATE = '''
<div class="rule">
    <div class="rule-name">$name</div>
    <div class="rule-definition">$definition</div>
</div>
'''


def strip_example(example):
    '''Takes a full example string, including hyphens and null morphemes, and
    returns its actual realisation.'''
    return example.replace('-', '').replace('ø', '')


def create_example(number, elem):
    '''Create an example HTML block.'''
    examples = []

    # For each example in the list, extract each part of the example.
    # Then substitute the parts into the example template.
    for example in elem.content:
        content = [line.strip() for line in
                   pf.stringify(example).split(',')]

        parts = {}
        parts['target'] = strip_example(content[0])
        parts['expanded_target'] = content[0]
        parts['gloss'] = content[1]
        parts['native'] = content[2]

        example_HTML = string.Template(EXAMPLE_TEMPLATE).substitute(parts)
        examples.append(example_HTML)

    # Substitute examples into the block div.
    block_settings = {'number': number, 'examples': '<br>'.join(examples)}
    example_block = string.Template(EXAMPLE_BLOCK_TEMPLATE)

    return pf.RawBlock(example_block.substitute(block_settings), format='html')


def create_rule(elem):
    '''Create a rule HTML block.'''
    name, definition = pf.stringify(elem)[3:].split(':')

    substitutions = dict(name=name, definition=definition)
    rule_HTML = string.Template(RULE_TEMPLATE).substitute(substitutions)

    return pf.RawBlock(rule_HTML, format='html')


def linguistic_features(elem, doc):
    ''' Detect individual syntax features and delegate to their creation
    functions.'''
    if type(elem) == pf.OrderedList and elem.style == 'Example':
        return create_example(elem.start, elem)
    elif type(elem) == pf.Para and pf.stringify(elem).startswith('(*)'):
        return create_rule(elem)
    else:
        return elem


def main(doc=None):
    return pf.run_filter(linguistic_features, doc=doc)


if __name__ == '__main__':
    main()
