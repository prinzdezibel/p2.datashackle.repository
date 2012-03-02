# -*- coding: utf-8 -*-

from optparse import OptionParser


from migrate.exceptions import DatabaseNotControlledError
from migrate.versioning.api import db_version, version_control
from migrate.versioning import shell


def main(url, repository):
    # Check if database is under version control
    try:
        db_version(url, repository)
    except DatabaseNotControlledError:
        # put database under version control
        version_control(url, repository)         

    kwargs = {'url': url,
        'repository': repository
    }

    shell.main(**kwargs)


