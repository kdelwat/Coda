# Coda

*This is the server implementation. For the front-end, please see [LingTools](https://www.github.com/kdelwat/LingTools).*

Coda is a web tool which helps with the creation of professional-looking
language reference grammars from sources written in an extended version of
Markdown. Currently, both interactive HTML and PDF outputs are supported. A
lexicon file can also be provided to include a translation dictionary in the
output.

This server is built using [Flask](http://flask.pocoo.org/) to serve files
generated by [Pandoc](http://pandoc.org/) (using
the [pypandoc](https://github.com/bebraw/pypandoc) wrapper). Custom themes and
filters are used to style the output.

## Usage

To run the server locally:

```bash
git clone git@github.com:kdelwat/Coda.git
cd Coda
pip install -r requirements.txt
python main.py
```

## Output Examples

![LaTeX PDF output](http://imgur.com/ix0TLvF.png)

![HTML output](http://imgur.com/cN4gHMc.png)

## Credits

The default LaTeX theme is modified
from
[The Legrand Orange Book](http://www.latextemplates.com/template/the-legrand-orange-book) from
latextemplates.com. It is used under the terms of
the [CC BY-NC-SA 3.0](http://creativecommons.org/licenses/by-nc-sa/3.0/)
license.
