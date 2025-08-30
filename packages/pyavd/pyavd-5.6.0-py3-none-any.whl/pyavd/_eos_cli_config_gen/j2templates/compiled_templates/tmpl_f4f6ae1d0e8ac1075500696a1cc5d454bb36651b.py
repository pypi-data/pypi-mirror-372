from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/ipv6-router-ospf.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ipv6_router_ospf = resolve('ipv6_router_ospf')
    l_0_namespace = resolve('namespace')
    l_0_has = resolve('has')
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
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_3(environment.getattr((undefined(name='ipv6_router_ospf') if l_0_ipv6_router_ospf is missing else l_0_ipv6_router_ospf), 'process_ids')):
        pass
        yield '\n### IPv6 Router OSPF\n\n#### IPv6 Router OSPF Summary\n\n| Process ID | VRF | Router ID | Auto Cost Reference Bandwidth |\n| ---------- | --- | --------- | ----------------------------- |\n'
        for l_1_process_id in t_2(environment.getattr((undefined(name='ipv6_router_ospf') if l_0_ipv6_router_ospf is missing else l_0_ipv6_router_ospf), 'process_ids'), 'id'):
            l_1_router_id = l_1_auto_cost_reference_bandwidth = missing
            _loop_vars = {}
            pass
            l_1_router_id = t_1(environment.getattr(l_1_process_id, 'router_id'), '-')
            _loop_vars['router_id'] = l_1_router_id
            l_1_auto_cost_reference_bandwidth = t_1(environment.getattr(l_1_process_id, 'auto_cost_reference_bandwidth'), '-')
            _loop_vars['auto_cost_reference_bandwidth'] = l_1_auto_cost_reference_bandwidth
            yield '| '
            yield str(environment.getattr(l_1_process_id, 'id'))
            yield ' | '
            yield str(t_1(environment.getattr(l_1_process_id, 'vrf'), '-'))
            yield ' | '
            yield str((undefined(name='router_id') if l_1_router_id is missing else l_1_router_id))
            yield ' | '
            yield str((undefined(name='auto_cost_reference_bandwidth') if l_1_auto_cost_reference_bandwidth is missing else l_1_auto_cost_reference_bandwidth))
            yield ' |\n'
        l_1_process_id = l_1_router_id = l_1_auto_cost_reference_bandwidth = missing
        l_0_has = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace))
        context.vars['has'] = l_0_has
        context.exported_vars.add('has')
        if not isinstance(l_0_has, Namespace):
            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
        l_0_has['found'] = False
        for l_1_process_id in environment.getattr((undefined(name='ipv6_router_ospf') if l_0_ipv6_router_ospf is missing else l_0_ipv6_router_ospf), 'process_ids'):
            _loop_vars = {}
            pass
            if t_3(environment.getattr(l_1_process_id, 'redistribute')):
                pass
                if not isinstance(l_0_has, Namespace):
                    raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                l_0_has['found'] = True
                break
        l_1_process_id = missing
        if t_3(environment.getattr((undefined(name='has') if l_0_has is missing else l_0_has), 'found'), True):
            pass
            yield '\n#### IPv6 Router OSPF Router Redistribution\n\n| Process ID | VRF | Source Protocol | Include Leaked | Route Map |\n| ---------- | --- | --------------- | -------------- | --------- |\n'
            for l_1_process_id in t_2(environment.getattr((undefined(name='ipv6_router_ospf') if l_0_ipv6_router_ospf is missing else l_0_ipv6_router_ospf), 'process_ids'), 'id'):
                l_1_source_protocols = resolve('source_protocols')
                l_1_include_leaked = resolve('include_leaked')
                l_1_isis_level = resolve('isis_level')
                _loop_vars = {}
                pass
                if t_3(environment.getattr(l_1_process_id, 'redistribute')):
                    pass
                    l_1_source_protocols = []
                    _loop_vars['source_protocols'] = l_1_source_protocols
                    if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'connected'), 'enabled'), True):
                        pass
                        if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'connected'), 'include_leaked'), True):
                            pass
                            l_1_include_leaked = 'enabled'
                            _loop_vars['include_leaked'] = l_1_include_leaked
                        else:
                            pass
                            l_1_include_leaked = '-'
                            _loop_vars['include_leaked'] = l_1_include_leaked
                        context.call(environment.getattr((undefined(name='source_protocols') if l_1_source_protocols is missing else l_1_source_protocols), 'append'), ('connected', (undefined(name='include_leaked') if l_1_include_leaked is missing else l_1_include_leaked), t_1(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'connected'), 'route_map'), '-')), _loop_vars=_loop_vars)
                    if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'static'), 'enabled'), True):
                        pass
                        if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'static'), 'include_leaked'), True):
                            pass
                            l_1_include_leaked = 'enabled'
                            _loop_vars['include_leaked'] = l_1_include_leaked
                        else:
                            pass
                            l_1_include_leaked = '-'
                            _loop_vars['include_leaked'] = l_1_include_leaked
                        context.call(environment.getattr((undefined(name='source_protocols') if l_1_source_protocols is missing else l_1_source_protocols), 'append'), ('static', (undefined(name='include_leaked') if l_1_include_leaked is missing else l_1_include_leaked), t_1(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'static'), 'route_map'), '-')), _loop_vars=_loop_vars)
                    if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'bgp'), 'enabled'), True):
                        pass
                        if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'bgp'), 'include_leaked'), True):
                            pass
                            l_1_include_leaked = 'enabled'
                            _loop_vars['include_leaked'] = l_1_include_leaked
                        else:
                            pass
                            l_1_include_leaked = '-'
                            _loop_vars['include_leaked'] = l_1_include_leaked
                        context.call(environment.getattr((undefined(name='source_protocols') if l_1_source_protocols is missing else l_1_source_protocols), 'append'), ('bgp', (undefined(name='include_leaked') if l_1_include_leaked is missing else l_1_include_leaked), t_1(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'bgp'), 'route_map'), '-')), _loop_vars=_loop_vars)
                    if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'dhcp'), 'enabled'), True):
                        pass
                        context.call(environment.getattr((undefined(name='source_protocols') if l_1_source_protocols is missing else l_1_source_protocols), 'append'), ('dhcp', '-', t_1(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'dhcp'), 'route_map'), '-')), _loop_vars=_loop_vars)
                    if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'enabled'), True):
                        pass
                        if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'include_leaked'), True):
                            pass
                            l_1_include_leaked = 'enabled'
                            _loop_vars['include_leaked'] = l_1_include_leaked
                        else:
                            pass
                            l_1_include_leaked = '-'
                            _loop_vars['include_leaked'] = l_1_include_leaked
                        if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'isis_level')):
                            pass
                            l_1_isis_level = str_join(('isis ', environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'isis_level'), ))
                            _loop_vars['isis_level'] = l_1_isis_level
                        else:
                            pass
                            l_1_isis_level = 'isis'
                            _loop_vars['isis_level'] = l_1_isis_level
                        context.call(environment.getattr((undefined(name='source_protocols') if l_1_source_protocols is missing else l_1_source_protocols), 'append'), ((undefined(name='isis_level') if l_1_isis_level is missing else l_1_isis_level), (undefined(name='include_leaked') if l_1_include_leaked is missing else l_1_include_leaked), t_1(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'route_map'), '-')), _loop_vars=_loop_vars)
                    if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'enabled'), True):
                        pass
                        context.call(environment.getattr((undefined(name='source_protocols') if l_1_source_protocols is missing else l_1_source_protocols), 'append'), ('ospfv3', 'enabled', t_1(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'route_map'), '-')), _loop_vars=_loop_vars)
                    if t_3(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_external'), 'enabled'), True):
                        pass
                        context.call(environment.getattr((undefined(name='source_protocols') if l_1_source_protocols is missing else l_1_source_protocols), 'append'), ('ospfv3 match external', 'enabled', t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_external'), 'route_map'), '-')), _loop_vars=_loop_vars)
                    if t_3(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_internal'), 'enabled'), True):
                        pass
                        context.call(environment.getattr((undefined(name='source_protocols') if l_1_source_protocols is missing else l_1_source_protocols), 'append'), ('ospfv3 match internal', 'enabled', t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_internal'), 'route_map'), '-')), _loop_vars=_loop_vars)
                    if t_3(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                        pass
                        context.call(environment.getattr((undefined(name='source_protocols') if l_1_source_protocols is missing else l_1_source_protocols), 'append'), ('ospfv3 match nssa external', 'enabled', t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_nssa_external'), 'route_map'), '-')), _loop_vars=_loop_vars)
                    for l_2_source_protocol in (undefined(name='source_protocols') if l_1_source_protocols is missing else l_1_source_protocols):
                        _loop_vars = {}
                        pass
                        yield '| '
                        yield str(environment.getattr(l_1_process_id, 'id'))
                        yield ' | '
                        yield str(t_1(environment.getattr(l_1_process_id, 'vrf'), '-'))
                        yield ' |'
                        yield str(environment.getitem(l_2_source_protocol, 0))
                        yield ' | '
                        yield str(environment.getitem(l_2_source_protocol, 1))
                        yield ' | '
                        yield str(environment.getitem(l_2_source_protocol, 2))
                        yield ' |\n'
                    l_2_source_protocol = missing
            l_1_process_id = l_1_source_protocols = l_1_include_leaked = l_1_isis_level = missing
        yield '\n#### IPv6 Router OSPF Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/ipv6-router-ospf.j2', 'documentation/ipv6-router-ospf.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'has': l_0_has}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=32&15=35&16=39&17=41&18=44&21=53&22=58&23=59&24=62&25=66&26=67&29=69&35=72&36=78&37=80&38=82&39=84&40=86&42=90&44=92&46=93&47=95&48=97&50=101&52=103&54=104&55=106&56=108&58=112&60=114&62=115&63=117&65=118&66=120&67=122&69=126&71=128&72=130&74=134&76=136&78=137&79=139&81=140&82=142&84=143&85=145&87=146&88=148&90=149&91=153&100=166'