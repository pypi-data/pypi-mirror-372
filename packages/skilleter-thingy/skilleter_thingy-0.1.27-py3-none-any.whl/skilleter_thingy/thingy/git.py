#! /usr/bin/env python3

################################################################################
""" Git module

    Copyright (C) 2017-18 John Skilleter

    Licence: GPL v3 or later

    Except where stated otherwise, functions in this module:

    * Return the output from the equivalent git command as an array of
      strings.

    * Functions will raise exceptions on error. If the underlying git command
      returns an error, a git.GitError() exception is raised.

    * TODO: Cache list of branches when git.branches/isbranch called
    * TODO: commit_info() doesn't like files that are renamed *and* changed
"""
################################################################################

import os
import shutil
import sys
import re
import logging
import fnmatch
import subprocess

import thingy.run as run
import thingy.gitlab as gitlab

################################################################################
# Configuration files to access

(LOCAL, GLOBAL, SYSTEM) = list(range(3))

################################################################################

class GitError(run.RunError):
    """ Run exception """

    def __init__(self, msg, status=1):
        super().__init__(msg, status)

################################################################################

def git(cmd, stdout=None, stderr=None):
    """ Wrapper for thingy.run.run that raises a GitError instead of RunError
        so that Git module users do not to include the run module just
        to get the exception.
        Optionally redirect stdout and stderr as specified. """

    logging.debug('Running git %s', ' '.join(cmd))

    try:
        return run.run(['git'] + cmd, stdout=stdout, stderr=stderr)
    except run.RunError as exc:
        raise GitError(exc.msg, exc.status)
    except FileNotFoundError as exc:
        raise GitError(exc, 1)

################################################################################

def git_run_status(cmd, stdout=None, stderr=None):
    """ Wrapper for run.run that returns the output and status, and
        does not raise an exception on error.
        Optionally redirect stdout and stderr as specified. """

    logging.debug('Running git %s', ' '.join(cmd))

    result = subprocess.run(['git'] + cmd,
                            stdout=stdout or subprocess.PIPE,
                            stderr=stderr or subprocess.PIPE,
                            text=True,
                            errors='ignore',
                            universal_newlines=True)

    return (result.stdout or result.stderr), result.returncode

################################################################################

def clone(reponame, directory=None):
    """ Clone a repo """

    cmd = ['clone', reponame]

    if directory:
        cmd.append(directory)

    return git(cmd)

################################################################################

def init(reponame, bare=False):
    """ Initialise a new working tree """

    cmd = ['init']

    if bare:
        cmd.append('--bare')

    cmd.append(reponame)

    return git(cmd)

################################################################################

def iscommit(commit, remote=False, remote_only=False):
    """ Return True if "commit" is a valid SHA1, branch or tag
        If remote==True then if there are no direct matches it will also
        check for a matching remote branch
        If remote_only==True, then ONLY remote branches will be checked."""

    # Optionally look for a matching local branch

    if not remote_only:
        cmd = ['cat-file', '-t', commit]
        try:
            result = git(cmd)[0]

            return result in ('commit', 'tag')
        except GitError:
            pass

    # Optionally look for matching remote branch

    if remote or remote_only:
        for branch in branches(all=True):
            if branch.startswith('remotes/'):
                localbranch = '/'.join(branch.split('/')[2:])

                if localbranch == commit:
                    return True

    return False

################################################################################

def branch(branchname='HEAD'):
    """ Return the name of the current git branch or None"""

    try:
        return git(['symbolic-ref', '--short', '-q', branchname])[0]
    except GitError:
        return None

################################################################################

def tag():
    """ If the current commit is tagged, return the tag(s) or None """

    try:
        return git(['describe', '--tags', '--exact-match'])[0]
    except GitError:
        return None

################################################################################

def tags():
    """ Return the list of tags in the current repo """

    return git(['tag'])

################################################################################

def set_tag(tag, commit):
    """ Apply a tag to a commit """

    return git(['tag', tag, commit])

