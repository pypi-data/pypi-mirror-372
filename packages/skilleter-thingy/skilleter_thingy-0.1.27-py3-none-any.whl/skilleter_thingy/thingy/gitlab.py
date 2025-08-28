#! /usr/bin/env python3

################################################################################
""" GitLab module - implemented using the REST API as some features are not
    available (or don't work) in the official Python module

    Copyright (C) 2017-20 John Skilleter

    Licence: GPL v3 or later

    Note: There are two types of function for returning data from GitLab;
    the paged functions and the non-paged ones - the paged ones return a page
    (normally 20 items) of data and need to be called repeated until no data is
    left whereas the non-paged ones query all the data and concatenate it
    together.

    The paged functions expect a full request string with the URL, as returned
    by the request_string() member. The non-paged ones call request_string()
    to add the URL & API prefix.
"""
################################################################################

import sys
import os

try:
    import requests
except ModuleNotFoundError:
    sys.stderr.write('This code requires the Python "requests" module which should be installed via your package manager\n')
    sys.exit(1)

################################################################################

class GitLabError(Exception):
    """ Gitlab exceptions """

    def __init__(self, response):
        """ Save the error code and text """

        self.status = response.status_code
        self.message = response.reason

    def __str__(self):
        """ Return a string version of the exception """

        return '%s: %s' % (self.status, self.message)

################################################################################

class GitLab:
    """ Class for GitLab access """

    def __init__(self, gitlab, token=None):
        """ Initialisation """

        # Save the GitLab URL

        self.gitlab = gitlab

        # If we have a private token use it, otherwise try and get it from
        # the environmnet

        self.token = token if token else os.getenv('GITLAB_TOKEN', None)

        # Create the default header for requests

        self.header = {'Private-Token': self.token}

    ################################################################################

    @staticmethod
    def encode_project(name):
        """ Encode a project name in the form request by GitLab requests """

        return name.replace('/', '%2F')

    ################################################################################

    def request_string(self, request):
        """ Add the URL/API header onto a request string """

        return '%s/api/v4/%s' % (self.gitlab, request)

    ################################################################################

    def request(self, request, parameters=None):
        """ Send a request to GitLab - handles pagination and returns all the
            results concatenated together """

        if parameters:
            request = '%s?%s' % (request, '&'.join(parameters))

        gl_request = self.request_string(request)

        # Keep requesting data until there's no 'next' link in the response

        while True:
            response = requests.get(gl_request, headers=self.header)

            if not response:
                raise GitLabError(response)

            yield response.json()

            if 'next' not in response.links:
                break

            gl_request = response.links['next']['url']

    ################################################################################

    def paged_request(self, request):
        """ Send a request to GitLab - returns all the results concatenated together
            and returns a page of results along with the request for the next page of
            results (if any).

            Note that the request parameter is the full request string as returned by
            request_string(). """

        response = requests.get(request, headers=self.header)

        result = response.json()

        if not response:
            raise GitLabError(response)

        request = response.links['next']['url'] if 'next' in response.links else None

        return result, request

    ################################################################################

    def projects(self):
        """ Return a list of projects """

        return self.request('projects')

    ################################################################################

    def branches(self, repo):
        """ Return the list of branches in a repo """

        for batch in self.request('projects/%s/repository/branches' % self.encode_project(repo)):
            for branch in batch:
                yield branch

    ################################################################################

    def merge_requests(self, **kwargs):
        """ Return a list of merge requests filtered according to the parameters """

        request = 'merge_requests'

        parameters = []

        for data in kwargs:
            parameters.append('%s=%s' % (data, kwargs[data]))

        for result in self.request(request, parameters):
            for r in result:
                yield r

    ################################################################################

    def default_branch(self, repo):
        """ Query gitlab to retreive the default branch for the repo """

        # Look for the default branch

        for branch in self.branches(repo):
            if branch['default']:
                return branch['name']

        return None

    ################################################################################

    def isbranch(self, repo, branchname):
        """ Return True if the branch exists in the repo """

        request = self.request_string('projects/%s/repository/branches' % self.encode_project(repo))

        while True:
            branches, request = self.paged_request(request)

            for branch in branches:
                if branch['name'] == branchname:
                    return True

            if not request:
                break

        return False
