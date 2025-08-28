#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2022-2023 Juliette Monsel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import tempfile
import configparser
from datetime import datetime, timedelta, MINYEAR
import time
import argparse
import os
import shutil
import sys
import smtplib
import ssl
import getpass
import signal
from socket import error as SocketError
import re
from email.message import EmailMessage
import logging
from logging.handlers import TimedRotatingFileHandler
from glob import glob
from webbrowser import open as webopen
import urllib.request

try:
    import readline
except ImportError: # readline not available in Windows
    try:
        from pyreadline3 import Readline
    except ImportError:
        class Readline:
            "Dummy readline instance that does nothing."

            def set_completer_delims(*args):
                pass

            def set_completer(*args):
                pass

            def parse_and_bind(*args):
                pass

            def set_auto_history(*args):
                pass

    readline = Readline()


import feedparser
# optional feature: import in zotero using Pyzotero (interactive CLI)
try:
    from pyzotero import zotero, zotero_errors
    ZOTERO = True
except ImportError:
    ZOTERO = False
# optional feature: progressbar for pdf download  (interactive CLI)
try:
    from tqdm import tqdm

    # from https://github.com/tqdm/tqdm#hooks-and-callbacks
    # tqdm: A fast, Extensible Progress Bar for Python and CLI (v4.65.0).
    # Zenodo. https://doi.org/10.5281/zenodo.7697295

    class TqdmUpTo(tqdm):
        """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""
        def update_to(self, b=1, bsize=1, tsize=None):
            """
            b  : int, optional
                Number of blocks transferred so far [default: 1].
            bsize  : int, optional
                Size of each block (in tqdm units) [default: 1].
            tsize  : int, optional
                Total size (in tqdm units). If [default: None] remains unchanged.
            """
            if tsize is not None:
                self.total = tsize
            return self.update(b * bsize - self.n)  # also sets self.n = b * bsize

except ImportError:

    # dummy class

    class TqdmUpTo:
        def __init__(self, *args, desc='', **kw):
            print(f"{desc + ':'*bool(desc)} downloading ...")
        def __enter__(self):
            return self
        def __exit__(self, type, value, traceback):
            pass
        def update_to(self, b=1, bsize=1, tsize=None):
            pass

VERSION = "1.2.0"


# --- logging setup
# write the log in ~/.cache or the temporary folder (useful for debugging when executing the script with cron)
if os.path.exists(os.path.join(os.path.expanduser("~"), ".cache")):
    PATH_LOG = os.path.join(os.path.join(os.path.expanduser("~"), ".cache"), "arxiv_update_cli.log")
else:
    PATH_LOG = os.path.join(tempfile.gettempdir(), "arxiv_update_cli.log")
handler = TimedRotatingFileHandler(PATH_LOG, when='midnight',
                                   interval=1, backupCount=7)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)-15s %(levelname)s: %(message)s',
                    handlers=[handler])
logging.getLogger().addHandler(logging.StreamHandler())


# --- input with timeout
TIMEOUT = 60

# windows
try:
    import msvcrt

    def input_timeout(prompt="", timeout=TIMEOUT):
        """
        Input with timeout.

        Based on https://stackoverflow.com/questions/15528939/time-limited-input
        """
        timer = time.monotonic
        sys.stdout.write(prompt)
        sys.stdout.flush()
        endtime = timer() + timeout
        result = []
        while timer() < endtime:
            if msvcrt.kbhit():
                result.append(msvcrt.getwche())
                if result[-1] == '\r':
                    return ''.join(result[:-1])
            time.sleep(0.04) # just to yield to other processes/threads
        raise TimeoutError(f'No input after {timeout}s.')

except ImportError:

    def timedout(signum, frame):
        raise TimeoutError(f'No input after {TIMEOUT}s.')


    signal.signal(signal.SIGALRM, timedout)


    def input_timeout(prompt="", timeout=TIMEOUT):
        """Input with timeout."""
        signal.alarm(timeout)
        text = input(prompt)
        signal.alarm(0)       # remove alarm
        return text


# --- default config file
default_config = {
    "General": {
        "categories": "quant-ph",  # comma separated values, e.g. "quant-ph,cond-mat.mes-hall"
        "#categories": "comma separated values, e.g. quant-ph, cond-mat.mes-hall",
        "keywords": "",
        "#keywords": "comma separated list, e.g. machine learning, optomechanics",  # comment
        "authors": "",
        "#authors": "comma separated list of authors to follow",  # comment
        "sort_by": "submittedDate", # or "lastUpdatedDate"
        "#sort_by": "how the articles are sorted submittedDate/lastUpdatedDate",
        "format": "full",
        "#format": "how the articles are displayed: full/condensed/bibtex/title/id",
        "last_update": "",
        "#note": "The script will fetch the articles submitted/updated after the last update date that belong to one of the categories and fulfill: (one of the authors is in the author list) OR (one of the keywords is in the title or abstract)",
    },
    "Email": {
        "smtp_server": "",
        "#smtp_server": "smtp server used to send the results by email, e.g. smtp.gmail.com",
        "smtp_port": "465",
        "email": "",
        "#email": "email address to send the results by email",
    },
    "Zotero": {
        "#pyzotero": "Settings to access Zotero API with Pyzotero to add articles. See https://pyzotero.readthedocs.io/en/latest/",
        "library_id": "",
        "library_type": "user",
        "api_key": "",
        "collection_key": "",
        "#collection_key": "ID of default collection where the items will be added, leave empty for main collection.",
        "choose_collection": "true",
        "#choose_collection": "Whether to be prompted for the collection in which to add the imported items.",
        "attach_pdf": "false",
        "#attach_pdf": "Whether to download and attach the pdf of the article to the item.",
        "local_database_path": "",
        "#local_database_path": "Path of local Zotero database, e.g. ~/Zotero. Only needed to get access to the attachments when files are not stored online, leave empty otherwise.",
    },
    "API": {
        "nb_results_per_query": 50,
        "#nb_results_per_query": "Sometimes there are issues with the API and changing nb_results_per_query helps solve them.",
        "max_trials": 5,
        "#max_trials": "Maximum number of attempts to fetch the data when there is some connection issue.",
    }
}


CONFIG = configparser.ConfigParser()
for section, options in default_config.items():
    CONFIG.setdefault(section, options)


# config path
PATH = os.path.dirname(__file__)
CONFIG_PATHS = []

# user config file
if 'linux' in sys.platform:
    # local directory containing config files
    if os.path.exists(os.path.join(os.path.expanduser("~"), ".config")):
        CONFIG_PATHS.append(os.path.join(os.path.expanduser("~"), ".config", "arxiv_update_cli.ini"))
    else:
        CONFIG_PATHS.append(os.path.join(os.path.expanduser("~"), ".arxiv_update_cli"))
else:
    # local directory containing config files
    CONFIG_PATHS.append(os.path.join(os.path.expanduser("~"), "arxiv_update_cli", "arxiv_update_cli.ini"))

# local folder config file (not installed), takes precedence over user config
if os.access(PATH, os.W_OK):
    CONFIG_PATHS.append(os.path.join(PATH, "arxiv_update_cli.ini"))

def save_config(filepath):
    with open(filepath, 'w') as file:
        CONFIG.write(file)


# --- keyring (for email sending)
try:
    import keyring
except ImportError:

    def store_pwd_in_keyring(username, pwd):
        pass

    def get_pwd_from_keyring(username):
        pass

else:
    if "linux" in sys.platform:
        try:
            # get the keyring to work when script is called from cron
            os.environ['DBUS_SESSION_BUS_ADDRESS'] = f'unix:path=/run/user/{os.getuid()}/bus'
            os.environ['DISPLAY'] = ':0'
        except Exception:
            pass

    def store_pwd_in_keyring(username, pwd):
        try:
            keyring.set_password("arxiv_update_cli", username, pwd)
        except keyring.errors.KeyringError:
            return


    def get_pwd_from_keyring(username):
        try:
            return keyring.get_password("arxiv_update_cli", username)
        except keyring.errors.KeyringError:
            return


# --- command line autocompletion
readline.set_completer_delims('')
readline.parse_and_bind('tab: complete')
readline.set_auto_history(False)


class BaseCompleter:
    """Base class for command line autocompletion with readline."""

    def __init__(self):
        """Create custom command line completer."""
        self.matches = []  # cache completions

    @staticmethod
    def get_matches(text):
        """Return autocompletion results."""
        return []  # to override in children classes

    def complete(self, text, state):
        """Return the possible completion for readline."""
        if state == 0:  # on first trigger, build possible matches
            self.matches = self.get_matches(text)
        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None


class OptionCompleter(BaseCompleter):
    """Command line autocompletion from list of options."""

    def __init__(self, options):
        """Create custom command line completer from list of options."""
        BaseCompleter.__init__(self)
        self.options = sorted(options)

    def __repr__(self):
        return "<OptionCompleter {}>".format(", ".join([f"'{opt}'" for opt in self.options]))

    def __str__(self):
        return ", ".join([f"'{opt}'" for opt in self.options])

    def add(self, option):
        """Add option to the autocompletion list."""
        self.options.append(option)
        self.options.sort()

    def get_matches(self, text):
        if text:  # cache matches (entries that start with entered text)
            return [s for s in self.options if s and s.startswith(text)]
        else:  # no text entered, all matches possible
            return self.options[:]


class PathCompleter(BaseCompleter):
    """Command line autocompletion for paths."""

    @staticmethod
    def get_matches(text):
        return sorted(glob(os.path.expanduser(text) + '*'))


# --- intractive CLI

class BaseCLI:
    """Base interactive client."""

    def __init__(self, header, exit_answers=('q', 'quit')):
        """Create the interactive client."""
        self.header = header
        self._re_ansi = re.compile(r"\x1b\[((\d+;)*\d+)m")
        self._usage = [("  •  \33[4mq\33[0muit", "quit")]
        self._abbrev = ['q']
        # command line prompt
        self._prompt = '> Action [{}]: '
        # command line autocompletion
        self.completer = OptionCompleter([ans for ans in exit_answers if len(ans) > 1])
        # answers (=user input) that end the interactive loop
        self.exit_answers = exit_answers
        # current user input
        self.answer = ""
        # menu actions
        self._actions = {}

    def add_action(self, command, answer, abbrev=1, desc=''):
        """
        Associate the user input ANSWER with action COMMAND.

        Arguments:
            * command : function
                Function taking no argument that will be executed when the user
                input is ANSWER. If COMMAND returns "break", it will end the
                interactive loop.

            * answer : str
                Answer from the user to the input prompt that will
                trigger COMMAND.

            * abbrev : int
                Number of letters of the abbreviation of ANSWER. The input
                consisting of the ABBREV fisrt letters of each word in ANSWER
                will also trigger COMMAND. If ABBREV <= 0, don't use any abbreviation.
                E.g. if ANSWER is "hide all" and ABBREV is 1, then "ha" will also
                trigger the command.
        """
        self._actions[answer] = command
        self.completer.add(answer)
        if abbrev > 0:
            words = answer.split()
            ans = ''.join(word[:abbrev] for word in words)
            self._actions[ans] = command
            self._abbrev.append(ans)
            words = [f"\33[4m{word[:abbrev]}\33[0m{word[abbrev:]}" for word in words]
            self._usage.append((f"  •  {' '.join(words)}", desc))
        else:
            self._abbrev.append(answer)
            self._usage.append((f"  •  {answer}", desc))

    def _pre_prompt(self):
        """Code to execute before showing input prompt."""

    def reset(self):
        pass

    def display_usage(self):
        """Display header and options."""
        print(self.header)
        len_usage = {usage: len(self._re_ansi.sub('', usage)) for usage, desc in self._usage}
        usage_length = max(len_usage.values()) + 1
        self._usage.sort()
        for usage, desc in self._usage:
            padding = usage_length - len_usage[usage]
            print(f'{usage}{" "*padding}' + f'--  {desc}' * bool(desc))
        print("")

    def interact(self):
        """Launch interactive loop."""
        self.reset()
        self.display_usage()  # show header and options
        readline.set_completer(self.completer.complete) # set command line autocompletion
        prompt = self._prompt.format("/".join(sorted(self._abbrev)))
        self.answer = ""
        try:
            while self.answer not in self.exit_answers:
                if not self.answer:
                    pass
                else:
                    action = self._actions.get(self.answer)
                    if action is None:
                        print(f'\33[91mInvalid action "{self.answer}".\33[0m')
                    else:
                        if action() == "break":
                            return
                self._pre_prompt()
                self.answer = input(prompt).strip()
        except KeyboardInterrupt:
            print("\n\33[91mKeyboardInterrupt\33[0m")
        except EOFError:
            sys.exit()


class InteractiveCLI(BaseCLI):
    def __init__(self, header, raw_entries, formatted_entries):
        BaseCLI.__init__(self, header)
        self.path_completer = PathCompleter()
        self.entries = raw_entries
        self.formatted_entries = formatted_entries
        self.index = 0
        self.add_action(self.next, 'next', desc='next article')
        self.add_action(self.prev, 'prev', desc='previous article')
        self.add_action(self.open, 'open', desc='open on arXiv')
        self.add_action(self.download, 'download', desc='download article')
        if ZOTERO:
            try:
                self.zotero = zotero.Zotero(CONFIG.get("Zotero", "library_id"),
                                            CONFIG.get("Zotero", "library_type"),
                                            CONFIG.get("Zotero", "api_key"))
            except zotero_errors.MissingCredentials:
                print("Set up the access to Zotero API in the [Zotero] section of the configuration file if you want to be able to add articles in your zotero collection.")
            else:
                try:
                    self.zotero.create_items([])
                except zotero_errors.PyZoteroError as err:
                    if not CONFIG.get("Zotero", "library_id") or not CONFIG.get("Zotero", "api_key"):
                        print("Set up the access to Zotero API in the [Zotero] section of the configuration file if you want to be able to add articles in your zotero collection.")
                    else:
                        print("Failed to access Zotero API.")
                        print(err)
                        print("Please correct the settings in the [Zotero] section of the configuration file.")
                else:
                    self.add_action(self.to_zotero, 'zotero', desc='import in zotero collection')

                    self.template = self.zotero.item_template("preprint")
                    self.template["creators"].clear()
                    self.template['repository'] = 'arXiv'

                    # self._collections = [f'{col["data"]["name"]} - {col["data"]["key"]}' for col in self.zotero.collections()]  # issue: not all collections, limit at 100
                    # Autocompletion restricted to toplevel collections + first level of sub-collections
                    self._collections = []
                    for col in self.zotero.collections_top():
                        self._collections.append(f'{col["data"]["name"]} - {col["key"]}')
                        self._collections.extend([f'{scol["data"]["name"]} - {scol["key"]}' for scol in self.zotero.collections_sub(col["key"])])
                    self.coll_completer = OptionCompleter(sorted(self._collections))
                    collection_key = CONFIG.get("Zotero", "collection_key")
                    if collection_key:
                        try:
                            self.default_collection = self._collections[[col.split(" - ")[-1] for col in self._collections].index(collection_key)]
                            self.template["collections"] = [collection_key]
                        except ValueError:
                            self.default_collection = "My Library"
                    else:
                        self.default_collection = "My Library"

        self._display = True

    def reset(self):
        self._display = True
        self.index = 0

    def _pre_prompt(self):
        """Code to execute before showing input prompt."""
        if self._display:
            print(f'\x1b[1m({self.index + 1}).\x1b[0m\n{self.formatted_entries[self.index]}')

    def next(self):
        self.index += 1
        if self.index == len(self.entries):
            print("No more entries.")
            sys.exit()
        self._display = True

    def prev(self):
        self.index -= 1
        if self.index < 0:
            print("No more entries.")
            sys.exit()
        self._display = True

    def open(self):
        """Open article arXiv page."""
        webopen(self.entries[self.index]["link"])
        self._display = False

    def download(self):
        """Download pdf file of the entry."""
        self._display = False
        readline.set_completer(self.path_completer.complete)
        path = input('>> Download to: ').strip()
        readline.set_completer(self.completer.complete)
        title = self.entries[self.index]["title"]
        link = self.entries[self.index]["link"]
        path = download(link, path)
        if path:
            print(f"Downloaded '{title}' to {path}.")
            webopen(path)

    def to_zotero(self):
        entry = self.entries[self.index]
        prop = self.template.copy()
        prop["title"] = entry["title"]
        prop["creators"] = [{"creatorType": "author", "name": a["name"]} for a in entry["authors"]]
        prop["url"] = entry["link"]
        arXivID = entry["link"].strip("/").split("/")[-1].split("v")[0]
        prop["archiveID"] = f"arXiv:{arXivID}"
        prop["date"] = datetime.fromtimestamp(time.mktime(entry["published_parsed"])).strftime("%Y-%m-%d")

        if CONFIG.getboolean("Zotero", "choose_collection"):
            readline.set_completer(self.coll_completer.complete)
            coll = input(f'>> To collection [{self.default_collection}]: ').strip()
            readline.set_completer(self.completer.complete)
            if not coll:
                coll = self.default_collection
            if coll == "My Library":
                prop["collections"] = []
            else:
                prop["collections"] = [coll.split(" - ")[-1]]

        res = self.zotero.create_items([prop])
        if len(res["successful"]):
            print("Succesfully imported article in zotero.")
            if CONFIG.getboolean("Zotero", "attach_pdf"):  # download article and attach it to the newly created item
                key = res["success"]["0"]
                link = entry["link"]
                desc = f"{link.split('/')[-1]}"
                path = os.path.join(tempfile.gettempdir(), f"{desc}.pdf")
                try:
                    with TqdmUpTo(unit='B', unit_scale=True, miniters=1, desc=desc) as t:
                        urllib.request.urlretrieve(link.replace('abs', 'pdf'), filename=path, reporthook=t.update_to)
                    res = self.zotero.attachment_simple([path], parentid=key)
                    # Need to write directly in local database when file sync is disabled
                    database_path = CONFIG.get("Zotero", "local_database_path")
                    if database_path:
                        database_path =  os.path.join(database_path, "storage")
                        if len(res["success"]):
                            item = res["success"][0]
                        elif len(res["unchanged"]):
                            item = res["unchanged"][0]
                        else:
                            item = {}
                        os.mkdir(os.path.join(database_path, item["key"]))
                        shutil.copy(path, os.path.join(database_path, item["key"], f"{desc}.pdf"))
                except Exception as e:
                    print(e)
                    res = {"failure": [1]}
                try:
                    os.remove(path)
                except FileNotFoundError:
                    pass
                if len(res["failure"]):
                    print("Failed to attach pdf file.")
                else:
                    print("Succesfully attached pdf file.")

        else:
            print("Failed to import article in zotero:", res["failed"]["0"])
        self._display = False


# --- command line arguments parser
desc = """
CLI tool to fetch new articles on arXiv in selected categories filtered by
 keywords or authors. The updates can also be sent by email so that the script
 can be automatically run with cron.

