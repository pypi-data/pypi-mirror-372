from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/traffic-policies.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_traffic_policies = resolve('traffic_policies')
    l_0_traffic_policy_interfaces = resolve('traffic_policy_interfaces')
    l_0_ethernet_interfaces = resolve('ethernet_interfaces')
    l_0_port_channel_interfaces = resolve('port_channel_interfaces')
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
        t_3 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_4 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_5 = environment.filters['lower']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'lower' found.")
    try:
        t_6 = environment.filters['map']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'map' found.")
    try:
        t_7 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_7((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies)):
        pass
        yield '\n### Traffic Policies information\n'
        if t_7(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets')):
            pass
            if t_7(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ipv4')):
                pass
                yield '\n#### IPv4 Field Sets\n\n| Field Set Name | IPv4 Prefixes | Excluded Prefixes |\n| -------------- | ------------- | ----------------- |\n'
                for l_1_field_set_ipv4 in t_2(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ipv4'), 'name'):
                    l_1_value = l_1_except_value = missing
                    _loop_vars = {}
                    pass
                    l_1_value = t_3(context.eval_ctx, t_2(t_1(environment.getattr(l_1_field_set_ipv4, 'prefixes'), ['-'])), '<br/>')
                    _loop_vars['value'] = l_1_value
                    l_1_except_value = t_3(context.eval_ctx, t_2(t_1(environment.getattr(l_1_field_set_ipv4, 'except'), ['-'])), '<br/>')
                    _loop_vars['except_value'] = l_1_except_value
                    yield '| '
                    yield str(environment.getattr(l_1_field_set_ipv4, 'name'))
                    yield ' | '
                    yield str((undefined(name='value') if l_1_value is missing else l_1_value))
                    yield ' | '
                    yield str((undefined(name='except_value') if l_1_except_value is missing else l_1_except_value))
                    yield ' |\n'
                l_1_field_set_ipv4 = l_1_value = l_1_except_value = missing
            if t_7(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ipv6')):
                pass
                yield '\n#### IPv6 Field Sets\n\n| Field Set Name | IPv6 Prefixes | Excluded Prefixes |\n| -------------- | ------------- | ----------------- |\n'
                for l_1_field_set_ipv6 in t_2(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ipv6'), 'name'):
                    l_1_value = l_1_except_value = missing
                    _loop_vars = {}
                    pass
                    l_1_value = t_3(context.eval_ctx, t_2(t_1(environment.getattr(l_1_field_set_ipv6, 'prefixes'), ['-'])), '<br/>')
                    _loop_vars['value'] = l_1_value
                    l_1_except_value = t_3(context.eval_ctx, t_2(t_1(environment.getattr(l_1_field_set_ipv6, 'except'), ['-'])), '<br/>')
                    _loop_vars['except_value'] = l_1_except_value
                    yield '| '
                    yield str(environment.getattr(l_1_field_set_ipv6, 'name'))
                    yield ' | '
                    yield str((undefined(name='value') if l_1_value is missing else l_1_value))
                    yield ' | '
                    yield str((undefined(name='except_value') if l_1_except_value is missing else l_1_except_value))
                    yield ' |\n'
                l_1_field_set_ipv6 = l_1_value = l_1_except_value = missing
            if t_7(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ports')):
                pass
                yield '\n#### L4 Port Field Sets\n\n| Field Set Name | L4 Ports |\n| -------------- | -------- |\n'
                for l_1_field_set_port in t_2(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ports'), 'name'):
                    _loop_vars = {}
                    pass
                    yield '| '
                    yield str(environment.getattr(l_1_field_set_port, 'name'))
                    yield ' | '
                    yield str(t_1(environment.getattr(l_1_field_set_port, 'port_range'), '-'))
                    yield ' |\n'
                l_1_field_set_port = missing
        if t_7(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'policies')):
            pass
            yield '\n#### Traffic Policies\n'
            for l_1_policy in t_2(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'policies'), 'name'):
                _loop_vars = {}
                pass
                yield '\n##### '
                yield str(environment.getattr(l_1_policy, 'name'))
                yield '\n'
                if t_7(environment.getattr(l_1_policy, 'counters')):
                    pass
                    yield '\nCounters: '
                    yield str(t_3(context.eval_ctx, environment.getattr(l_1_policy, 'counters'), ', '))
                    yield '\n'
                if t_7(environment.getattr(l_1_policy, 'matches')):
                    pass
                    yield '\n| Match set | Type | Sources | Destinations | Protocol | Source Port(s) | Source Field(s) | Destination port(s) | Destination Field(s) | Action |\n| --------- | ---- | ------- | ------------ | -------- | -------------- | --------------- | ------------------- | -------------------- | ------ |\n'
                    for l_2_match in t_2(environment.getattr(l_1_policy, 'matches'), 'name'):
                        l_2_namespace = resolve('namespace')
                        l_2_row_str_next_hop = resolve('row_str_next_hop')
                        l_2_ipv4_addresses = resolve('ipv4_addresses')
                        l_2_ipv6_addresses = resolve('ipv6_addresses')
                        l_2_row = missing
                        _loop_vars = {}
                        pass
                        l_2_row = context.call((undefined(name='namespace') if l_2_namespace is missing else l_2_namespace), _loop_vars=_loop_vars)
                        _loop_vars['row'] = l_2_row
                        if not isinstance(l_2_row, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_2_row['match_set'] = environment.getattr(l_2_match, 'name')
                        if not isinstance(l_2_row, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_2_row['type'] = t_5(environment.getattr(l_2_match, 'type'))
                        if not isinstance(l_2_row, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_2_row['src_net'] = ''
                        if t_7(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefix_lists')):
                            pass
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['src_net'] = t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefix_lists')), '<br/>')
                        elif t_7(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefixes')):
                            pass
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['src_net'] = t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefixes')), '<br/>')
                        else:
                            pass
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['src_net'] = 'any'
                        if not isinstance(l_2_row, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_2_row['dst_net'] = ''
                        if t_7(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefix_lists')):
                            pass
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['dst_net'] = t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefix_lists')), '<br/>')
                        elif t_7(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefixes')):
                            pass
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['dst_net'] = t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefixes')), '<br/>')
                        else:
                            pass
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['dst_net'] = 'any'
                        if not isinstance(l_2_row, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_2_row['protocols'] = ''
                        if not isinstance(l_2_row, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_2_row['src_port'] = []
                        if not isinstance(l_2_row, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_2_row['dst_port'] = []
                        if not isinstance(l_2_row, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_2_row['src_field'] = []
                        if not isinstance(l_2_row, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_2_row['dst_field'] = []
                        if t_7(environment.getattr(l_2_match, 'protocols')):
                            pass
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['protocols'] = t_3(context.eval_ctx, t_6(context, environment.getattr(l_2_match, 'protocols'), attribute='protocol'), '<br/>')
                            for l_3_protocol in environment.getattr(l_2_match, 'protocols'):
                                _loop_vars = {}
                                pass
                                if (t_5(environment.getattr(l_3_protocol, 'protocol')) in ['tcp', 'udp']):
                                    pass
                                    context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'src_port'), 'append'), t_1(environment.getattr(l_3_protocol, 'src_port'), 'any'), _loop_vars=_loop_vars)
                                    context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'src_field'), 'append'), t_1(environment.getattr(l_3_protocol, 'src_field'), '-'), _loop_vars=_loop_vars)
                                    context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'dst_port'), 'append'), t_1(environment.getattr(l_3_protocol, 'dst_port'), 'any'), _loop_vars=_loop_vars)
                                    context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'dst_field'), 'append'), t_1(environment.getattr(l_3_protocol, 'dst_field'), '-'), _loop_vars=_loop_vars)
                                else:
                                    pass
                                    context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'src_port'), 'append'), '-', _loop_vars=_loop_vars)
                                    context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'src_field'), 'append'), '-', _loop_vars=_loop_vars)
                                    context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'dst_port'), 'append'), '-', _loop_vars=_loop_vars)
                                    context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'dst_field'), 'append'), '-', _loop_vars=_loop_vars)
                            l_3_protocol = missing
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['src_port'] = t_3(context.eval_ctx, environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'src_port'), '<br/>')
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['dst_port'] = t_3(context.eval_ctx, environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'dst_port'), '<br/>')
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['src_field'] = t_3(context.eval_ctx, environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'src_field'), '<br/>')
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['dst_field'] = t_3(context.eval_ctx, environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'dst_field'), '<br/>')
                        else:
                            pass
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['protocols'] = '-'
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['src_port'] = '-'
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['src_field'] = '-'
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['dst_port'] = '-'
                            if not isinstance(l_2_row, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_2_row['dst_field'] = '-'
                        if not isinstance(l_2_row, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_2_row['actions'] = []
                        if t_7(environment.getattr(l_2_match, 'actions')):
                            pass
                            if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'drop'), True):
                                pass
                                context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), 'append'), 'action: DROP', _loop_vars=_loop_vars)
                            else:
                                pass
                                context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), 'append'), 'action: PASS', _loop_vars=_loop_vars)
                            if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'count')):
                                pass
                                context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), 'append'), str_join(('counter: ', environment.getattr(environment.getattr(l_2_match, 'actions'), 'count'), )), _loop_vars=_loop_vars)
                            if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'log'), True):
                                pass
                                context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), 'append'), 'logging', _loop_vars=_loop_vars)
                            if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'dscp')):
                                pass
                                context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), 'append'), str_join(('dscp marking: ', environment.getattr(environment.getattr(l_2_match, 'actions'), 'dscp'), )), _loop_vars=_loop_vars)
                            if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'traffic_class')):
                                pass
                                context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), 'append'), str_join(('traffic-class: ', environment.getattr(environment.getattr(l_2_match, 'actions'), 'traffic_class'), )), _loop_vars=_loop_vars)
                            if t_7(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'aggregation_groups')):
                                pass
                                context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), 'append'), str_join(('redirect aggregation groups: ', t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'aggregation_groups')), ' '), )), _loop_vars=_loop_vars)
                            if t_7(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'interface')):
                                pass
                                context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), 'append'), str_join(('redirect interface: ', environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'interface'), )), _loop_vars=_loop_vars)
                            if ((not (t_7(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'interface')) or t_7(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'aggregation_groups')))) and t_7(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'))):
                                pass
                                l_2_row_str_next_hop = ''
                                _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv4_addresses')):
                                    pass
                                    l_2_ipv4_addresses = t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv4_addresses')), ' ')
                                    _loop_vars['ipv4_addresses'] = l_2_ipv4_addresses
                                    if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                        pass
                                        l_2_row_str_next_hop = str_join(('redirect next-hop IPv4 address: ', (undefined(name='ipv4_addresses') if l_2_ipv4_addresses is missing else l_2_ipv4_addresses), ' vrf: ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                        _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                    else:
                                        pass
                                        l_2_row_str_next_hop = str_join(('redirect next-hop IPv4 address: ', (undefined(name='ipv4_addresses') if l_2_ipv4_addresses is missing else l_2_ipv4_addresses), ))
                                        _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv6_addresses')):
                                    pass
                                    l_2_ipv6_addresses = t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv6_addresses')), ' ')
                                    _loop_vars['ipv6_addresses'] = l_2_ipv6_addresses
                                    if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                        pass
                                        l_2_row_str_next_hop = str_join(('redirect next-hop IPv6 address: ', (undefined(name='ipv6_addresses') if l_2_ipv6_addresses is missing else l_2_ipv6_addresses), ' vrf: ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                        _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                    else:
                                        pass
                                        l_2_row_str_next_hop = str_join(('redirect next-hop IPv6 address: ', (undefined(name='ipv6_addresses') if l_2_ipv6_addresses is missing else l_2_ipv6_addresses), ))
                                        _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'groups')):
                                    pass
                                    l_2_row_str_next_hop = str_join(('redirect next-hop groups: ', t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'groups')), ' '), ))
                                    _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv4_addresses')):
                                    pass
                                    l_2_ipv4_addresses = t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv4_addresses')), ' ')
                                    _loop_vars['ipv4_addresses'] = l_2_ipv4_addresses
                                    if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                        pass
                                        l_2_row_str_next_hop = str_join(('redirect next-hop recursive IPv4 address: ', (undefined(name='ipv4_addresses') if l_2_ipv4_addresses is missing else l_2_ipv4_addresses), ' vrf: ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                        _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                    else:
                                        pass
                                        l_2_row_str_next_hop = str_join(('redirect next-hop recursive IPv4 address: ', (undefined(name='ipv4_addresses') if l_2_ipv4_addresses is missing else l_2_ipv4_addresses), ))
                                        _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv6_addresses')):
                                    pass
                                    l_2_ipv6_addresses = t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv6_addresses')), ' ')
                                    _loop_vars['ipv6_addresses'] = l_2_ipv6_addresses
                                    if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                        pass
                                        l_2_row_str_next_hop = str_join(('redirect next-hop recursive IPv6 address: ', (undefined(name='ipv6_addresses') if l_2_ipv6_addresses is missing else l_2_ipv6_addresses), ' vrf: ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                        _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                    else:
                                        pass
                                        l_2_row_str_next_hop = str_join(('redirect next-hop recursive IPv6 address: ', (undefined(name='ipv6_addresses') if l_2_ipv6_addresses is missing else l_2_ipv6_addresses), ))
                                        _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                if ((undefined(name='row_str_next_hop') if l_2_row_str_next_hop is missing else l_2_row_str_next_hop) and t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ttl'))):
                                    pass
                                    l_2_row_str_next_hop = str_join(((undefined(name='row_str_next_hop') if l_2_row_str_next_hop is missing else l_2_row_str_next_hop), ' ttl: ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ttl'), ))
                                    _loop_vars['row_str_next_hop'] = l_2_row_str_next_hop
                                if (undefined(name='row_str_next_hop') if l_2_row_str_next_hop is missing else l_2_row_str_next_hop):
                                    pass
                                    context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), 'append'), (undefined(name='row_str_next_hop') if l_2_row_str_next_hop is missing else l_2_row_str_next_hop), _loop_vars=_loop_vars)
                        else:
                            pass
                            context.call(environment.getattr(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), 'append'), 'default action: PASS', _loop_vars=_loop_vars)
                        yield '| '
                        yield str(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'match_set'))
                        yield ' | '
                        yield str(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'type'))
                        yield ' | '
                        yield str(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'src_net'))
                        yield ' | '
                        yield str(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'dst_net'))
                        yield ' | '
                        yield str(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'protocols'))
                        yield ' | '
                        yield str(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'src_port'))
                        yield ' | '
                        yield str(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'src_field'))
                        yield ' | '
                        yield str(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'dst_port'))
                        yield ' | '
                        yield str(environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'dst_field'))
                        yield ' | '
                        yield str(t_3(context.eval_ctx, environment.getattr((undefined(name='row') if l_2_row is missing else l_2_row), 'actions'), '<br/>'))
                        yield ' |\n'
                    l_2_match = l_2_namespace = l_2_row = l_2_row_str_next_hop = l_2_ipv4_addresses = l_2_ipv6_addresses = missing
            l_1_policy = missing
        l_0_traffic_policy_interfaces = []
        context.vars['traffic_policy_interfaces'] = l_0_traffic_policy_interfaces
        context.exported_vars.add('traffic_policy_interfaces')
        for l_1_ethernet_interface in t_2((undefined(name='ethernet_interfaces') if l_0_ethernet_interfaces is missing else l_0_ethernet_interfaces), 'name'):
            _loop_vars = {}
            pass
            if (t_7(environment.getattr(environment.getattr(l_1_ethernet_interface, 'traffic_policy'), 'input')) or t_7(environment.getattr(environment.getattr(l_1_ethernet_interface, 'traffic_policy'), 'output'))):
                pass
                context.call(environment.getattr((undefined(name='traffic_policy_interfaces') if l_0_traffic_policy_interfaces is missing else l_0_traffic_policy_interfaces), 'append'), l_1_ethernet_interface, _loop_vars=_loop_vars)
        l_1_ethernet_interface = missing
        for l_1_port_channel_interface in t_2((undefined(name='port_channel_interfaces') if l_0_port_channel_interfaces is missing else l_0_port_channel_interfaces), 'name'):
            _loop_vars = {}
            pass
            if (t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'traffic_policy'), 'input')) or t_7(environment.getattr(environment.getattr(l_1_port_channel_interface, 'traffic_policy'), 'output'))):
                pass
                context.call(environment.getattr((undefined(name='traffic_policy_interfaces') if l_0_traffic_policy_interfaces is missing else l_0_traffic_policy_interfaces), 'append'), l_1_port_channel_interface, _loop_vars=_loop_vars)
        l_1_port_channel_interface = missing
        if (t_4((undefined(name='traffic_policy_interfaces') if l_0_traffic_policy_interfaces is missing else l_0_traffic_policy_interfaces)) > 0):
            pass
            yield '\n##### Traffic-Policy Interfaces\n\n| Interface | Input Traffic-Policy | Output Traffic-Policy |\n| --------- | -------------------- | --------------------- |\n'
            for l_1_interface in (undefined(name='traffic_policy_interfaces') if l_0_traffic_policy_interfaces is missing else l_0_traffic_policy_interfaces):
                l_1_row_in_policy = l_1_row_out_policy = missing
                _loop_vars = {}
                pass
                l_1_row_in_policy = t_1(environment.getattr(environment.getattr(l_1_interface, 'traffic_policy'), 'input'), '-')
                _loop_vars['row_in_policy'] = l_1_row_in_policy
                l_1_row_out_policy = t_1(environment.getattr(environment.getattr(l_1_interface, 'traffic_policy'), 'output'), '-')
                _loop_vars['row_out_policy'] = l_1_row_out_policy
                yield '| '
                yield str(environment.getattr(l_1_interface, 'name'))
                yield ' | '
                yield str((undefined(name='row_in_policy') if l_1_row_in_policy is missing else l_1_row_in_policy))
                yield ' | '
                yield str((undefined(name='row_out_policy') if l_1_row_out_policy is missing else l_1_row_out_policy))
                yield ' |\n'
            l_1_interface = l_1_row_in_policy = l_1_row_out_policy = missing
        yield '\n#### Traffic Policies Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/traffic-policies.j2', 'documentation/traffic-policies.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'traffic_policy_interfaces': l_0_traffic_policy_interfaces}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=57&10=60&11=62&17=65&18=69&19=71&20=74&23=81&29=84&30=88&31=90&32=93&35=100&41=103&42=107&46=112&49=115&51=119&52=121&54=124&56=126&60=129&61=137&62=141&63=144&65=147&66=148&67=152&68=153&69=157&71=162&74=165&75=166&76=170&77=171&78=175&80=180&83=183&84=186&85=189&86=192&87=195&88=196&89=200&91=201&92=204&93=206&94=207&95=208&96=209&98=212&99=213&100=214&101=215&104=219&105=222&106=225&107=228&109=233&110=236&111=239&112=242&113=245&116=248&117=249&118=251&119=253&121=256&123=257&124=259&126=260&127=262&129=263&130=265&132=266&133=268&135=269&136=271&138=272&139=274&141=275&142=277&143=279&144=281&145=283&146=285&148=289&150=291&151=293&152=295&153=297&155=301&157=303&158=305&159=307&160=309&161=311&162=313&164=317&166=319&167=321&168=323&169=325&171=329&174=331&175=333&177=335&178=337&182=340&185=342&191=364&192=367&193=370&194=372&197=374&198=377&199=379&202=381&208=384&209=388&210=390&211=393&218=401'