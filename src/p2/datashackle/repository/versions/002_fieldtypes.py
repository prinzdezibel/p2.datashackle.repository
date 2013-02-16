# -*- coding: utf-8 -*-

import random

from sqlalchemy import *
from migrate import *
from migrate.changeset import *

mod = __import__('001_initial_schema')
p2_plan = getattr(mod, 'p2_plan')
p2_fieldtype = getattr(mod, 'p2_fieldtype')

def generate_random_identifier():
    n_id = random.randint(0, 100000000)
    id = "%08d" % n_id
    return id

metadata = MetaData()


def upgrade(migrate_engine):
    metadata.bind = migrate_engine
    
    p2_plan.insert().execute(plan_identifier='p2_fieldtype',
                             klass='p2_fieldtype', table='p2_fieldtype')

    p2_fieldtype.insert().execute(
        id=generate_random_identifier(),
        field_type='date',
    )
    p2_fieldtype.insert().execute(
        id=generate_random_identifier(),
        field_type='text',
    )
    p2_fieldtype.insert().execute(
        id=generate_random_identifier(),
        field_type='textline',
    )

    
def downgrade(migrate_engine):
    metadata.bind = migrate_engine