The script will fetch the articles on arXiv that

 (1) were *submitted/updated* after the last update date (or the provided date)

 **AND**

 (2) belong to one of the *categories*

 **AND**

 (3) (one of the *authors* is in the author list) **OR** (one of the *keywords* is in the title or abstract)

All the *options* are set in the configuration file.

Note that keywords can contain spaces, e.g. "machine learning".
"""

def download_folder(download_path):
    """Raise an exception if download_path is not an existing folder."""
    if not os.path.isdir(download_path):
        raise ValueError(f"'{download_path}' is not an existing folder.")
    return download_path


parser = argparse.ArgumentParser(description=desc,
                                 epilog="Thank you to arXiv for use of its open access interoperability.")
parser.add_argument('-e', '--email', action='store_true',
                    help='send result by email (prompt for missing settings)')
parser.add_argument('-s', '--since',
                    type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                    metavar="YYYY-MM-DD",
                    help='fetch update since YYYY-MM-DD 00:00')
parser.add_argument('-c', '--config', nargs="?", const="",
                    metavar="FILE",
                    help='config file to use or print path to default one and exit if no argument is provided')
parser.add_argument('-v', '--version', help='show version and exit',
                    action='store_true')
parser.add_argument('-o', '--output', dest='output',
                    metavar="FILE",
                    help='write the output into FILE')
parser.add_argument('-d', '--download', dest='download',
                    metavar="FOLDER", type=download_folder,
                    help='download all the articles as pdf fiĺes in FOLDER (folder must exist)')
parser.add_argument('-i', '--interactive', action='store_true',
                    help='display result in interactive CLI')
parser.add_argument('-f', '--format', dest='display',
                    choices=["id", "title", "condensed", "full", "bibtex"],
                    metavar="FORMAT",
                    help=('article formatting: "id" (arXiv id, "title" (title - date), '
                          '"condensed" (title, authors, date - url), '
                          '"full" (title, authors, date, abstract, url, ...), or '
                          '"bibtex"'))
parser.add_argument('--log', help='show path to log file and exit',
                    action='store_true')
parser.add_argument('--max-trials', dest="max_trials",
                    help='maximum number of attempts to fetch the data when there is some connection issue',
                    type=int, default=CONFIG.getint("API", "max_trials"))
parser.add_argument('--nb-results-per-query', dest="nb_results_per_query",
                    help='split queries in chunks of NB_RESULTS_PER_QUERY. Sometimes there are issues with the API and changing the number of results queried in one call helps solve them.',
                    type=int, default=CONFIG.getint("API", "nb_results_per_query"))

subparsers = parser.add_subparsers(description='', dest='subcmd')
parser_query = subparsers.add_parser('query', help='subcommand to send a custom query the arXiv API')

parser_query.add_argument('search_query', nargs="?", default="", metavar="QUERY",
                          help='API search query, see --api-query-help and https://arxiv.org/help/api/user-manual')
parser_query.add_argument('--api-query-help', dest='query_help', action='store_true',
                          help='display API search query help and exit')
parser_query.add_argument('--id-list', dest='id_list', nargs="+", metavar="ID",
                          default=[],
                          help='only results with given arXiv ids')
parser_query.add_argument('--sort-by', dest='sort_by',
                          choices=["relevance", "lastUpdatedDate", "submittedDate"],
                          metavar="SORT_BY",
                          default="lastUpdatedDate",
                          help='sort results by "relevance", "lastUpdatedDate" [default], or "submittedDate"')
parser_query.add_argument('--sort-order', dest='sort_order',
                          choices=["ascending", "descending"],
                          default="descending",
                          metavar="ORDER",
                          help='sort results in "ascending" or "descending" [default] order')
parser_query.add_argument('--start-date', dest='start_date',
                          type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                          metavar="YYYY-MM-DD",
                          help='minimum date')
parser_query.add_argument('--end-date', dest='end_date',
                          type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                          metavar="YYYY-MM-DD",
                          help='maximum date')
parser_query.add_argument('--max-results', dest='max_results',
                          type=int,
                          metavar="N",
                          help='display only the N first results')

# --- entry formatting
BIBTEX_TEMPLATE = """
@article{%(key)s,
    author = {%(authors)s},
    title = {%(title)s},
    journal = {arXiv},
    year = {%(year)s},
    eprint = {%(eprint)s},
    url = {%(link)s}
}

