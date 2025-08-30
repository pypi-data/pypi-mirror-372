from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/traffic-policies.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_traffic_policies = resolve('traffic_policies')
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
        t_6 = environment.filters['unique']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'unique' found.")
    try:
        t_7 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    try:
        t_8 = environment.tests['defined']
    except KeyError:
        @internalcode
        def t_8(*unused):
            raise TemplateRuntimeError("No test named 'defined' found.")
    pass
    if t_7((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies)):
        pass
        yield '!\ntraffic-policies\n'
        l_1_loop = missing
        for l_1_field_set_port, l_1_loop in LoopContext(t_2(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ports'), 'name'), undefined):
            _loop_vars = {}
            pass
            yield '   field-set l4-port '
            yield str(environment.getattr(l_1_field_set_port, 'name'))
            yield '\n'
            if t_7(environment.getattr(l_1_field_set_port, 'port_range')):
                pass
                yield '      '
                yield str(environment.getattr(l_1_field_set_port, 'port_range'))
                yield '\n'
            if (not environment.getattr(l_1_loop, 'last')):
                pass
                yield '   !\n'
        l_1_loop = l_1_field_set_port = missing
        l_1_loop = missing
        for l_1_field_set_ipv4, l_1_loop in LoopContext(t_2(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ipv4'), 'name'), undefined):
            _loop_vars = {}
            pass
            yield '   field-set ipv4 prefix '
            yield str(environment.getattr(l_1_field_set_ipv4, 'name'))
            yield '\n'
            if t_7(environment.getattr(l_1_field_set_ipv4, 'prefixes')):
                pass
                yield '      '
                yield str(t_3(context.eval_ctx, t_2(environment.getattr(l_1_field_set_ipv4, 'prefixes')), ' '))
                yield '\n'
            if t_7(environment.getattr(l_1_field_set_ipv4, 'except')):
                pass
                yield '      except '
                yield str(t_3(context.eval_ctx, t_2(environment.getattr(l_1_field_set_ipv4, 'except')), ' '))
                yield '\n'
            if (not environment.getattr(l_1_loop, 'last')):
                pass
                yield '   !\n'
        l_1_loop = l_1_field_set_ipv4 = missing
        l_1_loop = missing
        for l_1_field_set_ipv6, l_1_loop in LoopContext(t_2(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'field_sets'), 'ipv6'), 'name'), undefined):
            _loop_vars = {}
            pass
            yield '   field-set ipv6 prefix '
            yield str(environment.getattr(l_1_field_set_ipv6, 'name'))
            yield '\n'
            if t_7(environment.getattr(l_1_field_set_ipv6, 'prefixes')):
                pass
                yield '      '
                yield str(t_3(context.eval_ctx, t_2(environment.getattr(l_1_field_set_ipv6, 'prefixes')), ' '))
                yield '\n'
            if t_7(environment.getattr(l_1_field_set_ipv6, 'except')):
                pass
                yield '      except '
                yield str(t_3(context.eval_ctx, t_2(environment.getattr(l_1_field_set_ipv6, 'except')), ' '))
                yield '\n'
            if (not environment.getattr(l_1_loop, 'last')):
                pass
                yield '   !\n'
        l_1_loop = l_1_field_set_ipv6 = missing
        if t_7(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'options'), 'counter_per_interface'), True):
            pass
            yield '   counter interface per-interface ingress\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'options'), 'counter_interface_poll_interval')):
            pass
            yield '   counter interface poll interval '
            yield str(environment.getattr(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'options'), 'counter_interface_poll_interval'))
            yield ' seconds\n'
        for l_1_policy in t_2(environment.getattr((undefined(name='traffic_policies') if l_0_traffic_policies is missing else l_0_traffic_policies), 'policies'), 'name'):
            l_1_namespace = resolve('namespace')
            l_1_transient_values = missing
            _loop_vars = {}
            pass
            yield '   !\n   traffic-policy '
            yield str(environment.getattr(l_1_policy, 'name'))
            yield '\n'
            l_1_transient_values = context.call((undefined(name='namespace') if l_1_namespace is missing else l_1_namespace), counters=[], _loop_vars=_loop_vars)
            _loop_vars['transient_values'] = l_1_transient_values
            if t_7(environment.getattr(l_1_policy, 'counters')):
                pass
                context.call(environment.getattr(environment.getattr((undefined(name='transient_values') if l_1_transient_values is missing else l_1_transient_values), 'counters'), 'extend'), environment.getattr(l_1_policy, 'counters'), _loop_vars=_loop_vars)
            for l_2_match in t_1(environment.getattr(l_1_policy, 'matches'), []):
                _loop_vars = {}
                pass
                if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'count')):
                    pass
                    context.call(environment.getattr(environment.getattr((undefined(name='transient_values') if l_1_transient_values is missing else l_1_transient_values), 'counters'), 'append'), environment.getattr(environment.getattr(l_2_match, 'actions'), 'count'), _loop_vars=_loop_vars)
            l_2_match = missing
            if (t_4(environment.getattr((undefined(name='transient_values') if l_1_transient_values is missing else l_1_transient_values), 'counters')) > 0):
                pass
                yield '      counter '
                yield str(t_3(context.eval_ctx, t_2(t_6(environment, environment.getattr((undefined(name='transient_values') if l_1_transient_values is missing else l_1_transient_values), 'counters'))), ' '))
                yield '\n      !\n'
            if t_7(environment.getattr(l_1_policy, 'matches')):
                pass
                for l_2_match in environment.getattr(l_1_policy, 'matches'):
                    l_2_bgp_flag = resolve('bgp_flag')
                    l_2_redirect_cli = resolve('redirect_cli')
                    l_2_next_hop_flag = resolve('next_hop_flag')
                    _loop_vars = {}
                    pass
                    yield '      match '
                    yield str(environment.getattr(l_2_match, 'name'))
                    yield ' '
                    yield str(t_5(environment.getattr(l_2_match, 'type')))
                    yield '\n'
                    if t_7(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefixes')):
                        pass
                        yield '         source prefix '
                        yield str(t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefixes')), ' '))
                        yield '\n'
                    elif t_7(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefix_lists')):
                        pass
                        yield '         source prefix field-set '
                        yield str(t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(l_2_match, 'source'), 'prefix_lists')), ' '))
                        yield '\n'
                    if t_7(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefixes')):
                        pass
                        yield '         destination prefix '
                        yield str(t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefixes')), ' '))
                        yield '\n'
                    elif t_7(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefix_lists')):
                        pass
                        yield '         destination prefix field-set '
                        yield str(t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(l_2_match, 'destination'), 'prefix_lists')), ' '))
                        yield '\n'
                    if t_7(environment.getattr(l_2_match, 'protocols')):
                        pass
                        l_2_bgp_flag = True
                        _loop_vars['bgp_flag'] = l_2_bgp_flag
                        for l_3_protocol in environment.getattr(l_2_match, 'protocols'):
                            l_3_protocol_neighbors_cli = resolve('protocol_neighbors_cli')
                            l_3_bgp_flag = l_2_bgp_flag
                            l_3_protocol_cli = resolve('protocol_cli')
                            l_3_protocol_port_cli = resolve('protocol_port_cli')
                            l_3_protocol_field_cli = resolve('protocol_field_cli')
                            _loop_vars = {}
                            pass
                            if ((t_5(environment.getattr(l_3_protocol, 'protocol')) in ['neighbors', 'bgp']) and (undefined(name='bgp_flag') if l_3_bgp_flag is missing else l_3_bgp_flag)):
                                pass
                                if (t_5(environment.getattr(l_3_protocol, 'protocol')) == 'neighbors'):
                                    pass
                                    l_3_protocol_neighbors_cli = 'protocol neighbors bgp'
                                    _loop_vars['protocol_neighbors_cli'] = l_3_protocol_neighbors_cli
                                    if t_7(environment.getattr(l_3_protocol, 'enforce_gtsm'), True):
                                        pass
                                        l_3_protocol_neighbors_cli = str_join(((undefined(name='protocol_neighbors_cli') if l_3_protocol_neighbors_cli is missing else l_3_protocol_neighbors_cli), ' enforce ttl maximum-hops', ))
                                        _loop_vars['protocol_neighbors_cli'] = l_3_protocol_neighbors_cli
                                    yield '         '
                                    yield str((undefined(name='protocol_neighbors_cli') if l_3_protocol_neighbors_cli is missing else l_3_protocol_neighbors_cli))
                                    yield '\n'
                                else:
                                    pass
                                    yield '         protocol bgp\n'
                                break
                            else:
                                pass
                                l_3_bgp_flag = False
                                _loop_vars['bgp_flag'] = l_3_bgp_flag
                                l_3_protocol_cli = str_join(('protocol ', t_5(environment.getattr(l_3_protocol, 'protocol')), ))
                                _loop_vars['protocol_cli'] = l_3_protocol_cli
                                if (t_7(environment.getattr(l_3_protocol, 'flags')) and (t_5(environment.getattr(l_3_protocol, 'protocol')) == 'tcp')):
                                    pass
                                    for l_4_flag in environment.getattr(l_3_protocol, 'flags'):
                                        _loop_vars = {}
                                        pass
                                        yield '         '
                                        yield str((undefined(name='protocol_cli') if l_3_protocol_cli is missing else l_3_protocol_cli))
                                        yield ' flags '
                                        yield str(l_4_flag)
                                        yield '\n'
                                    l_4_flag = missing
                                if ((t_5(environment.getattr(l_3_protocol, 'protocol')) in ['tcp', 'udp']) and (((t_7(environment.getattr(l_3_protocol, 'src_port')) or t_7(environment.getattr(l_3_protocol, 'dst_port'))) or t_7(environment.getattr(l_3_protocol, 'src_field'))) or t_7(environment.getattr(l_3_protocol, 'dst_field')))):
                                    pass
                                    if (t_7(environment.getattr(l_3_protocol, 'src_port')) or t_7(environment.getattr(l_3_protocol, 'dst_port'))):
                                        pass
                                        l_3_protocol_port_cli = (undefined(name='protocol_cli') if l_3_protocol_cli is missing else l_3_protocol_cli)
                                        _loop_vars['protocol_port_cli'] = l_3_protocol_port_cli
                                        if t_7(environment.getattr(l_3_protocol, 'src_port')):
                                            pass
                                            l_3_protocol_port_cli = str_join(((undefined(name='protocol_port_cli') if l_3_protocol_port_cli is missing else l_3_protocol_port_cli), ' source port ', environment.getattr(l_3_protocol, 'src_port'), ))
                                            _loop_vars['protocol_port_cli'] = l_3_protocol_port_cli
                                        if t_7(environment.getattr(l_3_protocol, 'dst_port')):
                                            pass
                                            l_3_protocol_port_cli = str_join(((undefined(name='protocol_port_cli') if l_3_protocol_port_cli is missing else l_3_protocol_port_cli), ' destination port ', environment.getattr(l_3_protocol, 'dst_port'), ))
                                            _loop_vars['protocol_port_cli'] = l_3_protocol_port_cli
                                        yield '         '
                                        yield str((undefined(name='protocol_port_cli') if l_3_protocol_port_cli is missing else l_3_protocol_port_cli))
                                        yield '\n'
                                    if (t_7(environment.getattr(l_3_protocol, 'src_field')) or t_7(environment.getattr(l_3_protocol, 'dst_field'))):
                                        pass
                                        l_3_protocol_field_cli = (undefined(name='protocol_cli') if l_3_protocol_cli is missing else l_3_protocol_cli)
                                        _loop_vars['protocol_field_cli'] = l_3_protocol_field_cli
                                        if t_7(environment.getattr(l_3_protocol, 'src_field')):
                                            pass
                                            l_3_protocol_field_cli = str_join(((undefined(name='protocol_field_cli') if l_3_protocol_field_cli is missing else l_3_protocol_field_cli), ' source port field-set ', environment.getattr(l_3_protocol, 'src_field'), ))
                                            _loop_vars['protocol_field_cli'] = l_3_protocol_field_cli
                                        if t_7(environment.getattr(l_3_protocol, 'dst_field')):
                                            pass
                                            l_3_protocol_field_cli = str_join(((undefined(name='protocol_field_cli') if l_3_protocol_field_cli is missing else l_3_protocol_field_cli), ' destination port field-set ', environment.getattr(l_3_protocol, 'dst_field'), ))
                                            _loop_vars['protocol_field_cli'] = l_3_protocol_field_cli
                                        yield '         '
                                        yield str((undefined(name='protocol_field_cli') if l_3_protocol_field_cli is missing else l_3_protocol_field_cli))
                                        yield '\n'
                                elif (t_7(environment.getattr(l_3_protocol, 'icmp_type')) and (t_5(environment.getattr(l_3_protocol, 'protocol')) == 'icmp')):
                                    pass
                                    yield '         '
                                    yield str((undefined(name='protocol_cli') if l_3_protocol_cli is missing else l_3_protocol_cli))
                                    yield ' type '
                                    yield str(t_3(context.eval_ctx, t_2(environment.getattr(l_3_protocol, 'icmp_type')), ' '))
                                    yield ' code all\n'
                                else:
                                    pass
                                    yield '         '
                                    yield str((undefined(name='protocol_cli') if l_3_protocol_cli is missing else l_3_protocol_cli))
                                    yield '\n'
                        l_3_protocol = l_3_protocol_neighbors_cli = l_3_bgp_flag = l_3_protocol_cli = l_3_protocol_port_cli = l_3_protocol_field_cli = missing
                    if t_7(environment.getattr(environment.getattr(l_2_match, 'fragment'), 'offset')):
                        pass
                        yield '         fragment offset '
                        yield str(environment.getattr(environment.getattr(l_2_match, 'fragment'), 'offset'))
                        yield '\n'
                    elif t_8(environment.getattr(l_2_match, 'fragment')):
                        pass
                        yield '         fragment\n'
                    if t_7(environment.getattr(l_2_match, 'ttl')):
                        pass
                        yield '         ttl '
                        yield str(environment.getattr(l_2_match, 'ttl'))
                        yield '\n'
                    if ((((t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'count')) or t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'traffic_class'))) or t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'dscp'))) or t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'drop'), True)) or t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'))):
                        pass
                        yield '         !\n         actions\n'
                        if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'count')):
                            pass
                            yield '            count '
                            yield str(environment.getattr(environment.getattr(l_2_match, 'actions'), 'count'))
                            yield '\n'
                        if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'drop'), True):
                            pass
                            yield '            drop\n'
                            if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'log'), True):
                                pass
                                yield '            log\n'
                        if t_7(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'aggregation_groups')):
                            pass
                            yield '            redirect aggregation group '
                            yield str(t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'aggregation_groups')), ' '))
                            yield '\n'
                        if t_7(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'interface')):
                            pass
                            yield '            redirect interface '
                            yield str(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'interface'))
                            yield '\n'
                        if ((not (t_7(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'interface')) or t_7(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'aggregation_groups')))) and t_7(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'))):
                            pass
                            l_2_redirect_cli = 'redirect next-hop '
                            _loop_vars['redirect_cli'] = l_2_redirect_cli
                            l_2_next_hop_flag = False
                            _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv4_addresses')):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv4_addresses')), ' '), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                    pass
                                    l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), ' vrf ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                    _loop_vars['redirect_cli'] = l_2_redirect_cli
                                l_2_next_hop_flag = True
                                _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv6_addresses')):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ipv6_addresses')), ' '), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                    pass
                                    l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), ' vrf ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                    _loop_vars['redirect_cli'] = l_2_redirect_cli
                                l_2_next_hop_flag = True
                                _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'groups')):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), 'group ', t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'groups')), ' '), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                                l_2_next_hop_flag = True
                                _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv4_addresses')):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), 'recursive ', t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv4_addresses')), ' '), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                    pass
                                    l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), ' vrf ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                    _loop_vars['redirect_cli'] = l_2_redirect_cli
                                l_2_next_hop_flag = True
                                _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            elif t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv6_addresses')):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), 'recursive ', t_3(context.eval_ctx, t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'recursive_ipv6_addresses')), ' '), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                                if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf')):
                                    pass
                                    l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), ' vrf ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'vrf'), ))
                                    _loop_vars['redirect_cli'] = l_2_redirect_cli
                                l_2_next_hop_flag = True
                                _loop_vars['next_hop_flag'] = l_2_next_hop_flag
                            if (t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ttl')) and (undefined(name='next_hop_flag') if l_2_next_hop_flag is missing else l_2_next_hop_flag)):
                                pass
                                l_2_redirect_cli = str_join(((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli), ' ttl ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_2_match, 'actions'), 'redirect'), 'next_hop'), 'ttl'), ))
                                _loop_vars['redirect_cli'] = l_2_redirect_cli
                            if ((undefined(name='next_hop_flag') if l_2_next_hop_flag is missing else l_2_next_hop_flag) == True):
                                pass
                                yield '            '
                                yield str((undefined(name='redirect_cli') if l_2_redirect_cli is missing else l_2_redirect_cli))
                                yield '\n'
                        if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'dscp')):
                            pass
                            yield '            set dscp '
                            yield str(environment.getattr(environment.getattr(l_2_match, 'actions'), 'dscp'))
                            yield '\n'
                        if t_7(environment.getattr(environment.getattr(l_2_match, 'actions'), 'traffic_class')):
                            pass
                            yield '            set traffic class '
                            yield str(environment.getattr(environment.getattr(l_2_match, 'actions'), 'traffic_class'))
                            yield '\n'
                    yield '      !\n'
                l_2_match = l_2_bgp_flag = l_2_redirect_cli = l_2_next_hop_flag = missing
            yield '      match ipv4-all-default ipv4\n'
            if t_7(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4')):
                pass
                yield '         actions\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'count')):
                    pass
                    yield '            count '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'count'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'drop'), True):
                    pass
                    yield '            drop\n'
                    if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'log'), True):
                        pass
                        yield '            log\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'dscp')):
                    pass
                    yield '            set dscp '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'dscp'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'traffic_class')):
                    pass
                    yield '            set traffic class '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv4'), 'traffic_class'))
                    yield '\n'
            yield '      !\n      match ipv6-all-default ipv6\n'
            if t_7(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6')):
                pass
                yield '         actions\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'count')):
                    pass
                    yield '            count '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'count'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'drop'), True):
                    pass
                    yield '            drop\n'
                    if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'log'), True):
                        pass
                        yield '            log\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'dscp')):
                    pass
                    yield '            set dscp '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'dscp'))
                    yield '\n'
                if t_7(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'traffic_class')):
                    pass
                    yield '            set traffic class '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_policy, 'default_actions'), 'ipv6'), 'traffic_class'))
                    yield '\n'
        l_1_policy = l_1_namespace = l_1_transient_values = missing

