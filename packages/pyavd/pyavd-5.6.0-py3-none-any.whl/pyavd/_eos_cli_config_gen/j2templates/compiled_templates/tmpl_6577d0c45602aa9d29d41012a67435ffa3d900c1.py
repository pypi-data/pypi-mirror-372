from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/router-general.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_router_general = resolve('router_general')
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
    if t_5((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general)):
        pass
        yield '\n### Router General\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'router_id'), 'ipv4')):
            pass
            yield '\n- Global IPv4 Router ID: '
            yield str(environment.getattr(environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'router_id'), 'ipv4'))
            yield '\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'router_id'), 'ipv6')):
            pass
            yield '\n- Global IPv6 Router ID: '
            yield str(environment.getattr(environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'router_id'), 'ipv6'))
            yield '\n'
        if t_5(environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'nexthop_fast_failover'), True):
            pass
            yield '\n- Nexthop fast fail-over is enabled.\n'
        if t_5(environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'software_forwarding_hardware_offload_mtu')):
            pass
            yield '\n- Software Forwarding Hardware Offload MTU: '
            yield str(environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'software_forwarding_hardware_offload_mtu'))
            yield '\n'
        if t_3(context.eval_ctx, t_4(context, t_1(environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'vrfs'), []), 'software_forwarding_hardware_offload_mtu', 'arista.avd.defined')):
            pass
            yield '\n#### VRF Software Forwarding Hardware Offload MTU\n\n| VRF | MTU |\n|-----|-----|\n'
            for l_1_vrf in t_4(context, environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'vrfs'), 'software_forwarding_hardware_offload_mtu', 'arista.avd.defined'):
                _loop_vars = {}
                pass
                yield '| '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield ' | '
                yield str(environment.getattr(l_1_vrf, 'software_forwarding_hardware_offload_mtu'))
                yield ' |\n'
            l_1_vrf = missing
        if t_3(context.eval_ctx, t_4(context, t_1(environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'vrfs'), []), 'leak_routes', 'arista.avd.defined')):
            pass
            yield '\n#### VRF Route leaking\n\n| VRF | Source VRF | Route Map Policy | RCF Policy |\n|-----|------------|------------------| ---------- |\n'
            for l_1_vrf in environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'vrfs'):
                _loop_vars = {}
                pass
                for l_2_leak_route in t_2(environment.getattr(l_1_vrf, 'leak_routes')):
                    _loop_vars = {}
                    pass
                    if (t_5(environment.getattr(l_2_leak_route, 'source_vrf')) and (t_5(environment.getattr(l_2_leak_route, 'subscribe_policy')) or t_5(environment.getattr(l_2_leak_route, 'subscribe_rcf')))):
                        pass
                        yield '| '
                        yield str(environment.getattr(l_1_vrf, 'name'))
                        yield ' | '
                        yield str(environment.getattr(l_2_leak_route, 'source_vrf'))
                        yield ' | '
                        yield str(t_1(environment.getattr(l_2_leak_route, 'subscribe_policy'), '-'))
                        yield ' | '
                        yield str(t_1(environment.getattr(l_2_leak_route, 'subscribe_rcf'), '-'))
                        yield ' |\n'
                l_2_leak_route = missing
            l_1_vrf = missing
        if t_3(context.eval_ctx, t_4(context, t_1(environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'vrfs'), []), 'routes.dynamic_prefix_lists', 'arista.avd.defined')):
            pass
            yield '\n#### VRF Routes Dynamic Prefix-lists\n\n| VRF | Dynamic Prefix-list |\n|-----|---------------------|\n'
            for l_1_vrf in environment.getattr((undefined(name='router_general') if l_0_router_general is missing else l_0_router_general), 'vrfs'):
                _loop_vars = {}
                pass
                for l_2_dynamic_prefix_list in t_2(environment.getattr(environment.getattr(l_1_vrf, 'routes'), 'dynamic_prefix_lists'), 'name'):
                    _loop_vars = {}
                    pass
                    if t_5(environment.getattr(l_2_dynamic_prefix_list, 'name')):
                        pass
                        yield '| '
                        yield str(environment.getattr(l_1_vrf, 'name'))
                        yield ' | '
                        yield str(environment.getattr(l_2_dynamic_prefix_list, 'name'))
                        yield ' |\n'
                l_2_dynamic_prefix_list = missing
            l_1_vrf = missing
        yield '\n#### Router General Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/router-general.j2', 'documentation/router-general.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=42&10=45&12=48&14=50&16=53&18=55&22=58&24=61&26=63&32=66&33=70&36=75&42=78&43=81&44=84&45=87&50=97&56=100&57=103&58=106&59=109&68=116'