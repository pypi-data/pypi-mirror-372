#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" arch-wiki-search (c) Clem Lorteau 2025
License: MIT
"""

#TODO: convert html to markdown
#TODO: conv = darkhtml - custom css for dark mode
#TODO: conv = custom css - user supplied css
#TODO: arg to change number of days before cache expiry
#TODO: prompt while serving to search other terms
#TODO: option to select language

import sys
import asyncio
import argparse

try:
    from __init__ import __name__, __version__, __url__, __newwikirequesturl__, logger
    from exchange import ZIP
    from core import Core
    from wikis import Wikis
except ModuleNotFoundError:
    from arch_wiki_search import __name__, __version__, __url__, __newwikirequesturl__, logger
    from arch_wiki_search.exchange import ZIP
    from arch_wiki_search.core import Core
    from arch_wiki_search.wikis import Wikis

format_blue_underline = '\033[4;34m'
format_yellow = '\x1b[33;20m'
format_bold = '\033[1m'
format_reset = '\033[0m'

async def _main(core, search):
    await core.start()
    try:
        await core.search(search)
        await core.wait()
    except asyncio.CancelledError:
        print('')
        logger.info('Stopping')
    await core.stop()

async def _clear(core):
    """Clear the cache
    """
    await core.cachingproxy.printcachesize()
    logger.warning('This will clear your cache - are you sure? (type \'Yes\')')
    a = input ('> ') #TODO: prompts in curses
    if a != 'Yes': sys.exit(-7)
    await core.cachingproxy.clear()
    await core.cachingproxy.printcachesize()

def main():
    """Load pre-configured base_url/searchstring pairs from yaml file
    """
    knownwikis = None
    debug = False
    if '-d' in sys.argv: debug = True
    try:
        knownwikis = Wikis(debug=debug)
    except Exception as e:
        logger.error(e)
        print(knownwikis.gethelpstring())
        sys.exit(-6)
    
    parser = argparse.ArgumentParser(
        prog = sys.argv[0],
        description = f'''Read and search Archwiki and other wikis, online or offline, in HTML, markdown or text, on the desktop or the terminal 

Examples:
    {format_yellow}🡪 {format_reset}{sys.argv[0]} \"installation guide\"{format_reset}
    {format_yellow}🡪 {format_reset}{sys.argv[0]} --wiki=wikipedia --conv=txt \"MIT license\"{format_reset}''',
        epilog = f'''Options -u and -s overwrite the corresponding url or searchstring provided by -w
Known wiki names and their url/searchstring pairs are read from a \'{knownwikis.filename}\' file in \'{knownwikis.dirs[0]}\' and \'{knownwikis.dirs[1]}\'
Github: 🌐{format_blue_underline}{__url__}{format_reset}
Request to add new wiki: 🌐{format_blue_underline}{__newwikirequesturl__}{format_reset}''',
        formatter_class = argparse.RawTextHelpFormatter,
    )
    parser.add_argument('-w', '--wiki', default='archwiki',
                         help='Load a known wiki by name (ex: --wiki=wikipedia) [Default: archwiki]',
                         choices=knownwikis.getnames())
    parser.add_argument('-u', '--url', default=None,
                         help='URL of wiki to browse (ex: https://wikipedia.org, https://wiki.freebsd.org)')
    parser.add_argument('-s', '--searchstring', default=None,
                         help='alternative search string (ex: \"/wiki/Special:Search?go=Go&search=\", \"/FrontPage?action=fullsearch&value=\")')
    parser.add_argument('-c', '--conv', default=None,
                        choices=['raw', 'clean', 'txt'],
                        help='''conversion mode:
raw: no conversion (but still remove binaries)
clean: convert to simple html (basic formatting, no styles or scripts)
txt: convert to plain text
[Default: \'raw\' in graphical environment, \'clean\' otherwise]''',)
    parser.add_argument('--offline', '--test', default=False, action='store_true',
                         help='Don\'t try to go online, only use cached copy if it exists')
    parser.add_argument('--refresh', default=False, action='store_true',
                        help='Force going online and refresh the cache')
    parser.add_argument('-v', '--version', default=False, action='store_true',
                        help='Print version number and exit')
    parser.add_argument('-x', '--export', default=False, action='store_true',
                        help='Export cache as .zip file')
    parser.add_argument('-m', '--merge', default=None,
                        help='Import and merge cache from a zip file created with --export') #TODO validate the import
    parser.add_argument('--clear', default=False, action='store_true',
                        help='Clear cache and exit')
    parser.add_argument('-d', '--debug', default=False, action='store_true')
    parser.add_argument('search', help='string to search (ex: \"installation guide\")', nargs='?',
                        const=None, type=str)
    
    args = None
    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code != 0:
            msg = f'Could not parse {e} arguments'
            logger.critical(msg)
            print(knownwikis.gethelpstring())
        sys.exit(e.code)

    if (args.version):
        print(__version__)
        sys.exit(0)

    if (not args.search):
        search = ''
    else:
        search = args.search

    core = Core(knownwikis,
                # alt_browser=args.browser,
                conv=args.conv,
                base_url=args.url, 
                search_parm=args.searchstring,
                offline=args.offline,
                refresh=args.refresh,
                debug=args.debug,
                wiki=args.wiki,
                )

    if (args.clear):
        asyncio.run(_clear(core))
        sys.exit(0)

    if (args.export):
        if (args.merge):
            logger.critical('--export and --merge can\'t be used together')
            sys.exit(-6)
        ZIP().export(core.cachingproxy.cache_dir)
        sys.exit(0)

    if (args.merge):
        if args.export:
            logger.critical('--export and --merge can\'t be used together')
            zip.exit(-6)
        ZIP().merge(core.cachingproxy.cache_dir, args.merge)
        sys.exit(0)

    try:
        asyncio.run(_main(core, search))
    except KeyboardInterrupt:
        pass #exception CancelledError will be caught in main

if __name__ == '__main__':
    main()

sys.exit(main())