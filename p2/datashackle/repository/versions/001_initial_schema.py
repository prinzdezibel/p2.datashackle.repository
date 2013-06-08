# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2010
# Author:  Michael Jenny <michael.jenny%40projekt-und-partner.com>

import random

from sqlalchemy import *
from migrate import *
from migrate.changeset import *
from migrate.changeset.constraint import ForeignKeyConstraint


class upgradedataobj(object):

    def generate_random_identifier(self):
        n_id = random.randint(0, 100000000)
        id = "%08d" % n_id
        return id

metadata = MetaData()

p2_plan = Table('p2_plan',
                metadata,
                Column('plan_identifier', String(length=255), primary_key=True, nullable=False, autoincrement=False),
                Column('fk_default_form', String(10), index=True),
                Column('klass', String(255), nullable=True, unique=True),
                Column('table', String(255), nullable=True),
                mysql_engine='InnoDB',
                )


# Layout options
# 0 : form layout (absolute positioning)
# 1 : list layout (document flow)
# 2 : tree layout (document flow)
p2_form = Table('p2_form',
                metadata,
                Column('form_identifier', String(16), primary_key=True, autoincrement=False),
                Column('form_name', String(63)),
                Column('fk_p2_plan', 
                       ForeignKey('p2_plan.plan_identifier', onupdate="CASCADE"),
                       nullable=True),
                Column('css', String(1023), nullable=False, default=''),
                Column('fk_p2_formlayout',
                       ForeignKey('p2_formlayout.id', onupdate="CASCADE"),
                       default='FORM'),
                mysql_engine='InnoDB',
                )

p2_widget = Table('p2_widget',
                metadata,
                Column('widget_identifier', String(10), primary_key=True, autoincrement=False),
                Column('fk_p2_form', ForeignKey('p2_form.form_identifier')),
                Column('widget_type', ForeignKey('p2_plan.klass', onupdate="CASCADE")),
                Column('css', String(1023), nullable=False, default=''),
                Column('tab_order', Integer, nullable=False, default=0),
                mysql_engine='InnoDB',
                )

#p2_widget_type = Table('p2_widget_type', metadata,
#                       Column('id', String(63), primary_key=True, autoincrement=False),
#                       mysql_engine='InnoDB')

p2_cardinality = Table('p2_cardinality',
   metadata,
   Column('id', String(length=32), primary_key=True, nullable=False, autoincrement=False),
   Column('cardinality', String(64), nullable=False),
   mysql_engine='InnoDB',
)

#p2_embform_characteristic = Table('p2_embform_characteristic',
#   metadata,
#   Column('id', String(length=32), primary_key=True, nullable=False, autoincrement=False),
#   Column('title', String(64), nullable=False),
#   mysql_engine='InnoDB',
#)

p2_relation = Table('p2_relation',
             metadata,
             Column('id', String(10), primary_key=True, autoincrement=False),
             Column('foreignkeycol', String(63), nullable=True),
             Column('foreignkeycol2', String(63), nullable=True), # Required for n:m relations
             Column('source_table', String(255), nullable=True),
             Column('target_table', String(255), nullable=True),
             Column('xref_table', String(255), nullable=True),
             Column('fk_p2_cardinality', ForeignKey('p2_cardinality.id'), nullable=False),
             mysql_engine='InnoDB')

p2_linkage = Table('p2_linkage',
             metadata,
             Column('id', String(10), primary_key=True, autoincrement=False),
             Column('attr_name', String(63), nullable=True),
             Column('ref_key', String(63), nullable=True),
             Column('back_populates', String(63), nullable=True),
             Column('cascade', String(255), nullable=True),
             Column('fk_p2_relation', ForeignKey('p2_relation.id', onupdate="CASCADE"), nullable=True),
             Column('post_update', Boolean), #http://www.sqlalchemy.org/docs/05/mappers.html#rows-that-point-to-themselves-mutually-dependent-rows
             Column('fk_source_model', ForeignKey('p2_plan.plan_identifier', onupdate="CASCADE"), nullable=True),
             Column('fk_target_model', ForeignKey('p2_plan.plan_identifier', onupdate="CASCADE"), nullable=True),
             mysql_engine='InnoDB')


p2_span = Table('p2_span',
            metadata,
            Column('span_identifier', String(10)),
            Column('fk_p2_widget', ForeignKey('p2_widget.widget_identifier')),
            Column('span_name', String(63), index=True),
            Column('span_type', ForeignKey('p2_plan.klass', onupdate="CASCADE")),
            Column('span_value', String(255), nullable=True),
            Column('css', String(1023), nullable=False, default=''),
            Column('visible', Boolean, nullable=True, default=True),
            Column('order', Integer, primary_key=True, autoincrement=True), # Primary key is only temporarily. We are interested in the autoincrement functionality. See below.
            mysql_engine='InnoDB',
            )
# HACK: We want an autoincrementing order field. This allows the spans to retain the insert order.
# http://stackoverflow.com/questions/2937229/set-auto-increment-using-sqlalchemy-with-mysql-on-columns-with-non-primary-keys/5410205#5410205
from sqlalchemy.schema import DDL
DDL("ALTER TABLE p2_span DROP PRIMARY KEY, ADD UNIQUE KEY(`order`); ALTER TABLE p2_span ADD PRIMARY KEY(`span_identifier`);", on='mysql').execute_at('after-create', p2_span)



# This table inherits all attributes from p2_span!
p2_span_alphanumeric = Table('p2_span_alphanumeric',
                 metadata,
                 Column('span_identifier', String(10), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True), # Joined table inheritance!
                 Column('attr_name', String(63), nullable=True),
                 Column('field_identifier', String(63), nullable=True),
                 #Column('multi_line', Boolean, nullable=True),
                 Column('fk_field_type', ForeignKey('p2_fieldtype.id'), nullable=True),
                 Column('required', Boolean, nullable=True, default=True),
                 mysql_engine='InnoDB'
                 )

