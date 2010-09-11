# -*- coding: utf-8 -*-

"""
    rst_resume.deploy
    ~~~~~~~~~~~~~~~~~
    
    A python module to create the common needed files for a resume.
    
    :copyright: (c) 2010 by Rafael Goncalves Martins
    :license: BSD, see LICENSE for more details.
"""

__all__ = ['run']

from codecs import open
import os, sys

files = {
    'resume.cfg': """\
# -*- coding: utf-8 -*-

import os
cwd = os.path.dirname(os.path.abspath(__file__))

AUTHOR = 'Your name goes here'
RST_FILE = os.path.join(cwd, 'resume.rst')
STYLESHEETS_DIR = os.path.join(cwd, 'stylesheets')
""",
    'resume.rst': """\
.. Add a ``.. language:`` comment for each language you want to enable.
   The language should be available for rst-resume.


.. language: en-us

Put your English data here...

""",
    'resume.wsgi': """\
# -*- coding: utf-8 -*-

import os

cwd = os.path.dirname(os.path.abspath(__file__))
os.environ['RST_RESUME_SETTINGS'] = os.path.join(cwd, 'resume.cfg')

from rst_resume import app as application

""",
    'stylesheets': None,
}


def run(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    for file in files:
        try:
            my_file = os.path.join(directory, file)
            if not os.path.exists(my_file):
                if files[file] is not None:
                    with open(my_file, 'w', encoding='utf-8') as fp:
                        fp.write(files[file])
                else:
                    os.makedirs(os.path.join(directory, 'stylesheets'))
        except Exception, err:
            print >> sys.stderr, err
            return os.EX_OSERR
    return os.EX_OK


if __name__ == '__main__':
    sys.exit(run('.'))
