from pandocfilters import toJSONFilter, RawBlock, Para, Str, RawInline
import csv


def shrink_list(pandoc_list):
    '''Convert crazy pandoc nested list of Str and Space into
    a nice string.'''
    string = ''
    for item in pandoc_list:
        if item['t'] == 'Str':
            string += item['c']
        elif item['t'] == 'Space':
            string += ' '
    return string


def strip_example(example):
    '''Takes a full example string, including hyphens and null morphemes, and
    returns its actual realisation.'''
    return example.replace('-', '').replace('ø', '')


def create_example(example_no, example_list):
    all_examples = []

    for example in example_list:
        examples = [line.strip() for line in shrink_list(example[0]['c']).split(',')]
        target = '<div class="example-target">{0}</div>'.format(strip_example(examples[0]))
        target_expanded = '<div class="example-target-expanded">{0}</div>'.format(examples[0])
        gloss = '<div class="example-gloss">{0}</div>'.format(examples[1])
        native = '<div class="example-native">{0}</div>'.format(', '.join(examples[2:]))
        all_examples.append(target + target_expanded + gloss + native)

    example_id = 'example-' + str(example_no)
    id_span = '<span class="example-tag">({0})</span>'.format(example_no)
    html = '<div class="example" id="{0}">{1}{2}</div>'.format(example_id, id_span, '<br>'.join(all_examples))

    return RawBlock('html', html)


def create_rule(rule_list):
    raw = shrink_list(rule_list)[3:].split(':')
    rule_name = '<div class="rule-name">{0}</div>'.format(raw[0])
    rule_definition = '<div class="rule-definition">{0}</div>'.format(raw[1].strip())
    html = '<div class="rule">' + rule_name + rule_definition + '</div>'

    return RawBlock('html', html)


def create_definition(item):
    word = item['c'][1].strip()
    return RawInline('html', '{{' + word + '}}')

def filter_paragraph(paragraph):
    filtered = []
    for item in paragraph:
        if item['t'] == 'Code':
            filtered.append(create_definition(item))
        else:
            filtered.append(item)
    return Para(filtered)


def filter(key, value, format, meta):
    if key == 'OrderedList':
        if value[0][1]['t'] == 'Example':
            return create_example(value[0][0], value[1:][0])
    elif key == 'Para':
        if value[0]['t'] == 'Str':
            if value[0]['c'][0:3] == '(*)':
                return create_rule(value)

        return filter_paragraph(value)


if __name__ == "__main__":
    toJSONFilter(filter)
