from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/radius-proxy.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_radius_proxy = resolve('radius_proxy')
    l_0_hide_passwords = resolve('hide_passwords')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.hide_passwords']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.hide_passwords' found.")
    try:
        t_3 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_4 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_5 = environment.filters['sort']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'sort' found.")
    try:
        t_6 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    try:
        t_7 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    if t_6((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy)):
        pass
        yield '!\nradius proxy\n'
        if t_6(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'dynamic_authorization'), True):
            pass
            yield '   dynamic-authorization\n'
        if t_6(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'client_key')):
            pass
            yield '   client key 7 '
            yield str(t_2(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'client_key'), (undefined(name='hide_passwords') if l_0_hide_passwords is missing else l_0_hide_passwords)))
            yield '\n'
        if t_6(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'client_session_idle_timeout')):
            pass
            yield '   client session idle-timeout '
            yield str(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'client_session_idle_timeout'))
            yield ' seconds\n'
        for l_1_client_group in t_3(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'client_groups'), 'name'):
            l_1_all_ipv4_clients = l_1_all_ipv6_clients = l_1_all_host_clients = missing
            _loop_vars = {}
            pass
            yield '   !\n   client group '
            yield str(environment.getattr(l_1_client_group, 'name'))
            yield '\n'
            l_1_all_ipv4_clients = []
            _loop_vars['all_ipv4_clients'] = l_1_all_ipv4_clients
            l_1_all_ipv6_clients = []
            _loop_vars['all_ipv6_clients'] = l_1_all_ipv6_clients
            l_1_all_host_clients = []
            _loop_vars['all_host_clients'] = l_1_all_host_clients
            for l_2_vrf in t_5(environment, t_1(environment.getattr(l_1_client_group, 'vrfs'), []), attribute='name'):
                _loop_vars = {}
                pass
                for l_3_ipv4 in t_1(environment.getattr(l_2_vrf, 'ipv4_clients'), []):
                    _loop_vars = {}
                    pass
                    context.call(environment.getattr((undefined(name='all_ipv4_clients') if l_1_all_ipv4_clients is missing else l_1_all_ipv4_clients), 'append'), {'vrf': environment.getattr(l_2_vrf, 'name'), 'address': environment.getattr(l_3_ipv4, 'address'), 'key': (environment.getattr(l_3_ipv4, 'key') if t_6(environment.getattr(l_3_ipv4, 'key')) else cond_expr_undefined("the inline if-expression on line 28 in 'eos/radius-proxy.j2' evaluated to false and no else section was defined."))}, _loop_vars=_loop_vars)
                l_3_ipv4 = missing
                for l_3_ipv6 in t_1(environment.getattr(l_2_vrf, 'ipv6_clients'), []):
                    _loop_vars = {}
                    pass
                    context.call(environment.getattr((undefined(name='all_ipv6_clients') if l_1_all_ipv6_clients is missing else l_1_all_ipv6_clients), 'append'), {'vrf': environment.getattr(l_2_vrf, 'name'), 'address': environment.getattr(l_3_ipv6, 'address'), 'key': (environment.getattr(l_3_ipv6, 'key') if t_6(environment.getattr(l_3_ipv6, 'key')) else cond_expr_undefined("the inline if-expression on line 32 in 'eos/radius-proxy.j2' evaluated to false and no else section was defined."))}, _loop_vars=_loop_vars)
                l_3_ipv6 = missing
                for l_3_host in t_1(environment.getattr(l_2_vrf, 'host_clients'), []):
                    _loop_vars = {}
                    pass
                    context.call(environment.getattr((undefined(name='all_host_clients') if l_1_all_host_clients is missing else l_1_all_host_clients), 'append'), {'vrf': environment.getattr(l_2_vrf, 'name'), 'name': environment.getattr(l_3_host, 'name'), 'key': (environment.getattr(l_3_host, 'key') if t_6(environment.getattr(l_3_host, 'key')) else cond_expr_undefined("the inline if-expression on line 36 in 'eos/radius-proxy.j2' evaluated to false and no else section was defined."))}, _loop_vars=_loop_vars)
                l_3_host = missing
            l_2_vrf = missing
            for l_2_client in t_5(environment, (undefined(name='all_ipv4_clients') if l_1_all_ipv4_clients is missing else l_1_all_ipv4_clients), attribute='address'):
                l_2_client_ipv4 = missing
                _loop_vars = {}
                pass
                l_2_client_ipv4 = str_join(('client ipv4 ', environment.getattr(l_2_client, 'address'), ' vrf ', environment.getattr(l_2_client, 'vrf'), ))
                _loop_vars['client_ipv4'] = l_2_client_ipv4
                if t_7(environment.getattr(l_2_client, 'key')):
                    pass
                    l_2_client_ipv4 = str_join(((undefined(name='client_ipv4') if l_2_client_ipv4 is missing else l_2_client_ipv4), ' key 7 ', t_2(environment.getattr(l_2_client, 'key'), (undefined(name='hide_passwords') if l_0_hide_passwords is missing else l_0_hide_passwords)), ))
                    _loop_vars['client_ipv4'] = l_2_client_ipv4
                yield '      '
                yield str((undefined(name='client_ipv4') if l_2_client_ipv4 is missing else l_2_client_ipv4))
                yield '\n'
            l_2_client = l_2_client_ipv4 = missing
            for l_2_client in t_5(environment, (undefined(name='all_ipv6_clients') if l_1_all_ipv6_clients is missing else l_1_all_ipv6_clients), attribute='address'):
                l_2_client_ipv6 = missing
                _loop_vars = {}
                pass
                l_2_client_ipv6 = str_join(('client ipv6 ', environment.getattr(l_2_client, 'address'), ' vrf ', environment.getattr(l_2_client, 'vrf'), ))
                _loop_vars['client_ipv6'] = l_2_client_ipv6
                if t_7(environment.getattr(l_2_client, 'key')):
                    pass
                    l_2_client_ipv6 = str_join(((undefined(name='client_ipv6') if l_2_client_ipv6 is missing else l_2_client_ipv6), ' key 7 ', t_2(environment.getattr(l_2_client, 'key'), (undefined(name='hide_passwords') if l_0_hide_passwords is missing else l_0_hide_passwords)), ))
                    _loop_vars['client_ipv6'] = l_2_client_ipv6
                yield '      '
                yield str((undefined(name='client_ipv6') if l_2_client_ipv6 is missing else l_2_client_ipv6))
                yield '\n'
            l_2_client = l_2_client_ipv6 = missing
            for l_2_client in t_5(environment, (undefined(name='all_host_clients') if l_1_all_host_clients is missing else l_1_all_host_clients), attribute='name'):
                l_2_client_host = missing
                _loop_vars = {}
                pass
                l_2_client_host = str_join(('client host ', environment.getattr(l_2_client, 'name'), ' vrf ', environment.getattr(l_2_client, 'vrf'), ))
                _loop_vars['client_host'] = l_2_client_host
                if t_7(environment.getattr(l_2_client, 'key')):
                    pass
                    l_2_client_host = str_join(((undefined(name='client_host') if l_2_client_host is missing else l_2_client_host), ' key 7 ', t_2(environment.getattr(l_2_client, 'key'), (undefined(name='hide_passwords') if l_0_hide_passwords is missing else l_0_hide_passwords)), ))
                    _loop_vars['client_host'] = l_2_client_host
                yield '      '
                yield str((undefined(name='client_host') if l_2_client_host is missing else l_2_client_host))
                yield '\n'
            l_2_client = l_2_client_host = missing
            if t_6(environment.getattr(l_1_client_group, 'server_groups')):
                pass
                yield '      server group '
                yield str(t_4(context.eval_ctx, environment.getattr(l_1_client_group, 'server_groups'), ' '))
                yield '\n'
        l_1_client_group = l_1_all_ipv4_clients = l_1_all_ipv6_clients = l_1_all_host_clients = missing

blocks = {}
debug_info = '7=55&10=58&13=61&14=64&16=66&17=69&19=71&21=76&22=78&23=80&24=82&25=84&26=87&27=90&30=92&31=95&34=97&35=100&39=103&40=107&41=109&42=111&44=114&46=117&47=121&48=123&49=125&51=128&53=131&54=135&55=137&56=139&58=142&60=145&61=148'