from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/mpls.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_namespace = resolve('namespace')
    l_0_ethernet_interfaces = resolve('ethernet_interfaces')
    l_0_loopback_interfaces = resolve('loopback_interfaces')
    l_0_port_channel_interfaces = resolve('port_channel_interfaces')
    l_0_mpls = resolve('mpls')
    l_0_mpls_configured = missing
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    l_0_mpls_configured = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), ethernet_interfaces=False, loopback_interfaces=False, port_channel_interfaces=False)
    context.vars['mpls_configured'] = l_0_mpls_configured
    context.exported_vars.add('mpls_configured')
    for l_1_ethernet_interface in t_1((undefined(name='ethernet_interfaces') if l_0_ethernet_interfaces is missing else l_0_ethernet_interfaces), 'name'):
        _loop_vars = {}
        pass
        if t_2(environment.getattr(l_1_ethernet_interface, 'mpls')):
            pass
            if not isinstance(l_0_mpls_configured, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_mpls_configured['ethernet_interfaces'] = True
    l_1_ethernet_interface = missing
    for l_1_loopback_interface in t_1((undefined(name='loopback_interfaces') if l_0_loopback_interfaces is missing else l_0_loopback_interfaces), 'name'):
        _loop_vars = {}
        pass
        if t_2(environment.getattr(l_1_loopback_interface, 'mpls')):
            pass
            if not isinstance(l_0_mpls_configured, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_mpls_configured['loopback_interfaces'] = True
    l_1_loopback_interface = missing
    for l_1_port_channel_interface in t_1((undefined(name='port_channel_interfaces') if l_0_port_channel_interfaces is missing else l_0_port_channel_interfaces), 'name'):
        _loop_vars = {}
        pass
        if t_2(environment.getattr(l_1_port_channel_interface, 'mpls')):
            pass
            if not isinstance(l_0_mpls_configured, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_mpls_configured['port_channel_interfaces'] = True
    l_1_port_channel_interface = missing
    if ((((t_2((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls)) or environment.getattr((undefined(name='mpls_configured') if l_0_mpls_configured is missing else l_0_mpls_configured), 'ethernet_interfaces')) or environment.getattr((undefined(name='mpls_configured') if l_0_mpls_configured is missing else l_0_mpls_configured), 'loopback_interfaces')) or environment.getattr((undefined(name='mpls_configured') if l_0_mpls_configured is missing else l_0_mpls_configured), 'port_channel_interfaces')) or t_2(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'))):
        pass
        yield '\n## MPLS\n'
        template = environment.get_template('documentation/mpls-and-ldp.j2', 'documentation/mpls.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'mpls_configured': l_0_mpls_configured}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        template = environment.get_template('documentation/mpls-interfaces.j2', 'documentation/mpls.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'mpls_configured': l_0_mpls_configured}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        template = environment.get_template('documentation/mpls-rsvp.j2', 'documentation/mpls.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'mpls_configured': l_0_mpls_configured}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
    if (t_2((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls)) or t_2(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'))):
        pass
        yield '\n### MPLS Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/mpls.j2', 'documentation/mpls.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'mpls_configured': l_0_mpls_configured}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=29&8=32&9=35&10=39&13=41&14=44&15=48&18=50&19=53&20=57&23=59&27=62&29=68&31=74&33=80&38=83'