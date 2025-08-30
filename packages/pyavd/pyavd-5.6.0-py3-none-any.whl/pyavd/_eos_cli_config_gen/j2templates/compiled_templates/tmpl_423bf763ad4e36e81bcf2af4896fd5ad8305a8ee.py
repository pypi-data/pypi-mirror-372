from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/radius-proxy.j2'

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
        t_5 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_5((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy)):
        pass
        yield '\n### Radius Proxy\n\n| Settings | Value |\n| -------- | ----- |\n| Dynamic Authorization | '
        yield str(t_1(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'dynamic_authorization'), '-'))
        yield ' |\n| Client Type-7 Key | '
        yield str(t_1(t_2(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'client_key'), (undefined(name='hide_passwords') if l_0_hide_passwords is missing else l_0_hide_passwords)), '-'))
        yield ' |\n| Client Session Idle-timeout (seconds) | '
        yield str(t_1(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'client_session_idle_timeout'), '-'))
        yield ' |\n'
        if t_5(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'client_groups')):
            pass
            yield '\n#### Client Group Summary\n'
            for l_1_client_group in t_3(environment.getattr((undefined(name='radius_proxy') if l_0_radius_proxy is missing else l_0_radius_proxy), 'client_groups'), 'name'):
                _loop_vars = {}
                pass
                yield '\n##### Client Group: '
                yield str(environment.getattr(l_1_client_group, 'name'))
                yield '\n'
                if t_5(environment.getattr(l_1_client_group, 'server_groups')):
                    pass
                    yield '\nServer Groups: '
                    yield str(t_4(context.eval_ctx, environment.getattr(l_1_client_group, 'server_groups'), ', '))
                    yield '\n'
                for l_2_vrf in t_3(environment.getattr(l_1_client_group, 'vrfs'), 'name'):
                    _loop_vars = {}
                    pass
                    yield '\n###### VRF: '
                    yield str(environment.getattr(l_2_vrf, 'name'))
                    yield '\n'
                    if t_5(environment.getattr(l_2_vrf, 'ipv4_clients')):
                        pass
                        yield '\n####### IPv4 Clients\n\n| Address | Type-7 Key |\n| ------- | ---------- |\n'
                        for l_3_ipv4_client in environment.getattr(l_2_vrf, 'ipv4_clients'):
                            l_3_ipv4_client_key = resolve('ipv4_client_key')
                            _loop_vars = {}
                            pass
                            if t_5(environment.getattr(l_3_ipv4_client, 'key')):
                                pass
                                l_3_ipv4_client_key = t_2(environment.getattr(l_3_ipv4_client, 'key'), (undefined(name='hide_passwords') if l_0_hide_passwords is missing else l_0_hide_passwords))
                                _loop_vars['ipv4_client_key'] = l_3_ipv4_client_key
                            yield '| '
                            yield str(environment.getattr(l_3_ipv4_client, 'address'))
                            yield ' | '
                            yield str(t_1((undefined(name='ipv4_client_key') if l_3_ipv4_client_key is missing else l_3_ipv4_client_key), '-'))
                            yield ' |\n'
                        l_3_ipv4_client = l_3_ipv4_client_key = missing
                    if t_5(environment.getattr(l_2_vrf, 'ipv6_clients')):
                        pass
                        yield '\n####### IPv6 Clients\n\n| Address | Type-7 Key |\n| ------- | ---------- |\n'
                        for l_3_ipv6_client in environment.getattr(l_2_vrf, 'ipv6_clients'):
                            l_3_ipv6_client_key = resolve('ipv6_client_key')
                            _loop_vars = {}
                            pass
                            if t_5(environment.getattr(l_3_ipv6_client, 'key')):
                                pass
                                l_3_ipv6_client_key = t_2(environment.getattr(l_3_ipv6_client, 'key'), (undefined(name='hide_passwords') if l_0_hide_passwords is missing else l_0_hide_passwords))
                                _loop_vars['ipv6_client_key'] = l_3_ipv6_client_key
                            yield '| '
                            yield str(environment.getattr(l_3_ipv6_client, 'address'))
                            yield ' | '
                            yield str(t_1((undefined(name='ipv6_client_key') if l_3_ipv6_client_key is missing else l_3_ipv6_client_key), '-'))
                            yield ' |\n'
                        l_3_ipv6_client = l_3_ipv6_client_key = missing
                    if t_5(environment.getattr(l_2_vrf, 'host_clients')):
                        pass
                        yield '\n####### Host Clients\n\n| Name | Type-7 Key |\n| ---- | ---------- |\n'
                        for l_3_host_client in environment.getattr(l_2_vrf, 'host_clients'):
                            l_3_host_client_key = resolve('host_client_key')
                            _loop_vars = {}
                            pass
                            if t_5(environment.getattr(l_3_host_client, 'key')):
                                pass
                                l_3_host_client_key = t_2(environment.getattr(l_3_host_client, 'key'), (undefined(name='hide_passwords') if l_0_hide_passwords is missing else l_0_hide_passwords))
                                _loop_vars['host_client_key'] = l_3_host_client_key
                            yield '| '
                            yield str(environment.getattr(l_3_host_client, 'name'))
                            yield ' | '
                            yield str(t_1((undefined(name='host_client_key') if l_3_host_client_key is missing else l_3_host_client_key), '-'))
                            yield ' |\n'
                        l_3_host_client = l_3_host_client_key = missing
                l_2_vrf = missing
            l_1_client_group = missing
        yield '\n#### RADIUS Proxy Configuration\n\n```eos\n'
        template = environment.get_template('eos/radius-proxy.j2', 'documentation/radius-proxy.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=43&13=46&14=48&15=50&16=52&19=55&21=59&22=61&24=64&26=66&28=70&29=72&35=75&36=79&37=81&39=84&42=89&48=92&49=96&50=98&52=101&55=106&61=109&62=113&63=115&65=118&75=126'