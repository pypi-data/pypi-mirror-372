#! /usr/bin/env python3

################################################################################
""" Docker interface for Thingy

    Copyright (C) 2017 John Skilleter

    Note that this:
        * Only implements functions required by docker-purge
        * Only has basic error checking, in that it raises DockerError
          for any error returned by the external docker command.
"""
################################################################################

# TODO: Convert to use thingy.proc
import thingy.process as process

################################################################################

class DockerError(Exception):
    """ Exception for dockery things """

    pass

################################################################################

def instances(all=False):
    """ Return a list of all current Docker instances """

    cmd = ['docker', 'ps', '-q']

    if all:
        cmd.append('-a')

    try:
        for result in process.run(cmd):
            yield result
    except process.RunError as exc:
        raise DockerError(exc)

################################################################################

def stop(instance, force=False):
    """ Stop the specified Docker instance """

    # TODO: force option not implemented

    try:
        process.run(['docker', 'stop', instance])
    except process.RunError as exc:
        raise DockerError(exc)

################################################################################

def rm(instance, force=False):
    """ Remove the specified instance """

    cmd = ['docker', 'rm']

    if force:
        cmd.append('--force')

    cmd.append(instance)

    try:
        process.run(cmd)
    except process.RunError as exc:
        raise DockerError(exc)

################################################################################

def images():
    """ Return a list of all current Docker images """

    try:
        for result in process.run(['docker', 'images', '-q']):
            yield result
    except process.RunError as exc:
        raise DockerError(exc)

################################################################################

def rmi(image, force=False):
    """ Remove the specified image """

    cmd = ['docker', 'rmi']
    if force:
        cmd.append('--force')

    cmd.append(image)

    try:
        process.run(cmd)
    except process.RunError as exc:
        raise DockerError(exc)