################################################################################

def delete_tag(tag):
    """ Delete a tag """

    return git(['tag', '--delete', tag])

################################################################################

def current_commit(short=False):
    """ Return the SHA1 of the current commit """

    cmd = ['rev-parse']

    if short:
        cmd.append('--short')

    cmd.append('HEAD')

    return git(cmd)[0]

################################################################################

def pull(repo=None, all=False):
    """ Run a git pull """

    cmd = ['pull']

    if all:
        cmd.append('--all')

    if repo:
        cmd.append(repo)

    return git(cmd)

################################################################################

def checkout(branch, create=False, commit=None):
    """ Checkout a branch (optionally creating it or creating it from the
        specified commit) """

    cmd = ['checkout']

    if create or commit:
        cmd.append('-b')

    cmd.append(branch)

    if commit:
        cmd.append(commit)

    return git(cmd)

################################################################################

def merge(branch):
    """ Merge a branch """

    cmd = ['merge', branch]

    return git(cmd)

################################################################################

def abort_merge():
    """ Abort the current merge """

    return git(['merge', '--abort'])

################################################################################

def set_upstream(branch, upstream=None):
    """ Set the default upstream branch """

    if not upstream:
        upstream = f'origin/{branch}'

    cmd = ['branch', f'--set-upstream-to={upstream}', branch]

    return git(cmd)

################################################################################

def fetch(all=False):
    """ Run git fetch """

    cmd = ['fetch']

    if all:
        cmd.append('--all')

    return git(cmd)

################################################################################

def rebase_required(branch, parent):
    """ Return True if the specified branch needs to be rebased against its
        parent.
    """

    # Find the latest commit on the parent branch and the most recent commit
    # that both branches have in common.

    parent_tip = git(['show-ref', '--heads', '-s', parent])
    common_commit = git(['merge-base', parent, branch])

    # Different commits, so rebase is required

    return parent_tip[0] != common_commit[0]

################################################################################

def rebase(branch):
    """ Rebase the current branch against the specified branch """

    return git_run_status(['rebase', branch])

################################################################################

def abort_rebase():
    """ Abort the current rebase """

    return git(['rebase', '--abort'])

################################################################################

def rebasing():
    """ Return True if currently rebasing, False otherwise """

    gitdir = git_dir()

    return os.path.isdir(os.path.join(gitdir, 'rebase-apply')) or \
        os.path.isdir(os.path.join(gitdir, 'rebase-merge'))

################################################################################

def bisecting():
    """ Return True if currently rebasing, False otherwise """

    gitdir = git_dir()

    return os.path.isfile(os.path.join(gitdir, 'BISECT_START'))

################################################################################

def merging():
    """ Return True if currently merging, False otherwise """

    gitdir = git_dir()

    return os.path.isfile(os.path.join(gitdir, 'MERGE_MODE'))

################################################################################

def remotes():
    """ Return the list of git remotes """

    results = git(['remote', '-v'])

    git_remotes = {}

    for result in results:
        if result:
            remote_name, remote_url = result.split('\t')

            if remote_url.endswith(' (fetch)'):
                remote_url = remote_url[:-8]
            elif remote_url.endswith(' (push)'):
                remote_url = remote_url[:-7]

            git_remotes[remote_name] = remote_url

    return git_remotes

################################################################################

def remote_names():
    """ Return the list of remote names """

    results = git(['remote'])

    return results

################################################################################

def project(short=False):
    """ Return the name of the current git project """

    git_remotes = remotes()
    name = ''

    for remote in git_remotes:
        try:
            if '//' in git_remotes[remote]:
                name = git_remotes[remote].split('//')[-1].split('/', 1)[-1]
                break

            if '@' in git_remotes[remote]:
                name = git_remotes[remote].split(':')[-1]
                break

        except ValueError:
            continue

    if name.endswith('.git'):
        name = name[:-4]

    if short:
        name = os.path.basename(name)

    return name

################################################################################

