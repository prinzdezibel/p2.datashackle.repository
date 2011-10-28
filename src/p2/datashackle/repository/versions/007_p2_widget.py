# -*- coding: utf-8 -*-

from sqlalchemy.sql import select, and_

from p2.datashackle.repository.utils import styles_path
from p2.datashackle.repository.utils import write_cssrule, write_form_cssrule
from p2.datashackle.repository.utils import flush_cssrules

mod = __import__('001_initial_schema')
p2_fieldtype = getattr(mod, 'p2_fieldtype')
p2_widget = getattr(mod, 'p2_widget')
p2_plan = getattr(mod, 'p2_plan')
p2_form = getattr(mod, 'p2_form')
p2_linkage = getattr(mod, 'p2_linkage')
p2_span = getattr(mod, 'p2_span')
p2_span_alphanumeric = getattr(mod, 'p2_span_alphanumeric')
p2_span_checkbox = getattr(mod, 'p2_span_checkbox')
p2_span_embeddedform = getattr(mod, 'p2_span_embeddedform')
p2_span_action = getattr(mod, 'p2_span_action')
p2_span_dropdown = getattr(mod, 'p2_span_dropdown')


def write_widget_cssrule(id, value):
    plan_id = select([p2_plan.c.plan_identifier], 
        and_(p2_plan.c.plan_identifier == p2_form.c.fk_p2_plan,
        p2_form.c.form_identifier == p2_widget.c.fk_p2_form,
        p2_widget.c.widget_identifier == id)).execute().scalar()
    selector = 'div[data-widget-identifier="' + id + '"]'
    write_cssrule(plan_id, selector, value)

def write_span_cssrule(id, value):
    plan_id = select([p2_plan.c.plan_identifier], 
        and_(p2_plan.c.plan_identifier == p2_form.c.fk_p2_plan,
        p2_form.c.form_identifier == p2_widget.c.fk_p2_form,
        p2_widget.c.widget_identifier == p2_span.c.fk_p2_widget,
        p2_span.c.span_identifier == id)).execute().scalar()
    selector = 'div[data-span-identifier="' + id + '"]'
    write_cssrule(plan_id, selector, value)

def create_labeltext_widget(data,
        form_id,
        xpos,
        ypos,
        labeltext,
        field_identifier,
        defaultvalue,
        tab_order,
        label_width=150,
        text_width=150,
        required=True
    ):
    # widget
    insStmt = p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                             widget_type="labeltext",
                             fk_p2_form=form_id,
                             tab_order=tab_order)
    last_inserted_widget_id = result.inserted_primary_key[0]
    css_style="position: absolute; top: " + str(ypos) + "px; left: " + str(xpos) + "px;"
    write_widget_cssrule(last_inserted_widget_id, css_style)

    # span 1
    insStmt = p2_span.insert()
    span_identifier = data.generate_random_identifier() 
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                             span_identifier=span_identifier,
                             span_name="label",
                             span_type="label",
                             span_value=labeltext,
                             )
    css_style="width: " + str(label_width) + "px;"
    write_span_cssrule(span_identifier, css_style)
    
    # span 2
    insStmt = p2_span.insert()
    span_identifier = data.generate_random_identifier()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                             span_identifier=span_identifier,
                             span_name="piggyback",
                             span_type="alphanumeric",
                             span_value=defaultvalue,
                             tab_order=tab_order,
                             )
    css_style="left:" + str(label_width) + "px; width:" + str(text_width) + "px;"
    write_span_cssrule(span_identifier, css_style)

    fk_field_type = select([p2_fieldtype.c.id], p2_fieldtype.c.field_type == 'textline').execute().scalar()

    result = p2_span_alphanumeric.insert().execute(
        span_identifier=span_identifier,
        field_identifier=field_identifier,
        attr_name=field_identifier,
        fk_field_type=fk_field_type,
        required=required,
        )
    return data # not really needed, but to stay consistent with the other functions


    
def insert_save_button(data, form_id, tab_order):
    insStmt = p2_widget.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(widget_identifier=identifier,
                          widget_type="action",
                          fk_p2_form=form_id,
                          tab_order=tab_order)
    last_inserted_widget_id = result.inserted_primary_key[0]
    css_style="position: absolute; top: 270px; left: 0px;"
    write_widget_cssrule(identifier, css_style)
    
    insStmt = p2_span.insert()
    span_identifier = data.generate_random_identifier()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                         span_identifier=span_identifier,
                         span_name="button",
                         span_type="action",
                         span_value="OK",
                         ) 
    css_style="width:60px"
    write_span_cssrule(span_identifier, css_style)

    p2_span_action.insert().execute(span_identifier=span_identifier,
                                         msg_reset=False,
                                         msg_close=True
                                         )