blocks = {}
debug_info = '7=60&12=64&13=68&14=70&15=73&17=75&22=80&23=84&24=86&25=89&27=91&28=94&30=96&35=101&36=105&37=107&38=110&40=112&41=115&43=117&48=121&51=124&52=127&55=129&57=135&59=137&60=139&61=141&64=142&65=145&66=147&69=149&70=152&73=154&75=156&76=163&78=167&79=170&80=172&81=175&84=177&85=180&86=182&87=185&90=187&91=189&92=191&93=199&94=201&95=203&96=205&97=207&99=210&103=215&105=218&106=220&107=222&108=224&109=228&112=233&118=235&119=237&120=239&121=241&123=243&124=245&126=248&129=250&130=252&131=254&132=256&134=258&135=260&137=263&139=265&140=268&142=275&148=278&149=281&150=283&154=286&155=289&158=291&162=294&163=297&166=299&169=302&173=305&174=308&176=310&177=313&179=315&180=317&181=319&182=321&183=323&184=325&185=327&187=329&188=331&189=333&190=335&191=337&193=339&194=341&195=343&196=345&197=347&198=349&199=351&200=353&202=355&203=357&204=359&205=361&206=363&208=365&210=367&211=369&213=371&214=374&218=376&219=379&222=381&223=384&232=389&235=392&236=395&239=397&242=400&247=403&248=406&251=408&252=411&257=414&260=417&261=420&264=422&267=425&272=428&273=431&276=433&277=436'