ArXiv Update CLI
================
Fetch new articles on arXiv by keywords and authors.

CLI tool to fetch new articles on arXiv in selected categories (e.g. quant-ph) filtered by keywords or authors.
The results are printed in the command line but they can also be written into a file or be sent by email so that
the script can be run automatically with `cron <https://en.wikipedia.org/wiki/Cron>`_. There is also an interactive command line interface to browse the results.

The script will fetch the articles on arXiv that

 + were *submitted/updated* after the last update date (or the provided date, see ``--since`` option)

 **AND**

 + belong to one of the *categories*

 **AND**

 + (one of the *authors* is in the author list) **OR** (one of the *keywords* is in the title or abstract)

All the *options* are set in the configuration file. Note that keywords can contain spaces, e.g. *machine learning*.

The ``query`` subcommand allows for sending custom queries to the arXiv API, see section `Custom queries to the ArXiv API`_.

Thank you to arXiv for use of its open access interoperability.


.. contents:: Table of Contents

Dependencies
------------

- Python 3
- `feedparser <https://pypi.python.org/pypi/feedparser>`_

Optional dependenices:

- `keyring <https://pypi.org/project/keyring/>`_: Store password of email account in system keyring (for the ``--email`` option).
- `pyreadline3 <https://pypi.org/project/pyreadline3/>`_: Tab autocompletion in interactive mode ``--interactive`` (Windows only since the ``readline`` module is available on the other OSs).
- `pyzotero <https://pypi.org/project/pyzotero/>`_: Import articles in Zotero Library (interactive mode).

- `tqdm <https://pypi.org/project/tqdm/>`_: Progressbar for file downloads.

Running the tests in Windows also requires `pynput <https://pypi.org/project/pynput/>`_.


Install
-------

The script can be installed with pip

::

    $ pip install arxiv_update_cli

or by downloading the `source code <https://gitlab.com/j_4321/arxivscript/-/tags>`_ and running

::

    $ python setup.py install

from within the folder.


For Archlinux users, there is a ``PKGBUILD`` file in ``packaging_archlinux/``.


Quick start
-----------

Execute ``arxiv-update-cli``, or if the package is not installed, execute ``arxiv_update_cli.py`` with python.

Usage:

::

    arxiv_update_cli.py [-h] [-e] [-s YYYY-MM-DD] [-c [FILE]] [-v] [-o FILE] [-f FORMAT][-d FOLDER] [-i] [--log] [--max-trials MAX_TRIALS] {query} ...


Options:

=============================================  ========================================================================================
\-h, \-\-help                                  show the help message and exit

\-e, \-\-email                                 send result by email using SMTP (you will be prompted for missing settings)

\-s YYYY-MM-DD, \-\-since YYYY-MM-DD           fetch update since YYYY-MM-DD 00:00

\-c [FILE], \-\-config [FILE]                  config file to use or print path to default one and exit if no argument is provided

\-v, \-\-version                               show version and exit

\-o FILE, \-\-output FILE                      write the output into FILE

\-d FOLDER, \-\-download FOLDER                download all the articles as pdf fiĺes in FOLDER (folder must exist)

\-i, \-\-interactive                           display result in interactive CLI

