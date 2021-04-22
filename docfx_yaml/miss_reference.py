from docutils import nodes
from docutils.nodes import Element, Node

CLASS = 'class'
REFMETHOD = 'meth'
REFFUNCTION = 'func'

def missing_reference(app, env, node, contnode):
    reftarget = ''
    refdoc = ''
    reftype = ''
    module = ''
    if 'refdomain' in node.attributes and node.attributes['refdomain'] == 'py':
        reftarget = node['reftarget']
        reftype = node['reftype']
        if 'refdoc' in node:
            refdoc = node['refdoc']
        if 'py:module' in node:
            module = node['py:module']

        #Refactor reftarget to fullname if it is a short name
        if reftype in [CLASS, REFFUNCTION, REFMETHOD] and module and '.' not in reftarget:
            if reftype in [CLASS, REFFUNCTION]:
                fields = (module, reftarget)
            else:
                fields = (module, node['py:class'], reftarget)
            reftarget = '.'.join(field for field in fields if field is not None)

        return make_refnode(app.builder, refdoc, reftarget, '', contnode)

def make_refnode(builder: "Builder", fromdocname: str, todocname: str, targetid: str,
                 child: Node, title: str = None) -> nodes.reference:
    """Shortcut to create a reference node."""
    node = nodes.reference('', '', internal=True)
    if fromdocname == todocname and targetid:
        node['refid'] = targetid
    else:
        if targetid:
            node['refuri'] = (builder.get_relative_uri(fromdocname, todocname) +
                              '#' + targetid)
        else:
            node['refuri'] = builder.get_relative_uri(fromdocname, todocname)
    if title:
        node['reftitle'] = title
    node.append(child)
    return node