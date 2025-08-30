from jinja2 import Template,Environment,FileSystemLoader
def none_to_empty(value):A=value;return''if A is None else A
def template_render_string(template_str,context):return Template(template_str).render(context)
def template_render_infolder(filename,context,template_dir):A=FileSystemLoader([template_dir]);B=Environment(loader=A,finalize=none_to_empty);return B.get_template(filename).render(context)