from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/management-interfaces.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_management_interfaces = resolve('management_interfaces')
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
        t_3 = environment.filters['list']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'list' found.")
    try:
        t_4 = environment.filters['selectattr']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'selectattr' found.")
    try:
        t_5 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_5((undefined(name='management_interfaces') if l_0_management_interfaces is missing else l_0_management_interfaces)):
        pass
        yield '\n### Management Interfaces\n\n#### Management Interfaces Summary\n\n##### IPv4\n\n| Management Interface | Description | Type | VRF | IP Address | Gateway |\n| -------------------- | ----------- | ---- | --- | ---------- | ------- |\n'
        for l_1_management_interface in t_2((undefined(name='management_interfaces') if l_0_management_interfaces is missing else l_0_management_interfaces), 'name'):
            l_1_vrf = l_1_description = l_1_ip = l_1_ip_gateway = l_1_int_type = missing
            _loop_vars = {}
            pass
            l_1_vrf = t_1(environment.getattr(l_1_management_interface, 'vrf'), 'default')
            _loop_vars['vrf'] = l_1_vrf
            l_1_description = t_1(environment.getattr(l_1_management_interface, 'description'), '-')
            _loop_vars['description'] = l_1_description
            l_1_ip = t_1(environment.getattr(l_1_management_interface, 'ip_address'), '-')
            _loop_vars['ip'] = l_1_ip
            l_1_ip_gateway = t_1(environment.getattr(l_1_management_interface, 'gateway'), '-')
            _loop_vars['ip_gateway'] = l_1_ip_gateway
            l_1_int_type = t_1(environment.getattr(l_1_management_interface, 'type'), 'oob')
            _loop_vars['int_type'] = l_1_int_type
            yield '| '
            yield str(environment.getattr(l_1_management_interface, 'name'))
            yield ' | '
            yield str((undefined(name='description') if l_1_description is missing else l_1_description))
            yield ' | '
            yield str((undefined(name='int_type') if l_1_int_type is missing else l_1_int_type))
            yield ' | '
            yield str((undefined(name='vrf') if l_1_vrf is missing else l_1_vrf))
            yield ' | '
            yield str((undefined(name='ip') if l_1_ip is missing else l_1_ip))
            yield ' | '
            yield str((undefined(name='ip_gateway') if l_1_ip_gateway is missing else l_1_ip_gateway))
            yield ' |\n'
        l_1_management_interface = l_1_vrf = l_1_description = l_1_ip = l_1_ip_gateway = l_1_int_type = missing
        yield '\n##### IPv6\n\n| Management Interface | Description | Type | VRF | IPv6 Address | IPv6 Gateway |\n| -------------------- | ----------- | ---- | --- | ------------ | ------------ |\n'
        for l_1_management_interface in t_2((undefined(name='management_interfaces') if l_0_management_interfaces is missing else l_0_management_interfaces), 'name'):
            l_1_description = l_1_vrf = l_1_ipv6 = l_1_ipv6_gateway = l_1_int_type = missing
            _loop_vars = {}
            pass
            l_1_description = t_1(environment.getattr(l_1_management_interface, 'description'), '-')
            _loop_vars['description'] = l_1_description
            l_1_vrf = t_1(environment.getattr(l_1_management_interface, 'vrf'), 'default')
            _loop_vars['vrf'] = l_1_vrf
            l_1_ipv6 = t_1(environment.getattr(l_1_management_interface, 'ipv6_address'), '-')
            _loop_vars['ipv6'] = l_1_ipv6
            l_1_ipv6_gateway = t_1(environment.getattr(l_1_management_interface, 'ipv6_gateway'), '-')
            _loop_vars['ipv6_gateway'] = l_1_ipv6_gateway
            l_1_int_type = t_1(environment.getattr(l_1_management_interface, 'type'), 'oob')
            _loop_vars['int_type'] = l_1_int_type
            yield '| '
            yield str(environment.getattr(l_1_management_interface, 'name'))
            yield ' | '
            yield str((undefined(name='description') if l_1_description is missing else l_1_description))
            yield ' | '
            yield str((undefined(name='int_type') if l_1_int_type is missing else l_1_int_type))
            yield ' | '
            yield str((undefined(name='vrf') if l_1_vrf is missing else l_1_vrf))
            yield ' | '
            yield str((undefined(name='ipv6') if l_1_ipv6 is missing else l_1_ipv6))
            yield ' | '
            yield str((undefined(name='ipv6_gateway') if l_1_ipv6_gateway is missing else l_1_ipv6_gateway))
            yield ' |\n'
        l_1_management_interface = l_1_description = l_1_vrf = l_1_ipv6 = l_1_ipv6_gateway = l_1_int_type = missing
        if t_3(context.eval_ctx, t_4(context, t_1((undefined(name='management_interfaces') if l_0_management_interfaces is missing else l_0_management_interfaces), []), 'redundancy', 'arista.avd.defined')):
            pass
            yield '\n##### Interface Redundancy\n'
            for l_1_mgmt_intf in t_2(t_4(context, (undefined(name='management_interfaces') if l_0_management_interfaces is missing else l_0_management_interfaces), 'redundancy', 'arista.avd.defined'), 'name'):
                _loop_vars = {}
                pass
                yield '\n###### '
                yield str(environment.getattr(l_1_mgmt_intf, 'name'))
                yield '\n\n| Settings | Value |\n| -------- | ----- |\n'
                if t_5(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'fallback_delay')):
                    pass
                    yield '| Fallback Delay | '
                    yield str(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'fallback_delay'))
                    yield ' |\n'
                if t_5(environment.getattr(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'monitor'), 'link_state')):
                    pass
                    yield '| Monitor Link State | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'monitor'), 'link_state'))
                    yield ' |\n'
                elif t_5(environment.getattr(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'monitor'), 'neighbor')):
                    pass
                    yield '| Monitor Neighbor IPv6 Address | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'monitor'), 'neighbor'), 'ipv6_address'))
                    yield ' |\n| Monitor Neighbor Interval | '
                    yield str(t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'monitor'), 'neighbor'), 'interval'), '-'))
                    yield ' |\n| Monitor Neighbor Multiplier | '
                    yield str(t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'monitor'), 'neighbor'), 'multiplier'), '-'))
                    yield ' |\n'
                if t_5(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'supervisor_1')):
                    pass
                    yield '| Supervisor 1 Primary Interface | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'supervisor_1'), 'primary_management_interface'))
                    yield ' |\n| Supervisor 1 Backup Interfaces | '
                    yield str(context.call(environment.getattr(', ', 'join'), environment.getattr(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'supervisor_1'), 'backup_management_interfaces'), _loop_vars=_loop_vars))
                    yield ' |\n'
                if t_5(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'supervisor_2')):
                    pass
                    yield '| Supervisor 2 Primary Interface | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'supervisor_2'), 'primary_management_interface'))
                    yield ' |\n| Supervisor 2 Backup Interfaces | '
                    yield str(context.call(environment.getattr(', ', 'join'), environment.getattr(environment.getattr(environment.getattr(l_1_mgmt_intf, 'redundancy'), 'supervisor_2'), 'backup_management_interfaces'), _loop_vars=_loop_vars))
                    yield ' |\n'
            l_1_mgmt_intf = missing
        yield '\n#### Management Interfaces Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/management-interfaces.j2', 'documentation/management-interfaces.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=42&17=45&18=49&19=51&20=53&21=55&22=57&23=60&30=74&31=78&32=80&33=82&34=84&35=86&36=89&38=102&41=105&43=109&47=111&48=114&50=116&51=119&52=121&53=124&54=126&55=128&57=130&58=133&59=135&61=137&62=140&63=142&71=146'