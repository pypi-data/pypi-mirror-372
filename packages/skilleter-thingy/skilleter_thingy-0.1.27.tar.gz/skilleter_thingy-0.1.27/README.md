# Thingy

Licence: GPL v3

Author: John Skilleter v0.99

A collection of shell utilities and configuration stuff for Linux and MacOS. Untested on other operating systems.

Permanently (for the foreseeable future!) in a beta stage - usable, with a few rough edges, and probably with bugs when used in way I'm not expecting!

Install from PyPi via pip or pipx as the `skilleter-thingy` package; for instance - `pipx install skilleter_thingy`

The commands are categorised into:

* Git working tree management
* Miscellaneous commands
* Git Extensions
* General-purpose commands

# Git Working Tree Management

## Multigit

Multigit is a tool for managing a collection of related git working trees.

This is intended for use in a situation where you have a collection of related git working trees organised in a directory hierarchy which aren't managed using git submodules or any other tool. It allows you to run git commands on multiple working trees at once, without navigating around the different working trees to do so and to select which working trees commands are run in.

For ease of use it is recommended that you create an alias for multigit called `mg`. How you do this is dependent on the shell you use, for instance in Bash, you could create an alias in your `~/.bashrc` file:

    alias mg="multigit $@"

## Initialisation

To use multigit, start by creating working trees for the repositories that you want to use in a directory tree - the working trees can be at different levels or even nested, for example:

    multigit_tree
    |
    +----working tree 1
    |
    +---+subdirectory
    |   |
    |   +----working tree 2
    |   |
    |   +----working tree 3
    |
    +----working tree 4

Start by running ensuring that the default branch (e.g. `main`) is checked out in each of the working trees and, in the top-level directory, run `multigit init` to create the configuration file which, by default is called `multigit.toml` - this is just a text file that sets the configuration for each working tree in terms of name, origin, default branch, tags and location.

## Multigit Command Line

The multigit command line format is:

    multigit OPTIONS COMMAND

Where COMMAND is an internal multigit command if it starts with a `+` and is a git command otherwise (including the additional git commands described in this document).