def insert_reset_button(data, form_id, tab_order):    
    # Insert Reset Action widget into form
    insStmt = p2_widget.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(widget_identifier=identifier,
                          widget_type="action",
                          fk_p2_form=form_id,
                          tab_order=tab_order)
    last_inserted_widget_id = result.inserted_primary_key[0]
    css_style="position: absolute; top: 270px; left: 105px"
    write_widget_cssrule(identifier, css_style)

    # Button span
    span_identifier = data.generate_random_identifier()
    result = p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                         span_identifier=span_identifier,
                         span_name="button",
                         span_type="action",
                         span_value="Reset",
                         )
    css_style="width:60px"
    write_span_cssrule(span_identifier, css_style)

    p2_span_action.insert().execute(span_identifier=span_identifier,
                                         msg_reset=True,
                                         msg_close=False
                                         )
 

def create_embeddedform_widget(data, form_id, xpos, ypos, labeltext, linkage_id, form_name,
                            plan_identifier, tab_order, filter_clause=None, label_visible=True):
    # widget
    insStmt = p2_widget.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(widget_identifier=identifier,
                             widget_type="embeddedform",
                             fk_p2_form=form_id,
                             tab_order=tab_order)
    css_style="position: absolute; top: " + str(ypos) + "px; left: " + str(xpos) + "px;"
    write_widget_cssrule(identifier, css_style)
    
    last_inserted_widget_id = result.inserted_primary_key[0]


    # span 1
    if label_visible:
        label_width = 150
    else:
        label_width = 0 # Don't use up space for label

    insStmt = p2_span.insert()
    span_identifier = data.generate_random_identifier()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                             span_identifier=span_identifier,
                             span_name="label",
                             span_type="label",
                             span_value=labeltext,
                             visible=label_visible
                             )
    css_style="width: " + str(label_width) + "px;"
    write_span_cssrule(span_identifier, css_style)
    
    # span 2
    span_identifier = data.generate_random_identifier()
    result = p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                             span_identifier=span_identifier,
                             span_name="piggyback",
                             span_type="embeddedform",
                             span_value=None,
                             visible=True
                            )
    
    css_style="left:" + str(label_width) + "px;"
    write_span_cssrule(span_identifier, css_style)
    
    p2_span_embeddedform.insert().execute(
                                    span_identifier=span_identifier,
                                    fk_p2_linkage=linkage_id,
                                    form_name=form_name,
                                    label_visible=True,
                                    plan_identifier=plan_identifier,
                                    filter_clause=filter_clause,
                                    editable=False
                                    )
    return data # not really needed, but to stay consistent with the other functions


def create_checkbox_widget(data, form_id, labeltext, x, y, field_identifier, default, tab_order):
    
    label_width = 150
    
    insStmt = p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                             widget_type="checkbox",
                             fk_p2_form=form_id,
                             tab_order=tab_order)
    last_inserted_widget_id = result.inserted_primary_key[0]
    css_style="position: absolute; top: " + str(y) + "px; left: " + str(x) + "px;"
    write_widget_cssrule(last_inserted_widget_id, css_style)


    span_identifier = data.generate_random_identifier()
    result = p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                           span_identifier=span_identifier,
                           span_name="label",
                           span_type="label",
                           span_value=labeltext,
                           )                           
    css_style="width: " + str(label_width) + "px;"
    write_span_cssrule(span_identifier, css_style)
    
    span_identifier = data.generate_random_identifier()
    result = p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                           span_identifier=span_identifier,
                           #field_identifier=field_identifier,
                           span_name="piggyback",
                           span_type="checkbox",
                           span_value=default,
                           )
    
    css_style="left:" + str(label_width) + "px;"
    write_span_cssrule(span_identifier, css_style)
    
    result = p2_span_checkbox.insert().execute(
        span_identifier=span_identifier,
        field_identifier=field_identifier,
        attr_name=field_identifier
        ) 

