# -*- coding: utf-8 -*-


import random

from sqlalchemy import *
from migrate import *
from migrate.changeset import *

mod = __import__('001_initial_schema')
p2_plan = getattr(mod, 'p2_plan')
p2_cardinality = getattr(mod, 'p2_cardinality')

def generate_random_identifier():
    n_id = random.randint(0, 100000000)
    id = "%08d" % n_id
    return id

metadata = MetaData()

cardinalitydict = {}

def upgrade(migrate_engine):
    global cardinalitydict
    metadata.bind = migrate_engine
    
    migrate_engine.data['cardinalities'] = cardinalitydict = {
        '1:n' : 'ONE_TO_MANY',
        '1(fk):1' : 'ONE(FK)_TO_ONE',
        '1:1(fk)' : 'ONE_TO_ONE(FK)',
        'n:1' : 'MANY_TO_ONE',
        'n:m' : 'MANY_TO_MANY',
        'None': 'NONE',
        }
    
    for cardinalityvalue,cardinalityid in cardinalitydict.items():
        p2_cardinality.insert().execute(
            id=cardinalityid,
            cardinality=cardinalityvalue,
        )

    p2_plan.insert().execute(plan_identifier='p2_cardinality',
                             klass='Cardinality', table='p2_cardinality')
    

def downgrade(migrate_engine):
    metadata.bind = migrate_engine