def status_info(ignored=False, untracked=False):
    """ Git status, optionally include files ignored in .gitignore and/or
        untracked files.
        Returns data in the same dictionary format as used by commit_info() """

    cmd = ['status', '-z']

    if ignored:
        cmd.append('--ignored')

    if untracked:
        cmd.append('--untracked-files=all')

    results = git(cmd)

    # Dictionary of results, indexed by filename where the status is 2 characters
    # the first representing the state of the file in the index and the second the state
    # of the file in the working tree where:
    # M=modified, A=added, D=deleted, R=renamed, C=copied, U=unmerged, ?=untracked, !=ignored
    # Where a file has been renamed we don't report the original name

    info = {}

    if results:
        result_list = results[0].split('\0')

        for result in result_list:
            if len(result) > 3 and result[2] == ' ':
                git_status = result[0:2]
                name = result[3:]

                info[name] = git_status

    return info

################################################################################

def status(ignored=False, untracked=False):
    """ Git status, optionally include files ignored in .gitignore and/or
        untracked files.
        Similar to status_info, but returns data as a list, rather than a
        dictionary. """

    cmd = ['status', '--porcelain']

    if ignored:
        cmd.append('--ignored')

    if untracked:
        cmd.append('--untracked-files=all')

    results = git(cmd)

    # Nested list of results. For each entry:
    # item 0 is the status where: M=modified, A=added, D=deleted, R=renamed, C=copied, U=unmerged, ?=untracked, !=ignored
    # item 1 is the name
    # item 2 (if present) is the old name in cases where a file has been renamed.

    # TODO: This can't handle the case where a file has ' -> ' in the filename
    # TODO: This can't handle the case where a filename is enclosed in double quotes in the results

    info = []

    for result in results:
        stats = []
        stats.append(result[0:2])

        name = result[3:]
        if ' -> ' in name:
            stats += name.split(' -> ', 1)
        else:
            stats.append(name)

        info.append(stats)

    return info

################################################################################

def working_tree():
    """ Location of the current working tree or None if we are not in a working tree """

    try:
        return git(['rev-parse', '--show-toplevel'])[0]
    except GitError:
        return None

################################################################################

def git_dir():
    """ Return the relative path to the .git directory """

    return git(['rev-parse', '--git-dir'])[0]

################################################################################

def tree_path(filename):
    """ Normalise a filename (absolute or relative to the current directory)
        so that it is relative to the top-level directory of the working tree """

    git_tree = working_tree()

    return os.path.relpath(filename, git_tree)

################################################################################

def difftool(commit_1=None, commit_2=None, files=None, tool=None):
    """ Run git difftool """

    cmd = ['difftool']

    if tool:
        cmd += ['--tool', tool]

    if commit_1:
        cmd.append(commit_1)

    if commit_2:
        cmd.append(commit_2)

    if files:
        cmd.append('--')

        if isinstance(files, str):
            cmd.append(files)
        else:
            cmd += files

    return git(cmd)

################################################################################

# Match 'git diff --numstat' output - first re splits into lines added, removed
# and name. Second one is used if a file has been renamed, to get the old and
# new name components.

_DIFF_OUTPUT_RE = re.compile(r'(-|\d+)\s+(-|\d+)\s+(.*)')
_DIFF_OUTPUT_RENAME_RE = re.compile(r'(.*)\{(.*) => (.*)\}(.*)')

