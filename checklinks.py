import os
import argparse

from dclinkchecker import check_all_links

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Check external links in a Digital Commons Content Inventory spreadsheet.'
    )
    parser.add_argument(
        'input_file',
        type=str,
        help='Content Inventory file containing links to be checked.'
    )
    parser.add_argument(
        '-o', '--output-file',
        dest='destination',
        type=str,
        help='Output Excel file. Default is <input file>.xlsx.'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='verbose',
        help="Print status messages."
    )
    parser.add_argument(
        '-t', '--timeout',
        dest='timeout',
        type=int,
        help='GET response timeout, in seconds. Default is 10.'
    )
    parser.add_argument(
        '-b', '--buy-links',
        action='store_true',
        dest='buy_links',
        help='Check buy links in book gallery landing pages. Default is externally linked documents.'
    )
    args = parser.parse_args()

    # Split filename from extension before passing to the various functions. Use input filename for template
    # if no output filename specified.
    if args.destination:
        output_file = args.destination
    else:
        output_file, output_extension = os.path.splitext(args.input_file)
        output_file = output_file + "-checked" + output_extension

    check_all_links(args.input_file, output_file, args.verbose, args.buy_links, args.timeout)
