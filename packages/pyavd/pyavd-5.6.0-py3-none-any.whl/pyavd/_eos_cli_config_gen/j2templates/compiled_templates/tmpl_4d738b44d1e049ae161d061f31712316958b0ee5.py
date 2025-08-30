from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/mac-address-table.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_mac_address_table = resolve('mac_address_table')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_3 = environment.filters['sort']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'sort' found.")
    try:
        t_4 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_4((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table)):
        pass
        yield '\n## MAC Address Table\n\n### MAC Address Table Summary\n'
        if t_4(environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'aging_time')):
            pass
            yield '\n- MAC address table entry maximum age: '
            yield str(environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'aging_time'))
            yield ' seconds\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'notification_host_flap'), 'logging'), False):
            pass
            yield '\n- Logging MAC address interface flapping is Disabled\n'
        elif t_4(environment.getattr(environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'notification_host_flap'), 'logging'), True):
            pass
            yield '\n- Logging MAC address interface flapping is Enabled\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'notification_host_flap'), 'detection'), 'moves')):
            pass
            yield '\n- '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'notification_host_flap'), 'detection'), 'moves'))
            yield ' MAC moves are considered as one flap\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'notification_host_flap'), 'detection'), 'window')):
            pass
            yield '\n- Size of the flap detection time window: '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'notification_host_flap'), 'detection'), 'window'))
            yield ' seconds\n'
        if t_4(environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'static_entries')):
            pass
            yield '\n### Static MAC Address Entries\n\n| MAC Address | VLAN | DROP Traffic | Interface | Eligibility Forwarding |\n|-------------|------|--------------|-----------|------------------------|\n'
            for l_1_static_entry in t_2(t_3(environment, environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'static_entries'), attribute='mac_address'), 'vlan'):
                _loop_vars = {}
                pass
                yield '| '
                yield str(environment.getattr(l_1_static_entry, 'mac_address'))
                yield ' | '
                yield str(environment.getattr(l_1_static_entry, 'vlan'))
                yield ' | '
                yield str(t_1(environment.getattr(l_1_static_entry, 'drop'), '-'))
                yield ' | '
                yield str(t_1(environment.getattr(l_1_static_entry, 'interface'), '-'))
                yield ' | '
                yield str(t_1(environment.getattr(l_1_static_entry, 'eligibility_forwarding'), '-'))
                yield ' |\n'
            l_1_static_entry = missing
        yield '\n### MAC Address Table Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/mac-address-table-aging-time.j2', 'documentation/mac-address-table.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        template = environment.get_template('eos/mac-address-table-static-entries.j2', 'documentation/mac-address-table.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        template = environment.get_template('eos/mac-address-table-notification.j2', 'documentation/mac-address-table.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=36&12=39&14=42&16=44&19=47&23=50&25=53&27=55&29=58&31=60&37=63&38=67&45=79&46=85&47=91'