"""


def format_entry(entry, display):
    """
    Format entry (from feedparser) as string.

    display: str
        "id": arxiv id
        "title": title - date
        "condensed": title, authors, date - url
        "full": title, authors, date, abstract, comments and url
        "bibtex": bibtex items
    """
    if display is None:
        display = CONFIG.get("General", "format")
    if display == "id":
        return entry['link'].split('/')[-1]
    title = entry['title'].strip().replace('\n ', '')
    date = datetime.fromtimestamp(time.mktime(entry['updated_parsed']))
    link = entry['link']
    if display == "title":
        return f"{date.strftime('%Y-%m-%d')} - {title} - \033[36m{link}\033[0m"
    authors = [a['name'] for a in entry['authors']]
    if display == "bibtex":
        return format_bibtex(title, authors, link, date)
    if display == "condensed":
        return f"{title}\n  {', '.join(authors)}\n  {date.strftime('%Y-%m-%d %H:%M')} - \033[36m{link}\033[0m\n"
    abstract = entry['summary'].splitlines()
    txt = [f'\033[1mTitle:\033[0m {title}',
           f'\033[1mAuthors:\033[0m {", ".join(authors)}',
           f'\033[1mDate:\033[0m {date.strftime("%Y-%m-%d %H:%M")}',
           f'\033[1mAbstract:\033[0m {" ".join(abstract)}']
    comments = entry.get('arxiv_comment')
    if comments:
        txt.append(f'\033[1mComments:\033[0m {comments}')
    tags = entry.get('tags')
    if tags:
        main = entry.get('arxiv_primary_category', tags[0])['term']
        tags = [tag['term'] for tag in tags[1:]]
        if tags:
            txt.append(f'\033[1mSubjects:\033[0m \033[4m{main}\033[0m, {", ".join(tags)}')
        else:
            txt.append(f'\033[1mSubject:\033[0m {main}')
    ref = entry.get('arxiv_journal_ref')
    if ref:
        txt.append(f'\033[1mJournal reference:\033[0m {ref}')
    doi = entry.get('arxiv_doi')
    if doi:
        txt.append(f'\033[1mDOI:\033[0m \033[36mhttps://doi.org/{doi}\033[0m')
    txt.append(f'\033[1mURL:\033[0m \033[36m{link}\033[0m')

    return '\n'.join(line.strip() for line in re.findall(r'.{1,80}(?:\s+|$)', '\n'.join(txt))) + '\n'


def format_bibtex(title, authors, url, date):
    """Return bibtex entry (internal function)."""
    data = {'title': title}
    data['link'] = url
    data['eprint'] = url.split('/')[-1]
    data['year'] = date.year
    auths = [a.split(' ') for a in authors]
    tit = title.split()[0].lower()
    if tit in ['a', 'the', 'an']:
        tit = title.split()[1].lower()
    auth = auths[0][-1]
    data['key'] = '{auth}_{title}_{year}'.format(auth=auth, title=tit,
                                                 year=data['year']).lower()
    auths = [a[-1] + ', ' + ' '.join(a[:-1]) for a in auths]
    data['authors'] = ' and '.join(auths)
    return BIBTEX_TEMPLATE % data


# --- feed query
API_URL = 'http://export.arxiv.org/api/query?'
MINDATE = datetime(MINYEAR, 1, 1)


def _query(url, start=0, trial_nb=1, max_trials=10):
    """Fetch query results and retry MAX_TRIALS in case of failure."""
    res = feedparser.parse(url.format(start=start))
    if res['entries']:
        return res['entries']
    err = res.get('bozo_exception', '')
    if err:
        raise ValueError(str(err))
    tot_results = int(res['feed']['opensearch_totalresults'])
    if start < tot_results:  # entries shouldn't be empty
        if trial_nb >= max_trials:
            raise ValueError("Failed to retrieve results from API. Changing NB_RESULTS_PER_QUERY sometimes fixes the issue.")
        return _query(url, start, trial_nb + 1, max_trials)
    return []  # no results


def api_query(start_date, nb_results_per_query=CONFIG.getint("API", "nb_results_per_query")):
    """Return arXiv API query results as a generator."""
    categories = "+OR+".join([cat.strip() for cat in CONFIG.get("General", "categories").split(",")])
    if not categories:
        raise ValueError("No category selected. Please edit the configuration file.")
    keywords = "+OR+".join([f'%22{kw.strip().replace(" ", "+")}%22' for kw in CONFIG.get("General", "keywords").split(",") if kw.strip()])
    authors = "+OR+".join([f'%22{auth.strip().replace(" ", "+")}%22' for auth in CONFIG.get("General", "authors").split(",") if auth.strip()])
    sort_by = CONFIG.get("General", "sort_by")
    date = datetime.now()

    args = []
    if keywords:
        # search for keywords in both title and abstract of articles in given categories
        args.append(f"%28ti:%28{keywords}%29+OR+abs:%28{keywords}%29%29")
    if authors:
        args.append(f"au:%28{authors}%29")
    if args:
        search_query = f"cat:%28{categories}%29+AND+%28{'+OR+'.join(args)}%29"
    else:
        # no filtering, get all articles from the categories
        search_query = f"cat:%28{categories}%29"

    url = f'{API_URL}search_query={search_query}' \
          f'&sortBy={sort_by}&sortOrder=descending&max_results={nb_results_per_query}' \
          '&start={start}'
    i = 0
    entries = _query(url, i, 1)
    t = time.time()
    entry = None
    while entries and date >= start_date:
        for entry in entries:
            date = datetime.fromtimestamp(time.mktime(entry['updated_parsed']))
            if date < start_date:
                return # all next entries will be older
            yield entry
        # if len(entries) < nb_results_per_query: # no more entries -> this does not work as there are some errors
            # return
        i += nb_results_per_query
        # enforce 3s between query rate limit https://info.arxiv.org/help/api/tou.html
        dt = time.time() - t
        if dt < 3:
            time.sleep(3-dt)
        err = True
        while err:
            try:
                entries = _query(url, i, 1)
                err = False
            except ValueError:
                # there is an issue with entry i, try the next one
                i += 1


API_DOC = 'Query construction for the arXiv API\n' \
          '====================================\n\n' \
          '\x1b[1mTypical form:\x1b[0m \x1b[7m<field>:<query>+<operator>+<field>:<query>...\x1b[0m\n\n' \
          'Fields\n' \
          '------\n\n' \
          '======  ========================\n' \
          'prefix  explanation\n' \
          '======  ========================\n' \
          'ti      Title\n' \
          'au      Author\n' \
          'abs     Abstract\n' \
          'co      Comment\n' \
          'jr      Journal Reference\n' \
          'cat     Subject Category\n' \
          'rn      Report Number\n' \
          'all     All of the above\n' \
          '======  ========================\n\n' \
          '\x1b[1mExample:\x1b[0m: \x1b[7mti:checkerboard\x1b[0m to list the articles whose titles contain the word \x1b[3mcheckerboard\x1b[0m.\n\n\n' \
          'Operators\n' \
          '---------\n\n' \
          'Several fields can be combined using boolean operators:\n\n' \
          '- AND\n' \
          '- OR\n' \
          '- ANDNOT\n\n' \
          '\x1b[1mExample:\x1b[0m: \x1b[7mau:del_maestro+ANDNOT+ti:checkerboard\x1b[0m to list the articles of \x1b[3mAdrian DelMaestro\x1b[0m with titles that do not contain the word \x1b[3mcheckerboard\x1b[0m\n\n\n' \
          'Grouping operators\n' \
          '------------------\n\n' \
          '- More complex queries can be used by using parentheses for grouping the Boolean expressions.\n' \
          '- Entire phrases can be used in a search field by enclosing them in double quotes.\n\n' \
          'The grouping operators are encoded in the following way:\n\n' \
          '==============  ========  ========================================================================\n' \
          'symbol          encoding  explanation\n' \
          '==============  ========  ========================================================================\n' \
          '( )             %28 %29   Used to group Boolean expressions for Boolean operator precedence.\n' \
          '""              %22 %22   Used to group multiple words into phrases to search a particular field.\n' \
          'space           \\+        Used to extend a search_query to include multiple fields.\n' \
          '==============  ========  ========================================================================\n\n' \
          '\x1b[1mExample\x1b[0m: \x1b[7mti:%22quantum+criticality%22\x1b[0m to list the articles whose titles contain the words \x1b[3mquantum\x1b[0m and \x1b[3mcriticality\x1b[0m.\n\n\n' \
          'More about the arXiv API: \033[36mhttps://arxiv.org/help/api/user-manual\033[0m\n'


def api_general_query(search_query="", id_list=(), sort_by="lastUpdatedDate", sort_order="descending",
                      start_date=None, end_date=None, max_results=None,
                      nb_results_per_query=CONFIG.getint("API", "nb_results_per_query")):
    """
    Return arXiv API query results as a generator.

    Arguments:
        * search_query: str
            API search query, see show_api_doc() and https://arxiv.org/help/api/user-manual
        * id_list: tuple or list
            list of arXiv ids
        * sort_by: str
            "relevance", "lastUpdatedDate", "submittedDate"
        * sort_order: str
            "ascending" or "descending"
        * start_date: datetime
            minimum date (ignored with sort_by="relevance")
        * end_date: datetime
            maximum date (ignored with sort_by="relevance")
        * max_results: int or None
            maximum number of results
    """
    if start_date is None:
        start_date = MINDATE
    if end_date is None:
        end_date = datetime.now()
    url = f'{API_URL}search_query={search_query}&id_list={",".join(id_list)}' \
          f'&sortBy={sort_by}&sortOrder={sort_order}&max_results={nb_results_per_query}' \
          '&start={start}'
    start = 0
    entries = _query(url, start, 1)

    entry = None
    counter = 0 # valid results
    if sort_by == "relevance": # ignore start and end dates
        while entries and (max_results is None or counter < max_results):
            for entry in entries:
                counter += 1
                yield entry

                if max_results is not None and counter == max_results:
                    return

            start += nb_results_per_query
            entries = _query(url, start, 1)
    else:
        date_key = "published_parsed" if sort_by == "submittedDate" else "updated_parsed"
        if sort_order == "descending":
            # find first entry older than end_date
            while entries and datetime.fromtimestamp(time.mktime(entries[-1][date_key])) > end_date:
                start += nb_results_per_query
                entries = _query(url, start, 1)
            if entries:
                date = datetime.fromtimestamp(time.mktime(entries[0][date_key]))
            while entries and date >= start_date and (max_results is None or counter < max_results):
                for entry in entries:
                    try:
                        date = datetime.fromtimestamp(time.mktime(entry[date_key]))
                    except KeyError:
                        continue  # ignore invalid entries
                    if start_date > date:
                        return
                    elif date <= end_date:
                        counter += 1
                        yield entry

                        if max_results is not None and counter == max_results:
                            return
                start += nb_results_per_query
                entries = _query(url, start, 1)
        else: # sortOrder == "ascending":
            while entries and datetime.fromtimestamp(time.mktime(entries[-1][date_key])) < start_date:
                start += nb_results_per_query
                entries = _query(url, start, 1)
            if entries:
                date = datetime.fromtimestamp(time.mktime(entries[0][date_key]))
            while entries and date <= end_date and (max_results is None or counter < max_results):
                for entry in entries:
                    try:
                        date = datetime.fromtimestamp(time.mktime(entry[date_key]))
                    except KeyError:
                        continue  # ignore invalid entries
                    if date > end_date:
                        return
                    elif start_date <= date:
                        counter += 1
                        yield entry

                        if max_results is not None and counter == max_results:
                            return
                start += nb_results_per_query
                entries = _query(url, start, 1)


def download(link, path, desc=None):
    """
    Download pdf file of the entry.

    * link: url of pdf file
    * path: destination folder or file
    * desc: description for the progressbar
    * force_folder: only accept existing folder as path

    Return path of downloaded file
    """
    if not path:
        return ''
    if desc is None:
        desc = link.split('/')[-1]
    if os.path.isdir(path):
        path = os.path.join(path, f"{link.split('/')[-1]}.pdf")
    ans = "y"
    if os.path.exists(path):
        ans = input(f'>> File {path} already exists. Do you want to replace it? [Y/n] ').strip()
        if not ans:
            ans = "y"
    if ans.lower() in ["y", "yes"]:
        with TqdmUpTo(unit='B', unit_scale=True, miniters=1, desc=desc) as t:
            urllib.request.urlretrieve(link.replace('abs', 'pdf'), filename=path, reporthook=t.update_to)
        return path
    return ""


ansi_regexp = re.compile(r"\033\[[0-9]+m")


def send_email(txt, subject):
    """Return True if the email is sent."""
    # SMTP server settings
    smtp_server = CONFIG.get("Email", "smtp_server", fallback="")
    port = CONFIG.getint("Email", "smtp_port")
    if not smtp_server:
        smtp_server = input_timeout("SMTP server (e.g. smtp.gmail.com): ")
        CONFIG.set("Email", "smtp_server", smtp_server)
    login = CONFIG.get("Email", "email", fallback="")
    if not login:
        login = input_timeout("email: ")
        CONFIG.set("Email", "email", login)

    password = get_pwd_from_keyring(login)
    if password is None:
        password = getpass.getpass(f"Password for {login}: ")

    # mail content
    msg = EmailMessage()
    msg.set_content(ansi_regexp.sub('', txt))
    msg['Subject'] = subject
    msg['From'] = login
    msg['To'] = login

    # server connexion
    context = ssl.create_default_context()  # create SSL context
    trial_nb = 0
    while trial_nb < 3:
        try:
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(login, password)
                server.send_message(msg)
        except smtplib.SMTPAuthenticationError:
            trial_nb += 1
            logging.error("Authentication failed for %s", login)
            password = getpass.getpass(f"Password for {login}: ")
        except Exception:
            logging.exception("Email sending failed, please check the configuration file")
            return False
        else:
            store_pwd_in_keyring(login, password)
            logging.info("Email sent")
            return True
    return False


def load_default_config():
    """Load default config file and return the filepath."""
    try:
        path_config = CONFIG.read(CONFIG_PATHS)[-1]  # the last valid file overrides the others
    except IndexError: # config file does not exists
        path_config = CONFIG_PATHS[-1]
        folder = os.path.dirname(path_config)
        if not os.path.exists(folder):
            os.mkdir(folder)
        with open(path_config, 'w') as file:
            CONFIG.write(file)
        logging.info("No configuration file found. Default configuration file '%s' has been created. "
                     "Please edit it and run the script again.", path_config)
        sys.exit()
    return path_config


# --- main
def _main(args, trial_nb=1):
    # version
    if args.version:
        print('arxiv_update_cli ', VERSION)
        sys.exit()

    # log
    if args.log:
        print("log file: ", PATH_LOG)
        sys.exit()

    # config file
    if args.config == "":
        print("Default config file: ", load_default_config())
        sys.exit()

    if args.config: # try to load provided config file
        try:
            path_config = CONFIG.read(args.config)[-1]
        except IndexError:
            logging.warning("Invalid config file %s, default config file used instead.", args.config)
            path_config = load_default_config()
    else:
        path_config = load_default_config()

    # query
    try:  # catch connection issues
        if args.subcmd == 'query': # custom API query
            # retrieve options
            if args.query_help:
                print(API_DOC)
                sys.exit()

            keys = ['search_query', 'id_list', 'sort_by', 'sort_order',
                    'start_date', 'end_date', 'max_results', 'nb_results_per_query']
            kw = {key: getattr(args, key, '') for key in keys}
            # run query
            results = api_general_query(**kw)
            header = f"arXiv query '{args.search_query}'"
            footer = "\033[3m%% {nb} articles found.\033[0m"
            no_result_msg = "No article found."
            new_last_update = ""

        else: # standard update
            # start date
            now = datetime.now()
            if args.since is None:
                try:
                    start_date = datetime.strptime(CONFIG.get("General", "last_update"),
                                                   '%Y-%m-%d %H:%M')
                except ValueError:
                    start_date = now - timedelta(days=1)
            else:
                start_date = args.since
            # run query
            results = api_query(start_date, args.nb_results_per_query)
            header = f"arXiv update {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            footer = "\033[3m%% {nb} new articles since " + f"{start_date.strftime('%Y-%m-%d %H:%M')}\033[0m."
            no_result_msg = f"No new articles since {start_date.strftime('%Y-%m-%d %H:%M')}."

            new_last_update = now.strftime('%Y-%m-%d %H:%M')  # do notr save it immediately as it can still fail


        # format results
        i = -1
        articles = []
        results = list(results)
    except SocketError:
        logging.exception("An error occured")
        if trial_nb < args.max_trials:
            time.sleep(3)  # wait for 3s (following the rate limit https://info.arxiv.org/help/api/tou.html) and try again
            logging.info(f"Trying again. Try #{trial_nb+1}/{args.max_trials}")
            _main(args, trial_nb=trial_nb+1)
        return
    # after this step, the result collection succeeded
    if new_last_update:
        CONFIG.set("General", "last_update", new_last_update)
        save_config(path_config)

    for i, article in enumerate(results):
        articles.append(format_entry(article, args.display))
    nb = i+1
    footer = footer.format(nb=nb)

    if not articles:
        logging.info(no_result_msg)
        return

    output = "\n".join(articles)
    if args.email:
        send_email(f"{footer}\n\n{output}\n{footer}", header)
    if args.output:
        with open(args.output, "w") as file:
            file.write(header + "\n\n")
            file.write(ansi_regexp.sub('', output) + "\n")
            file.write(ansi_regexp.sub('', footer))
    if args.download:
        for i, article in enumerate(results, 1):
            link = article["link"]
            desc = f"{i}/{nb} {link.split('/')[-1]}"
            download(link, args.download, desc)
    if args.interactive:
        cli = InteractiveCLI(f"{header}\n{footer}", results, articles)
        cli.interact()
    elif not args.output:
        print(output)
    logging.info(footer)


def main(argv=None):
    if argv is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)

    try: # log exceptions
        _main(args)
    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt")
    except Exception:
        logging.exception("An error occured")
    finally:
        logging.shutdown()


# --- execute
if __name__ == "__main__":
    main()