def create_dropdown_widget(
        migrate_engine,
        form_id,
        x,
        y,
        label,
        foreignkeycol,
        attr_name,
        target_plan,
        target_attr_name,
        required,
        tab_order
    ):
    (source_classname, source_module) = select([p2_plan.c.so_type, p2_plan.c.so_module],
            and_(p2_form.c.fk_p2_plan == p2_plan.c.plan_identifier, p2_form.c.form_identifier == form_id)
        ).execute().fetchone()
    (target_classname, target_module) = select([p2_plan.c.so_type, p2_plan.c.so_module],
        p2_plan.c.plan_identifier == target_plan).execute().fetchone()
    label_width = 150
    
    identifier = migrate_engine.generate_random_identifier()
    result = p2_widget.insert().execute(
        widget_identifier=identifier,
        widget_type="dropdown",
        fk_p2_form=form_id,
        tab_order=tab_order
    )
    
    css_style="position: absolute; top: " + str(y) + "px; left: " + str(x) + "px;"
    write_widget_cssrule(identifier, css_style)
    
    last_inserted_widget_id = result.inserted_primary_key[0]
    identifier = migrate_engine.generate_random_identifier()
    result = p2_span.insert().execute(
        fk_p2_widget=last_inserted_widget_id,
        span_identifier=identifier,
        span_name="label",
        span_type="label",
        span_value=label,
    )                           
    
    css_style="width: " + str(label_width) + "px;"
    write_span_cssrule(identifier, css_style)

    linkage_id = migrate_engine.generate_random_identifier()
    result = p2_linkage.insert().execute(
        id=linkage_id,
        attr_name=attr_name,
        ref_type='object',
        ref_key=None,
        foreignkeycol=foreignkeycol,
        source_module=source_module,
        source_classname=source_classname,
        target_module=target_module,
        target_classname=target_classname,
        back_populates = None,
        fk_cardinality=migrate_engine.data['cardinalities']['n:1'],
        cascade='save-update,merge',
        post_update=None,
    )

    span_identifier = migrate_engine.generate_random_identifier()
    p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                           span_identifier=span_identifier,
                           span_name="piggyback",
                           span_type="dropdown",
                           )
    css_style="left:" + str(label_width) + "px; width: 150px;"
    write_span_cssrule(span_identifier, css_style)
    
    result = p2_span_dropdown.insert().execute(
        span_identifier=span_identifier,
        fk_p2_linkage=linkage_id,
        plan_identifier=target_plan,
        attr_name=target_attr_name,
        required=required,
   ) 