def commit_info(commit_1=None, commit_2=None, paths=None, diff_stats=False):
    """ Return details of changes either in single commit (defaulting to the most
        recent one) or between two commits, optionally restricted a path or paths
        and optionally returning diff statistics, with and/or without taking
        whitespace into account.
    """

    def parse_diff_output(result):
        """Extract previous and current filename (which may be the same) and lines added/deleted
           from output from git diff --numstat"""

        p = _DIFF_OUTPUT_RE.fullmatch(result)

        # This shouldn't happen...

        if not p:
            return 'ERROR', 'ERROR', 0, 0

        # Extract number of lines added/removed

        lines_ins = 0 if p.group(1) == '-' else int(p.group(1))
        lines_del = 0 if p.group(2) == '-' else int(p.group(2))

        # Check for rename and get both old and new names

        if ' => ' in p.group(3):
            q = _DIFF_OUTPUT_RENAME_RE.fullmatch(p.group(3))

            if q:
                old_filename = q.group(1) + q.group(2) + q.group(4)
                new_filename = q.group(1) + q.group(3) + q.group(4)
            else:
                old_filename, new_filename = p.group(3).split(' => ')
        else:
            old_filename = new_filename = p.group(3)

        return old_filename, new_filename, lines_ins, lines_del

    # Either get changes between the two commits, or changes in the specified commit

    params = []

    if commit_1:
        params.append(commit_1)

    if commit_2:
        params.append(commit_2)

    if paths:
        params.append('--')

        if isinstance(paths, str):
            params.append(paths)
        else:
            params += paths

    results = git(['diff', '--name-status'] + params)

    # Parse the output

    info = {}

    for result in results:
        if result == '':
            continue

        # Renames and copies have an extra field (which we ignore) for the destination
        # file. We just get the status (Add, Move, Delete, Type-change, Copy, Rename)
        # and the name.

        if result[0] in ('R', 'C'):
            filestatus, oldname, filename = result.split('\t')
            info[filename] = {'status': filestatus[0], 'oldname': oldname}
        else:
            filestatus, filename = result.split('\t')
            info[filename] = {'status': filestatus[0], 'oldname': filename}

    # Add the diff stats, if requested

    if diff_stats:
        # Run git diff to get stats, and add them to the info
        # TODO: Need to extract old name of renamed files

        results = git(['diff', '--numstat'] + params)

        for result in results:
            old_filename, new_filename, lines_ins, lines_del = parse_diff_output(result)

            info[new_filename]['deleted'] = lines_del
            info[new_filename]['added'] = lines_ins

        # Run git diff to get stats ignoring whitespace changes and add them

        results = git(['diff', '--numstat', '--ignore-all-space', '--ignore-blank-lines'] + params)

        for result in results:
            old_filename, new_filename, lines_ins, lines_del = parse_diff_output(result)

            info[new_filename]['non-ws deleted'] = lines_del
            info[new_filename]['non-ws added'] = lines_ins

        # Fill in the blanks - files

        for filename in info:
            if 'deleted' not in info[filename]:
                info[filename]['deleted'] = info[filename]['added'] = 0

            if 'non-ws deleted' not in info[filename]:
                info[filename]['non-ws deleted'] = info[filename]['non-ws added'] = 0

    return info

################################################################################

def diff(commit=None, renames=True, copies=True, relative=False):
    """ Return a list of differences between two commits, working tree and a commit or working tree and head """

    if commit:
        if isinstance(commit, list):
            if len(commit) > 2:
                raise GitError('git.diff - invalid parameters')

        else:
            commit = [commit]
    else:
        commit = []

    cmd = ['diff', '--name-status']

    if renames:
        cmd.append('--find-renames')

    if copies:
        cmd.append('--find-copies')

    if relative:
        cmd.append('--relative')

    cmd += commit

    return git(cmd)

################################################################################

def diff_status(commit1, commit2='HEAD'):
    """ Return True if there is no difference between the two commits, False otherwise """

    cmd = ['diff', '--no-patch', '--exit-code', commit1, commit2]

    try:
        git(cmd)
    except GitError:
        return False

    return True

################################################################################

def show(revision, filename, outfile=None):
    """ Return the output from git show revision:filename """

    return git(['show', f'{revision}:{filename}'], stdout=outfile)

################################################################################

def add(files):
    """ Add file to git """

    return git(['add'] + files)

################################################################################

def rm(files):
    """ Remove files from git """

    return git(['rm'] + files)

################################################################################

