from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/mac-address-table-static-entries.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_namespace = resolve('namespace')
    l_0_mac_address_table = resolve('mac_address_table')
    l_0_ns = missing
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['sort']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'sort' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    l_0_ns = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), has_valid_entry=False)
    context.vars['ns'] = l_0_ns
    context.exported_vars.add('ns')
    for l_1_static_entry in t_1(environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'static_entries')):
        _loop_vars = {}
        pass
        if (t_3(environment.getattr(l_1_static_entry, 'drop'), True) or t_3(environment.getattr(l_1_static_entry, 'interface'))):
            pass
            if not isinstance(l_0_ns, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_ns['has_valid_entry'] = True
            break
    l_1_static_entry = missing
    if environment.getattr((undefined(name='ns') if l_0_ns is missing else l_0_ns), 'has_valid_entry'):
        pass
        yield '!\n'
        for l_1_static_entry in t_1(t_2(environment, environment.getattr((undefined(name='mac_address_table') if l_0_mac_address_table is missing else l_0_mac_address_table), 'static_entries'), attribute='mac_address'), 'vlan'):
            l_1_mac_entry_base = resolve('mac_entry_base')
            _loop_vars = {}
            pass
            if (t_3(environment.getattr(l_1_static_entry, 'drop'), True) or t_3(environment.getattr(l_1_static_entry, 'interface'))):
                pass
                l_1_mac_entry_base = str_join(('mac address-table static ', environment.getattr(l_1_static_entry, 'mac_address'), ' vlan ', environment.getattr(l_1_static_entry, 'vlan'), ' ', ))
                _loop_vars['mac_entry_base'] = l_1_mac_entry_base
                if t_3(environment.getattr(l_1_static_entry, 'drop'), True):
                    pass
                    l_1_mac_entry_base = str_join(((undefined(name='mac_entry_base') if l_1_mac_entry_base is missing else l_1_mac_entry_base), 'drop', ))
                    _loop_vars['mac_entry_base'] = l_1_mac_entry_base
                elif t_3(environment.getattr(l_1_static_entry, 'eligibility_forwarding'), True):
                    pass
                    l_1_mac_entry_base = str_join(((undefined(name='mac_entry_base') if l_1_mac_entry_base is missing else l_1_mac_entry_base), 'interface ', environment.getattr(l_1_static_entry, 'interface'), ' eligibility forwarding', ))
                    _loop_vars['mac_entry_base'] = l_1_mac_entry_base
                else:
                    pass
                    l_1_mac_entry_base = str_join(((undefined(name='mac_entry_base') if l_1_mac_entry_base is missing else l_1_mac_entry_base), 'interface ', environment.getattr(l_1_static_entry, 'interface'), ))
                    _loop_vars['mac_entry_base'] = l_1_mac_entry_base
                yield str((undefined(name='mac_entry_base') if l_1_mac_entry_base is missing else l_1_mac_entry_base))
                yield '\n'
        l_1_static_entry = l_1_mac_entry_base = missing

blocks = {}
debug_info = '7=32&8=35&9=38&10=42&11=43&14=45&17=48&18=52&19=54&20=56&21=58&22=60&23=62&25=66&27=68'