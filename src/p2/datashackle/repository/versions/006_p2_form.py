# -*- coding: utf-8 -*-

from p2.datashackle.repository.utils import write_form_cssrule
from p2.datashackle.repository.utils import flush_cssrules

mod = __import__('001_initial_schema')
p2_plan = getattr(mod, 'p2_plan')
p2_form = getattr(mod, 'p2_form')

def upgrade(migrate_engine):
    insStmt = p2_form.insert()
    identifier = migrate_engine.generate_random_identifier()
    result = insStmt.execute(active=True,
                             form_identifier=identifier,
                             form_name="plans",
                             fk_p2_plan='p2_plan')
    write_form_cssrule(identifier, 'height:40px; width:410px')

    migrate_engine.data['p2_plan_form_id'] = result.inserted_primary_key[0]
    p2_plan.update().where(p2_plan.c.plan_identifier == 'p2_plan').\
        execute(fk_default_form=migrate_engine.data['p2_plan_form_id']) 

    flush_cssrules()

def downgrade(migrate_engine):
    pass