def commit(files=None,
           message=None,
           all=False, amend=False, foreground=False, patch=False, dry_run=False):
    """ Commit files to git """

    cmd = ['commit']

    if amend:
        cmd.append('--amend')

    if all:
        cmd.append('--all')

    if patch:
        cmd.append('--patch')
        foreground = True

    if dry_run:
        cmd.append('--dry-run')

    if files is not None:
        cmd += files

    if message:
        cmd += ['-m', message]

    if foreground:
        return git(cmd, stdout=sys.stdout, stderr=sys.stderr)

    return git(cmd)

################################################################################

def push(all=False, mirror=False, tags=False, atomic=False, dry_run=False,
         follow_tags=False, receive_pack=False, repo=None, force=False, delete=False,
         prune=False, verbose=False, set_upstream=False, push_options=[], signed=None,
         force_with_lease=False, no_verify=False, repository=None, refspec=None):
    """ Push commits to a remote """

    cmd = ['push']

    if all:
        cmd.append('--all')

    if mirror:
        cmd.append('--mirror')

    if tags:
        cmd.append('--tags')

    if atomic:
        cmd.append('--atomic')

    if dry_run:
        cmd.append('--dry-run')

    if follow_tags:
        cmd.append('--follow-tags')

    if receive_pack:
        cmd.append(f'--receive-pack={receive_pack}')

    if repo:
        cmd.append(f'--repo={repo}')

    if force:
        cmd.append('--force')

    if delete:
        cmd.append('--delete')

    if prune:
        cmd.append('--prune')

    if verbose:
        cmd.append('--verbose')

    if set_upstream:
        cmd.append('--set-upstream')

    if push_options:
        for option in push_options:
            cmd.append(f'--push-option={option}')

    if signed:
        cmd.append(f'--signed={signed}')

    if force_with_lease:
        cmd.append('--force-with-lease')

    if no_verify:
        cmd.append('--no-verify')

    if repository:
        cmd.append(repository)

    if refspec:
        for ref in refspec:
            cmd.append(ref)

    return git(cmd)

################################################################################

def reset(sha1):
    """ Run git reset """

    return git(['reset', sha1])

################################################################################

def config_get(section, key, source=LOCAL, defaultvalue=None):
    """ Return the specified configuration entry
        Returns a default value if no matching configuration entry exists """

    cmd = ['config']

    if source == GLOBAL:
        cmd.append('--global')
    elif source == SYSTEM:
        cmd.append('--system')

    cmd += ['--get', f'{section}.{key}']

    try:
        return git(cmd)[0]
    except GitError:
        return defaultvalue

################################################################################

def config_set(section, key, value, source=LOCAL):
    """ Set a configuration entry """

    cmd = ['config']

    if source == GLOBAL:
        cmd.append('--global')
    elif source == SYSTEM:
        cmd.append('--system')

    cmd += ['--replace-all', f'{section}.{key}', value]

    return git(cmd)

################################################################################

def config_rm(section, key, source=LOCAL):
    """ Remove a configuration entry """

    cmd = ['config']

    if source == GLOBAL:
        cmd.append('--global')
    elif source == SYSTEM:
        cmd.append('--system')

    cmd += ['--unset', f'{section}.{key}']

    return git(cmd)

################################################################################

def ref(fields=('objectname'), sort=None, remotes=False):
    """ Wrapper for git for-each-ref """

    cmd = ['for-each-ref']

    if sort:
        cmd.append(f'--sort={sort}')

    field_list = []
    for field in fields:
        field_list.append('%%(%s)' % field)

    cmd += ['--format=%s' % '%00'.join(field_list), 'refs/heads']

    if remotes:
        cmd.append('refs/remotes/origin')

    for output in git(cmd):
        yield output.split('\0')

################################################################################

def branches(all=False):
    """ Return a list of all the branches in the current repo """

    cmd = ['branch']

    if all:
        cmd.append('--all')

    results = []
    for output in git(cmd):
        if ' -> ' not in output and '(HEAD detached at ' not in output:
            results.append(output[2:])

    return results