\-f FORMAT, \-\-format FORMAT                  article formatting: "id" (arXiv id, "title" (title - date),
                                               "condensed" (title, authors, date - url),
                                               "full" (title, authors, date, abstract, url, ...), or "bibtex"

\-\-log                                        show path to log file and exit

\-\-max-trials MAX_TRIALS                      maximum number of attempts to fetch the data when there is some connection issue

\-\-nb-results-per-query NB_RESULTS_PER_QUERY  split queries in chunks of NB_RESULTS_PER_QUERY. Sometimes there are issues with the API 
                                               and changing the number of results queried in one call helps solve them.

query                                          subcommand to send a custom query the arXiv API, see `Custom queries to the ArXiv API`_

=============================================  ========================================================================================

If no configuration file exists, one will be created. Then, you can edit the
*categories*, *keywords* and *authors* fields and run the script again.


Configuration file
------------------

The location of the configuration file is given by the ``-c`` option. The file contains to sections:

- General: configuration of the filtering of the arXiv updates.
- Email: email settings to receive the updates by email. You will be prompted to fill in the missing email settings when you run the script.
- Zotero: settings to access Zotero API and be able to import articles in `Zotero <https://www.zotero.org>`_ from the interactive CLI (requires pyzotero).

There are comments in the file explaining how to fill in the options in each section.
Note that some options in the configuration file can be overriden by command line arguments.


Custom queries to the ArXiv API
-------------------------------

Usage:

::

    arxiv_update_cli.py [-e/o/f/d/i] query [-h] [--api-query-help] [--id-list ID [ID ...]] [--sort-by SORT_BY] [--sort-order ORDER]
                                                  [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD] [--max-results N] [QUERY]


Options:

=========================  ==============================================================================================
\-h, \-\-help              show this help message and exit

\-\-api-query-help         display API search query help and exit

\-\-id-list ID [ID ...]    only results with given arXiv ids

\-\-sort-by SORT_BY        sort results by "relevance", "lastUpdatedDate" [default], or "submittedDate"

\-\-sort-order ORDER       sort results in "ascending" or "descending" [default] order

\-\-start-date YYYY-MM-DD  minimum date

\-\-end-date YYYY-MM-DD    maximum date

\-\-max-results N          display only the N first results
=========================  ==============================================================================================


Positional arguments:

=========================  ==============================================================================================
QUERY                      API search query, typical form: ``<field>:<query>+<operator>+<field>:<query>...``
=========================  ==============================================================================================

Fields
~~~~~~

======  ========================
prefix  explanation
======  ========================
ti      Title
au      Author
abs     Abstract
co      Comment
jr      Journal Reference
cat     Subject Category
rn      Report Number
all     All of the above
======  ========================

**Example:**: ``ti:checkerboard`` to list the articles whose titles contain the word *checkerboard*.


Operators
~~~~~~~~~

Several fields can be combined using boolean operators:

- AND
- OR
- ANDNOT

**Example:**: ``au:del_maestro+ANDNOT+ti:checkerboard`` to list the articles of *Adrian DelMaestro* with titles that do not contain the word *checkerboard*


Grouping operators
~~~~~~~~~~~~~~~~~~

- More complex queries can be used by using parentheses for grouping the Boolean expressions.
- Entire phrases can be used in a search field by enclosing them in double quotes.

The grouping operators are encoded in the following way:

==============  ========  ========================================================================
symbol          encoding  explanation
==============  ========  ========================================================================
( )             %28 %29   Used to group Boolean expressions for Boolean operator precedence.
""              %22 %22   Used to group multiple words into phrases to search a particular field.
space           \+        Used to extend a search_query to include multiple fields.
==============  ========  ========================================================================

**Example**: ``ti:%22quantum+criticality%22`` to list the articles whose titles contain the words *quantum* and *criticality*.


More about the arXiv API: https://arxiv.org/help/api/user-manual


Automatic execution
-------------------

Once the email setttings have been configured and the password saved in the keyring, regular executions of ``arxiv_update_cli`` can be scheduled. For instance, one can receive daily email updates at 9:30 on working days with the following `crontab <https://en.wikipedia.org/wiki/Cron>`_ (Unix)

::

    30 09 * * 1-5 arxiv-update-cli -e


Troubleshooting
---------------

Errors are logged in the file ``arxiv_update_cli.log`` in the system's temporary folder. Use the ``--log`` option to display the path.

License
-------

| Copyright (c) 2022-2025 Juliette Monsel
|
| Permission is hereby granted, free of charge, to any person obtaining a copy
| of this software and associated documentation files (the "Software"), to deal
| in the Software without restriction, including without limitation the rights
| to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
| copies of the Software, and to permit persons to whom the Software is
| furnished to do so, subject to the following conditions:
|
| The above copyright notice and this permission notice shall be included in all
| copies or substantial portions of the Software.
|
| THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
| IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
| FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
| AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
| LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
| OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
| SOFTWARE.


Changelog
---------
+ arxiv-update-cli 1.2.1
    * Fix recent issues related to the retrieval of the data from the API.
    * Add option (in configuration file) to attach pdf file to zotero item.
    * Add option (in configuration file) to choose collection in Zotero. The default collection is still determined by the `collection_key` option.
    * Add option to change the number of results per query when fetching results (in configuration file and command line). Sometimes there are issues with the API and changing the number of results queried in one call helps solve them.
    * Add option to change the maximum number of trials (in configuration file).

+ arxiv-update-cli 1.2.0
    * Add interactive CLI to visualize results in the terminal
    * Add possibility to import articles in Zotero
    * Handle better failures to retrieve results from arXiv API (especially Connection reset by peer), trying several times and not saving the new latest update date when failing

+ arxiv-update-cli 1.1.0
    * Add *format* option to choose how the articles are displayed
    * Add *output* option to write the results in a text file
    * Add direct queries to the arXiv API
    * Make compatible with Windows

+ arxiv-update-cli 1.0.3
    * Set default config path to local folder if the script is not installed

+ arxiv-update-cli 1.0.2
    * Add comment field to the article summary
    * Color the article URL in blue like the DOI link in the terminal

+ arxiv-update-cli 1.0.1
    * Fix URL in PKGBUILD and setup.py

+ arxiv-update-cli 1.0.0
    * First release