By default, when multigit is invoked with a git command, it runs a the command in each of the working trees selected by the command line options passed to multigit (if no options are specified then the command is run in *all* the working trees.

The command takes a number of options that can be used to select the list of working trees that each of the subcommands that it supports runs in:

`--repos REPO` / `-r REPO` Allows a list of working trees to be specfied, either by path, name or a wildcard matching either.

`--modified` / `-m` Run only in working trees containing locally modified files

`--branched` / `-b` Run only in working trees where the current branch that is checked out is NOT the default branch

`--tag TAG` / `-t TAG` Run only in working trees that are tagged with the specified tag

`--sub` / `-s` Run only in working trees that are in the current directory tree.

`--continue` / `-o` Continue if a git command returns an error (by default, executation terminates when a command fails)

`--path PATH` / `-C PATH` Run as if the command was started in PATH instead of the current working directory

These options are AND-ed together, so specifying `--modified --branched --tag WOMBAT` will select only working trees that are modified AND branched AND tagged with `WOMBAT`, but the parameters to the `--repos` and `--tag` options are OR-ed together, so specifying `--tag WOMBAT --tag EMU` will select repos that are tagged as `WOMBAT` *OR* `EMU`.

Multigit tags are stored in the configuration file, not within the working tree and each working tree can have multiple tags.

## Multigit Commands

Multigit supports a small list of subcommands, each of which are prefixed with a `+` to distinguish them from Git commands:

`+clone REPO <BRANCH>` - Clone REPO (which should contain a multigit configuration file), checking out BRANCH, if specified, then clone all the repos specified in the configuration, checking out the default branch in each one.

`+init` - Create or update the configuration file

`+dir NAME` - Given the name of a working tree, output relative path(s) to one or more matching working trees. If `NAME` does NOT contains wildcard characters (`*` or `?`) then matching takes place as if `*` were prefixed and appended to it, otherwise, the wildcards are used as specified. If `NAME` is not specified then the location of the directory where the multigit configuration file resides is output.

`+list` - Return a list of the top level directories of each of the Git repos

`+config` - Print the name and location of the multigit configuration file.

`+tag TAG` - If no tag specified list tags applied to the specified working trees. If a tag *is* specified, then *apply* the tag to the specified working trees.

`+untag TAG` - Remove the tag from the specified working trees (do nothing if the tag is not applied in the first place).

`+run COMMAND` - Run the specified command in each of the specified working trees

`+add REPO DIR` - Clone REPO into the DIR directory and, if successful, add it to the multigit configuration

Any command *not* prefixed with `+` is run in each of the working trees (filtered by the various multigit options) as a git command.

For example; `multigit -m commit -ab` would run `git commit -a` in each of the working trees that is branched and contains modified files.

The `+dir` command can be used with shell aliases (or their equivalent in the user's shell of choice) to create an alias to run, for example, `cd (multigit +dir "$@")` (Bash) or `cd (multigit +dir $argv)` (for the Fish shell) that would cd to the top level directory.

# Miscellaneous Git Utilities

## gitprompt

Output a string containing colour-coded shell nesting level, current directory and git working tree status. It is intended to be used in the shell prompt; for instance, for Bash via adding:

    export PS1=$(gitprompt)

to the `~/.bashrc` file.

The appearance of the prompt is controlled by configuration settings in the `.gitconfig` file:

    [prompt]
    prefix = 0..2

The `prefix` value determines what git status information is shown in the prompt:

* 0 - No status information
* 1 - A single letter followed by a file count showing the number of stashed, untracked, modified, etc. files in the working tree
* 2 - As 1, but using a word, rather than a single letter

If a rebase, bisect or merge is process, this is also shown in the prompt.

The name of the repo and the current branch are also appended and the prompt is also colour-coded according to the state of the working tree.

# Git Extensions

Due to the way that the git command works, these can be run as they were additional git subcommands, although, due to a limitation in git, the only things that does not work is the `--help` option where the command has to be run with a hyphen between `git` and the subcommand - for example `git ca --help` does not work, but `git-ca --help` does.

## Branch Names

Where one of the git extensions takes an existing branch name as a parameter, the branch name can be abbreviated and the abbreviated form is expanded according to the following rules:

* If the specified branch name exactly matches an existing branch, tag or commit ID then that is used (this includes remote branches where appropriate, if no local branches match).
* Otherwise, the branch name is compared to existing branches (again, including remote branches where appropriate, if no local branches match) and, if the specified name uniquely partially matches an existing branch (optionally using `*` and `?` wildcard characters) that branch is used. If it matches multiple branches than an error is reported.

For example, given a repo with the following branches:

        origin/wombat
        origin/platypus
        wombat
        emu
        battery
        chaos

Then:

* 'emu' will match 'emu'
* 'wombat' will match 'wombat' but not 'origin/wombat' since the local branch takes precedence
* 'at' will match both 'wombat' and 'battery' and will report an error
* 'pus' will match 'origin/platypus'

This is most useful where branches contain ticket numbers so, for instance given a branch called `feature/SKIL-103` you can check it out using `git co 103` assuming no other local branches contain `103` in their name.

Note that the concept of the default branch `DEFAULT` mentioned above *only* applies when using the `multigit` command, although some of the commands will treat branches called `master` or `main` as special cases (see the individual command documentation).

## git ca

Improved version of 'git commit --amend'. Updates files that are already in the commit and, optionally, adds and commits additional files.

        usage: git-ca [-h] [--added] [--all] [--everything] [--ignored] [--patch] [--verbose] [--dry-run] [files ...]

        positional arguments:
          files             List of files to add to the commit

        options:
          -h, --help        show this help message and exit
          --added, -A       Update files in the current commit, including files added with `git add`
          --all, -a         Append all locally-modified, tracked files to the current commit
          --everything, -e  Append all modified and untracked files to the current commit (implies `~--all`)
          --ignored, -i     Include files normally hidden by `.gitignore`
          --patch, -p       Use the interactive patch selection interface to chose which changes to commit.
          --verbose, -v     Verbose mode
          --dry-run, -D     Dry-run

## git cleanup

List or delete branches that have already been merged and delete tracking branches that are no longer on the remote.

        git-cleanup [-h] [--delete] [--master MASTER] [--force] [--unmerged] [--yes] [--debug] [branches ...]

        positional arguments:

        branches              List of branches to check (default is all branches)

        options:
        -h, --help            show this help message and exit
        --delete, -d          Delete all branches that have been merged
        --master MASTER, -m MASTER, --main MASTER
                              Specify the master branch (Attempts to read this from GitLab or defaults to "develop" if present or "master" or "main" otherwise
        --force, -f           Allow protected branches (e.g. master) to be removed
        --unmerged, -u        List branches that have NOT been merged
        --yes, -y             Assume "yes" in response to any prompts (e.g. to delete branches)
        --debug               Enable debug output

## git co

Equivalent to `git checkout` but with enhanced branch matching as described above. The command does not support the full range of options supported by the `git checkout` comamnd which should still be used where additional functionality is required.

        git-co [-h] [--branch] [--update] [--rebase] [--force] [--exact] [--debug] branchname

        positional arguments:

        branchname    The branch name (or a partial name that matches uniquely against a local branch, remote branch, commit ID or tag)

        options:
        -h, --help    show this help message and exit
        --branch, -b  Create the specified branch
        --update, -u  If a remote branch exists, delete any local branch and check out the remote version
        --rebase, -r  Rebase the branch onto its parent after checking it out
        --force, -f   When using the update option, recreate the local branch even if it is owned by the current user (based on the author of the most recent commit)
        --exact, -e   Do not use branch name matching - check out the branch as specified (if it exists)
        --debug       Enable debug output

## git parent

Attempt to determine the parent branch for the specified branch (defaulting to the current one).

        git-parent [-h] [--all] [--verbose] [branch]

        Attempt to determine the parent branch for the specified branch (defaulting to the current one)

        positional arguments:
          branch         Branch, commit or commit (defaults to current branch; main)

        options:
          -h, --help     show this help message and exit
          --all, -a      Include feature branches as possible parents
          --verbose, -v  Report verbose results (includes number of commits between branch and parent)

## git update

Update the rworking tree from the remote, rebase local branch(es) against their parents and optionally run git cleanup.

    git-update [-h] [--cleanup] [--all] [--everything] [--default] [--parent PARENT] [--all-parents] [--stop] [--ignore IGNORE] [--verbose] [--dry-run]

    options:
      -h, --help            show this help message and exit
      --cleanup, -c         After updating a branch, delete it if there are no differences between it and its parent branch
      --all, -a             Update all local branches, not just the current one
      --everything, -A      Update all local branches, not just the current one and ignore the default ignore list specified in the Git configuration
      --default, -d         Checkout the main or master branch on completion
      --parent PARENT, -p PARENT
                            Specify the parent branch, rather than trying to work it out
      --all-parents, -P     Feature branches are not considered as alternative parents unless this option is specified
      --stop, -s            Stop if a rebase problem occurs, instead of skipping the branch
      --ignore IGNORE, -i IGNORE
                            List of one or more wildcard branch names not to attempt to update (uses update.ignore from the Git configuration if not specified)
      --verbose             Enable verbose output
      --dry-run             Report what would be done without actually doing it

## git wt

Output the top level directory of the git working tree or return an error if we are not in a git working tree.

    git-wt [-h] [--parent] [--dir DIR] [level]

    positional arguments:
      level              Number of levels below the top-level directory to report

    options:
      -h, --help         show this help message and exit
      --parent, -p       If we are already at the top of the working tree, check if the parent directory is in a working tree and output the top-level directory of that tree.
      --dir DIR, -d DIR  Find the location of the top-level directory in the working tree starting at the specified directory

## git review

Menu-driven Git code review tool

    git-review [-h] [--commit COMMIT] [--branch BRANCH] [--change] [--debug] [--dir DIR] [--difftool DIFFTOOL] [commits ...]

    positional arguments:
      commits               Commit(s) or paths to compare

    options:
      -h, --help            show this help message and exit
      --commit COMMIT, -c COMMIT
                            Compare the specified commit with its parent
      --branch BRANCH, -b BRANCH
                            Compare the specified commit to branch point on specified branch
      --change, -C          Compare the current commit with its parent
      --debug, -d           Start a debug session over Telnet using pudb
      --dir DIR             Work in the specified directory
      --difftool DIFFTOOL   Override the default git diff tool

# General Commands

## addpath

Add or remove entries from a path list (e.g. as used by the PATH environment variable)

    addpath [-h] [--add ADD] [--prefix PREFIX] [--suffix SUFFIX] [--remove REMOVE] [--force FORCE] [--separator SEPARATOR] path

    positional arguments:
      path                  The path to modify

    options:
      -h, --help            show this help message and exit
      --add ADD             Add an entry to the front of the path (do nothing if it is already present in the path)
      --prefix PREFIX       Add an entry to the front of the path (or move it there if it is already present)
      --suffix SUFFIX       Add an entry to the end of the path (or move it there if it is already present)
      --remove REMOVE       Remove an entry from the path (do nothing if it is not present
      --force FORCE         Add entries even if a corresponding directory does not exist
      --separator SEPARATOR
                            Override the default path separator

## docker-purge

Stop or kill docker instances and/or remove docker images.

    docker-purge [-h] [--stop] [--kill] [--remove] [--list] [--force] [--debug] [images ...]

    positional arguments:
      images        List of Docker containers (regular expression)

    options:
      -h, --help    show this help message and exit
      --stop, -s    Stop Docker instances
      --kill, -k    Kill Docker instances
      --remove, -r  Remove Docker images
      --list, -l    List what would be done without doing it
      --force, -f   Forcibly kill/remove instances
      --debug       Enable debug output

## ffind

Simple file find utility - replaces the `find` command with something that is more human-friendly.

    ffind [-h] [--path PATH] [--long] [--colour] [--no-colour] [--all] [--zero] [--iname] [--follow] [--git] [--diff] [--regex] [--fullpath] [--human-readable] [--grep GREP] [--abspath]
                [--unquoted] [--quiet] [--invert] [--exec EXEC] [--count] [--count-only] [--type TYPE] [--file] [--dir] [--block] [--char] [--pipe] [--symlink] [--socket] [--any] [--verbose]
                [--debug]
                [patterns ...]

    positional arguments:
      patterns              List of things to search for.

    options:
      -h, --help            show this help message and exit
      --path PATH, -p PATH  Search the specified path, rather than the current directory
      --long, -l            Output details of any files that match (cannot be used with -0/--zero)
      --colour, -C, --color
                            Colourise output even if not outputting to the terminal
      --no-colour, -N, --no-color
                            Never colourise output
      --all                 Search all directories (do not skip .git, and similar control directories)
      --zero, -0            Output results separated by NUL characters
      --iname, -i           Perform case-independent search
      --follow, -F          Follow symlinks
      --git, -g             Only search for objects in the current git repository
      --diff, -D, --diffuse
                            Run Diffuse to on all the found objects (files only)
      --regex, -R           Use regex matching rather than globbing
      --fullpath, -P        Match the entire path, rather than just the filename
      --human-readable, -H  When reporting results in long format, use human-readable sizes
      --grep GREP, -G GREP  Only report files that contain text that matches the specified regular expression
      --abspath, -A         Report the absolute path to matching entities, rather than the relative path
      --unquoted, -U        Do not use quotation marks around results containing spaces
      --quiet, -q           Do not report permission errors that prevented a complete search
      --invert, -I          Invert the wildcard - list files that do not match
      --exec EXEC, -x EXEC  Execute the specified command on each match (optionally use ^ to mark the position of the filename)
      --count, -K           Report the number of objects found
      --count-only, -c      Just report the number of objects found
      --type TYPE, -t TYPE  Type of item(s) to include in the results, where b=block device, c=character device, d=directory, p=pipe, f=file, l=symlink, s=socket. Defaults to files and directories
      --file, -f            Include files in the results (the default if no other type specified)
      --dir, -d             Include directories in the results
      --block               Include block devices in the results
      --char                Include character devices in the results
      --pipe                Include pipes in the results
      --symlink, --link     Include symbolic links in the results
      --socket              Include sockets in the results
      --any, -a             Include all types of item (the default unless specific types specified)
      --verbose, -v         Output verbose data
      --debug               Output debug data

## linecount

Summarise number of files, lines of text and total size of files in a directory tree

    usage: linecount [-h] [--ext]

    options:
      -h, --help  show this help message and exit
      --ext, -e   Identify file type using the file extension (faster but less accurrate)

## py-audit

Query api.osv.dev to determine whether a specified version of a particular Python package is subject to known security vulnerabilities

    py-audit [-h] [requirements ...]

    positional arguments:
      requirements  The requirements file (if not specified, then the script searches for a requirements.txt file)

    options:
      -h, --help    show this help message and exit

## readable

Remove 'cruft' from log files to make them easier to read and compare. Can remove times, dates, hashes and has options to remove a lot of the 'noise' that Terraform generates and tidy up the output.

    readable [-h] [--light] [--dark] [--none] [--tidy] [--strip-blank] [--debug] [--out] [--dir DIR] [--aws] [--terraform] [--replace REPLACE] [--verbose] [--minimal] [--non-minimal]
                    [files ...]

    positional arguments:
      files                 The files to convert (use stdin/stout if no input files are specified)

    options:
      -h, --help            show this help message and exit
      --light, -l           Modify colours for a light background (the default)
      --dark, -d            Modify colours for a dark background
      --none, -n            Remove all colour codes
      --tidy, -t            Remove colour codes and stuff that typically occurs in log files causing diffs, but is of no particular interest (e.g. SHA1 values, times, dates)
      --strip-blank, -s     Strip all blank lines
      --debug, -D           Replace colours with debug information
      --out, -o             Output to standard output rather than overwriting input files
      --dir DIR, -O DIR     Store output files in the specified directory (creating it if it doesn't exist)
      --aws, -a             Remove AWS resource IDs
      --terraform, -T       Clean Terraform plan/apply log files
      --replace REPLACE, -R REPLACE
                            Additional regex replacements in the form "REGEX=REPLACEMENT"
      --verbose, -v         Output verbose status
      --minimal, -m         Remove unnecessary data from the file (e.g. Terraform progress updates (Refreshing..., Reading..., etc.))
      --non-minimal, -M     Do not remove unnecessary data from the file (e.g. Terraform progress updates (Refreshing..., Reading..., etc.))

## remdir

Recursively delete empty directories

    remdir [-h] [--dry-run] [--debug] [--verbose] [--ignore IGNORE] [--keep KEEP] dirs [dirs ...]

    positional arguments:
      dirs                  Directories to prune

    options:
      -h, --help            show this help message and exit
      --dry-run, -D         Dry-run - report what would be done without doing anything
      --debug               Output debug information
      --verbose             Output verbose information
      --ignore IGNORE, -I IGNORE
                            Files to ignore when considering whether a directory is empty
      --keep KEEP, -K KEEP  Directories that should be kept even if they are empty

## rmdupe

Search for duplicate files.

    rmdupe [-h] [--debug] [--save SAVE] [--load LOAD] [--script SCRIPT] [--exclude EXCLUDE] [--ignore IGNORE] [path]

    positional arguments:
      path               Path(s) to search for duplicates

    options:
      -h, --help         show this help message and exit
      --debug            Debug output
      --save SAVE        Save duplicate file list
      --load LOAD        Load duplicate file list
      --script SCRIPT    Generate a shell script to delete the duplicates
      --exclude EXCLUDE  Directories to skip when looking for duplicates
      --ignore IGNORE    Wildcards to ignore when looking for duplicates

## rpylint

Run pylint on all the Python source files in a directory tree

    usage: rpylint [-h] [paths ...]

    positional arguments:
      paths       List of files or paths to lint

    options:
      -h, --help  show this help message and exit

## s3-sync

Synchronise files from S3 to local storage.

## strreplace

Simple search and replace utility for those times when trying to escape characters in a regexp to use sed is more hassle than it is worth.

  strreplace [-h] [--inplace] search replace [infile] [outfile]

  positional arguments:
    search         Search text
    replace        Replacment text
    infile         Input file
    outfile        Output file

  options:
    -h, --help     show this help message and exit
    --inplace, -i  Do an in-place search and replace on the input file

## tfm

Console-based file-manager, similar to Midnight Commander but aiming to be better.

    usage: tfm [-h] [--pudb]

    options:
      -h, --help  show this help message and exit
      --pudb      Invoke pudb debugger over Telnet

## tfparse

Read JSON Terraform output and convert back to human-readable text

This allows multiple errors and warnings to be reported as there's no way of doing this directly from Terraform

    usage: tfparse [-h] [--abspath] [infile ...]

    positional arguments:
      infile         The error file (defaults to standard input if not specified)

    options:
      -h, --help     show this help message and exit
      --abspath, -a  Output absolute file paths

## trimpath

Intelligently trim a path to fit a given width (used by gitprompt)

## venv-create

Create a script to create/update a virtual environment and run a python script in it.

    usage: venv-create [-h] name

    positional arguments:
      name        Name of the script to create

    options:
      -h, --help  show this help message and exit

## xchmod

Command to run chmod only on files that need it (only modifies files that don't have the required permissions already).

    usage: xchmod [-h] [--debug] [--verbose] [--recursive] mode paths [paths ...]

    positional arguments:
      mode             Mode to set
      paths            List of directory paths to search

    options:
      -h, --help       show this help message and exit
      --debug          Output the list of files (if any) that need to be made publically writeable
      --verbose        List files as they are updated
      --recursive, -R  Operate recursively

## yamlcheck

YAML validator - checks that a file is valid YAML (use yamllint to verify that it is nicely-formatted YAML).

    usage: yamlcheck [-h] [--dump] [--block] [--flow] [--hiera] files [files ...]

    positional arguments:
      files       YAML source file

    options:
      -h, --help  show this help message and exit
      --dump      Dump the YAML data after parsing it
      --block     Force block style when dumping the YAML data
      --flow      Force flow style when dumping the YAML data
      --hiera     Process the file as Puppet Hiera data

# Obsolescent Utilities

These will be moved to the skilleter-extras package in due course.

## borger

Wrapper for the borg backup utility to make it easier to use with a fixed set of options.

## consolecolours

Display all available colours in the console.

## diskspacecheck

Check how much free space is available on all filesystems, ignoring read-only filesystems, /dev and tmpfs.

Issue a warning if any are above 90% used.

## gphotosync & localphotosync

Utilities for syncing photos from Google Photos or a local directory to local storage

## moviemover

Search for files matching a wildcard in a directory tree and move them to an equivalent location in a different tree

## phototidier

Perform various tidying operations on a directory full of photos:

* Remove leading '$' and '_' from filenames
* Move files in hidden directories up 1 level
* If the EXIF data in a photo indicates that it was taken on date that doesn't match the name of the directory it is stored in (in YYYY-MM-DD format) then it is moved to the correct directory, creating it if necessary.

All move/rename operations are carried out safely with the file being moved having
a numeric suffix added to the name if it conflicts with an existing file.

## photodupe

Search for duplicate images in a directory tree

## splitpics

Copy a directory full of pictures to a destination, creating subdiretories with a fixed number of pictures in each in the destination directory for use with FAT filesystems and digital photo frames.

## sysmon

Simple console system monitor

## window-rename

Monitor window titles and rename them to fit an alphabetical grouping in 'Appname - Document' format.

# Obsolescent Commands

These commands will probably be retired in future versions of Thingy

## ggit

Run a git command in all working trees under the current directory (superceded by multigit).

## ggrep

Run 'git grep' in all repos under the current directory (superceded by multigit).

## GitLab Commands

### git mr

Push a feature branch to GitLab and create a merge request

### gl

Command line for GitLab
