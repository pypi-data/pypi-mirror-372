#! /usr/bin/env python3

""" Nearly MVP of a command to do things to GitLab
    Currently just implements the 'mr-list' command which outputs a list
    of merge requests from all projects in CSV format.

    TODO: Lots and lots of things! """

################################################################################

import argparse
import os
import sys
from collections import defaultdict

import thingy.colour as colour
import thingy.gitlab as gitlab

################################################################################

def mr_list(args):
    """ List merge requests """

    gl = gitlab.GitLab(args.server)

    # TODO: Could incorporate some/all filtering in the request rather than getting all MRs and filtering them

    mrs = gl.merge_requests(scope='all')

    # TODO: Output format other than CSV
    # TODO: More filtering

    if args.summary:
        authors = defaultdict(int)
        reviewers = defaultdict(int)
        combos = defaultdict(int)

        count = 0
        for mr in mrs:
            author = mr['author']['username']
            authors[author] += 1

            if mr['state'] == 'merged':
                try:
                    reviewer = mr['merged_by']['username']
                except TypeError:
                    reviewer = 'UNKNOWN'

                reviewers[reviewer] += 1
                combos[f"{author}|{reviewer}"] += 1

            count += 1
            if args.limit and count > args.limit:
                break

        print('Number of merge requests by author')

        for value in sorted(set(authors.values()), reverse=True):
            for person in authors:
                if authors[person] == value:
                    print(f'    {person:32}: {authors[person]}')

        print()
        print('Number of merge requests by reviewer')

        for value in sorted(set(reviewers.values()), reverse=True):
            for person in reviewers:
                if reviewers[person] == value:
                    print(f'    {person:32}: {reviewers[person]}')

        print()
        print('Author/Reviewer combinations for merged changes')

        for value in sorted(set(combos.values()), reverse=True):
            for combo in combos:
                if combos[combo] == value:
                    author, reviewer = combo.split('|')

                    print(f'    Written by {author}, reviewed by {reviewer}: {combos[combo]}')

    else:
        print('state,merge id,project id,author,approver,title,merge date')

        for mr in mrs:
            if args.author and mr['author']['username'] != args.author:
                continue

            if mr['state'] == 'merged':
                try:
                    merged_by = mr['merged_by']['username']
                except TypeError:
                    merged_by = 'NONE'

                if args.approver and merged_by != args.approver:
                    continue

                if not args.summary:
                    print('%s,%s,%s,%s,%s,%s,"%s"' % (mr['state'], mr['id'], mr['project_id'],
                          mr['author']['username'], merged_by, mr['title'], mr['merged_at']))
            elif args.all and not args.summary:
                print('%s,%s,%s,%s,,"%s",' % (mr['state'], mr['id'], mr['project_id'], mr['author']['username'], mr['title']))

            count += 1
            if args.limit and count > args.limit:
                break

################################################################################

def main():
    """ Entry point """

    parser = argparse.ArgumentParser(description='Gitlab commands')

    parser.add_argument('--dryrun', '--dry-run', '-D', action='store_true', help='Dry-run comands')
    parser.add_argument('--debug', '-d', action='store_true', help='Debug')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbosity to the maximum')
    parser.add_argument('--server', '-s', default=None, help='The GitLab server')
    parser.add_argument('--token', '-t', default=None, help='The GitLab access token')

    subparsers = parser.add_subparsers(dest='command')

    parser_mr_list = subparsers.add_parser('mr-list', help='List merge requests')
    parser_mr_list.add_argument('--all', action='store_true', help='List un-merged merge requests')
    parser_mr_list.add_argument('--author', action='store', help='List merge requests created by a specific user')
    parser_mr_list.add_argument('--approver', action='store', help='List merge requests approved by a specific user')
    parser_mr_list.add_argument('--summary', action='store_true', help='Produce a summary report')
    parser_mr_list.add_argument('--limit', action='store', type=int, help='Output the first N merge requests')

    # TODO: Other subcommands

    # Parse the command line

    args = parser.parse_args()

    # Check the server/token configuration

    if not args.server:
        args.server = os.environ.get('GITLAB_SERVER', None)

        if not args.server:
            colour.error('The GitLab server must be specified on the command line or via the [BLUE:GITLAB_SERVER] environment variable')

    if not args.token:
        args.token = os.environ.get('GITLAB_TOKEN', None)

        if not args.token:
            colour.error('GitLab access token must be specified on the command line or via the [BLUE:GITLAB_TOKEN] environment variable')

    # Invoke the subcommand

    if args.command == 'mr-list':
        mr_list(args)

    elif not args.command:
        colour.error('No command specified')
    else:
        colour.error(f'Invalid command: "{args.command}"')

################################################################################

def gl():
    """Entry point"""

    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    gl()
