# -*- coding: utf-8 -*-

import os
import sys
from optparse import OptionParser

import cssutils
from sqlalchemy.sql import select, and_

mod = __import__('001_initial_schema', fromlist=['.versions'])
p2_plan = getattr(mod, 'p2_plan')
p2_form = getattr(mod, 'p2_form')

parser = OptionParser()
parser.add_option("-m", "--management-styles",
    dest="management_styles",
    default=False,
    help="Use this option to specify directory of management css styles.")
options, args = parser.parse_args(sys.argv)
styles_path = options.management_styles

stylesheets = {}

def write_form_cssrule(form_id, style):
    style = ';'.join([style, 'position:relative'])
    plan_id = select([p2_plan.c.plan_identifier], 
        and_(p2_plan.c.plan_identifier == p2_form.c.fk_p2_plan,
        p2_form.c.form_identifier == form_id)).execute().scalar()
    selector = 'div[data-form-identifier="' + form_id + '"]'
    write_cssrule(plan_id, selector, style)
      
    # add strip-selector rule for forms
    style="left: 15px"
    selector = 'div[data-form-identifier="' + form_id + '"].selector-strip'
    write_cssrule(plan_id, selector, style)

def write_cssrule(plan_id, selector_text, value):
    stylesheet_name = str(plan_id) + '.css'
    if stylesheet_name in stylesheets:
        stylesheet = stylesheets[stylesheet_name]
    else:
        stylesheet_filepath = os.path.join(styles_path, stylesheet_name)
        stylesheet_exists = os.path.exists(stylesheet_filepath)
        if stylesheet_exists:
            stylesheet = cssutils.parseFile(stylesheet_filepath, encoding='utf-8')
        else:
            stylesheet = cssutils.css.CSSStyleSheet()
        stylesheets[stylesheet_name] = stylesheet

    declarations = value.split(';')
    for declaration in declarations:
        colon = declaration.find(':')
        if colon == -1:
            # nothing found
            continue
        css_name = declaration[:colon]
        css_value = declaration[colon + 1:]
        css_property = cssutils.css.Property(name=css_name, value=css_value)
        found = False
        # Check if selector already exists
        for css_rule in stylesheet.cssRules:
            if not isinstance(css_rule, cssutils.css.CSSStyleRule):
                continue
            for selector in css_rule.selectorList:
                if selector_text == selector.selectorText:
                    found = True
                    css_rule.style.setProperty(css_property)
        if not found:
            declaration = cssutils.css.CSSStyleDeclaration()
            declaration.setProperty(css_property)
            css_rule = cssutils.css.CSSStyleRule(
                selectorText=selector_text,
                style=declaration
            )
            stylesheet.add(css_rule)

def flush_cssrules():
    global stylesheets
    for (stylesheet_name, stylesheet) in stylesheets.items():
        stylesheet_filepath = os.path.join(styles_path, stylesheet_name)
        fh = open(stylesheet_filepath, 'w+')
        fh.write(stylesheet.cssText)
        fh.close()
    stylesheets = {}