# This table inherits all attributes from p2_span!
p2_span_checkbox = Table('p2_span_checkbox',
                 metadata,
                 Column('span_identifier', String(10), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True), # Joined table inheritance!
                 Column('attr_name', String(63), nullable=True),
                 Column('field_identifier', String(63), nullable=True),
                 mysql_engine='InnoDB'
                 )

# This table inherits all attributes from p2_span!
p2_span_dropdown = Table('p2_span_dropdown',
                 metadata,
                 Column('span_identifier', String(10), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True),
                 Column('fk_p2_linkage', ForeignKey('p2_linkage.id', onupdate="CASCADE")),
                 Column('plan_identifier', String(63), nullable=True),
                 Column('attr_name', String(63), nullable=True),
                 Column('required', Boolean, nullable=True, default=False),
                 mysql_engine='InnoDB'
                 )

# This table inherits all attributes from p2_span!
p2_span_embeddedform = Table('p2_span_embeddedform',
                 metadata,
                 Column('span_identifier', String(10), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True),
                 Column('form_name', String(63), nullable=True),
                 Column('plan_identifier', String(63), nullable=True),
                 Column('filter_clause', String(255), nullable=True),
                 Column('editable', Boolean, default=True),
                 Column('fk_p2_linkage', ForeignKey('p2_linkage.id', onupdate="CASCADE"), nullable=True),
                 #Column('fk_characteristic', ForeignKey('p2_embform_characteristic.id', onupdate="CASCADE"), nullable=False, default="LIST"),
                 #Column('adjacency_linkage', String(10), nullable=True),
                 mysql_engine='InnoDB'
                 )

# Joined table inheritance. This table inherits all attributes from p2_span!
p2_span_fileupload = Table('p2_span_fileupload',
                 metadata,
                 Column('span_identifier', String(10), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True),
                 Column('fk_p2_linkage', ForeignKey('p2_linkage.id', onupdate="CASCADE")),
                 Column('fk_p2_relation', ForeignKey('p2_relation.id', onupdate="CASCADE")),
                 mysql_engine='InnoDB'
                 )

# This table inherits all attributes from p2_span!
p2_span_action = Table('p2_span_action',
                 metadata,
                 Column('span_identifier', String(10), ForeignKey('p2_span.span_identifier', onupdate="CASCADE"), primary_key=True),
                 Column('aktion', String(63), nullable=True),
                 mysql_engine='InnoDB'
                 )

p2_archetype = Table('p2_archetype',
                         metadata,
                         Column('id', String(10), primary_key=True, autoincrement=False),
                         mysql_engine='InnoDB'
                         )

p2_media = Table('p2_media',
                  metadata,
                  Column('id', String(10), primary_key=True, autoincrement=True),
                  Column('filename', String(255), nullable=True),
                  Column('size', Integer, nullable=True),
                  Column('data', BLOB(16777215)),
                  Column('thumbnail', BLOB),
                  Column('mime_type', String(63)),
                  mysql_engine='InnoDB'
                 )

p2_fieldtype = Table('p2_fieldtype',
   metadata,
   Column('id', String(10), primary_key=True, nullable=False, autoincrement=False),
   Column('field_type', String(32), nullable=False),
   mysql_engine='InnoDB',
)

p2_country = Table('p2_country',
   metadata,
   Column('id', String(10), primary_key=True, nullable=False, autoincrement=False),
   Column('country_name', String(64), nullable=False),
   Column('country_iso_code_2', CHAR(length=2), nullable=False),
   Column('country_iso_code_3', CHAR(length=3), nullable=False),
   mysql_engine='InnoDB',
)


p2_formlayout = Table('p2_formlayout', metadata, 
                      Column('id', String(10),
                      primary_key=True, autoincrement=False), 
                      Column('name', String(32)),
                      mysql_engine='InnoDB')

                                
def upgrade(migrate_engine):
    # Upgrade operations go here.
    metadata.bind = migrate_engine
    
    metadata.create_all()

    ForeignKeyConstraint(columns=[p2_plan.c.fk_default_form]  , refcolumns=[p2_form.c.form_identifier]).create()
    
    # data dict for user data during upgrade/downgrade process 
    migrate_engine.data = {}
   
    def generate_random_identifier():
        n_id = random.randint(0, 100000000)
        id = "%08d" % n_id
        return id
    
    migrate_engine.generate_random_identifier = generate_random_identifier 

    
def downgrade(migrate_engine):
    metadata.bind = migrate_engine 
    ForeignKeyConstraint(columns=[p2_plan.c.fk_default_form]  , refcolumns=[p2_form.c.form_identifier]).drop()
    
    # Operations to reverse the above upgrade go here.
    p2_span_dropdown.drop(migrate_engine)
    p2_span_checkbox.drop(migrate_engine)
    p2_span_alphanumeric.drop(migrate_engine)
    p2_span_action.drop(migrate_engine)
    p2_span_fileupload.drop(migrate_engine)
    p2_span_embeddedform.drop(migrate_engine)
    p2_linkage.drop(migrate_engine)
    p2_relation.drop(migrate_engine) 
    #p2_embform_characteristic.drop(migrate_engine)
    p2_span.drop(migrate_engine)
    p2_archetype.drop(migrate_engine)
    p2_widget.drop(migrate_engine)
    p2_form.drop(migrate_engine)
    p2_plan.drop(migrate_engine)
    p2_fieldtype.drop(migrate_engine)
    p2_cardinality.drop()
    p2_country.drop()
    p2_formlayout.drop()
    #p2_widget_type.drop()
