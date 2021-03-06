# -*- coding: utf-8 -*-

"""
    rst_resume
    ~~~~~~~~~~
    
    A small Flask application to serve a resume written using
    RestructuredText in several formats: html, pdf, odt or raw rst.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

from codecs import open
from contextlib import closing
from cStringIO import StringIO
from docutils.core import publish_string
from flask import Flask, Response, redirect, request, render_template
from flaskext.babel import Babel, lazy_gettext as _
from glob import glob
from rst2pdf.createpdf import RstToPdf

import os, re
cwd = os.path.dirname(os.path.abspath(__file__))

__author__ = 'Rafael Goncalves Martins'
__email__ = 'rafael@rafaelmartins.eng.br'

__description__ = """\
A small Flask application to serve a resume written using
RestructuredText in several formats: html, pdf, odt or raw rst.
"""

__url__ = 'https://github.com/rafaelmartins/rst-resume'
__copyright__ = '(c) 2010 %s <%s>' % (__author__, __email__)
__license__ = 'BSD'

__version__ = '0.1pre'

# code snippet from sphinx
# http://bitbucket.org/birkenfeld/sphinx/src/tip/sphinx/__init__.py
if '+' in __version__ or 'pre' in __version__:
    # try to find out the changeset hash if checked out from hg, and append
    # it to __version__ (since we use this value from setup.py, it gets
    # automatically propagated to an installed copy as well)
    try:
        import subprocess
        p = subprocess.Popen(
            ['hg', 'id', '-i', '-R', os.path.join(cwd, '..')],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE
        )
        out, err = p.communicate()
        if out:
            __version__ += '/' + out.strip()
    except Exception:
        pass


app = Flask(__name__)
babel = Babel(app)
app.config['RST_FILE'] = os.path.join(cwd, 'resume.rst')
app.config['ALLOWED_LOCALES'] = {
    'en-us': {
        'locale': 'en_US',
        'name': 'English',
        'help': 'Please select one of the languages above.',
    },
    'pt-br': {
        'locale': 'pt_BR',
        'name': u'Português do Brasil',
        'help': 'Por favor escolha um dos idiomas acima.',
    },
}
app.config['ALLOWED_FORMATS'] = [
    ('html', _('HyperText Markup Language'), 'HTML'),
    ('pdf', _('Portable Document Format'), 'PDF'),
    ('odt', _('OpenDocument Text'), 'ODT'),
    ('rst', _('reStructuredText'), 'RST'),
]

app.config.from_envvar('RST_RESUME_SETTINGS', True)


@app.context_processor
def setup_jinja2():
    return dict(
        author = app.config.get('AUTHOR', _('Your name')),
        allowed_locales = app.config.get('LOCALES', {}),
        version = __version__
    )


@app.before_request
def available_locales():
    locales_from_rst = split_rst_file().keys()
    app.config['LOCALES'] = {}
    for locale in app.config['ALLOWED_LOCALES']:
        if locale in locales_from_rst:
            app.config['LOCALES'][locale] = \
                app.config['ALLOWED_LOCALES'][locale]


@babel.localeselector
def get_locale():
    match = re.match(r'/(?P<locale>[^/]+).*', request.path)
    if match is not None:
        locale = match.group('locale')
        if locale in app.config['LOCALES']:
            return app.config['LOCALES'][locale]['locale']


def load_stylesheets(pattern):
    default_dir = os.path.join(cwd, 'stylesheets')
    config_dir = app.config.get('STYLESHEETS_DIR', None)
    stylesheets = glob(os.path.join(default_dir, pattern))
    if config_dir is not None:
        stylesheets += glob(os.path.join(config_dir, pattern))
    return stylesheets


def split_rst_file(locale=None):
    with open(app.config['RST_FILE'], 'r', encoding='utf-8') as fp:
        pieces = re.split(r'.. language: ([a-zA-Z-]+)', fp.read())
    rd = {}
    for i in range(1, len(pieces), 2):
        rd[pieces[i]] = pieces[i+1].strip()
    if locale is None:
        return rd
    return rd.get(locale, None)


def docutils_base(locale, output_format='html', **extra_settings):
    settings = {
        'input_encoding': 'utf-8',
        'output_encoding': 'utf-8',
        'doctitle_xform': 0,
    }
    settings.update(extra_settings)
    rs = publish_string(
        source = split_rst_file(locale),
        writer_name = output_format,
        settings_overrides = settings
    )
    return rs


def html_output(locale, **extra_settings):
    if 'stylesheet_path' not in extra_settings:
        stylesheets = load_stylesheets('*.css')
        extra_settings['stylesheet_path'] = ','.join(stylesheets)
        # force embed_stylesheet, because we don't serve CSS files statically
        extra_settings['embed_stylesheet'] = True
    return docutils_base(locale, 'html4css1', **extra_settings)


def odt_output(locale, **extra_settings):
    return docutils_base(locale, 'odf_odt', **extra_settings)


def pdf_output(locale, **extra_settings):
    if 'styleshees' not in extra_settings:
        extra_settings['stylesheets'] = load_stylesheets('*.style')
    if 'breaklevel' not in extra_settings:
        extra_settings['breaklevel'] = 0
    parser = RstToPdf(**extra_settings)
    with closing(StringIO()) as fp:
        parser.createPdf(
            text = split_rst_file(locale),
            output = fp,
        )
        rs = fp.getvalue()
    return rs


@app.route('/<locale>/resume.html')
def html(locale):
    return html_output(locale)


@app.route('/<locale>/resume.pdf')
def pdf(locale):
    return Response(pdf_output(locale), mimetype = 'application/pdf')


@app.route('/<locale>/resume.odt')
def odt(locale):
    return Response(
        odt_output(locale),
        mimetype = 'application/vnd.oasis.opendocument.text',
    )


@app.route('/<locale>/resume.rst')
def rst(locale):
    return Response(split_rst_file(locale), mimetype = 'text/plain')


@app.route('/<locale>/')
def list_files(locale):
    return render_template('list.html',
        current_locale = locale,
        allowed_formats = app.config['ALLOWED_FORMATS']
    )


@app.route('/')
def home():
    if len(app.config['LOCALES']) == 1:
        locale = app.config['LOCALES'].keys()[0]
        return redirect(request.url_root + locale + '/')
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
