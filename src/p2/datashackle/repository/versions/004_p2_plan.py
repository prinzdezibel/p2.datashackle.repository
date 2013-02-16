# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010-2011
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import random
import pdb
import os.path

from sqlalchemy import *
from migrate import *
from migrate.changeset import *


mod = __import__('001_initial_schema')
p2_plan = getattr(mod, 'p2_plan')
p2_form = getattr(mod, 'p2_form')


def upgrade(migrate_engine):
    pass    

def downgrade(migrate_engine):
    pass