################################################################################

def delete_branch(branch, force=False, remote=False):
    """ Delete a branch, optionally forcefully and/or including the
        remote tracking branch """

    cmd = ['branch', '--delete']

    if force:
        cmd.append('--force')

    if remote:
        cmd.append('--remote')

    cmd.append(branch)

    return git(cmd)

################################################################################

def remote_prune(remote, dry_run=False):
    """ Return a list of remote tracking branches that no longer exist on the
        specified remote """

    cmd = ['remote', 'prune', remote]

    if dry_run:
        cmd.append('--dry-run')

    results = git(cmd)

    prunable_branches = []

    prune_re = re.compile(r'\s[*]\s\[would prune\]\s(.*)')

    for result in results:
        matches = prune_re.match(result)
        if matches:
            prunable_branches.append(matches.group(1))

    return prunable_branches

################################################################################

def get_commits(commit1, commit2):
    """ Get a list of commits separating two commits """

    return git(['rev-list', commit1, f'^{commit2}'])

################################################################################

def commit_count(commit1, commit2):
    """ Get a count of the number of commits between two commits """

    return int(git(['rev-list', '--count', commit1, f'^{commit2}'])[0])

################################################################################

def branch_name(branch):
    """ Return the full name of a branch given an abbreviation - e.g. @{upstream}
        for the upstream branch """

    return git(['rev-parse', '--abbrev-ref', '--symbolic-full-name', branch])[0]

################################################################################

def author(commit):
    """ Return the author of a commit """

    return git(['show', '--format=format:%an', commit])[0]

################################################################################

def commit_changes(commit='HEAD'):
    """Return a list of the files changed in a commit"""

    return git(['show', '--name-only', '--pretty=format:', commit])

################################################################################

def files(dir=None):
    """ Return the output from 'git ls-files' """

    cmd = ['ls-files']

    if dir:
        cmd.append(dir)

    return git(cmd)

################################################################################

def stash():
    """ Return the list of stashed items (if any) """

    cmd = ['stash', 'list']

    return git(cmd)

################################################################################

def parents(commit=None, ignore=None):
    """ Look at the commits down the history of the specified branch,
        looking for another branch or branches that also contain the same commit.
        The first found is the parent (or equally-likely parents) of the
        branch - note due to fundamental git-ness a given branch can have multiple
        equally-plasuible parents.

        Return the list of possible parents and the distance down the branch
        from the current commit to those posible parents """

    # Get the history of the branch

    current_branch = commit or branch('HEAD')

    current_history = git(['rev-list', current_branch])

    # Look down the commits on the current branch for other branches that have
    # the same commit, using the ignore pattern if there is one.

    for distance, ancestor in enumerate(current_history):
        branches = []
        for brnch in git(['branch', '--contains', ancestor]):
            brnch = brnch[2:]
            if brnch != current_branch and '(HEAD detached at' not in brnch:
                if not ignore or (ignore and not fnmatch.fnmatch(brnch, ignore)):
                    branches.append(brnch)

        if branches:
            break
    else:
        return None, 0

    return branches, distance

################################################################################

def find_common_ancestor(branch1='HEAD', branch2='master'):
    """ Find the first (oldest) commit that the two branches have in common
        i.e. the point where one branch was forked from the other """

    common = git(['merge-base', branch1, branch2])[0]

    return common

################################################################################

# List of boolean options to git.grep with corresponding command line option to use if option is True