def upgrade(migrate_engine):
    data = mod.upgradedataobj()
    data.p2_plan = getattr(mod, 'p2_plan')
    data.p2_form = getattr(mod, 'p2_form')
    data.p2_widget = getattr(mod, 'p2_widget')
    data.p2_span = getattr(mod, 'p2_span')
    data.p2_linkage = getattr(mod, 'p2_linkage')
    data.p2_span_embeddedform = getattr(mod, 'p2_span_embeddedform')
    data.p2_span_fileupload = getattr(mod, 'p2_span_fileupload')
    data.p2_span_action = getattr(mod, 'p2_span_action')
    data.p2_span_alphanumeric = getattr(mod, 'p2_span_alphanumeric')
    data.p2_span_checkbox = getattr(mod, 'p2_span_checkbox')
    data.p2_span_dropdown = getattr(mod, 'p2_span_dropdown')

    #
    # Labeltext
    #
    insStmt = data.p2_form.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(active=True,
                             form_identifier=identifier,
                             form_name="labeltext",
                             fk_p2_plan='p2_widget')
    write_form_cssrule(identifier, 'height:310px; width:310px')
    labeltext_form_id = result.inserted_primary_key[0]
    
    create_embeddedform_widget(data, labeltext_form_id, 0, 0,
                                        labeltext="Labeltext widget -> label properties",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_label",
                                        plan_identifier="p2_span",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="label"', # we are only in the label interested
                                        tab_order=0,
                                        )
    create_embeddedform_widget(data, labeltext_form_id, 0, 25,
                                        labeltext="Labeltext widget -> alphanumeric properties",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_alphanumeric",
                                        plan_identifier="p2_span_alphanumeric",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the alphanumeric span
                                        tab_order=1,
                                        )
    create_labeltext_widget(data, labeltext_form_id, 0, 125, labeltext="Tab order", field_identifier="tab_order", defaultvalue="0", tab_order=2)

    insert_save_button(data, labeltext_form_id, tab_order=3)
    insert_reset_button(data, labeltext_form_id, tab_order=4)
    

    # Properties label span            
    identifier = data.generate_random_identifier()
    result = data.p2_form.insert().execute(active=True,
                         form_identifier=identifier,
                         form_name="properties_label",
                         fk_p2_plan='p2_span')
    write_form_cssrule(identifier, 'height:20px; width:200px')

    properties_label_id = result.inserted_primary_key[0]
    
    create_checkbox_widget(data, properties_label_id, 'Label visible', 0, 0, 'visible', True, tab_order=0)
   

    # Properties alphanumeric span
    identifier = data.generate_random_identifier()
    result = data.p2_form.insert().execute(active=True,
        form_identifier=identifier,
        form_name="properties_alphanumeric",
        fk_p2_plan='p2_span_alphanumeric'
    )
    write_form_cssrule(identifier, 'height:100px; width:302px')
    properties_alphanumeric_id = result.inserted_primary_key[0]


    create_labeltext_widget(data, properties_alphanumeric_id, 0, 0, 'Table field', 'field_identifier', None, tab_order=0)
    create_labeltext_widget(data, properties_alphanumeric_id, 0, 20, 'Mapped attribute', 'attr_name', None, tab_order=1)
    #create_checkbox_widget(data, properties_alphanumeric_id, 'Multiline', 0, 40, 'multi_line', False, tab_order=2)
    create_checkbox_widget(data, properties_alphanumeric_id, 'Required', 0, 40, 'required', True, tab_order=3)

    create_dropdown_widget(
        migrate_engine,
        properties_alphanumeric_id,
        0,
        80,
        label='Field formatting',
        foreignkeycol='fk_field_type',
        attr_name='field_type',
        target_plan='p2_fieldtype',
        target_attr_name='field_type',
        required=True,
        tab_order=4
        )

   
    #
    # Labeltext archetype.
    #
    # Archetype widget
    insStmt = data.p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                          widget_type="labeltext",
                          fk_p2_form=migrate_engine.data['archetype_form_id'])
    last_inserted_widget_id = result.inserted_primary_key[0]
    
    label_width = 95
    # Archetype widget: span 1
    insStmt = data.p2_span.insert()
    span_identifier=data.generate_random_identifier()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                         span_identifier=span_identifier,
                         span_name="label",
                         span_type="label",
                         span_value="Text",
                         characteristic=None)
    css_style="width:" + str(label_width) + "px;"
    write_span_cssrule(span_identifier, css_style)

    fk_field_type = select([p2_fieldtype.c.id], p2_fieldtype.c.field_type == 'textline').execute().scalar()  
                     
    # Archetype widget: span 2
    span_identifier = data.generate_random_identifier()
    result = data.p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                        span_identifier=span_identifier,
                        span_name="piggyback",
                        span_type="alphanumeric",
                        span_value="",
                        characteristic="text")
    
    css_style="left:" + str(label_width) + "px; width:" + str(label_width) + "px;"
    write_span_cssrule(span_identifier, css_style)
    
    data.p2_span_alphanumeric.insert().execute(
        span_identifier=span_identifier,
        fk_field_type=fk_field_type,
        attr_name='dummy_labeltext_archetype',
        field_identifier='dummy_labeltext_archetype',
    )
   

    #
    # Fileupload
    #
    insStmt = data.p2_form.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(active=True,
                             form_identifier=identifier,
                             form_name="fileupload",
                             fk_p2_plan='p2_widget')
    write_form_cssrule(identifier, 'height:320px; width:400px')
    propertyform_id = result.inserted_primary_key[0]
    
    create_embeddedform_widget(data, propertyform_id, 0, 0,
                                        labeltext="Fileupload widget -> label properties",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_label",
                                        plan_identifier="p2_span",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="label"', # we are only interested in the label
                                        tab_order=0,
                                        )
    
    create_embeddedform_widget(data, propertyform_id, 0, 20,
                                        labeltext="Fileupload widget -> fileupload span properties",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_fileupload",
                                        plan_identifier="p2_span_fileupload",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"',
                                        tab_order=1,
                                        )
    create_labeltext_widget(data, propertyform_id, 0, 65, labeltext="Tab order", field_identifier="tab_order", defaultvalue="0", tab_order=2)
    
    # properties_linkage form:
    insStmt = data.p2_form.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(active=True,
                         form_identifier=identifier,
                         form_name="properties_linkage_fileupload",
                         fk_p2_plan='p2_linkage')
    write_form_cssrule(identifier, 'height:80px; width:345px')
    form_id = result.inserted_primary_key[0]
    
    # add widgets
    create_labeltext_widget(data, form_id, 0, 0,
        labeltext="Mapping attribute", field_identifier="attr_name", defaultvalue="", tab_order=0)
    create_labeltext_widget(data, form_id, 0, 20,
        labeltext="Foreign key name", field_identifier="foreignkeycol", defaultvalue="", tab_order=1)
    
    
    # properties_fileupload form
    identifier = data.generate_random_identifier()
    result = data.p2_form.insert().execute(
                             active=True,
                             form_identifier=identifier,
                             form_name="properties_fileupload",
                             fk_p2_plan='p2_span_fileupload',
                             )
    write_form_cssrule(identifier, 'height:125px; width:350px')
    form_id = result.inserted_primary_key[0]

    create_embeddedform_widget(data, form_id, 0, 0,
                             labeltext="Linkage properties (Embeddedform span -> Linkage)",
                             linkage_id=migrate_engine.data['span_fileupload2linkage'],
                             form_name="properties_linkage_fileupload",
                             plan_identifier="p2_linkage",
                             label_visible=False, # we don't want to display the label,
                             tab_order=0,
                             )
    
    insert_save_button(data, propertyform_id, tab_order=3)
    insert_reset_button(data, propertyform_id, tab_order=4)
    

    #                    
    # Fileupload widget for archetype form
    #
    insStmt = data.p2_widget.insert()
    result = insStmt.execute(widget_identifier='09087162',
                          widget_type="fileupload",
                          fk_p2_form=migrate_engine.data['archetype_form_id'])
    last_inserted_widget_id = result.inserted_primary_key[0]
    css_style="position: absolute; top: 60px; left: 0px;"
    write_widget_cssrule(last_inserted_widget_id, css_style)
    
    # Span 1 for Fileupload widget
    insStmt = data.p2_span.insert()
    span_identifier = data.generate_random_identifier()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                            span_identifier=span_identifier,
                            span_name="label",
                            span_type="label",
                            span_value="Fileupload",
                            characteristic=None)
    css_style="width: 60px;"
    write_span_cssrule(span_identifier, css_style)

    # Span 2 for Fileupload widget
    identifier = data.generate_random_identifier()
    insStmt = data.p2_span.insert()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                            span_identifier=identifier,
                            span_name="piggyback",
                            span_type="fileupload",
                            span_value=None,
                            characteristic=None)
    data.p2_span_fileupload.insert().execute(span_identifier=identifier)
    css_style="left: 95px; width:50px; height:50px;"
    write_span_cssrule(identifier, css_style)   
 
    #
    # Checkbox 
    #
    insStmt = data.p2_form.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(active=True,
                             form_identifier=identifier,
                             form_name="checkbox",
                             fk_p2_plan='p2_widget')
    write_form_cssrule(identifier, 'height:310px; width:310px')
    form_id = result.inserted_primary_key[0]
    

    create_embeddedform_widget(data, form_id, 0, 0,
                                        labeltext="Checkbox widget -> label properties",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_label",
                                        plan_identifier="p2_span",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="label"', # we are only in the label interested
                                        tab_order=0,
                                        )
    create_embeddedform_widget(data, form_id, 0, 25,
                                        labeltext="Checkbox widget -> checkbox properties",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_checkbox",
                                        plan_identifier="p2_span_checkbox",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the checkbox span
                                        tab_order=1,
                                        )
    create_labeltext_widget(data, form_id, 0, 65, 'Tab order', 'tab_order', None, tab_order=2)
    insert_save_button(data, form_id, tab_order=3)
    insert_reset_button(data, form_id, tab_order=4)
   

    # Properties checkbox span
    identifier = data.generate_random_identifier()
    result = data.p2_form.insert().execute(active=True,
                         form_identifier=identifier,
                         form_name="properties_checkbox",
                         fk_p2_plan='p2_span_checkbox')
    write_form_cssrule(identifier, 'height:40px;width:302px')
    form_id = result.inserted_primary_key[0]

    create_labeltext_widget(data, form_id, 0, 0, 'Table field', 'field_identifier', None, tab_order=0)
    create_labeltext_widget(data, form_id, 0, 20, 'Mapped attribute', 'attr_name', None, tab_order=1)

    # END LABELTEXT PROPERTIES #
    
    # Checkbox archetype.
    #
    # Archetype widget
    insStmt = data.p2_widget.insert()
    result = insStmt.execute(widget_identifier='09087262',
                          widget_type="checkbox",
                          fk_p2_form=migrate_engine.data['archetype_form_id'])
    last_inserted_widget_id = result.inserted_primary_key[0]
    css_style="position: absolute; top: 30px; left: 0px;"
    write_widget_cssrule(last_inserted_widget_id, css_style)
    
    label_width = 95
    # Archetype widget: span 1
    insStmt = data.p2_span.insert()
    span_identifier = data.generate_random_identifier()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                            span_identifier=span_identifier,
                            span_name="label",
                            span_type="label",
                            span_value="Checkbox",
                            characteristic=None)
    css_style="width:" + str(label_width) + "px;"
    write_span_cssrule(span_identifier, css_style)
                            
    # Archetype widget: span 2
    identifier = data.generate_random_identifier()
    result = data.p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                            span_identifier=identifier,
                            span_name="piggyback",
                            span_type="checkbox",
                            span_value=None,
                            characteristic=None)
    data.p2_span_checkbox.insert().execute(span_identifier=identifier)
    css_style="left:" + str(label_width) + "px;"
    write_span_cssrule(identifier, css_style)
    
        

    # --- Embeddedform ---

    #
    # Embeddedform widget
    #
    
    insStmt = data.p2_form.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(active=True,
                             form_identifier=identifier,
                             form_name="embeddedform",
                             fk_p2_plan='p2_widget')
    write_form_cssrule(identifier, 'height:300px; width:400px') 
    form_id = result.inserted_primary_key[0]
    
    create_embeddedform_widget(data, form_id, 0, 0,
                                        labeltext="target form wrapper",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="target_form",
                                        plan_identifier="p2_span_embeddedform",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the embeddedform span
                                        tab_order=0,
                                        )
    create_embeddedform_widget(data, form_id, 0, 40,
                                        labeltext="Linkage properties (Embeddedform widget -> Embeddedform span)",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_linkage",
                                        plan_identifier="p2_span_embeddedform",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the label
                                        tab_order=1,
                                        )
    create_embeddedform_widget(data, form_id, 0, 140,
        labeltext="Labeltext widget -> Embeddedform span properties",
        linkage_id=migrate_engine.data['widget_span_linkage'],
        form_name="properties_embeddedform",
        plan_identifier="p2_span_embeddedform",
        label_visible=False, # we don't want to display the label,
        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the embeddedform span
        tab_order=2,
        )
    create_embeddedform_widget(data, form_id, 0, 220,
                                        labeltext="Labeltext widget -> label properties",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_label",
                                        plan_identifier="p2_span",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="label"', # we are only interested in the label
                                        tab_order=3,
                                        )
    
    create_labeltext_widget(data, form_id, 0, 240, labeltext="Tab order", field_identifier="tab_order", defaultvalue="0", tab_order=3)
    insert_save_button(data, form_id, tab_order=4)
    insert_reset_button(data, form_id, tab_order=5)



    # BEG target form form
    identifier = data.generate_random_identifier()
    result = data.p2_form.insert().execute(
                             active=True,
                             form_identifier=identifier,
                             form_name="target_form",
                             fk_p2_plan='p2_span_embeddedform',
                             )
    write_form_cssrule(identifier, 'height:40px; width:350px') 
    form_id = result.inserted_primary_key[0]
     
    # "plan_identifier" widget
    create_labeltext_widget(data, form_id, 0, 0,
        labeltext="Plan used for display", field_identifier="plan_identifier", defaultvalue="", tab_order=0)
    
    # "form_name" widget
    create_labeltext_widget(data, form_id, 0, 20,
        labeltext="Used Form", field_identifier="form_name", defaultvalue="default_form", tab_order=1)
    
    # END target form form


    # properties_embeddedform form
    identifier = data.generate_random_identifier()
    result = data.p2_form.insert().execute(
                             active=True,
                             form_identifier=identifier,
                             form_name="properties_embeddedform",
                             fk_p2_plan='p2_span_embeddedform',
                             )
    write_form_cssrule(identifier, 'height:40px; width:350px')
    form_id = result.inserted_primary_key[0]
     
    # "filter clause"   
    create_labeltext_widget(data, form_id, 0, 0,
        labeltext="Optional filter",
        field_identifier="filter_clause",
        defaultvalue="",
        tab_order=0,
        required=False
    )
    
    create_checkbox_widget(data,
          form_id,
          labeltext="Editable",
          x=0,
          y=20,
          field_identifier="editable",
          default=True,
          tab_order=3,
          )


    # properties_linkage form (only wrapper form for p2_embeddedform_span)
    identifier = data.generate_random_identifier()
    result = data.p2_form.insert().execute(
                             active=True,
                             form_identifier=identifier,
                             form_name="properties_linkage",
                             fk_p2_plan='p2_span_embeddedform',
                             )
    write_form_cssrule(identifier, 'height:140px; width:350px')
    form_id = result.inserted_primary_key[0]
    
    create_embeddedform_widget(data, form_id, 0, 0,
          labeltext="Linkage properties (Embeddedform span -> Linkage)",
          linkage_id=migrate_engine.data['span_embeddedform2linkage'],
          form_name="properties_linkage",
          plan_identifier="p2_linkage",
          label_visible=False, # we don't want to display the label,
          tab_order=1,
          )

    # properties_linkage form
    insStmt = data.p2_form.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(active=True,
                         form_identifier=identifier,
                         form_name="properties_linkage",
                         fk_p2_plan='p2_linkage')
    write_form_cssrule(identifier, 'height:100px; width:345px')
    form_id = result.inserted_primary_key[0]
    
    create_dropdown_widget(
        migrate_engine,
        form_id,
        0,
        0,
        'Relation type',
        'fk_cardinality',
        'cardinality',
        'p2_cardinality',
        'cardinality',
        False,
        tab_order=0
    )

    create_labeltext_widget(data, form_id, 0, 20,
        labeltext="Mapping attribute", field_identifier="attr_name", defaultvalue="", tab_order=1)
    create_labeltext_widget(data, form_id, 0, 40,
        labeltext="xref table name", field_identifier="xref_table", defaultvalue="", tab_order=2, required=False)
    create_labeltext_widget(data, form_id, 0, 60,
        labeltext="Foreign key name", field_identifier="foreignkeycol", defaultvalue="", tab_order=3)
    create_labeltext_widget(data, form_id, 0, 80,
        labeltext="Second foreign key", field_identifier="foreignkeycol2", defaultvalue="", tab_order=4, required=False)
 
    #                    
    # Embeddedform archetype.
    #
    insStmt = data.p2_widget.insert()
    widget_identifier=data.generate_random_identifier()
    result = insStmt.execute(widget_identifier=widget_identifier,
                          widget_type="embeddedform",
                          fk_p2_form=migrate_engine.data['archetype_form_id'])
    css_style="position: absolute; top: 130px; left: 0px;"
    write_widget_cssrule(widget_identifier, css_style)

    last_inserted_widget_id = result.inserted_primary_key[0]
    
    
    label_width = 95
    # Archetype widget: span 1
    insStmt = data.p2_span.insert()
    span_identifier = data.generate_random_identifier()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                         span_identifier=span_identifier,
                         span_name="label",
                         span_type="label",
                         span_value="Embedded form",
                         characteristic=None)
    css_style="width:" + str(label_width) + "px;"
    write_span_cssrule(span_identifier, css_style)
                         
    # Archetype widget: span 2
    identifier = data.generate_random_identifier()
    result = data.p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                        span_identifier=identifier,
                        span_name="piggyback",
                        span_type="embeddedform",
                        span_value="",
                        characteristic=None)
    css_style="left:" + str(label_width) + "px; width: 50px; height:50px;"
    write_span_cssrule(identifier, css_style)
    
    id = data.generate_random_identifier()
    data.p2_linkage.insert().execute(
        id=id,
        attr_name="dummy_embeddedform_archetype"
    )
    data.p2_span_embeddedform.insert().execute(span_identifier=identifier,
        fk_p2_linkage=id, cardinality='1,1'
    )

    # 
    # Dropdown
    #
    result = data.p2_plan.insert().execute(plan_identifier='p2_span_dropdown',
                             so_module='p2.datashackle.management.span.dropdown',
                             so_type='Dropdown')
    dropdown_plan_id = result.inserted_primary_key[0]
    
    # p2_span_dropdown -> p2_linkage
    result = data.p2_linkage.insert().execute(id=data.generate_random_identifier(),
                             attr_name='linkage',
                             ref_type='object',
                             foreignkeycol='fk_p2_linkage',
                             source_module='p2.datashackle.management.span.dropdown',
                             source_classname='Dropdown',
                             target_classname='Linkage',
                             target_module='p2.datashackle.core.models.linkage',
                             fk_cardinality=migrate_engine.data['cardinalities']['n:1'],
                             shareable=False,
                             cascade='all'
                             )
    linkage_id = result.inserted_primary_key[0]
    
    #
    # Dropdown widget
    #
    identifier = data.generate_random_identifier() 
    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                             form_identifier=identifier,
                             form_name="dropdown",
                             fk_p2_plan='p2_widget')
    write_form_cssrule(identifier, 'height:300px; width:400px')
    form_id = result.inserted_primary_key[0]
    
    create_embeddedform_widget(data, form_id, 0, 0,
                                        labeltext="dropdown widget -> label properties",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_label",
                                        plan_identifier="p2_span",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="label"', # we are only interested in the label
                                        tab_order=0,
                                        )
    create_embeddedform_widget(data, form_id, 0, 20,
                                        labeltext="Linkage properties (dropdown widget -> dropdown span)",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_dropdown_linkage",
                                        plan_identifier="p2_span_dropdown",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the label
                                        tab_order=1,
                                        )
    create_embeddedform_widget(data, form_id, 0, 80,
                                        labeltext="dropdown widget -> dropdown span properties",
                                        linkage_id=migrate_engine.data['widget_span_linkage'],
                                        form_name="properties_dropdown",
                                        plan_identifier="p2_span_dropdown",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the embeddedform span
                                        tab_order=2,
                                        )
    create_labeltext_widget(data, form_id, 0,150,
        labeltext="Tab order",
        field_identifier="tab_order",
        defaultvalue="0",
        label_width=220,
        text_width = 80,
        tab_order=3,
    )
    insert_save_button(data, form_id, tab_order=4)
    insert_reset_button(data, form_id, tab_order=5)


    # Property forms for dropdown widget
    identifier = data.generate_random_identifier()
    result = data.p2_form.insert().execute(
                             active=True,
                             form_identifier=identifier,
                             form_name="properties_dropdown",
                             fk_p2_plan='p2_span_dropdown',
                             )
    write_form_cssrule(identifier, 'height:100px; width:400px')
    form_id = result.inserted_primary_key[0]
     
    ## "filter clause"   
    #data.helpers.create_labeltext_widget(data, form_id, 0, 0,
    #                                     labeltext="Optional filter", field_identifier="filter_clause", defaultvalue="")
    #
    create_labeltext_widget(data, form_id, 0,0,
        labeltext="Plan used for populating dropdown",
        field_identifier="plan_identifier",
        defaultvalue="",
        label_width=220,
        text_width= 80,
        tab_order=0,
    )
    create_labeltext_widget(data, form_id, 0,20,
        labeltext="Attribute used for populating dropdown",
        field_identifier="attr_name",
        defaultvalue="",
        label_width=220,
        text_width = 80,
        tab_order=1,
    )
    create_checkbox_widget(data, form_id, 'Required', 0, 40, 'required', True, tab_order=2)

    # properties_dropdown_linkage form for plan p2_span_dropdown (only wrapper form)
    identifier = data.generate_random_identifier()
    result = data.p2_form.insert().execute(
                             active=True,
                             form_identifier=identifier,
                             form_name="properties_dropdown_linkage",
                             fk_p2_plan='p2_span_dropdown',
                             )
    write_form_cssrule(identifier, 'height:45px; width:350px')
    form_id = result.inserted_primary_key[0]
    
    create_embeddedform_widget(data, form_id, 0, 0,
                                        labeltext="Linkage properties (dropdown span -> Linkage)",
                                        linkage_id=linkage_id,
                                        form_name="properties_dropdown_linkage",
                                        plan_identifier="p2_linkage",
                                        label_visible=False, # we don't want to display the label,
                                        tab_order=0,
                                        )

    
    # properties_dropdown_linkage form for plan p2_linkage
    insStmt = data.p2_form.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(active=True,
                         form_identifier=identifier,
                         form_name="properties_dropdown_linkage",
                         fk_p2_plan='p2_linkage')
    write_form_cssrule(identifier, 'height:40px; width:345px')
    form_id = result.inserted_primary_key[0]
    
    # add widgets
    create_labeltext_widget(data, form_id, 0, 0,
        labeltext="Foreign key name", field_identifier="foreignkeycol", defaultvalue="", tab_order=0)
    create_labeltext_widget(data, form_id, 0, 20,
        labeltext="Attribute name", field_identifier="attr_name", defaultvalue="", tab_order=1)

    #                    
    # Dropdown archetype.
    #
    insStmt = data.p2_widget.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(widget_identifier=identifier,
                          widget_type="dropdown",
                          fk_p2_form=migrate_engine.data['archetype_form_id'])
    last_inserted_widget_id = result.inserted_primary_key[0]
    css_style="position: absolute; top: 190px; left: 0px;"
    write_widget_cssrule(identifier, css_style)
    
    label_width = 95
    # Archetype span 1
    insStmt = data.p2_span.insert()
    identifier = data.generate_random_identifier()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                         span_identifier=identifier,
                         span_name="label",
                         span_type="label",
                         span_value="Dropdown",
                         characteristic=None)
    css_style="width:" + str(label_width) + "px;"
    write_span_cssrule(identifier, css_style)
                         
    # Archetype span 2
    identifier = data.generate_random_identifier()
    result = data.p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                        span_identifier=identifier,
                        span_name="piggyback",
                        span_type="dropdown",
                        span_value="",
                        characteristic=None)
    css_style="left:" + str(label_width) + "px; width: 95px;"
    write_span_cssrule(identifier, css_style)

    id = data.generate_random_identifier()
    data.p2_linkage.insert().execute(
        id=id,
        attr_name="dummy_dropdown_archetype"
        )
    data.p2_span_dropdown.insert().execute(span_identifier=identifier,
        fk_p2_linkage=id, cardinality='1,1'
    )


    # Form for p2_plan
    create_labeltext_widget(data, migrate_engine.data['p2_plan_form_id'], 0, 0, 'Setobject module', 'so_module', None, tab_order=0, text_width=250)
    create_labeltext_widget(data, migrate_engine.data['p2_plan_form_id'], 0, 20, 'Setobject class name', 'so_type', None, tab_order=1, text_width=250)
   


    # PropertyForm for p2_form
    identifier = data.generate_random_identifier()
    result = data.p2_form.insert().execute(
        active=True,
        form_identifier=identifier,
        form_name="form_properties",
        fk_p2_plan='p2_form',
    )
    write_form_cssrule(identifier, 'height:300px; width:400px')
    
    create_labeltext_widget(data, identifier, 0, 0,
        labeltext="Form name", field_identifier="form_name", defaultvalue="", tab_order=0)


    # write stylesheets out to disk
    flush_cssrules()
    
def downgrade(migrate_engine):
    pass