_GREP_OPTLIST = \
    (
        ('color', '--color=always'),
        ('count', '--count'),
        ('folow', '--follow'),
        ('unmatch', '-I'),
        ('textconf', '--textconv'),
        ('ignore_case', '--ignore-case'),
        ('word_regexp', '--word-regexp'),
        ('invert_match', '--invert-match'),
        ('full_name', '--full-name'),
        ('extended_regexp', '--extended-regexp'),
        ('basic_regexp', '--basic-regexp'),
        ('perl_regexp', '--perl-regexp'),
        ('fixed_strings', '--fixed-strings'),
        ('line_number', '--line-number'),
        ('files_with_matches', '--files-with-matches'),
        ('files_without_match', '--files-without-match'),
        ('names_only', '--names-only'),
        ('null', '--null'),
        ('count', '--count'),
        ('all_match', '--all-match'),
        ('quiet', '--quiet'),
        ('color', '--color=always'),
        ('no_color', '--no-color'),
        ('break', '--break'),
        ('heading', '--heading'),
        ('show_function', '--show-function'),
        ('function_context', '--function-context'),
        ('only_matching', '--only-matching'),
    )

# List of non-boolean options to git.grep with corresponding command line option

_GREP_NON_BOOL_OPTLIST = \
    (
        ('root', '--root'),
        ('max_depth', '--max-depth'),
        ('after_context', '--after-context'),
        ('before_context', '--before-context'),
        ('context', '--context'),
        ('threads', '--threads'),
        ('file', '--file'),
        ('parent_basename', '--parent-basename')
    )

def grep(pattern, git_dir=None, work_tree=None, options=None, wildcards=None):
    """ Run git grep - takes a painfully large number of options passed
        as a dictionary. """

    cmd = []

    if git_dir:
        cmd += ['--git-dir', git_dir]

    if work_tree:
        cmd += ['--work-tree', work_tree]

    cmd += ['grep']

    if options:
        # Boolean options

        for opt in _GREP_OPTLIST:
            if options.get(opt[0], False):
                cmd.append(opt[1])

        # Non-boolean options

        for opt in _GREP_NON_BOOL_OPTLIST:
            value = options.get(opt[0], None)
            if value:
                cmd += (opt[1], value)

    if isinstance(pattern, list):
        cmd += pattern
    else:
        cmd += [pattern]

    if wildcards:
        cmd.append('--')
        cmd += wildcards

    return git_run_status(cmd)

################################################################################

def isbranch(branchname):
    """ Return true if the specified branch exists """

    return branchname in branches(True)

################################################################################

def default_branch():
    """ Return the name of the default branch, attempting to interrogate GitLab
        if the repo appears to have been cloned from there and falling back to
        returning whichever one of 'develop', 'main' or 'master' exists. """

    remote_list = remotes()
    if remote_list:
        for name in remote_list:
            if 'gitlab' in remote_list[name]:
                url = remote_list[name].split('@')[1].split(':')[0]
                repo = remote_list[name].split(':')[1]

                if not url.startswith('http://') or not url.startswith('https://'):
                    url = f'https://{url}'

                if repo.endswith('.git'):
                    repo = repo[:-4]

                try:
                    gl = gitlab.GitLab(url)
                    return gl.default_branch(repo)

                except gitlab.GitLabError:
                    return None

    git_branches = branches()

    for branch in ('develop', 'main', 'master'):
        if branch in git_branches:
            return branch

    return None

################################################################################

def matching_branch(branchname, case=False):
    """ Look for a branch matching the specified name and return it
        out if it is an exact match or there is only one partial
        match. If there are multiple branches that match, return them
        as a list.

        If case == True then the comparison is case-sensitive.

        If the branchname contains '*' or '?' wildcard matching is used,.
        otherwise, it just checks for a branches containing the branchname
        as a substring. """

    all_branches = branches(all=True)

    # Always return exact matches

    if branchname in all_branches:
        return [branchname]

    matching = []
    matching_remote = []

    if not case:
        branchname = branchname.lower()

    if branchname == '-' * len(branchname):
        matching = [branchname]
    else:
        wildcard = '?' in branchname or '*' in branchname

        if wildcard:
            if branchname[0] not in ('?', '*'):
                branchname = f'*{branchname}'

            if branchname[-1] not in ('?', '*'):
                branchname = f'{branchname}*'

        for branch in all_branches:
            branchmatch = branch if case else branch.lower()

            # We have a partial match

            if (not wildcard and branchname in branchmatch) or (wildcard and fnmatch.fnmatch(branchmatch, branchname)):
                # If the match is a remote branch, ignore it if we already have the equivalent
                # local branch, otherwise add the name of the local branch that would be created.

                if branch.startswith('remotes/'):
                    localbranch = '/'.join(branch.split('/')[2:])
                    if localbranch not in matching:
                        matching_remote.append(localbranch)
                else:
                    matching.append(branch)

    # If we don't have matching local branches use the remote branch list (which may also be empty)

    if not matching:
        matching = matching_remote

    # Return the list of matches

    return matching

################################################################################

def update(clean=False, all=False):
    """ Run git update (which is a thingy command, and may end up as a module
        but for the moment, we'll treat it as any other git command) """

    cmd = ['update']

    if clean:
        cmd.append('--clean')

    if all:
        cmd.append('--all')

    return git(cmd)

################################################################################

def object_type(name):
    """ Return the git object type (commit, tag, blob, ...) """

    return git(['cat-file', '-t', name])[0]

################################################################################

def matching_commit(name):
    """ Similar to matching_branch() (see above).
        If the name uniquely matches a branch, return that
        If it matches multiple branches return a list
        If it doesn't match any branches, repeat the process for tags
        if it doesn't match any tags, repeat the process for commit IDs

        TODO: Currently matches multiple branches, tag, but only a unique commit - not sure if this the best behaviour, but it works """

    # First, look for exact matching object

    if iscommit(name):
        return [name]

    # Look for at least one matching branch

    matches = matching_branch(name)

    if matches:
        return matches

    # Look for at least one matching tag

    matches = []
    for tag in tags():
        if name in tag:
            matches.append(tag)

    if matches:
        return matches

    # Look for a matching commit

    try:
        commit_type = object_type(name)

        if commit_type == 'commit':
            matches = [name]
    except GitError:
        matches = []

    return matches

################################################################################

def log(branch1, branch2=None):
    """ Return the git log between the given commits """

    if branch2:
        cmd = ['log', f'{branch1}...{branch2}']
    else:
        cmd = ['log', '-n1', branch1]

    return git(cmd)

################################################################################

def run_tests():
    """Test suite for the module"""

    print('Creating local git repo')

    init('test-repo')
    os.chdir('test-repo')

    try:
        print('Initial status:')
        print('  User name:            %s' % config_get('user', 'name'))
        print('  Project:              %s' % project())
        print('  Remotes:              %s' % remotes())
        print('  Current branch:       %s' % branch())
        print('  Current working tree: %s' % working_tree())
        print('  Rebasing?             %s' % rebasing())
        print('  Status:               %s' % status())
        print()

        print('Adding a removing a configuration value')

        config_set('user', 'size', 'medium')

        print('  User size config:     %s' % config_get('user', 'size'))

        config_rm('user', 'size')

        value = config_get('user', 'size')
        if value is None:
            print('  Successfully failed to read the newly-deleted config data')
        else:
            raise GitError('Unexpected lack of error reading configuration data', 1)

        config_set('user', 'email', 'user@localhost')
        config_set('user', 'name', 'User Name')

        print('')

        with open('newfile.txt', 'w') as newfile:
            newfile.write('THIS IS A TEST')

        print('Adding and committing "newfile.txt"')

        add(['newfile.txt'])

        commit(['newfile.txt'], 'Test the add and commit functionality')

        print('Removing and committing "newfile.txt"')

        rm(['newfile.txt'])

        commit(None, 'Removed "newfile.txt"')

        print('Removing the last commit')

        reset('HEAD~1')

        print('Commit info for HEAD  %s' % commit_info('HEAD'))

    except GitError as exc:
        sys.stderr.write('ERROR: %s' % exc.msg)
        sys.exit(1)

    finally:
        # If anything fails, then clean up afterwards

        os.chdir('..')
        shutil.rmtree('test-repo')

################################################################################
# Entry point

if __name__ == '__main__':
    run_tests()
