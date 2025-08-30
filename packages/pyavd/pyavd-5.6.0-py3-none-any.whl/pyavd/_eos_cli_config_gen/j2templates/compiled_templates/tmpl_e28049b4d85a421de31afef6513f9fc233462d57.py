from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/router-bgp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_router_bgp = resolve('router_bgp')
    l_0_timers_bgp_cli = resolve('timers_bgp_cli')
    l_0_distance_cli = resolve('distance_cli')
    l_0_rr_preserve_attributes_cli = resolve('rr_preserve_attributes_cli')
    l_0_paths_cli = resolve('paths_cli')
    l_0_redistribute_var = resolve('redistribute_var')
    l_0_redistribute_conn = resolve('redistribute_conn')
    l_0_redistribute_isis = resolve('redistribute_isis')
    l_0_redistribute_ospf = resolve('redistribute_ospf')
    l_0_redistribute_ospf_match = resolve('redistribute_ospf_match')
    l_0_redistribute_ospfv3 = resolve('redistribute_ospfv3')
    l_0_redistribute_ospfv3_match = resolve('redistribute_ospfv3_match')
    l_0_redistribute_static = resolve('redistribute_static')
    l_0_redistribute_rip = resolve('redistribute_rip')
    l_0_redistribute_host = resolve('redistribute_host')
    l_0_redistribute_dynamic = resolve('redistribute_dynamic')
    l_0_redistribute_bgp = resolve('redistribute_bgp')
    l_0_redistribute_user = resolve('redistribute_user')
    l_0_encapsulation_cli = resolve('encapsulation_cli')
    l_0_evpn_mpls_resolution_ribs = resolve('evpn_mpls_resolution_ribs')
    l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli = resolve('evpn_neighbor_default_nhs_received_evpn_routes_cli')
    l_0_hostflap_detection_cli = resolve('hostflap_detection_cli')
    l_0_layer2_cli = resolve('layer2_cli')
    l_0_v4_bgp_lu_resolution_ribs = resolve('v4_bgp_lu_resolution_ribs')
    l_0_redistribute_dhcp = resolve('redistribute_dhcp')
    l_0_path_selection_roles = resolve('path_selection_roles')
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
        t_4 = environment.filters['indent']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'indent' found.")
    try:
        t_5 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
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
    try:
        t_8 = environment.tests['number']
    except KeyError:
        @internalcode
        def t_8(*unused):
            raise TemplateRuntimeError("No test named 'number' found.")
    pass
    if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'as')):
        pass
        yield '!\nrouter bgp '
        yield str(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'as'))
        yield '\n'
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'as_notation')):
            pass
            yield '   bgp asn notation '
            yield str(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'as_notation'))
            yield '\n'
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'router_id')):
            pass
            yield '   router-id '
            yield str(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'router_id'))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'updates'), 'wait_for_convergence'), True):
            pass
            yield '   update wait-for-convergence\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'updates'), 'wait_install'), True):
            pass
            yield '   update wait-install\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'default'), 'ipv4_unicast'), True):
            pass
            yield '   bgp default ipv4-unicast\n'
        elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'default'), 'ipv4_unicast'), False):
            pass
            yield '   no bgp default ipv4-unicast\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'default'), 'ipv4_unicast_transport_ipv6'), True):
            pass
            yield '   bgp default ipv4-unicast transport ipv6\n'
        elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'default'), 'ipv4_unicast_transport_ipv6'), False):
            pass
            yield '   no bgp default ipv4-unicast transport ipv6\n'
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers')):
            pass
            l_0_timers_bgp_cli = 'timers bgp'
            context.vars['timers_bgp_cli'] = l_0_timers_bgp_cli
            context.exported_vars.add('timers_bgp_cli')
            if (t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers'), 'keepalive_time')) and t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers'), 'hold_time'))):
                pass
                l_0_timers_bgp_cli = str_join(((undefined(name='timers_bgp_cli') if l_0_timers_bgp_cli is missing else l_0_timers_bgp_cli), ' ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers'), 'keepalive_time'), ' ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers'), 'hold_time'), ))
                context.vars['timers_bgp_cli'] = l_0_timers_bgp_cli
                context.exported_vars.add('timers_bgp_cli')
            if (t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers'), 'min_hold_time')) or t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers'), 'send_failure_hold_time'))):
                pass
                if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers'), 'min_hold_time')):
                    pass
                    l_0_timers_bgp_cli = str_join(((undefined(name='timers_bgp_cli') if l_0_timers_bgp_cli is missing else l_0_timers_bgp_cli), ' min-hold-time ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers'), 'min_hold_time'), ))
                    context.vars['timers_bgp_cli'] = l_0_timers_bgp_cli
                    context.exported_vars.add('timers_bgp_cli')
                if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers'), 'send_failure_hold_time')):
                    pass
                    l_0_timers_bgp_cli = str_join(((undefined(name='timers_bgp_cli') if l_0_timers_bgp_cli is missing else l_0_timers_bgp_cli), ' send-failure hold-time ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'timers'), 'send_failure_hold_time'), ))
                    context.vars['timers_bgp_cli'] = l_0_timers_bgp_cli
                    context.exported_vars.add('timers_bgp_cli')
            yield '   '
            yield str((undefined(name='timers_bgp_cli') if l_0_timers_bgp_cli is missing else l_0_timers_bgp_cli))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'external_routes')):
            pass
            l_0_distance_cli = str_join(('distance bgp ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'external_routes'), ))
            context.vars['distance_cli'] = l_0_distance_cli
            context.exported_vars.add('distance_cli')
            if (t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'internal_routes')) and t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'local_routes'))):
                pass
                l_0_distance_cli = str_join(((undefined(name='distance_cli') if l_0_distance_cli is missing else l_0_distance_cli), ' ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'internal_routes'), ' ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'distance'), 'local_routes'), ))
                context.vars['distance_cli'] = l_0_distance_cli
                context.exported_vars.add('distance_cli')
            yield '   '
            yield str((undefined(name='distance_cli') if l_0_distance_cli is missing else l_0_distance_cli))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart'), 'enabled'), True):
            pass
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart'), 'restart_time')):
                pass
                yield '   graceful-restart restart-time '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart'), 'restart_time'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart'), 'stalepath_time')):
                pass
                yield '   graceful-restart stalepath-time '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart'), 'stalepath_time'))
                yield '\n'
            yield '   graceful-restart\n'
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp_cluster_id')):
            pass
            yield '   bgp cluster-id '
            yield str(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp_cluster_id'))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart_helper'), 'enabled'), False):
            pass
            yield '   no graceful-restart-helper\n'
        elif t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart_helper'), 'enabled'), True):
            pass
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart_helper'), 'restart_time')):
                pass
                yield '   graceful-restart-helper restart-time '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart_helper'), 'restart_time'))
                yield '\n'
            elif t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'graceful_restart_helper'), 'long_lived'), True):
                pass
                yield '   graceful-restart-helper long-lived\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'route_reflector_preserve_attributes'), 'enabled'), True):
            pass
            l_0_rr_preserve_attributes_cli = 'bgp route-reflector preserve-attributes'
            context.vars['rr_preserve_attributes_cli'] = l_0_rr_preserve_attributes_cli
            context.exported_vars.add('rr_preserve_attributes_cli')
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'route_reflector_preserve_attributes'), 'always'), True):
                pass
                l_0_rr_preserve_attributes_cli = str_join(((undefined(name='rr_preserve_attributes_cli') if l_0_rr_preserve_attributes_cli is missing else l_0_rr_preserve_attributes_cli), ' always', ))
                context.vars['rr_preserve_attributes_cli'] = l_0_rr_preserve_attributes_cli
                context.exported_vars.add('rr_preserve_attributes_cli')
            yield '   '
            yield str((undefined(name='rr_preserve_attributes_cli') if l_0_rr_preserve_attributes_cli is missing else l_0_rr_preserve_attributes_cli))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'maximum_paths'), 'paths')):
            pass
            l_0_paths_cli = str_join(('maximum-paths ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'maximum_paths'), 'paths'), ))
            context.vars['paths_cli'] = l_0_paths_cli
            context.exported_vars.add('paths_cli')
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'maximum_paths'), 'ecmp')):
                pass
                l_0_paths_cli = str_join(((undefined(name='paths_cli') if l_0_paths_cli is missing else l_0_paths_cli), ' ecmp ', environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'maximum_paths'), 'ecmp'), ))
                context.vars['paths_cli'] = l_0_paths_cli
                context.exported_vars.add('paths_cli')
            yield '   '
            yield str((undefined(name='paths_cli') if l_0_paths_cli is missing else l_0_paths_cli))
            yield '\n'
        for l_1_bgp_default in t_1(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp_defaults'), []):
            _loop_vars = {}
            pass
            yield '   '
            yield str(l_1_bgp_default)
            yield '\n'
        l_1_bgp_default = missing
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'receive'), True):
            pass
            yield '   bgp additional-paths receive\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'receive'), False):
            pass
            yield '   no bgp additional-paths receive\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'send')):
            pass
            if (environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'send') == 'disabled'):
                pass
                yield '   no bgp additional-paths send\n'
            elif (t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'send') == 'ecmp')):
                pass
                yield '   bgp additional-paths send ecmp limit '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'send_limit'))
                yield '\n'
            elif (environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'send') == 'limit'):
                pass
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'send_limit')):
                    pass
                    yield '   bgp additional-paths send limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'send_limit'))
                    yield '\n'
            else:
                pass
                yield '   bgp additional-paths send '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'additional_paths'), 'send'))
                yield '\n'
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'listen_ranges')):
            pass
            def t_9(fiter):
                for l_1_listen_range in fiter:
                    if ((t_6(environment.getattr(l_1_listen_range, 'peer_group')) and t_6(environment.getattr(l_1_listen_range, 'prefix'))) and (t_6(environment.getattr(l_1_listen_range, 'peer_filter')) or t_6(environment.getattr(l_1_listen_range, 'remote_as')))):
                        yield l_1_listen_range
            for l_1_listen_range in t_9(t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'listen_ranges'), 'peer_group')):
                l_1_listen_range_cli = missing
                _loop_vars = {}
                pass
                l_1_listen_range_cli = str_join(('bgp listen range ', environment.getattr(l_1_listen_range, 'prefix'), ))
                _loop_vars['listen_range_cli'] = l_1_listen_range_cli
                if t_6(environment.getattr(l_1_listen_range, 'peer_id_include_router_id'), True):
                    pass
                    l_1_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_1_listen_range_cli is missing else l_1_listen_range_cli), ' peer-id include router-id', ))
                    _loop_vars['listen_range_cli'] = l_1_listen_range_cli
                l_1_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_1_listen_range_cli is missing else l_1_listen_range_cli), ' peer-group ', environment.getattr(l_1_listen_range, 'peer_group'), ))
                _loop_vars['listen_range_cli'] = l_1_listen_range_cli
                if t_6(environment.getattr(l_1_listen_range, 'peer_filter')):
                    pass
                    l_1_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_1_listen_range_cli is missing else l_1_listen_range_cli), ' peer-filter ', environment.getattr(l_1_listen_range, 'peer_filter'), ))
                    _loop_vars['listen_range_cli'] = l_1_listen_range_cli
                elif t_6(environment.getattr(l_1_listen_range, 'remote_as')):
                    pass
                    l_1_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_1_listen_range_cli is missing else l_1_listen_range_cli), ' remote-as ', environment.getattr(l_1_listen_range, 'remote_as'), ))
                    _loop_vars['listen_range_cli'] = l_1_listen_range_cli
                yield '   '
                yield str((undefined(name='listen_range_cli') if l_1_listen_range_cli is missing else l_1_listen_range_cli))
                yield '\n'
            l_1_listen_range = l_1_listen_range_cli = missing
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'bestpath'), 'd_path'), True):
            pass
            yield '   bgp bestpath d-path\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'neighbor_default'), 'send_community'), 'all'):
            pass
            yield '   neighbor default send-community\n'
        elif t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'neighbor_default'), 'send_community')):
            pass
            yield '   neighbor default send-community '
            yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'neighbor_default'), 'send_community'))
            yield '\n'
        for l_1_peer_group in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'peer_groups'), 'name'):
            l_1_remove_private_as_cli = resolve('remove_private_as_cli')
            l_1_allowas_in_cli = resolve('allowas_in_cli')
            l_1_neighbor_rib_in_pre_policy_retain_cli = resolve('neighbor_rib_in_pre_policy_retain_cli')
            l_1_hide_passwords = resolve('hide_passwords')
            l_1_default_originate_cli = resolve('default_originate_cli')
            l_1_maximum_routes_cli = resolve('maximum_routes_cli')
            l_1_link_bandwidth_cli = resolve('link_bandwidth_cli')
            l_1_remove_private_as_ingress_cli = resolve('remove_private_as_ingress_cli')
            _loop_vars = {}
            pass
            yield '   neighbor '
            yield str(environment.getattr(l_1_peer_group, 'name'))
            yield ' peer group\n'
            if t_6(environment.getattr(l_1_peer_group, 'remote_as')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' remote-as '
                yield str(environment.getattr(l_1_peer_group, 'remote_as'))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'next_hop_self'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' next-hop-self\n'
            if t_6(environment.getattr(l_1_peer_group, 'next_hop_peer'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' next-hop-peer\n'
            if t_6(environment.getattr(l_1_peer_group, 'next_hop_unchanged'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' next-hop-unchanged\n'
            if t_6(environment.getattr(l_1_peer_group, 'shutdown'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' shutdown\n'
            if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as'), 'enabled'), True):
                pass
                l_1_remove_private_as_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' remove-private-as', ))
                _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as'), 'all'), True):
                    pass
                    l_1_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli), ' all', ))
                    _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                    if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as'), 'replace_as'), True):
                        pass
                        l_1_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli), ' replace-as', ))
                        _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                yield '   '
                yield str((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli))
                yield '\n'
            elif t_6(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as'), 'enabled'), False):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' remove-private-as\n'
            if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'as_path'), 'prepend_own_disabled'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' as-path prepend-own disabled\n'
            if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'as_path'), 'remote_as_replace_out'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' as-path remote-as replace out\n'
            if t_6(environment.getattr(l_1_peer_group, 'local_as')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' local-as '
                yield str(environment.getattr(l_1_peer_group, 'local_as'))
                yield ' no-prepend replace-as\n'
            if t_6(environment.getattr(l_1_peer_group, 'weight')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' weight '
                yield str(environment.getattr(l_1_peer_group, 'weight'))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'passive'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' passive\n'
            if t_6(environment.getattr(l_1_peer_group, 'update_source')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' update-source '
                yield str(environment.getattr(l_1_peer_group, 'update_source'))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'bfd'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' bfd\n'
                if ((t_6(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'interval')) and t_6(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'min_rx'))) and t_6(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'multiplier'))):
                    pass
                    yield '   neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' bfd interval '
                    yield str(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'interval'))
                    yield ' min-rx '
                    yield str(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'min_rx'))
                    yield ' multiplier '
                    yield str(environment.getattr(environment.getattr(l_1_peer_group, 'bfd_timers'), 'multiplier'))
                    yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'description')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' description '
                yield str(environment.getattr(l_1_peer_group, 'description'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'allowas_in'), 'enabled'), True):
                pass
                l_1_allowas_in_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' allowas-in', ))
                _loop_vars['allowas_in_cli'] = l_1_allowas_in_cli
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'allowas_in'), 'times')):
                    pass
                    l_1_allowas_in_cli = str_join(((undefined(name='allowas_in_cli') if l_1_allowas_in_cli is missing else l_1_allowas_in_cli), ' ', environment.getattr(environment.getattr(l_1_peer_group, 'allowas_in'), 'times'), ))
                    _loop_vars['allowas_in_cli'] = l_1_allowas_in_cli
                yield '   '
                yield str((undefined(name='allowas_in_cli') if l_1_allowas_in_cli is missing else l_1_allowas_in_cli))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'rib_in_pre_policy_retain'), 'enabled'), True):
                pass
                l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' rib-in pre-policy retain', ))
                _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'rib_in_pre_policy_retain'), 'all'), True):
                    pass
                    l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli), ' all', ))
                    _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                yield '   '
                yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli))
                yield '\n'
            elif t_6(environment.getattr(environment.getattr(l_1_peer_group, 'rib_in_pre_policy_retain'), 'enabled'), False):
                pass
                l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(('no neighbor ', environment.getattr(l_1_peer_group, 'name'), ' rib-in pre-policy retain', ))
                _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                yield '   '
                yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'ebgp_multihop')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' ebgp-multihop '
                yield str(environment.getattr(l_1_peer_group, 'ebgp_multihop'))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'ttl_maximum_hops')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' ttl maximum-hops '
                yield str(environment.getattr(l_1_peer_group, 'ttl_maximum_hops'))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'route_reflector_client'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' route-reflector-client\n'
            if t_6(environment.getattr(l_1_peer_group, 'session_tracker')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' session tracker '
                yield str(environment.getattr(l_1_peer_group, 'session_tracker'))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'timers')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' timers '
                yield str(environment.getattr(l_1_peer_group, 'timers'))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'route_map_in')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' route-map '
                yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                yield ' in\n'
            if t_6(environment.getattr(l_1_peer_group, 'route_map_out')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' route-map '
                yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                yield ' out\n'
            if t_6(environment.getattr(l_1_peer_group, 'password')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' password 7 '
                yield str(t_2(environment.getattr(l_1_peer_group, 'password'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
                yield '\n'
            if (t_6(environment.getattr(environment.getattr(l_1_peer_group, 'shared_secret'), 'profile')) and t_6(environment.getattr(environment.getattr(l_1_peer_group, 'shared_secret'), 'hash_algorithm'))):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' password shared-secret profile '
                yield str(environment.getattr(environment.getattr(l_1_peer_group, 'shared_secret'), 'profile'))
                yield ' algorithm '
                yield str(environment.getattr(environment.getattr(l_1_peer_group, 'shared_secret'), 'hash_algorithm'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'enabled'), True):
                pass
                l_1_default_originate_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' default-originate', ))
                _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'route_map')):
                    pass
                    l_1_default_originate_cli = str_join(((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli), ' route-map ', environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'route_map'), ))
                    _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'always'), True):
                    pass
                    l_1_default_originate_cli = str_join(((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli), ' always', ))
                    _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                yield '   '
                yield str((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'send_community'), 'all'):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' send-community\n'
            elif t_6(environment.getattr(l_1_peer_group, 'send_community')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' send-community '
                yield str(environment.getattr(l_1_peer_group, 'send_community'))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'maximum_routes')):
                pass
                l_1_maximum_routes_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' maximum-routes ', environment.getattr(l_1_peer_group, 'maximum_routes'), ))
                _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                if t_6(environment.getattr(l_1_peer_group, 'maximum_routes_warning_limit')):
                    pass
                    l_1_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli), ' warning-limit ', environment.getattr(l_1_peer_group, 'maximum_routes_warning_limit'), ))
                    _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                if t_6(environment.getattr(l_1_peer_group, 'maximum_routes_warning_only'), True):
                    pass
                    l_1_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli), ' warning-only', ))
                    _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                yield '   '
                yield str((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli))
                yield '\n'
            if t_6(environment.getattr(l_1_peer_group, 'missing_policy')):
                pass
                for l_2_direction in ['in', 'out']:
                    l_2_missing_policy_cli = resolve('missing_policy_cli')
                    l_2_dir = l_2_policy = missing
                    _loop_vars = {}
                    pass
                    l_2_dir = str_join(('direction_', l_2_direction, ))
                    _loop_vars['dir'] = l_2_dir
                    l_2_policy = environment.getitem(environment.getattr(l_1_peer_group, 'missing_policy'), (undefined(name='dir') if l_2_dir is missing else l_2_dir))
                    _loop_vars['policy'] = l_2_policy
                    if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'action')):
                        pass
                        l_2_missing_policy_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' missing-policy address-family all', ))
                        _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                        if ((t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_community_list'), True) or t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_prefix_list'), True)) or t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_sub_route_map'), True)):
                            pass
                            l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' include', ))
                            _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_community_list'), True):
                                pass
                                l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' community-list', ))
                                _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_prefix_list'), True):
                                pass
                                l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' prefix-list', ))
                                _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_sub_route_map'), True):
                                pass
                                l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' sub-route-map', ))
                                _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                        l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' direction ', l_2_direction, ' action ', environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'action'), ))
                        _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                        yield '   '
                        yield str((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli))
                        yield '\n'
                l_2_direction = l_2_dir = l_2_policy = l_2_missing_policy_cli = missing
            if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'link_bandwidth'), 'enabled'), True):
                pass
                l_1_link_bandwidth_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' link-bandwidth', ))
                _loop_vars['link_bandwidth_cli'] = l_1_link_bandwidth_cli
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'link_bandwidth'), 'default')):
                    pass
                    l_1_link_bandwidth_cli = str_join(((undefined(name='link_bandwidth_cli') if l_1_link_bandwidth_cli is missing else l_1_link_bandwidth_cli), ' default ', environment.getattr(environment.getattr(l_1_peer_group, 'link_bandwidth'), 'default'), ))
                    _loop_vars['link_bandwidth_cli'] = l_1_link_bandwidth_cli
                yield '   '
                yield str((undefined(name='link_bandwidth_cli') if l_1_link_bandwidth_cli is missing else l_1_link_bandwidth_cli))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as_ingress'), 'enabled'), True):
                pass
                l_1_remove_private_as_ingress_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' remove-private-as ingress', ))
                _loop_vars['remove_private_as_ingress_cli'] = l_1_remove_private_as_ingress_cli
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as_ingress'), 'replace_as'), True):
                    pass
                    l_1_remove_private_as_ingress_cli = str_join(((undefined(name='remove_private_as_ingress_cli') if l_1_remove_private_as_ingress_cli is missing else l_1_remove_private_as_ingress_cli), ' replace-as', ))
                    _loop_vars['remove_private_as_ingress_cli'] = l_1_remove_private_as_ingress_cli
                yield '   '
                yield str((undefined(name='remove_private_as_ingress_cli') if l_1_remove_private_as_ingress_cli is missing else l_1_remove_private_as_ingress_cli))
                yield '\n'
            elif t_6(environment.getattr(environment.getattr(l_1_peer_group, 'remove_private_as_ingress'), 'enabled'), False):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_peer_group, 'name'))
                yield ' remove-private-as ingress\n'
        l_1_peer_group = l_1_remove_private_as_cli = l_1_allowas_in_cli = l_1_neighbor_rib_in_pre_policy_retain_cli = l_1_hide_passwords = l_1_default_originate_cli = l_1_maximum_routes_cli = l_1_link_bandwidth_cli = l_1_remove_private_as_ingress_cli = missing
        for l_1_neighbor in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'neighbors'), 'ip_address'):
            l_1_remove_private_as_cli = resolve('remove_private_as_cli')
            l_1_allowas_in_cli = resolve('allowas_in_cli')
            l_1_neighbor_rib_in_pre_policy_retain_cli = resolve('neighbor_rib_in_pre_policy_retain_cli')
            l_1_hide_passwords = resolve('hide_passwords')
            l_1_default_originate_cli = resolve('default_originate_cli')
            l_1_maximum_routes_cli = resolve('maximum_routes_cli')
            l_1_link_bandwidth_cli = resolve('link_bandwidth_cli')
            l_1_remove_private_as_ingress_cli = resolve('remove_private_as_ingress_cli')
            _loop_vars = {}
            pass
            if t_6(environment.getattr(l_1_neighbor, 'peer_group')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' peer group '
                yield str(environment.getattr(l_1_neighbor, 'peer_group'))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'remote_as')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' remote-as '
                yield str(environment.getattr(l_1_neighbor, 'remote_as'))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'next_hop_self'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' next-hop-self\n'
            if t_6(environment.getattr(l_1_neighbor, 'next_hop_peer'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' next-hop-peer\n'
            if t_6(environment.getattr(l_1_neighbor, 'shutdown'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' shutdown\n'
            if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as'), 'enabled'), True):
                pass
                l_1_remove_private_as_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' remove-private-as', ))
                _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as'), 'all'), True):
                    pass
                    l_1_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli), ' all', ))
                    _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                    if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as'), 'replace_as'), True):
                        pass
                        l_1_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli), ' replace-as', ))
                        _loop_vars['remove_private_as_cli'] = l_1_remove_private_as_cli
                yield '   '
                yield str((undefined(name='remove_private_as_cli') if l_1_remove_private_as_cli is missing else l_1_remove_private_as_cli))
                yield '\n'
            elif t_6(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as'), 'enabled'), False):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' remove-private-as\n'
            if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'as_path'), 'prepend_own_disabled'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' as-path prepend-own disabled\n'
            if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'as_path'), 'remote_as_replace_out'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' as-path remote-as replace out\n'
            if t_6(environment.getattr(l_1_neighbor, 'local_as')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' local-as '
                yield str(environment.getattr(l_1_neighbor, 'local_as'))
                yield ' no-prepend replace-as\n'
            if t_6(environment.getattr(l_1_neighbor, 'weight')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' weight '
                yield str(environment.getattr(l_1_neighbor, 'weight'))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'passive'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' passive\n'
            if t_6(environment.getattr(l_1_neighbor, 'update_source')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' update-source '
                yield str(environment.getattr(l_1_neighbor, 'update_source'))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'bfd'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' bfd\n'
                if ((t_6(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'interval')) and t_6(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'min_rx'))) and t_6(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'multiplier'))):
                    pass
                    yield '   neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' bfd interval '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'interval'))
                    yield ' min-rx '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'min_rx'))
                    yield ' multiplier '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'bfd_timers'), 'multiplier'))
                    yield '\n'
            elif (t_6(environment.getattr(l_1_neighbor, 'bfd'), False) and t_6(environment.getattr(l_1_neighbor, 'peer_group'))):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' bfd\n'
            if t_6(environment.getattr(l_1_neighbor, 'description')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' description '
                yield str(environment.getattr(l_1_neighbor, 'description'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'allowas_in'), 'enabled'), True):
                pass
                l_1_allowas_in_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' allowas-in', ))
                _loop_vars['allowas_in_cli'] = l_1_allowas_in_cli
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'allowas_in'), 'times')):
                    pass
                    l_1_allowas_in_cli = str_join(((undefined(name='allowas_in_cli') if l_1_allowas_in_cli is missing else l_1_allowas_in_cli), ' ', environment.getattr(environment.getattr(l_1_neighbor, 'allowas_in'), 'times'), ))
                    _loop_vars['allowas_in_cli'] = l_1_allowas_in_cli
                yield '   '
                yield str((undefined(name='allowas_in_cli') if l_1_allowas_in_cli is missing else l_1_allowas_in_cli))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'rib_in_pre_policy_retain'), 'enabled'), True):
                pass
                l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' rib-in pre-policy retain', ))
                _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'rib_in_pre_policy_retain'), 'all'), True):
                    pass
                    l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli), ' all', ))
                    _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                yield '   '
                yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli))
                yield '\n'
            elif t_6(environment.getattr(environment.getattr(l_1_neighbor, 'rib_in_pre_policy_retain'), 'enabled'), False):
                pass
                l_1_neighbor_rib_in_pre_policy_retain_cli = str_join(('no neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' rib-in pre-policy retain', ))
                _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_1_neighbor_rib_in_pre_policy_retain_cli
                yield '   '
                yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_1_neighbor_rib_in_pre_policy_retain_cli is missing else l_1_neighbor_rib_in_pre_policy_retain_cli))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'ebgp_multihop')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' ebgp-multihop '
                yield str(environment.getattr(l_1_neighbor, 'ebgp_multihop'))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'ttl_maximum_hops')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' ttl maximum-hops '
                yield str(environment.getattr(l_1_neighbor, 'ttl_maximum_hops'))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'route_reflector_client'), True):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' route-reflector-client\n'
            elif t_6(environment.getattr(l_1_neighbor, 'route_reflector_client'), False):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' route-reflector-client\n'
            if t_6(environment.getattr(l_1_neighbor, 'session_tracker')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' session tracker '
                yield str(environment.getattr(l_1_neighbor, 'session_tracker'))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'timers')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' timers '
                yield str(environment.getattr(l_1_neighbor, 'timers'))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' route-map '
                yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                yield ' in\n'
            if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' route-map '
                yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                yield ' out\n'
            if (t_6(environment.getattr(environment.getattr(l_1_neighbor, 'shared_secret'), 'profile')) and t_6(environment.getattr(environment.getattr(l_1_neighbor, 'shared_secret'), 'hash_algorithm'))):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' password shared-secret profile '
                yield str(environment.getattr(environment.getattr(l_1_neighbor, 'shared_secret'), 'profile'))
                yield ' algorithm '
                yield str(environment.getattr(environment.getattr(l_1_neighbor, 'shared_secret'), 'hash_algorithm'))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'password')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' password 7 '
                yield str(t_2(environment.getattr(l_1_neighbor, 'password'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'enabled'), True):
                pass
                l_1_default_originate_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' default-originate', ))
                _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'route_map')):
                    pass
                    l_1_default_originate_cli = str_join(((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli), ' route-map ', environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'route_map'), ))
                    _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'always'), True):
                    pass
                    l_1_default_originate_cli = str_join(((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli), ' always', ))
                    _loop_vars['default_originate_cli'] = l_1_default_originate_cli
                yield '   '
                yield str((undefined(name='default_originate_cli') if l_1_default_originate_cli is missing else l_1_default_originate_cli))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'send_community'), 'all'):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' send-community\n'
            elif t_6(environment.getattr(l_1_neighbor, 'send_community')):
                pass
                yield '   neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' send-community '
                yield str(environment.getattr(l_1_neighbor, 'send_community'))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'maximum_routes')):
                pass
                l_1_maximum_routes_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' maximum-routes ', environment.getattr(l_1_neighbor, 'maximum_routes'), ))
                _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                if t_6(environment.getattr(l_1_neighbor, 'maximum_routes_warning_limit')):
                    pass
                    l_1_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli), ' warning-limit ', environment.getattr(l_1_neighbor, 'maximum_routes_warning_limit'), ))
                    _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                if t_6(environment.getattr(l_1_neighbor, 'maximum_routes_warning_only'), True):
                    pass
                    l_1_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli), ' warning-only', ))
                    _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                yield '   '
                yield str((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli))
                yield '\n'
            if t_6(environment.getattr(l_1_neighbor, 'missing_policy')):
                pass
                for l_2_direction in ['in', 'out']:
                    l_2_missing_policy_cli = resolve('missing_policy_cli')
                    l_2_dir = l_2_policy = missing
                    _loop_vars = {}
                    pass
                    l_2_dir = str_join(('direction_', l_2_direction, ))
                    _loop_vars['dir'] = l_2_dir
                    l_2_policy = environment.getitem(environment.getattr(l_1_neighbor, 'missing_policy'), (undefined(name='dir') if l_2_dir is missing else l_2_dir))
                    _loop_vars['policy'] = l_2_policy
                    if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'action')):
                        pass
                        l_2_missing_policy_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' missing-policy address-family all', ))
                        _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                        if ((t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_community_list'), True) or t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_prefix_list'), True)) or t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_sub_route_map'), True)):
                            pass
                            l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' include', ))
                            _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_community_list'), True):
                                pass
                                l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' community-list', ))
                                _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_prefix_list'), True):
                                pass
                                l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' prefix-list', ))
                                _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_sub_route_map'), True):
                                pass
                                l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' sub-route-map', ))
                                _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                        l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' direction ', l_2_direction, ' action ', environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'action'), ))
                        _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                        yield '   '
                        yield str((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli))
                        yield '\n'
                l_2_direction = l_2_dir = l_2_policy = l_2_missing_policy_cli = missing
            if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'link_bandwidth'), 'enabled'), True):
                pass
                l_1_link_bandwidth_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' link-bandwidth', ))
                _loop_vars['link_bandwidth_cli'] = l_1_link_bandwidth_cli
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'link_bandwidth'), 'default')):
                    pass
                    l_1_link_bandwidth_cli = str_join(((undefined(name='link_bandwidth_cli') if l_1_link_bandwidth_cli is missing else l_1_link_bandwidth_cli), ' default ', environment.getattr(environment.getattr(l_1_neighbor, 'link_bandwidth'), 'default'), ))
                    _loop_vars['link_bandwidth_cli'] = l_1_link_bandwidth_cli
                yield '   '
                yield str((undefined(name='link_bandwidth_cli') if l_1_link_bandwidth_cli is missing else l_1_link_bandwidth_cli))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as_ingress'), 'enabled'), True):
                pass
                l_1_remove_private_as_ingress_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' remove-private-as ingress', ))
                _loop_vars['remove_private_as_ingress_cli'] = l_1_remove_private_as_ingress_cli
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as_ingress'), 'replace_as'), True):
                    pass
                    l_1_remove_private_as_ingress_cli = str_join(((undefined(name='remove_private_as_ingress_cli') if l_1_remove_private_as_ingress_cli is missing else l_1_remove_private_as_ingress_cli), ' replace-as', ))
                    _loop_vars['remove_private_as_ingress_cli'] = l_1_remove_private_as_ingress_cli
                yield '   '
                yield str((undefined(name='remove_private_as_ingress_cli') if l_1_remove_private_as_ingress_cli is missing else l_1_remove_private_as_ingress_cli))
                yield '\n'
            elif t_6(environment.getattr(environment.getattr(l_1_neighbor, 'remove_private_as_ingress'), 'enabled'), False):
                pass
                yield '   no neighbor '
                yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                yield ' remove-private-as ingress\n'
        l_1_neighbor = l_1_remove_private_as_cli = l_1_allowas_in_cli = l_1_neighbor_rib_in_pre_policy_retain_cli = l_1_hide_passwords = l_1_default_originate_cli = l_1_maximum_routes_cli = l_1_link_bandwidth_cli = l_1_remove_private_as_ingress_cli = missing
        if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'redistribute_internal'), True):
            pass
            yield '   bgp redistribute-internal\n'
        elif t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'bgp'), 'redistribute_internal'), False):
            pass
            yield '   no bgp redistribute-internal\n'
        for l_1_aggregate_address in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'aggregate_addresses'), 'prefix'):
            l_1_aggregate_address_cli = missing
            _loop_vars = {}
            pass
            l_1_aggregate_address_cli = str_join(('aggregate-address ', environment.getattr(l_1_aggregate_address, 'prefix'), ))
            _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_6(environment.getattr(l_1_aggregate_address, 'as_set'), True):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' as-set', ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_6(environment.getattr(l_1_aggregate_address, 'summary_only'), True):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' summary-only', ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_6(environment.getattr(l_1_aggregate_address, 'attribute_map')):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' attribute-map ', environment.getattr(l_1_aggregate_address, 'attribute_map'), ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_6(environment.getattr(l_1_aggregate_address, 'match_map')):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' match-map ', environment.getattr(l_1_aggregate_address, 'match_map'), ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            if t_6(environment.getattr(l_1_aggregate_address, 'advertise_only'), True):
                pass
                l_1_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli), ' advertise-only', ))
                _loop_vars['aggregate_address_cli'] = l_1_aggregate_address_cli
            yield '   '
            yield str((undefined(name='aggregate_address_cli') if l_1_aggregate_address_cli is missing else l_1_aggregate_address_cli))
            yield '\n'
        l_1_aggregate_address = l_1_aggregate_address_cli = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'redistribute')):
            pass
            l_0_redistribute_var = environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'redistribute')
            context.vars['redistribute_var'] = l_0_redistribute_var
            context.exported_vars.add('redistribute_var')
            if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'enabled'), True):
                pass
                l_0_redistribute_conn = 'redistribute connected'
                context.vars['redistribute_conn'] = l_0_redistribute_conn
                context.exported_vars.add('redistribute_conn')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' include leaked', ))
                    context.vars['redistribute_conn'] = l_0_redistribute_conn
                    context.exported_vars.add('redistribute_conn')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'route_map')):
                    pass
                    l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'route_map'), ))
                    context.vars['redistribute_conn'] = l_0_redistribute_conn
                    context.exported_vars.add('redistribute_conn')
                elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'rcf')):
                    pass
                    l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'rcf'), ))
                    context.vars['redistribute_conn'] = l_0_redistribute_conn
                    context.exported_vars.add('redistribute_conn')
                yield '   '
                yield str((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'enabled'), True):
                pass
                l_0_redistribute_isis = 'redistribute isis'
                context.vars['redistribute_isis'] = l_0_redistribute_isis
                context.exported_vars.add('redistribute_isis')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'isis_level')):
                    pass
                    l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'isis_level'), ))
                    context.vars['redistribute_isis'] = l_0_redistribute_isis
                    context.exported_vars.add('redistribute_isis')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' include leaked', ))
                    context.vars['redistribute_isis'] = l_0_redistribute_isis
                    context.exported_vars.add('redistribute_isis')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'route_map')):
                    pass
                    l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'route_map'), ))
                    context.vars['redistribute_isis'] = l_0_redistribute_isis
                    context.exported_vars.add('redistribute_isis')
                elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'rcf')):
                    pass
                    l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'rcf'), ))
                    context.vars['redistribute_isis'] = l_0_redistribute_isis
                    context.exported_vars.add('redistribute_isis')
                yield '   '
                yield str((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'enabled'), True):
                pass
                l_0_redistribute_ospf = 'redistribute ospf'
                context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                context.exported_vars.add('redistribute_ospf')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' include leaked', ))
                    context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                    context.exported_vars.add('redistribute_ospf')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'route_map')):
                    pass
                    l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'route_map'), ))
                    context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                    context.exported_vars.add('redistribute_ospf')
                yield '   '
                yield str((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf))
                yield '\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'enabled'), True):
                pass
                l_0_redistribute_ospf = 'redistribute ospf match internal'
                context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                context.exported_vars.add('redistribute_ospf')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' include leaked', ))
                    context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                    context.exported_vars.add('redistribute_ospf')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'route_map')):
                    pass
                    l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'route_map'), ))
                    context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                    context.exported_vars.add('redistribute_ospf')
                yield '   '
                yield str((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'enabled'), True):
                pass
                l_0_redistribute_ospf_match = 'redistribute ospf match external'
                context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                context.exported_vars.add('redistribute_ospf_match')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' include leaked', ))
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'route_map')):
                    pass
                    l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'route_map'), ))
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                yield '   '
                yield str((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'enabled'), True):
                pass
                l_0_redistribute_ospf_match = 'redistribute ospf match nssa-external'
                context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                context.exported_vars.add('redistribute_ospf_match')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type')):
                    pass
                    l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type'), ))
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' include leaked', ))
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map')):
                    pass
                    l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map'), ))
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                yield '   '
                yield str((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'enabled'), True):
                pass
                l_0_redistribute_ospfv3 = 'redistribute ospfv3'
                context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                context.exported_vars.add('redistribute_ospfv3')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' include leaked', ))
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'route_map')):
                    pass
                    l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'route_map'), ))
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                yield '   '
                yield str((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3))
                yield '\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'enabled'), True):
                pass
                l_0_redistribute_ospfv3 = 'redistribute ospfv3 match internal'
                context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                context.exported_vars.add('redistribute_ospfv3')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' include leaked', ))
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map')):
                    pass
                    l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map'), ))
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                yield '   '
                yield str((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'enabled'), True):
                pass
                l_0_redistribute_ospfv3_match = 'redistribute ospfv3 match external'
                context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                context.exported_vars.add('redistribute_ospfv3_match')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' include leaked', ))
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'route_map')):
                    pass
                    l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'route_map'), ))
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                yield '   '
                yield str((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                pass
                l_0_redistribute_ospfv3_match = 'redistribute ospfv3 match nssa-external'
                context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                context.exported_vars.add('redistribute_ospfv3_match')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type')):
                    pass
                    l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type'), ))
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' include leaked', ))
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                    pass
                    l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                yield '   '
                yield str((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'enabled'), True):
                pass
                l_0_redistribute_static = 'redistribute static'
                context.vars['redistribute_static'] = l_0_redistribute_static
                context.exported_vars.add('redistribute_static')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'include_leaked'), True):
                    pass
                    l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' include leaked', ))
                    context.vars['redistribute_static'] = l_0_redistribute_static
                    context.exported_vars.add('redistribute_static')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'route_map')):
                    pass
                    l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'route_map'), ))
                    context.vars['redistribute_static'] = l_0_redistribute_static
                    context.exported_vars.add('redistribute_static')
                elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'rcf')):
                    pass
                    l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'rcf'), ))
                    context.vars['redistribute_static'] = l_0_redistribute_static
                    context.exported_vars.add('redistribute_static')
                yield '   '
                yield str((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'rip'), 'enabled'), True):
                pass
                l_0_redistribute_rip = 'redistribute rip'
                context.vars['redistribute_rip'] = l_0_redistribute_rip
                context.exported_vars.add('redistribute_rip')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'rip'), 'route_map')):
                    pass
                    l_0_redistribute_rip = str_join(((undefined(name='redistribute_rip') if l_0_redistribute_rip is missing else l_0_redistribute_rip), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'rip'), 'route_map'), ))
                    context.vars['redistribute_rip'] = l_0_redistribute_rip
                    context.exported_vars.add('redistribute_rip')
                yield '   '
                yield str((undefined(name='redistribute_rip') if l_0_redistribute_rip is missing else l_0_redistribute_rip))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'enabled'), True):
                pass
                l_0_redistribute_host = 'redistribute attached-host'
                context.vars['redistribute_host'] = l_0_redistribute_host
                context.exported_vars.add('redistribute_host')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'route_map')):
                    pass
                    l_0_redistribute_host = str_join(((undefined(name='redistribute_host') if l_0_redistribute_host is missing else l_0_redistribute_host), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'route_map'), ))
                    context.vars['redistribute_host'] = l_0_redistribute_host
                    context.exported_vars.add('redistribute_host')
                yield '   '
                yield str((undefined(name='redistribute_host') if l_0_redistribute_host is missing else l_0_redistribute_host))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'enabled'), True):
                pass
                l_0_redistribute_dynamic = 'redistribute dynamic'
                context.vars['redistribute_dynamic'] = l_0_redistribute_dynamic
                context.exported_vars.add('redistribute_dynamic')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'route_map')):
                    pass
                    l_0_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_0_redistribute_dynamic is missing else l_0_redistribute_dynamic), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'route_map'), ))
                    context.vars['redistribute_dynamic'] = l_0_redistribute_dynamic
                    context.exported_vars.add('redistribute_dynamic')
                elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'rcf')):
                    pass
                    l_0_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_0_redistribute_dynamic is missing else l_0_redistribute_dynamic), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'rcf'), ))
                    context.vars['redistribute_dynamic'] = l_0_redistribute_dynamic
                    context.exported_vars.add('redistribute_dynamic')
                yield '   '
                yield str((undefined(name='redistribute_dynamic') if l_0_redistribute_dynamic is missing else l_0_redistribute_dynamic))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'bgp'), 'enabled'), True):
                pass
                l_0_redistribute_bgp = 'redistribute bgp leaked'
                context.vars['redistribute_bgp'] = l_0_redistribute_bgp
                context.exported_vars.add('redistribute_bgp')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'bgp'), 'route_map')):
                    pass
                    l_0_redistribute_bgp = str_join(((undefined(name='redistribute_bgp') if l_0_redistribute_bgp is missing else l_0_redistribute_bgp), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'bgp'), 'route_map'), ))
                    context.vars['redistribute_bgp'] = l_0_redistribute_bgp
                    context.exported_vars.add('redistribute_bgp')
                yield '   '
                yield str((undefined(name='redistribute_bgp') if l_0_redistribute_bgp is missing else l_0_redistribute_bgp))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'user'), 'enabled'), True):
                pass
                l_0_redistribute_user = 'redistribute user'
                context.vars['redistribute_user'] = l_0_redistribute_user
                context.exported_vars.add('redistribute_user')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'user'), 'rcf')):
                    pass
                    l_0_redistribute_user = str_join(((undefined(name='redistribute_user') if l_0_redistribute_user is missing else l_0_redistribute_user), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'user'), 'rcf'), ))
                    context.vars['redistribute_user'] = l_0_redistribute_user
                    context.exported_vars.add('redistribute_user')
                yield '   '
                yield str((undefined(name='redistribute_user') if l_0_redistribute_user is missing else l_0_redistribute_user))
                yield '\n'
        elif t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'redistribute_routes')):
            pass
            for l_1_redistribute_route in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'redistribute_routes'), 'source_protocol'):
                l_1_redistribute_route_cli = missing
                _loop_vars = {}
                pass
                l_1_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_1_redistribute_route, 'source_protocol'), ))
                _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                if (environment.getattr(l_1_redistribute_route, 'source_protocol') in ['ospf', 'ospfv3']):
                    pass
                    if t_6(environment.getattr(l_1_redistribute_route, 'ospf_route_type')):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' match ', environment.getattr(l_1_redistribute_route, 'ospf_route_type'), ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                if (environment.getattr(l_1_redistribute_route, 'source_protocol') == 'bgp'):
                    pass
                    l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' leaked', ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                elif t_6(environment.getattr(l_1_redistribute_route, 'include_leaked'), True):
                    pass
                    l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' include leaked', ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                if t_6(environment.getattr(l_1_redistribute_route, 'route_map')):
                    pass
                    l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' route-map ', environment.getattr(l_1_redistribute_route, 'route_map'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                elif (environment.getattr(l_1_redistribute_route, 'source_protocol') in ['connected', 'static', 'isis', 'user', 'dynamic']):
                    pass
                    if t_6(environment.getattr(l_1_redistribute_route, 'rcf')):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' rcf ', environment.getattr(l_1_redistribute_route, 'rcf'), ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                yield '   '
                yield str((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli))
                yield '\n'
            l_1_redistribute_route = l_1_redistribute_route_cli = missing
        for l_1_neighbor_interface in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'neighbor_interfaces'), 'name'):
            _loop_vars = {}
            pass
            if (t_6(environment.getattr(l_1_neighbor_interface, 'peer_group')) and t_6(environment.getattr(l_1_neighbor_interface, 'remote_as'))):
                pass
                yield '   neighbor interface '
                yield str(environment.getattr(l_1_neighbor_interface, 'name'))
                yield ' peer-group '
                yield str(environment.getattr(l_1_neighbor_interface, 'peer_group'))
                yield ' remote-as '
                yield str(environment.getattr(l_1_neighbor_interface, 'remote_as'))
                yield '\n'
            elif (t_6(environment.getattr(l_1_neighbor_interface, 'peer_group')) and t_6(environment.getattr(l_1_neighbor_interface, 'peer_filter'))):
                pass
                yield '   neighbor interface '
                yield str(environment.getattr(l_1_neighbor_interface, 'name'))
                yield ' peer-group '
                yield str(environment.getattr(l_1_neighbor_interface, 'peer_group'))
                yield ' peer-filter '
                yield str(environment.getattr(l_1_neighbor_interface, 'peer_filter'))
                yield '\n'
        l_1_neighbor_interface = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vlans')):
            pass
            for l_1_vlan in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vlans')):
                _loop_vars = {}
                pass
                yield '   !\n   vlan '
                yield str(environment.getattr(l_1_vlan, 'id'))
                yield '\n'
                if t_6(environment.getattr(l_1_vlan, 'rd')):
                    pass
                    yield '      rd '
                    yield str(environment.getattr(l_1_vlan, 'rd'))
                    yield '\n'
                if (t_6(environment.getattr(environment.getattr(l_1_vlan, 'rd_evpn_domain'), 'domain')) and t_6(environment.getattr(environment.getattr(l_1_vlan, 'rd_evpn_domain'), 'rd'))):
                    pass
                    yield '      rd evpn domain '
                    yield str(environment.getattr(environment.getattr(l_1_vlan, 'rd_evpn_domain'), 'domain'))
                    yield ' '
                    yield str(environment.getattr(environment.getattr(l_1_vlan, 'rd_evpn_domain'), 'rd'))
                    yield '\n'
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'both')):
                    _loop_vars = {}
                    pass
                    yield '      route-target both '
                    yield str(l_2_route_target)
                    yield '\n'
                l_2_route_target = missing
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'import')):
                    _loop_vars = {}
                    pass
                    yield '      route-target import '
                    yield str(l_2_route_target)
                    yield '\n'
                l_2_route_target = missing
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'export')):
                    _loop_vars = {}
                    pass
                    yield '      route-target export '
                    yield str(l_2_route_target)
                    yield '\n'
                l_2_route_target = missing
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'import_evpn_domains')):
                    _loop_vars = {}
                    pass
                    yield '      route-target import evpn domain '
                    yield str(environment.getattr(l_2_route_target, 'domain'))
                    yield ' '
                    yield str(environment.getattr(l_2_route_target, 'route_target'))
                    yield '\n'
                l_2_route_target = missing
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'export_evpn_domains')):
                    _loop_vars = {}
                    pass
                    yield '      route-target export evpn domain '
                    yield str(environment.getattr(l_2_route_target, 'domain'))
                    yield ' '
                    yield str(environment.getattr(l_2_route_target, 'route_target'))
                    yield '\n'
                l_2_route_target = missing
                for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan, 'route_targets'), 'import_export_evpn_domains')):
                    _loop_vars = {}
                    pass
                    yield '      route-target import export evpn domain '
                    yield str(environment.getattr(l_2_route_target, 'domain'))
                    yield ' '
                    yield str(environment.getattr(l_2_route_target, 'route_target'))
                    yield '\n'
                l_2_route_target = missing
                for l_2_redistribute_route in t_3(environment.getattr(l_1_vlan, 'redistribute_routes')):
                    _loop_vars = {}
                    pass
                    yield '      redistribute '
                    yield str(l_2_redistribute_route)
                    yield '\n'
                l_2_redistribute_route = missing
                for l_2_no_redistribute_route in t_3(environment.getattr(l_1_vlan, 'no_redistribute_routes')):
                    _loop_vars = {}
                    pass
                    yield '      no redistribute '
                    yield str(l_2_no_redistribute_route)
                    yield '\n'
                l_2_no_redistribute_route = missing
                if t_6(environment.getattr(l_1_vlan, 'eos_cli')):
                    pass
                    yield '      !\n      '
                    yield str(t_4(environment.getattr(l_1_vlan, 'eos_cli'), 6, False))
                    yield '\n'
            l_1_vlan = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vpws')):
            pass
            for l_1_vpws_service in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vpws'), 'name'):
                _loop_vars = {}
                pass
                yield '   !\n'
                if t_6(environment.getattr(l_1_vpws_service, 'name')):
                    pass
                    yield '   vpws '
                    yield str(environment.getattr(l_1_vpws_service, 'name'))
                    yield '\n'
                    if t_6(environment.getattr(l_1_vpws_service, 'rd')):
                        pass
                        yield '      rd '
                        yield str(environment.getattr(l_1_vpws_service, 'rd'))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(l_1_vpws_service, 'route_targets'), 'import_export')):
                        pass
                        yield '      route-target import export evpn '
                        yield str(environment.getattr(environment.getattr(l_1_vpws_service, 'route_targets'), 'import_export'))
                        yield '\n'
                    if t_6(environment.getattr(l_1_vpws_service, 'mpls_control_word'), True):
                        pass
                        yield '      mpls control-word\n'
                    if t_6(environment.getattr(l_1_vpws_service, 'label_flow'), True):
                        pass
                        yield '      label flow\n'
                    if t_6(environment.getattr(l_1_vpws_service, 'mtu')):
                        pass
                        yield '      mtu '
                        yield str(environment.getattr(l_1_vpws_service, 'mtu'))
                        yield '\n'
                    for l_2_pw in t_3(environment.getattr(l_1_vpws_service, 'pseudowires'), 'name'):
                        _loop_vars = {}
                        pass
                        if ((t_6(environment.getattr(l_2_pw, 'name')) and t_6(environment.getattr(l_2_pw, 'id_local'))) and t_6(environment.getattr(l_2_pw, 'id_remote'))):
                            pass
                            yield '      !\n      pseudowire '
                            yield str(environment.getattr(l_2_pw, 'name'))
                            yield '\n         evpn vpws id local '
                            yield str(environment.getattr(l_2_pw, 'id_local'))
                            yield ' remote '
                            yield str(environment.getattr(l_2_pw, 'id_remote'))
                            yield '\n'
                    l_2_pw = missing
            l_1_vpws_service = missing
        for l_1_vlan_aware_bundle in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vlan_aware_bundles'), 'name'):
            _loop_vars = {}
            pass
            yield '   !\n   vlan-aware-bundle '
            yield str(environment.getattr(l_1_vlan_aware_bundle, 'name'))
            yield '\n'
            if t_6(environment.getattr(l_1_vlan_aware_bundle, 'rd')):
                pass
                yield '      rd '
                yield str(environment.getattr(l_1_vlan_aware_bundle, 'rd'))
                yield '\n'
            if (t_6(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'rd_evpn_domain'), 'domain')) and t_6(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'rd_evpn_domain'), 'rd'))):
                pass
                yield '      rd evpn domain '
                yield str(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'rd_evpn_domain'), 'domain'))
                yield ' '
                yield str(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'rd_evpn_domain'), 'rd'))
                yield '\n'
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'both')):
                _loop_vars = {}
                pass
                yield '      route-target both '
                yield str(l_2_route_target)
                yield '\n'
            l_2_route_target = missing
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'import')):
                _loop_vars = {}
                pass
                yield '      route-target import '
                yield str(l_2_route_target)
                yield '\n'
            l_2_route_target = missing
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'export')):
                _loop_vars = {}
                pass
                yield '      route-target export '
                yield str(l_2_route_target)
                yield '\n'
            l_2_route_target = missing
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'import_evpn_domains')):
                _loop_vars = {}
                pass
                yield '      route-target import evpn domain '
                yield str(environment.getattr(l_2_route_target, 'domain'))
                yield ' '
                yield str(environment.getattr(l_2_route_target, 'route_target'))
                yield '\n'
            l_2_route_target = missing
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'export_evpn_domains')):
                _loop_vars = {}
                pass
                yield '      route-target export evpn domain '
                yield str(environment.getattr(l_2_route_target, 'domain'))
                yield ' '
                yield str(environment.getattr(l_2_route_target, 'route_target'))
                yield '\n'
            l_2_route_target = missing
            for l_2_route_target in t_3(environment.getattr(environment.getattr(l_1_vlan_aware_bundle, 'route_targets'), 'import_export_evpn_domains')):
                _loop_vars = {}
                pass
                yield '      route-target import export evpn domain '
                yield str(environment.getattr(l_2_route_target, 'domain'))
                yield ' '
                yield str(environment.getattr(l_2_route_target, 'route_target'))
                yield '\n'
            l_2_route_target = missing
            for l_2_redistribute_route in t_3(environment.getattr(l_1_vlan_aware_bundle, 'redistribute_routes')):
                _loop_vars = {}
                pass
                yield '      redistribute '
                yield str(l_2_redistribute_route)
                yield '\n'
            l_2_redistribute_route = missing
            for l_2_no_redistribute_route in t_3(environment.getattr(l_1_vlan_aware_bundle, 'no_redistribute_routes')):
                _loop_vars = {}
                pass
                yield '      no redistribute '
                yield str(l_2_no_redistribute_route)
                yield '\n'
            l_2_no_redistribute_route = missing
            yield '      vlan '
            yield str(environment.getattr(l_1_vlan_aware_bundle, 'vlan'))
            yield '\n'
            if t_6(environment.getattr(l_1_vlan_aware_bundle, 'eos_cli')):
                pass
                yield '      !\n      '
                yield str(t_4(environment.getattr(l_1_vlan_aware_bundle, 'eos_cli'), 6, False))
                yield '\n'
        l_1_vlan_aware_bundle = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn')):
            pass
            yield '   !\n   address-family evpn\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'route'), 'export_ethernet_segment_ip_mass_withdraw'), True):
                pass
                yield '      route export ethernet-segment ip mass-withdraw\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'route'), 'import_ethernet_segment_ip_mass_withdraw'), True):
                pass
                yield '      route import ethernet-segment ip mass-withdraw\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp'), 'additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp_additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp'), 'additional_paths'), 'send')):
                pass
                if (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp'), 'additional_paths'), 'send') == 'disabled'):
                    pass
                    yield '      no bgp additional-paths send\n'
                elif (t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp'), 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp'), 'additional_paths'), 'send') == 'ecmp')):
                    pass
                    yield '      bgp additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp'), 'additional_paths'), 'send_limit'))
                    yield '\n'
                elif (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp'), 'additional_paths'), 'send') == 'limit'):
                    pass
                    if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp'), 'additional_paths'), 'send_limit')):
                        pass
                        yield '      bgp additional-paths send limit '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp'), 'additional_paths'), 'send_limit'))
                        yield '\n'
                else:
                    pass
                    yield '      bgp additional-paths send '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp'), 'additional_paths'), 'send'))
                    yield '\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp_additional_paths'), 'send'), 'any'), True):
                pass
                yield '      bgp additional-paths send any\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp_additional_paths'), 'send'), 'backup'), True):
                pass
                yield '      bgp additional-paths send backup\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp_additional_paths'), 'send'), 'ecmp'), True):
                pass
                yield '      bgp additional-paths send ecmp\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp_additional_paths'), 'send'), 'ecmp_limit')):
                pass
                yield '      bgp additional-paths send ecmp limit '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp_additional_paths'), 'send'), 'ecmp_limit'))
                yield '\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp_additional_paths'), 'send'), 'limit')):
                pass
                yield '      bgp additional-paths send limit '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'bgp_additional_paths'), 'send'), 'limit'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'next_hop_unchanged'), True):
                pass
                yield '      bgp next-hop-unchanged\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'encapsulation')):
                pass
                l_0_encapsulation_cli = str_join(('neighbor default encapsulation ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'encapsulation'), ))
                context.vars['encapsulation_cli'] = l_0_encapsulation_cli
                context.exported_vars.add('encapsulation_cli')
                if (t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'encapsulation'), 'mpls') and t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'next_hop_self_source_interface'))):
                    pass
                    l_0_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_0_encapsulation_cli is missing else l_0_encapsulation_cli), ' next-hop-self source-interface ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'next_hop_self_source_interface'), ))
                    context.vars['encapsulation_cli'] = l_0_encapsulation_cli
                    context.exported_vars.add('encapsulation_cli')
                yield '      '
                yield str((undefined(name='encapsulation_cli') if l_0_encapsulation_cli is missing else l_0_encapsulation_cli))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'next_hop_mpls_resolution_ribs')):
                pass
                l_0_evpn_mpls_resolution_ribs = []
                context.vars['evpn_mpls_resolution_ribs'] = l_0_evpn_mpls_resolution_ribs
                context.exported_vars.add('evpn_mpls_resolution_ribs')
                for l_1_rib in environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'next_hop_mpls_resolution_ribs'):
                    _loop_vars = {}
                    pass
                    if t_6(environment.getattr(l_1_rib, 'rib_type'), 'tunnel-rib-colored'):
                        pass
                        context.call(environment.getattr((undefined(name='evpn_mpls_resolution_ribs') if l_0_evpn_mpls_resolution_ribs is missing else l_0_evpn_mpls_resolution_ribs), 'append'), 'tunnel-rib colored system-colored-tunnel-rib', _loop_vars=_loop_vars)
                    elif (t_6(environment.getattr(l_1_rib, 'rib_type'), 'tunnel-rib') and t_6(environment.getattr(l_1_rib, 'rib_name'))):
                        pass
                        context.call(environment.getattr((undefined(name='evpn_mpls_resolution_ribs') if l_0_evpn_mpls_resolution_ribs is missing else l_0_evpn_mpls_resolution_ribs), 'append'), str_join(('tunnel-rib ', environment.getattr(l_1_rib, 'rib_name'), )), _loop_vars=_loop_vars)
                    elif t_6(environment.getattr(l_1_rib, 'rib_type')):
                        pass
                        context.call(environment.getattr((undefined(name='evpn_mpls_resolution_ribs') if l_0_evpn_mpls_resolution_ribs is missing else l_0_evpn_mpls_resolution_ribs), 'append'), environment.getattr(l_1_rib, 'rib_type'), _loop_vars=_loop_vars)
                l_1_rib = missing
                if (undefined(name='evpn_mpls_resolution_ribs') if l_0_evpn_mpls_resolution_ribs is missing else l_0_evpn_mpls_resolution_ribs):
                    pass
                    yield '      next-hop mpls resolution ribs '
                    yield str(t_5(context.eval_ctx, (undefined(name='evpn_mpls_resolution_ribs') if l_0_evpn_mpls_resolution_ribs is missing else l_0_evpn_mpls_resolution_ribs), ' '))
                    yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'peer_groups'), 'name'):
                l_1_peer_group_default_route_cli = resolve('peer_group_default_route_cli')
                l_1_encapsulation_cli = l_0_encapsulation_cli
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_peer_group, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_peer_group, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer_group, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_peer_group, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'enabled'), True):
                    pass
                    l_1_peer_group_default_route_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' default-route', ))
                    _loop_vars['peer_group_default_route_cli'] = l_1_peer_group_default_route_cli
                    if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'rcf')):
                        pass
                        l_1_peer_group_default_route_cli = str_join(((undefined(name='peer_group_default_route_cli') if l_1_peer_group_default_route_cli is missing else l_1_peer_group_default_route_cli), ' rcf ', environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'rcf'), ))
                        _loop_vars['peer_group_default_route_cli'] = l_1_peer_group_default_route_cli
                    elif t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'route_map')):
                        pass
                        l_1_peer_group_default_route_cli = str_join(((undefined(name='peer_group_default_route_cli') if l_1_peer_group_default_route_cli is missing else l_1_peer_group_default_route_cli), ' route-map ', environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'route_map'), ))
                        _loop_vars['peer_group_default_route_cli'] = l_1_peer_group_default_route_cli
                    yield '      '
                    yield str((undefined(name='peer_group_default_route_cli') if l_1_peer_group_default_route_cli is missing else l_1_peer_group_default_route_cli))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' additional-paths send\n'
                    elif (t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'ecmp')):
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' additional-paths send ecmp limit '
                        yield str(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit'))
                        yield '\n'
                    elif (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'limit'):
                        pass
                        if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit')):
                            pass
                            yield '      neighbor '
                            yield str(environment.getattr(l_1_peer_group, 'name'))
                            yield ' additional-paths send limit '
                            yield str(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit'))
                            yield '\n'
                    else:
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' additional-paths send '
                        yield str(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'))
                        yield '\n'
                if t_6(environment.getattr(l_1_peer_group, 'encapsulation')):
                    pass
                    l_1_encapsulation_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' encapsulation ', environment.getattr(l_1_peer_group, 'encapsulation'), ))
                    _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                    if ((environment.getattr(l_1_peer_group, 'encapsulation') == 'mpls') and t_6(environment.getattr(l_1_peer_group, 'next_hop_self_source_interface'))):
                        pass
                        l_1_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli), ' next-hop-self source-interface ', environment.getattr(l_1_peer_group, 'next_hop_self_source_interface'), ))
                        _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                    yield '      '
                    yield str((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer_group, 'domain_remote'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' domain remote\n'
            l_1_peer_group = l_1_peer_group_default_route_cli = l_1_encapsulation_cli = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbors'), 'ip_address'):
                l_1_neighbor_default_route_cli = resolve('neighbor_default_route_cli')
                l_1_encapsulation_cli = l_0_encapsulation_cli
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'enabled'), True):
                    pass
                    l_1_neighbor_default_route_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' default-route', ))
                    _loop_vars['neighbor_default_route_cli'] = l_1_neighbor_default_route_cli
                    if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'rcf')):
                        pass
                        l_1_neighbor_default_route_cli = str_join(((undefined(name='neighbor_default_route_cli') if l_1_neighbor_default_route_cli is missing else l_1_neighbor_default_route_cli), ' rcf ', environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'rcf'), ))
                        _loop_vars['neighbor_default_route_cli'] = l_1_neighbor_default_route_cli
                    elif t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'route_map')):
                        pass
                        l_1_neighbor_default_route_cli = str_join(((undefined(name='neighbor_default_route_cli') if l_1_neighbor_default_route_cli is missing else l_1_neighbor_default_route_cli), ' route-map ', environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'route_map'), ))
                        _loop_vars['neighbor_default_route_cli'] = l_1_neighbor_default_route_cli
                    yield '      '
                    yield str((undefined(name='neighbor_default_route_cli') if l_1_neighbor_default_route_cli is missing else l_1_neighbor_default_route_cli))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send\n'
                    elif (t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'ecmp')):
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send ecmp limit '
                        yield str(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit'))
                        yield '\n'
                    elif (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'limit'):
                        pass
                        if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit')):
                            pass
                            yield '      neighbor '
                            yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                            yield ' additional-paths send limit '
                            yield str(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit'))
                            yield '\n'
                    else:
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send '
                        yield str(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'))
                        yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'encapsulation')):
                    pass
                    l_1_encapsulation_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' encapsulation ', environment.getattr(l_1_neighbor, 'encapsulation'), ))
                    _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                    if ((environment.getattr(l_1_neighbor, 'encapsulation') == 'mpls') and t_6(environment.getattr(l_1_neighbor, 'next_hop_self_source_interface'))):
                        pass
                        l_1_encapsulation_cli = str_join(((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli), ' next-hop-self source-interface ', environment.getattr(l_1_neighbor, 'next_hop_self_source_interface'), ))
                        _loop_vars['encapsulation_cli'] = l_1_encapsulation_cli
                    yield '      '
                    yield str((undefined(name='encapsulation_cli') if l_1_encapsulation_cli is missing else l_1_encapsulation_cli))
                    yield '\n'
            l_1_neighbor = l_1_neighbor_default_route_cli = l_1_encapsulation_cli = missing
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'domain_identifier')):
                pass
                yield '      domain identifier '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'domain_identifier'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'domain_identifier_remote')):
                pass
                yield '      domain identifier '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'domain_identifier_remote'))
                yield ' remote\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'next_hop'), 'resolution_disabled'), True):
                pass
                yield '      next-hop resolution disabled\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'route'), 'import_match_failure_action'), 'discard'):
                pass
                yield '      route import match-failure action discard\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'next_hop_self_received_evpn_routes'), 'enable'), True):
                pass
                l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli = 'neighbor default next-hop-self received-evpn-routes route-type ip-prefix'
                context.vars['evpn_neighbor_default_nhs_received_evpn_routes_cli'] = l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli
                context.exported_vars.add('evpn_neighbor_default_nhs_received_evpn_routes_cli')
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'neighbor_default'), 'next_hop_self_received_evpn_routes'), 'inter_domain'), True):
                    pass
                    l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli = str_join(((undefined(name='evpn_neighbor_default_nhs_received_evpn_routes_cli') if l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli is missing else l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli), ' inter-domain', ))
                    context.vars['evpn_neighbor_default_nhs_received_evpn_routes_cli'] = l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli
                    context.exported_vars.add('evpn_neighbor_default_nhs_received_evpn_routes_cli')
                yield '      '
                yield str((undefined(name='evpn_neighbor_default_nhs_received_evpn_routes_cli') if l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli is missing else l_0_evpn_neighbor_default_nhs_received_evpn_routes_cli))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'enabled'), False):
                pass
                yield '      no host-flap detection\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'enabled'), True):
                pass
                l_0_hostflap_detection_cli = ''
                context.vars['hostflap_detection_cli'] = l_0_hostflap_detection_cli
                context.exported_vars.add('hostflap_detection_cli')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'window')):
                    pass
                    l_0_hostflap_detection_cli = str_join(((undefined(name='hostflap_detection_cli') if l_0_hostflap_detection_cli is missing else l_0_hostflap_detection_cli), ' window ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'window'), ))
                    context.vars['hostflap_detection_cli'] = l_0_hostflap_detection_cli
                    context.exported_vars.add('hostflap_detection_cli')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'threshold')):
                    pass
                    l_0_hostflap_detection_cli = str_join(((undefined(name='hostflap_detection_cli') if l_0_hostflap_detection_cli is missing else l_0_hostflap_detection_cli), ' threshold ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'threshold'), ))
                    context.vars['hostflap_detection_cli'] = l_0_hostflap_detection_cli
                    context.exported_vars.add('hostflap_detection_cli')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'expiry_timeout')):
                    pass
                    l_0_hostflap_detection_cli = str_join(((undefined(name='hostflap_detection_cli') if l_0_hostflap_detection_cli is missing else l_0_hostflap_detection_cli), ' expiry timeout ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_hostflap_detection'), 'expiry_timeout'), ' seconds', ))
                    context.vars['hostflap_detection_cli'] = l_0_hostflap_detection_cli
                    context.exported_vars.add('hostflap_detection_cli')
                if ((undefined(name='hostflap_detection_cli') if l_0_hostflap_detection_cli is missing else l_0_hostflap_detection_cli) != ''):
                    pass
                    yield '      host-flap detection'
                    yield str((undefined(name='hostflap_detection_cli') if l_0_hostflap_detection_cli is missing else l_0_hostflap_detection_cli))
                    yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'layer_2_fec_in_place_update'), 'enabled'), True):
                pass
                l_0_layer2_cli = 'layer-2 fec in-place update'
                context.vars['layer2_cli'] = l_0_layer2_cli
                context.exported_vars.add('layer2_cli')
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'layer_2_fec_in_place_update'), 'timeout')):
                    pass
                    l_0_layer2_cli = str_join(((undefined(name='layer2_cli') if l_0_layer2_cli is missing else l_0_layer2_cli), ' timeout ', environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'layer_2_fec_in_place_update'), 'timeout'), ' seconds', ))
                    context.vars['layer2_cli'] = l_0_layer2_cli
                    context.exported_vars.add('layer2_cli')
                yield '      '
                yield str((undefined(name='layer2_cli') if l_0_layer2_cli is missing else l_0_layer2_cli))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'route'), 'import_overlay_index_gateway'), True):
                pass
                yield '      route import overlay-index gateway\n'
            for l_1_segment in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_evpn'), 'evpn_ethernet_segment'), 'domain'):
                _loop_vars = {}
                pass
                yield '      !\n      evpn ethernet-segment domain '
                yield str(environment.getattr(l_1_segment, 'domain'))
                yield '\n'
                if t_6(environment.getattr(l_1_segment, 'identifier')):
                    pass
                    yield '         identifier '
                    yield str(environment.getattr(l_1_segment, 'identifier'))
                    yield '\n'
                if t_6(environment.getattr(l_1_segment, 'route_target_import')):
                    pass
                    yield '         route-target import '
                    yield str(environment.getattr(l_1_segment, 'route_target_import'))
                    yield '\n'
            l_1_segment = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4')):
            pass
            yield '   !\n   address-family flow-spec ipv4\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                pass
                yield '      bgp missing-policy direction in action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                pass
                yield '      bgp missing-policy direction out action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv4'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
            l_1_neighbor = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6')):
            pass
            yield '   !\n   address-family flow-spec ipv6\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                pass
                yield '      bgp missing-policy direction in action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                pass
                yield '      bgp missing-policy direction out action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_flow_spec_ipv6'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
            l_1_neighbor = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4')):
            pass
            yield '   !\n   address-family ipv4\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'install'), True):
                pass
                yield '      bgp additional-paths install\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'install_ecmp_primary'), True):
                pass
                yield '      bgp additional-paths install ecmp-primary\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send')):
                pass
                if (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send') == 'disabled'):
                    pass
                    yield '      no bgp additional-paths send\n'
                elif (t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send') == 'ecmp')):
                    pass
                    yield '      bgp additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send_limit'))
                    yield '\n'
                elif (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send') == 'limit'):
                    pass
                    if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send_limit')):
                        pass
                        yield '      bgp additional-paths send limit '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send_limit'))
                        yield '\n'
                else:
                    pass
                    yield '      bgp additional-paths send '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send'))
                    yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'peer_groups'), 'name'):
                l_1_neighbor_default_originate_cli = resolve('neighbor_default_originate_cli')
                l_1_add_path_cli = resolve('add_path_cli')
                l_1_nexthop_v6_cli = resolve('nexthop_v6_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_peer_group, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_peer_group, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer_group, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_peer_group, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer_group, 'prefix_list_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_peer_group, 'prefix_list_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer_group, 'prefix_list_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_peer_group, 'prefix_list_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_peer_group, 'default_originate')):
                    pass
                    l_1_neighbor_default_originate_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' default-originate', ))
                    _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'route_map')):
                        pass
                        l_1_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli), ' route-map ', environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'route_map'), ))
                        _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_originate'), 'always'), True):
                        pass
                        l_1_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli), ' always', ))
                        _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    yield '      '
                    yield str((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' additional-paths send\n'
                    else:
                        pass
                        if (t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'ecmp')):
                            pass
                            l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' additional-paths send ecmp limit ', environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        elif (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'limit'):
                            pass
                            if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit')):
                                pass
                                l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' additional-paths send limit ', environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit'), ))
                                _loop_vars['add_path_cli'] = l_1_add_path_cli
                        else:
                            pass
                            l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' additional-paths send ', environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        if (t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'prefix_list')) and t_6((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli))):
                            pass
                            l_1_add_path_cli = str_join(((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli), ' prefix-list ', environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'prefix_list'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        if t_6((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli)):
                            pass
                            yield '      '
                            yield str((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli))
                            yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'next_hop'), 'address_family_ipv6'), 'enabled'), True):
                    pass
                    l_1_nexthop_v6_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' next-hop address-family ipv6', ))
                    _loop_vars['nexthop_v6_cli'] = l_1_nexthop_v6_cli
                    if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_peer_group, 'next_hop'), 'address_family_ipv6'), 'originate'), True):
                        pass
                        l_1_nexthop_v6_cli = str_join(((undefined(name='nexthop_v6_cli') if l_1_nexthop_v6_cli is missing else l_1_nexthop_v6_cli), ' originate', ))
                        _loop_vars['nexthop_v6_cli'] = l_1_nexthop_v6_cli
                    yield '      '
                    yield str((undefined(name='nexthop_v6_cli') if l_1_nexthop_v6_cli is missing else l_1_nexthop_v6_cli))
                    yield '\n'
            l_1_peer_group = l_1_neighbor_default_originate_cli = l_1_add_path_cli = l_1_nexthop_v6_cli = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'neighbors'), 'ip_address'):
                l_1_neighbor_default_originate_cli = resolve('neighbor_default_originate_cli')
                l_1_add_path_cli = resolve('add_path_cli')
                l_1_ipv6_originate_cli = resolve('ipv6_originate_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'prefix_list_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_neighbor, 'prefix_list_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'prefix_list_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_neighbor, 'prefix_list_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_neighbor, 'default_originate')):
                    pass
                    l_1_neighbor_default_originate_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' default-originate', ))
                    _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'route_map')):
                        pass
                        l_1_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli), ' route-map ', environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'route_map'), ))
                        _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_originate'), 'always'), True):
                        pass
                        l_1_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli), ' always', ))
                        _loop_vars['neighbor_default_originate_cli'] = l_1_neighbor_default_originate_cli
                    yield '      '
                    yield str((undefined(name='neighbor_default_originate_cli') if l_1_neighbor_default_originate_cli is missing else l_1_neighbor_default_originate_cli))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send\n'
                    else:
                        pass
                        if (t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'ecmp')):
                            pass
                            l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' additional-paths send ecmp limit ', environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        elif (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'limit'):
                            pass
                            if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit')):
                                pass
                                l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' additional-paths send limit ', environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit'), ))
                                _loop_vars['add_path_cli'] = l_1_add_path_cli
                        else:
                            pass
                            l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' additional-paths send ', environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'prefix_list')):
                            pass
                            l_1_add_path_cli = str_join(((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli), ' prefix-list ', environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'prefix_list'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        if t_6((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli)):
                            pass
                            yield '      '
                            yield str((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli))
                            yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_neighbor, 'next_hop'), 'address_family_ipv6'), 'enabled')):
                    pass
                    if environment.getattr(environment.getattr(environment.getattr(l_1_neighbor, 'next_hop'), 'address_family_ipv6'), 'enabled'):
                        pass
                        l_1_ipv6_originate_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' next-hop address-family ipv6', ))
                        _loop_vars['ipv6_originate_cli'] = l_1_ipv6_originate_cli
                        if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_neighbor, 'next_hop'), 'address_family_ipv6'), 'originate'), True):
                            pass
                            l_1_ipv6_originate_cli = str_join(((undefined(name='ipv6_originate_cli') if l_1_ipv6_originate_cli is missing else l_1_ipv6_originate_cli), ' originate', ))
                            _loop_vars['ipv6_originate_cli'] = l_1_ipv6_originate_cli
                        yield '      '
                        yield str((undefined(name='ipv6_originate_cli') if l_1_ipv6_originate_cli is missing else l_1_ipv6_originate_cli))
                        yield '\n'
                    else:
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' next-hop address-family ipv6\n'
            l_1_neighbor = l_1_neighbor_default_originate_cli = l_1_add_path_cli = l_1_ipv6_originate_cli = missing
            for l_1_network in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'networks'), 'prefix'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_network, 'route_map')):
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_1_network, 'prefix'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_network, 'route_map'))
                    yield '\n'
                else:
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_1_network, 'prefix'))
                    yield '\n'
            l_1_network = missing
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'redistribute_internal'), True):
                pass
                yield '      bgp redistribute-internal\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'bgp'), 'redistribute_internal'), False):
                pass
                yield '      no bgp redistribute-internal\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'redistribute')):
                pass
                l_0_redistribute_var = environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'redistribute')
                context.vars['redistribute_var'] = l_0_redistribute_var
                context.exported_vars.add('redistribute_var')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'enabled'), True):
                    pass
                    l_0_redistribute_host = 'redistribute attached-host'
                    context.vars['redistribute_host'] = l_0_redistribute_host
                    context.exported_vars.add('redistribute_host')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'route_map')):
                        pass
                        l_0_redistribute_host = str_join(((undefined(name='redistribute_host') if l_0_redistribute_host is missing else l_0_redistribute_host), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'route_map'), ))
                        context.vars['redistribute_host'] = l_0_redistribute_host
                        context.exported_vars.add('redistribute_host')
                    yield '      '
                    yield str((undefined(name='redistribute_host') if l_0_redistribute_host is missing else l_0_redistribute_host))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'bgp'), 'enabled'), True):
                    pass
                    l_0_redistribute_bgp = 'redistribute bgp leaked'
                    context.vars['redistribute_bgp'] = l_0_redistribute_bgp
                    context.exported_vars.add('redistribute_bgp')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'bgp'), 'route_map')):
                        pass
                        l_0_redistribute_bgp = str_join(((undefined(name='redistribute_bgp') if l_0_redistribute_bgp is missing else l_0_redistribute_bgp), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'bgp'), 'route_map'), ))
                        context.vars['redistribute_bgp'] = l_0_redistribute_bgp
                        context.exported_vars.add('redistribute_bgp')
                    yield '      '
                    yield str((undefined(name='redistribute_bgp') if l_0_redistribute_bgp is missing else l_0_redistribute_bgp))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'enabled'), True):
                    pass
                    l_0_redistribute_conn = 'redistribute connected'
                    context.vars['redistribute_conn'] = l_0_redistribute_conn
                    context.exported_vars.add('redistribute_conn')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' include leaked', ))
                        context.vars['redistribute_conn'] = l_0_redistribute_conn
                        context.exported_vars.add('redistribute_conn')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'route_map')):
                        pass
                        l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'route_map'), ))
                        context.vars['redistribute_conn'] = l_0_redistribute_conn
                        context.exported_vars.add('redistribute_conn')
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'rcf')):
                        pass
                        l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'rcf'), ))
                        context.vars['redistribute_conn'] = l_0_redistribute_conn
                        context.exported_vars.add('redistribute_conn')
                    yield '      '
                    yield str((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'enabled'), True):
                    pass
                    l_0_redistribute_dynamic = 'redistribute dynamic'
                    context.vars['redistribute_dynamic'] = l_0_redistribute_dynamic
                    context.exported_vars.add('redistribute_dynamic')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'route_map')):
                        pass
                        l_0_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_0_redistribute_dynamic is missing else l_0_redistribute_dynamic), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'route_map'), ))
                        context.vars['redistribute_dynamic'] = l_0_redistribute_dynamic
                        context.exported_vars.add('redistribute_dynamic')
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'rcf')):
                        pass
                        l_0_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_0_redistribute_dynamic is missing else l_0_redistribute_dynamic), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'rcf'), ))
                        context.vars['redistribute_dynamic'] = l_0_redistribute_dynamic
                        context.exported_vars.add('redistribute_dynamic')
                    yield '      '
                    yield str((undefined(name='redistribute_dynamic') if l_0_redistribute_dynamic is missing else l_0_redistribute_dynamic))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'user'), 'enabled'), True):
                    pass
                    l_0_redistribute_user = 'redistribute user'
                    context.vars['redistribute_user'] = l_0_redistribute_user
                    context.exported_vars.add('redistribute_user')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'user'), 'rcf')):
                        pass
                        l_0_redistribute_user = str_join(((undefined(name='redistribute_user') if l_0_redistribute_user is missing else l_0_redistribute_user), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'user'), 'rcf'), ))
                        context.vars['redistribute_user'] = l_0_redistribute_user
                        context.exported_vars.add('redistribute_user')
                    yield '      '
                    yield str((undefined(name='redistribute_user') if l_0_redistribute_user is missing else l_0_redistribute_user))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'enabled'), True):
                    pass
                    l_0_redistribute_isis = 'redistribute isis'
                    context.vars['redistribute_isis'] = l_0_redistribute_isis
                    context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'isis_level')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'isis_level'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' include leaked', ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'route_map')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'route_map'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'rcf')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'rcf'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    yield '      '
                    yield str((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf = 'redistribute ospf'
                    context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                    context.exported_vars.add('redistribute_ospf')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' include leaked', ))
                        context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                        context.exported_vars.add('redistribute_ospf')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'route_map')):
                        pass
                        l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'route_map'), ))
                        context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                        context.exported_vars.add('redistribute_ospf')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf = 'redistribute ospf match internal'
                    context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                    context.exported_vars.add('redistribute_ospf')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' include leaked', ))
                        context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                        context.exported_vars.add('redistribute_ospf')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'route_map')):
                        pass
                        l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'route_map'), ))
                        context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                        context.exported_vars.add('redistribute_ospf')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3 = 'redistribute ospfv3'
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' include leaked', ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'route_map'), ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3 = 'redistribute ospfv3 match internal'
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' include leaked', ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map'), ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3_match = 'redistribute ospfv3 match external'
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' include leaked', ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'route_map'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3_match = 'redistribute ospfv3 match nssa-external'
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' include leaked', ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf_match = 'redistribute ospf match external'
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' include leaked', ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'route_map'), ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf_match = 'redistribute ospf match nssa-external'
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type')):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type'), ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' include leaked', ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map'), ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'rip'), 'enabled'), True):
                    pass
                    l_0_redistribute_rip = 'redistribute rip'
                    context.vars['redistribute_rip'] = l_0_redistribute_rip
                    context.exported_vars.add('redistribute_rip')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'rip'), 'route_map')):
                        pass
                        l_0_redistribute_rip = str_join(((undefined(name='redistribute_rip') if l_0_redistribute_rip is missing else l_0_redistribute_rip), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'rip'), 'route_map'), ))
                        context.vars['redistribute_rip'] = l_0_redistribute_rip
                        context.exported_vars.add('redistribute_rip')
                    yield '      '
                    yield str((undefined(name='redistribute_rip') if l_0_redistribute_rip is missing else l_0_redistribute_rip))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'enabled'), True):
                    pass
                    l_0_redistribute_static = 'redistribute static'
                    context.vars['redistribute_static'] = l_0_redistribute_static
                    context.exported_vars.add('redistribute_static')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' include leaked', ))
                        context.vars['redistribute_static'] = l_0_redistribute_static
                        context.exported_vars.add('redistribute_static')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'route_map')):
                        pass
                        l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'route_map'), ))
                        context.vars['redistribute_static'] = l_0_redistribute_static
                        context.exported_vars.add('redistribute_static')
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'rcf')):
                        pass
                        l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'rcf'), ))
                        context.vars['redistribute_static'] = l_0_redistribute_static
                        context.exported_vars.add('redistribute_static')
                    yield '      '
                    yield str((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static))
                    yield '\n'
            elif t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'redistribute_routes')):
                pass
                for l_1_redistribute_route in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4'), 'redistribute_routes'), 'source_protocol'):
                    l_1_redistribute_route_cli = missing
                    _loop_vars = {}
                    pass
                    l_1_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_1_redistribute_route, 'source_protocol'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if (environment.getattr(l_1_redistribute_route, 'source_protocol') in ['ospf', 'ospfv3']):
                        pass
                        if t_6(environment.getattr(l_1_redistribute_route, 'ospf_route_type')):
                            pass
                            l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' match ', environment.getattr(l_1_redistribute_route, 'ospf_route_type'), ))
                            _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if (environment.getattr(l_1_redistribute_route, 'source_protocol') == 'bgp'):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    elif (t_6(environment.getattr(l_1_redistribute_route, 'include_leaked'), True) and (environment.getattr(l_1_redistribute_route, 'source_protocol') in ['connected', 'static', 'isis', 'ospf', 'ospfv3'])):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' include leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if t_6(environment.getattr(l_1_redistribute_route, 'route_map')):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' route-map ', environment.getattr(l_1_redistribute_route, 'route_map'), ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    elif (environment.getattr(l_1_redistribute_route, 'source_protocol') in ['connected', 'static', 'isis', 'user', 'dynamic']):
                        pass
                        if t_6(environment.getattr(l_1_redistribute_route, 'rcf')):
                            pass
                            l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' rcf ', environment.getattr(l_1_redistribute_route, 'rcf'), ))
                            _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    yield '      '
                    yield str((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli))
                    yield '\n'
                l_1_redistribute_route = l_1_redistribute_route_cli = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast')):
            pass
            yield '   !\n   address-family ipv4 labeled-unicast\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'update_wait_for_convergence'), True):
                pass
                yield '      update wait-for-convergence\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'missing_policy')):
                pass
                for l_1_direction in ['in', 'out']:
                    l_1_missing_policy_cli = resolve('missing_policy_cli')
                    l_1_dir = l_1_policy = missing
                    _loop_vars = {}
                    pass
                    l_1_dir = str_join(('direction_', l_1_direction, ))
                    _loop_vars['dir'] = l_1_dir
                    l_1_policy = environment.getitem(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'missing_policy'), (undefined(name='dir') if l_1_dir is missing else l_1_dir))
                    _loop_vars['policy'] = l_1_policy
                    if t_6(environment.getattr((undefined(name='policy') if l_1_policy is missing else l_1_policy), 'action')):
                        pass
                        l_1_missing_policy_cli = 'bgp missing-policy'
                        _loop_vars['missing_policy_cli'] = l_1_missing_policy_cli
                        if ((t_6(environment.getattr((undefined(name='policy') if l_1_policy is missing else l_1_policy), 'include_community_list'), True) or t_6(environment.getattr((undefined(name='policy') if l_1_policy is missing else l_1_policy), 'include_prefix_list'), True)) or t_6(environment.getattr((undefined(name='policy') if l_1_policy is missing else l_1_policy), 'include_sub_route_map'), True)):
                            pass
                            l_1_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_1_missing_policy_cli is missing else l_1_missing_policy_cli), ' include', ))
                            _loop_vars['missing_policy_cli'] = l_1_missing_policy_cli
                            if t_6(environment.getattr((undefined(name='policy') if l_1_policy is missing else l_1_policy), 'include_community_list'), True):
                                pass
                                l_1_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_1_missing_policy_cli is missing else l_1_missing_policy_cli), ' community-list', ))
                                _loop_vars['missing_policy_cli'] = l_1_missing_policy_cli
                            if t_6(environment.getattr((undefined(name='policy') if l_1_policy is missing else l_1_policy), 'include_prefix_list'), True):
                                pass
                                l_1_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_1_missing_policy_cli is missing else l_1_missing_policy_cli), ' prefix-list', ))
                                _loop_vars['missing_policy_cli'] = l_1_missing_policy_cli
                            if t_6(environment.getattr((undefined(name='policy') if l_1_policy is missing else l_1_policy), 'include_sub_route_map'), True):
                                pass
                                l_1_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_1_missing_policy_cli is missing else l_1_missing_policy_cli), ' sub-route-map', ))
                                _loop_vars['missing_policy_cli'] = l_1_missing_policy_cli
                        l_1_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_1_missing_policy_cli is missing else l_1_missing_policy_cli), ' direction ', l_1_direction, ' action ', environment.getattr((undefined(name='policy') if l_1_policy is missing else l_1_policy), 'action'), ))
                        _loop_vars['missing_policy_cli'] = l_1_missing_policy_cli
                        yield '      '
                        yield str((undefined(name='missing_policy_cli') if l_1_missing_policy_cli is missing else l_1_missing_policy_cli))
                        yield '\n'
                l_1_direction = l_1_dir = l_1_policy = l_1_missing_policy_cli = missing
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'additional_paths'), 'send')):
                pass
                if (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'additional_paths'), 'send') == 'disabled'):
                    pass
                    yield '      no bgp additional-paths send\n'
                elif (t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'additional_paths'), 'send') == 'ecmp')):
                    pass
                    yield '      bgp additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'additional_paths'), 'send_limit'))
                    yield '\n'
                elif (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'additional_paths'), 'send') == 'limit'):
                    pass
                    if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'additional_paths'), 'send_limit')):
                        pass
                        yield '      bgp additional-paths send limit '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'additional_paths'), 'send_limit'))
                        yield '\n'
                else:
                    pass
                    yield '      bgp additional-paths send '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'additional_paths'), 'send'))
                    yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'bgp'), 'next_hop_unchanged'), True):
                pass
                yield '      bgp next-hop-unchanged\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'neighbor_default'), 'next_hop_self'), True):
                pass
                yield '      neighbor default next-hop-self\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'next_hop_resolution_ribs')):
                pass
                l_0_v4_bgp_lu_resolution_ribs = []
                context.vars['v4_bgp_lu_resolution_ribs'] = l_0_v4_bgp_lu_resolution_ribs
                context.exported_vars.add('v4_bgp_lu_resolution_ribs')
                for l_1_rib in environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'next_hop_resolution_ribs'):
                    _loop_vars = {}
                    pass
                    if t_6(environment.getattr(l_1_rib, 'rib_type'), 'tunnel-rib-colored'):
                        pass
                        context.call(environment.getattr((undefined(name='v4_bgp_lu_resolution_ribs') if l_0_v4_bgp_lu_resolution_ribs is missing else l_0_v4_bgp_lu_resolution_ribs), 'append'), 'tunnel-rib colored system-colored-tunnel-rib', _loop_vars=_loop_vars)
                    elif t_6(environment.getattr(l_1_rib, 'rib_type'), 'tunnel-rib'):
                        pass
                        if t_6(environment.getattr(l_1_rib, 'rib_name')):
                            pass
                            context.call(environment.getattr((undefined(name='v4_bgp_lu_resolution_ribs') if l_0_v4_bgp_lu_resolution_ribs is missing else l_0_v4_bgp_lu_resolution_ribs), 'append'), str_join(('tunnel-rib ', environment.getattr(l_1_rib, 'rib_name'), )), _loop_vars=_loop_vars)
                    elif t_6(environment.getattr(l_1_rib, 'rib_type')):
                        pass
                        context.call(environment.getattr((undefined(name='v4_bgp_lu_resolution_ribs') if l_0_v4_bgp_lu_resolution_ribs is missing else l_0_v4_bgp_lu_resolution_ribs), 'append'), environment.getattr(l_1_rib, 'rib_type'), _loop_vars=_loop_vars)
                l_1_rib = missing
                if (undefined(name='v4_bgp_lu_resolution_ribs') if l_0_v4_bgp_lu_resolution_ribs is missing else l_0_v4_bgp_lu_resolution_ribs):
                    pass
                    yield '      next-hop resolution ribs '
                    yield str(t_5(context.eval_ctx, (undefined(name='v4_bgp_lu_resolution_ribs') if l_0_v4_bgp_lu_resolution_ribs is missing else l_0_v4_bgp_lu_resolution_ribs), ' '))
                    yield '\n'
            for l_1_peer in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'peer_groups'), 'name'):
                l_1_maximum_routes_cli = resolve('maximum_routes_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' activate\n'
                else:
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_peer, 'graceful_restart'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' graceful-restart\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer, 'graceful_restart_helper'), 'stale_route_map')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' graceful-restart-helper stale-route route-map '
                    yield str(environment.getattr(environment.getattr(l_1_peer, 'graceful_restart_helper'), 'stale_route_map'))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_peer, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_peer, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_peer, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_peer, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_peer, 'name'))
                        yield ' additional-paths send\n'
                    elif (t_6(environment.getattr(environment.getattr(l_1_peer, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_1_peer, 'additional_paths'), 'send') == 'ecmp')):
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_peer, 'name'))
                        yield ' additional-paths send ecmp limit '
                        yield str(environment.getattr(environment.getattr(l_1_peer, 'additional_paths'), 'send_limit'))
                        yield '\n'
                    elif (environment.getattr(environment.getattr(l_1_peer, 'additional_paths'), 'send') == 'limit'):
                        pass
                        if t_6(environment.getattr(environment.getattr(l_1_peer, 'additional_paths'), 'send_limit')):
                            pass
                            yield '      neighbor '
                            yield str(environment.getattr(l_1_peer, 'name'))
                            yield ' additional-paths send limit '
                            yield str(environment.getattr(environment.getattr(l_1_peer, 'additional_paths'), 'send_limit'))
                            yield '\n'
                    else:
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_peer, 'name'))
                        yield ' additional-paths send '
                        yield str(environment.getattr(environment.getattr(l_1_peer, 'additional_paths'), 'send'))
                        yield '\n'
                if t_6(environment.getattr(l_1_peer, 'next_hop_unchanged'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' next-hop-unchanged\n'
                if t_6(environment.getattr(l_1_peer, 'next_hop_self'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' next-hop-self\n'
                if t_6(environment.getattr(l_1_peer, 'next_hop_self_v4_mapped_v6_source_interface')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' next-hop-self v4-mapped-v6 source-interface '
                    yield str(environment.getattr(l_1_peer, 'next_hop_self_v4_mapped_v6_source_interface'))
                    yield '\n'
                elif t_6(environment.getattr(l_1_peer, 'next_hop_self_source_interface')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' next-hop-self source-interface '
                    yield str(environment.getattr(l_1_peer, 'next_hop_self_source_interface'))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer, 'maximum_advertised_routes')):
                    pass
                    l_1_maximum_routes_cli = str_join(('neighbor ', environment.getattr(l_1_peer, 'name'), ' maximum-advertised-routes ', environment.getattr(l_1_peer, 'maximum_advertised_routes'), ))
                    _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                    if t_6(environment.getattr(l_1_peer, 'maximum_advertised_routes_warning_limit')):
                        pass
                        l_1_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli), ' warning-limit ', environment.getattr(l_1_peer, 'maximum_advertised_routes_warning_limit'), ))
                        _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                    yield '      '
                    yield str((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer, 'missing_policy')):
                    pass
                    for l_2_direction in ['in', 'out']:
                        l_2_missing_policy_cli = resolve('missing_policy_cli')
                        l_2_dir = l_2_policy = missing
                        _loop_vars = {}
                        pass
                        l_2_dir = str_join(('direction_', l_2_direction, ))
                        _loop_vars['dir'] = l_2_dir
                        l_2_policy = environment.getitem(environment.getattr(l_1_peer, 'missing_policy'), (undefined(name='dir') if l_2_dir is missing else l_2_dir))
                        _loop_vars['policy'] = l_2_policy
                        if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'action')):
                            pass
                            l_2_missing_policy_cli = str_join(('neighbor ', environment.getattr(l_1_peer, 'name'), ' missing-policy', ))
                            _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            if ((t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_community_list'), True) or t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_prefix_list'), True)) or t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_sub_route_map'), True)):
                                pass
                                l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' include', ))
                                _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                                if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_community_list'), True):
                                    pass
                                    l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' community-list', ))
                                    _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                                if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_prefix_list'), True):
                                    pass
                                    l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' prefix-list', ))
                                    _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                                if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_sub_route_map'), True):
                                    pass
                                    l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' sub-route-map', ))
                                    _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' direction ', l_2_direction, ' action ', environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'action'), ))
                            _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            yield '      '
                            yield str((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli))
                            yield '\n'
                    l_2_direction = l_2_dir = l_2_policy = l_2_missing_policy_cli = missing
                if t_6(environment.getattr(l_1_peer, 'aigp_session'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' aigp-session\n'
                if t_6(environment.getattr(l_1_peer, 'multi_path'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer, 'name'))
                    yield ' multi-path\n'
            l_1_peer = l_1_maximum_routes_cli = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'neighbors'), 'ip_address'):
                l_1_maximum_routes_cli = resolve('maximum_routes_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                else:
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_neighbor, 'graceful_restart'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' graceful-restart\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'graceful_restart_helper'), 'stale_route_map')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' graceful-restart-helper stale-route route-map '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'graceful_restart_helper'), 'stale_route_map'))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send\n'
                    elif (t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'ecmp')):
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send ecmp limit '
                        yield str(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit'))
                        yield '\n'
                    elif (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'limit'):
                        pass
                        if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit')):
                            pass
                            yield '      neighbor '
                            yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                            yield ' additional-paths send limit '
                            yield str(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit'))
                            yield '\n'
                    else:
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send '
                        yield str(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'))
                        yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'next_hop_unchanged'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' next-hop-unchanged\n'
                if t_6(environment.getattr(l_1_neighbor, 'next_hop_self'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' next-hop-self\n'
                if t_6(environment.getattr(l_1_neighbor, 'next_hop_self_v4_mapped_v6_source_interface')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' next-hop-self v4-mapped-v6 source-interface '
                    yield str(environment.getattr(l_1_neighbor, 'next_hop_self_v4_mapped_v6_source_interface'))
                    yield '\n'
                elif t_6(environment.getattr(l_1_neighbor, 'next_hop_self_source_interface')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' next-hop-self source-interface '
                    yield str(environment.getattr(l_1_neighbor, 'next_hop_self_source_interface'))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'maximum_advertised_routes')):
                    pass
                    l_1_maximum_routes_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' maximum-advertised-routes ', environment.getattr(l_1_neighbor, 'maximum_advertised_routes'), ))
                    _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                    if t_6(environment.getattr(l_1_neighbor, 'maximum_advertised_routes_warning_limit')):
                        pass
                        l_1_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli), ' warning-limit ', environment.getattr(l_1_neighbor, 'maximum_advertised_routes_warning_limit'), ))
                        _loop_vars['maximum_routes_cli'] = l_1_maximum_routes_cli
                    yield '      '
                    yield str((undefined(name='maximum_routes_cli') if l_1_maximum_routes_cli is missing else l_1_maximum_routes_cli))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'missing_policy')):
                    pass
                    for l_2_direction in ['in', 'out']:
                        l_2_missing_policy_cli = resolve('missing_policy_cli')
                        l_2_dir = l_2_policy = missing
                        _loop_vars = {}
                        pass
                        l_2_dir = str_join(('direction_', l_2_direction, ))
                        _loop_vars['dir'] = l_2_dir
                        l_2_policy = environment.getitem(environment.getattr(l_1_neighbor, 'missing_policy'), (undefined(name='dir') if l_2_dir is missing else l_2_dir))
                        _loop_vars['policy'] = l_2_policy
                        if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'action')):
                            pass
                            l_2_missing_policy_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' missing-policy ', ))
                            _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            if ((t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_community_list'), True) or t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_prefix_list'), True)) or t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_sub_route_map'), True)):
                                pass
                                l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' include', ))
                                _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                                if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_community_list'), True):
                                    pass
                                    l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' community-list', ))
                                    _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                                if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_prefix_list'), True):
                                    pass
                                    l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' prefix-list', ))
                                    _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                                if t_6(environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'include_sub_route_map'), True):
                                    pass
                                    l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' sub-route-map', ))
                                    _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            l_2_missing_policy_cli = str_join(((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli), ' direction ', l_2_direction, ' action ', environment.getattr((undefined(name='policy') if l_2_policy is missing else l_2_policy), 'action'), ))
                            _loop_vars['missing_policy_cli'] = l_2_missing_policy_cli
                            yield '      '
                            yield str((undefined(name='missing_policy_cli') if l_2_missing_policy_cli is missing else l_2_missing_policy_cli))
                            yield '\n'
                    l_2_direction = l_2_dir = l_2_policy = l_2_missing_policy_cli = missing
                if t_6(environment.getattr(l_1_neighbor, 'aigp_session'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' aigp-session\n'
                if t_6(environment.getattr(l_1_neighbor, 'multi_path'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' multi-path\n'
            l_1_neighbor = l_1_maximum_routes_cli = missing
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'networks')):
                pass
                for l_1_network in environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'networks'):
                    l_1_network_cli = missing
                    _loop_vars = {}
                    pass
                    l_1_network_cli = str_join(('network ', environment.getattr(l_1_network, 'prefix'), ))
                    _loop_vars['network_cli'] = l_1_network_cli
                    if t_6(environment.getattr(l_1_network, 'route_map')):
                        pass
                        l_1_network_cli = str_join(((undefined(name='network_cli') if l_1_network_cli is missing else l_1_network_cli), ' route-map ', environment.getattr(l_1_network, 'route_map'), ))
                        _loop_vars['network_cli'] = l_1_network_cli
                    yield '      '
                    yield str((undefined(name='network_cli') if l_1_network_cli is missing else l_1_network_cli))
                    yield '\n'
                l_1_network = l_1_network_cli = missing
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'next_hops')):
                pass
                for l_1_next_hop in environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'next_hops'):
                    l_1_next_hop_cli = missing
                    _loop_vars = {}
                    pass
                    l_1_next_hop_cli = str_join(('next-hop ', environment.getattr(l_1_next_hop, 'ip_address'), ' originate', ))
                    _loop_vars['next_hop_cli'] = l_1_next_hop_cli
                    if t_6(environment.getattr(l_1_next_hop, 'lfib_backup_ip_forwarding'), True):
                        pass
                        l_1_next_hop_cli = str_join(((undefined(name='next_hop_cli') if l_1_next_hop_cli is missing else l_1_next_hop_cli), ' lfib-backup ip-forwarding', ))
                        _loop_vars['next_hop_cli'] = l_1_next_hop_cli
                    yield '      '
                    yield str((undefined(name='next_hop_cli') if l_1_next_hop_cli is missing else l_1_next_hop_cli))
                    yield '\n'
                l_1_next_hop = l_1_next_hop_cli = missing
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'lfib_entry_installation_skipped'), True):
                pass
                yield '      lfib entry installation skipped\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'label_local_termination')):
                pass
                yield '      label local-termination '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'label_local_termination'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'graceful_restart'), True):
                pass
                yield '      graceful-restart\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'tunnel_source_protocols')):
                pass
                for l_1_tunnel_source_protocol in environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'tunnel_source_protocols'):
                    l_1_tunnel_source_protocol_cli = missing
                    _loop_vars = {}
                    pass
                    l_1_tunnel_source_protocol_cli = str_join(('tunnel source-protocol ', environment.getattr(l_1_tunnel_source_protocol, 'protocol'), ))
                    _loop_vars['tunnel_source_protocol_cli'] = l_1_tunnel_source_protocol_cli
                    if t_6(environment.getattr(l_1_tunnel_source_protocol, 'rcf')):
                        pass
                        l_1_tunnel_source_protocol_cli = str_join(((undefined(name='tunnel_source_protocol_cli') if l_1_tunnel_source_protocol_cli is missing else l_1_tunnel_source_protocol_cli), ' rcf ', environment.getattr(l_1_tunnel_source_protocol, 'rcf'), ))
                        _loop_vars['tunnel_source_protocol_cli'] = l_1_tunnel_source_protocol_cli
                    yield '      '
                    yield str((undefined(name='tunnel_source_protocol_cli') if l_1_tunnel_source_protocol_cli is missing else l_1_tunnel_source_protocol_cli))
                    yield '\n'
                l_1_tunnel_source_protocol = l_1_tunnel_source_protocol_cli = missing
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'aigp_session')):
                pass
                for l_1_aigp_session_type in ['ibgp', 'confederation', 'ebgp']:
                    _loop_vars = {}
                    pass
                    if t_6(environment.getitem(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_labeled_unicast'), 'aigp_session'), l_1_aigp_session_type), True):
                        pass
                        yield '      aigp-session '
                        yield str(l_1_aigp_session_type)
                        yield '\n'
                l_1_aigp_session_type = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast')):
            pass
            yield '   !\n   address-family ipv4 multicast\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast'), 'bgp'), 'additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
            l_1_neighbor = missing
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast'), 'redistribute')):
                pass
                l_0_redistribute_var = environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast'), 'redistribute')
                context.vars['redistribute_var'] = l_0_redistribute_var
                context.exported_vars.add('redistribute_var')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'enabled'), True):
                    pass
                    l_0_redistribute_host = 'redistribute attached-host'
                    context.vars['redistribute_host'] = l_0_redistribute_host
                    context.exported_vars.add('redistribute_host')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'route_map')):
                        pass
                        l_0_redistribute_host = str_join(((undefined(name='redistribute_host') if l_0_redistribute_host is missing else l_0_redistribute_host), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'route_map'), ))
                        context.vars['redistribute_host'] = l_0_redistribute_host
                        context.exported_vars.add('redistribute_host')
                    yield '      '
                    yield str((undefined(name='redistribute_host') if l_0_redistribute_host is missing else l_0_redistribute_host))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'enabled'), True):
                    pass
                    l_0_redistribute_conn = 'redistribute connected'
                    context.vars['redistribute_conn'] = l_0_redistribute_conn
                    context.exported_vars.add('redistribute_conn')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'route_map')):
                        pass
                        l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'route_map'), ))
                        context.vars['redistribute_conn'] = l_0_redistribute_conn
                        context.exported_vars.add('redistribute_conn')
                    yield '      '
                    yield str((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'enabled'), True):
                    pass
                    l_0_redistribute_isis = 'redistribute isis'
                    context.vars['redistribute_isis'] = l_0_redistribute_isis
                    context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'isis_level')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'isis_level'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' include leaked', ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'route_map')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'route_map'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'rcf')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'rcf'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    yield '      '
                    yield str((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf = 'redistribute ospf'
                    context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                    context.exported_vars.add('redistribute_ospf')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'route_map')):
                        pass
                        l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'route_map'), ))
                        context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                        context.exported_vars.add('redistribute_ospf')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf = 'redistribute ospf match internal'
                    context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                    context.exported_vars.add('redistribute_ospf')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'route_map')):
                        pass
                        l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'route_map'), ))
                        context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                        context.exported_vars.add('redistribute_ospf')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3 = 'redistribute ospfv3'
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'route_map'), ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3 = 'redistribute ospfv3 match internal'
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map'), ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3_match = 'redistribute ospfv3 match external'
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'route_map'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3_match = 'redistribute ospfv3 match nssa-external'
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf_match = 'redistribute ospf match external'
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'route_map'), ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf_match = 'redistribute ospf match nssa-external'
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type')):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type'), ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map'), ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'enabled'), True):
                    pass
                    l_0_redistribute_static = 'redistribute static'
                    context.vars['redistribute_static'] = l_0_redistribute_static
                    context.exported_vars.add('redistribute_static')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'route_map')):
                        pass
                        l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'route_map'), ))
                        context.vars['redistribute_static'] = l_0_redistribute_static
                        context.exported_vars.add('redistribute_static')
                    yield '      '
                    yield str((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static))
                    yield '\n'
            elif t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast'), 'redistribute_routes')):
                pass
                for l_1_redistribute_route in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_multicast'), 'redistribute_routes'), 'source_protocol'):
                    l_1_redistribute_route_cli = missing
                    _loop_vars = {}
                    pass
                    l_1_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_1_redistribute_route, 'source_protocol'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if (environment.getattr(l_1_redistribute_route, 'source_protocol') in ['ospf', 'ospfv3']):
                        pass
                        if t_6(environment.getattr(l_1_redistribute_route, 'ospf_route_type')):
                            pass
                            l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' match ', environment.getattr(l_1_redistribute_route, 'ospf_route_type'), ))
                            _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if (t_6(environment.getattr(l_1_redistribute_route, 'include_leaked'), True) and (environment.getattr(l_1_redistribute_route, 'source_protocol') == 'isis')):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' include leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if t_6(environment.getattr(l_1_redistribute_route, 'route_map')):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' route-map ', environment.getattr(l_1_redistribute_route, 'route_map'), ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    elif ((environment.getattr(l_1_redistribute_route, 'source_protocol') == 'isis') and t_6(environment.getattr(l_1_redistribute_route, 'rcf'))):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' rcf ', environment.getattr(l_1_redistribute_route, 'rcf'), ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    yield '      '
                    yield str((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli))
                    yield '\n'
                l_1_redistribute_route = l_1_redistribute_route_cli = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_sr_te')):
            pass
            yield '   !\n   address-family ipv4 sr-te\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_sr_te'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv4_sr_te'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
            l_1_neighbor = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6')):
            pass
            yield '   !\n   address-family ipv6\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'install'), True):
                pass
                yield '      bgp additional-paths install\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'install_ecmp_primary'), True):
                pass
                yield '      bgp additional-paths install ecmp-primary\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send')):
                pass
                if (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send') == 'disabled'):
                    pass
                    yield '      no bgp additional-paths send\n'
                elif (t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send') == 'ecmp')):
                    pass
                    yield '      bgp additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send_limit'))
                    yield '\n'
                elif (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send') == 'limit'):
                    pass
                    if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send_limit')):
                        pass
                        yield '      bgp additional-paths send limit '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send_limit'))
                        yield '\n'
                else:
                    pass
                    yield '      bgp additional-paths send '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send'))
                    yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'peer_groups'), 'name'):
                l_1_add_path_cli = resolve('add_path_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_peer_group, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_peer_group, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer_group, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_peer_group, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer_group, 'prefix_list_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_peer_group, 'prefix_list_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer_group, 'prefix_list_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_peer_group, 'prefix_list_out'))
                    yield ' out\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' additional-paths send\n'
                    else:
                        pass
                        if (t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'ecmp')):
                            pass
                            l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' additional-paths send ecmp limit ', environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        elif (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'limit'):
                            pass
                            if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit')):
                                pass
                                l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' additional-paths send limit ', environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit'), ))
                                _loop_vars['add_path_cli'] = l_1_add_path_cli
                        else:
                            pass
                            l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' additional-paths send ', environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'prefix_list')):
                            pass
                            l_1_add_path_cli = str_join(((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli), ' prefix-list ', environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'prefix_list'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        if t_6((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli)):
                            pass
                            yield '      '
                            yield str((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli))
                            yield '\n'
            l_1_peer_group = l_1_add_path_cli = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'neighbors'), 'ip_address'):
                l_1_add_path_cli = resolve('add_path_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'prefix_list_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_neighbor, 'prefix_list_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'prefix_list_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' prefix-list '
                    yield str(environment.getattr(l_1_neighbor, 'prefix_list_out'))
                    yield ' out\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send\n'
                    else:
                        pass
                        if (t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'ecmp')):
                            pass
                            l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' additional-paths send ecmp limit ', environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        elif (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'limit'):
                            pass
                            if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit')):
                                pass
                                l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' additional-paths send limit ', environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit'), ))
                                _loop_vars['add_path_cli'] = l_1_add_path_cli
                        else:
                            pass
                            l_1_add_path_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' additional-paths send ', environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'prefix_list')):
                            pass
                            l_1_add_path_cli = str_join(((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli), ' prefix-list ', environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'prefix_list'), ))
                            _loop_vars['add_path_cli'] = l_1_add_path_cli
                        if t_6((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli)):
                            pass
                            yield '      '
                            yield str((undefined(name='add_path_cli') if l_1_add_path_cli is missing else l_1_add_path_cli))
                            yield '\n'
            l_1_neighbor = l_1_add_path_cli = missing
            for l_1_network in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'networks'), 'prefix'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_network, 'route_map')):
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_1_network, 'prefix'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_network, 'route_map'))
                    yield '\n'
                else:
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_1_network, 'prefix'))
                    yield '\n'
            l_1_network = missing
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'redistribute_internal'), True):
                pass
                yield '      bgp redistribute-internal\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'bgp'), 'redistribute_internal'), False):
                pass
                yield '      no bgp redistribute-internal\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'redistribute')):
                pass
                l_0_redistribute_var = environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'redistribute')
                context.vars['redistribute_var'] = l_0_redistribute_var
                context.exported_vars.add('redistribute_var')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'enabled'), True):
                    pass
                    l_0_redistribute_host = 'redistribute attached-host'
                    context.vars['redistribute_host'] = l_0_redistribute_host
                    context.exported_vars.add('redistribute_host')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'route_map')):
                        pass
                        l_0_redistribute_host = str_join(((undefined(name='redistribute_host') if l_0_redistribute_host is missing else l_0_redistribute_host), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'attached_host'), 'route_map'), ))
                        context.vars['redistribute_host'] = l_0_redistribute_host
                        context.exported_vars.add('redistribute_host')
                    yield '      '
                    yield str((undefined(name='redistribute_host') if l_0_redistribute_host is missing else l_0_redistribute_host))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'bgp'), 'enabled'), True):
                    pass
                    l_0_redistribute_bgp = 'redistribute bgp leaked'
                    context.vars['redistribute_bgp'] = l_0_redistribute_bgp
                    context.exported_vars.add('redistribute_bgp')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'bgp'), 'route_map')):
                        pass
                        l_0_redistribute_bgp = str_join(((undefined(name='redistribute_bgp') if l_0_redistribute_bgp is missing else l_0_redistribute_bgp), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'bgp'), 'route_map'), ))
                        context.vars['redistribute_bgp'] = l_0_redistribute_bgp
                        context.exported_vars.add('redistribute_bgp')
                    yield '      '
                    yield str((undefined(name='redistribute_bgp') if l_0_redistribute_bgp is missing else l_0_redistribute_bgp))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dhcp'), 'enabled'), True):
                    pass
                    l_0_redistribute_dhcp = 'redistribute dhcp'
                    context.vars['redistribute_dhcp'] = l_0_redistribute_dhcp
                    context.exported_vars.add('redistribute_dhcp')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dhcp'), 'route_map')):
                        pass
                        l_0_redistribute_dhcp = str_join(((undefined(name='redistribute_dhcp') if l_0_redistribute_dhcp is missing else l_0_redistribute_dhcp), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dhcp'), 'route_map'), ))
                        context.vars['redistribute_dhcp'] = l_0_redistribute_dhcp
                        context.exported_vars.add('redistribute_dhcp')
                    yield '      '
                    yield str((undefined(name='redistribute_dhcp') if l_0_redistribute_dhcp is missing else l_0_redistribute_dhcp))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'enabled'), True):
                    pass
                    l_0_redistribute_conn = 'redistribute connected'
                    context.vars['redistribute_conn'] = l_0_redistribute_conn
                    context.exported_vars.add('redistribute_conn')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' include leaked', ))
                        context.vars['redistribute_conn'] = l_0_redistribute_conn
                        context.exported_vars.add('redistribute_conn')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'route_map')):
                        pass
                        l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'route_map'), ))
                        context.vars['redistribute_conn'] = l_0_redistribute_conn
                        context.exported_vars.add('redistribute_conn')
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'rcf')):
                        pass
                        l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'rcf'), ))
                        context.vars['redistribute_conn'] = l_0_redistribute_conn
                        context.exported_vars.add('redistribute_conn')
                    yield '      '
                    yield str((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'enabled'), True):
                    pass
                    l_0_redistribute_dynamic = 'redistribute dynamic'
                    context.vars['redistribute_dynamic'] = l_0_redistribute_dynamic
                    context.exported_vars.add('redistribute_dynamic')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'route_map')):
                        pass
                        l_0_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_0_redistribute_dynamic is missing else l_0_redistribute_dynamic), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'route_map'), ))
                        context.vars['redistribute_dynamic'] = l_0_redistribute_dynamic
                        context.exported_vars.add('redistribute_dynamic')
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'rcf')):
                        pass
                        l_0_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_0_redistribute_dynamic is missing else l_0_redistribute_dynamic), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'dynamic'), 'rcf'), ))
                        context.vars['redistribute_dynamic'] = l_0_redistribute_dynamic
                        context.exported_vars.add('redistribute_dynamic')
                    yield '      '
                    yield str((undefined(name='redistribute_dynamic') if l_0_redistribute_dynamic is missing else l_0_redistribute_dynamic))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'user'), 'enabled'), True):
                    pass
                    l_0_redistribute_user = 'redistribute user'
                    context.vars['redistribute_user'] = l_0_redistribute_user
                    context.exported_vars.add('redistribute_user')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'user'), 'rcf')):
                        pass
                        l_0_redistribute_user = str_join(((undefined(name='redistribute_user') if l_0_redistribute_user is missing else l_0_redistribute_user), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'user'), 'rcf'), ))
                        context.vars['redistribute_user'] = l_0_redistribute_user
                        context.exported_vars.add('redistribute_user')
                    yield '      '
                    yield str((undefined(name='redistribute_user') if l_0_redistribute_user is missing else l_0_redistribute_user))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'enabled'), True):
                    pass
                    l_0_redistribute_isis = 'redistribute isis'
                    context.vars['redistribute_isis'] = l_0_redistribute_isis
                    context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'isis_level')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'isis_level'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' include leaked', ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'route_map')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'route_map'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'rcf')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'rcf'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    yield '      '
                    yield str((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3 = 'redistribute ospfv3'
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' include leaked', ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'route_map'), ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3 = 'redistribute ospfv3 match internal'
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' include leaked', ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map'), ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3_match = 'redistribute ospfv3 match external'
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' include leaked', ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'route_map'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3_match = 'redistribute ospfv3 match nssa-external'
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' include leaked', ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'enabled'), True):
                    pass
                    l_0_redistribute_static = 'redistribute static'
                    context.vars['redistribute_static'] = l_0_redistribute_static
                    context.exported_vars.add('redistribute_static')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' include leaked', ))
                        context.vars['redistribute_static'] = l_0_redistribute_static
                        context.exported_vars.add('redistribute_static')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'route_map')):
                        pass
                        l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'route_map'), ))
                        context.vars['redistribute_static'] = l_0_redistribute_static
                        context.exported_vars.add('redistribute_static')
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'rcf')):
                        pass
                        l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'rcf'), ))
                        context.vars['redistribute_static'] = l_0_redistribute_static
                        context.exported_vars.add('redistribute_static')
                    yield '      '
                    yield str((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static))
                    yield '\n'
            elif t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'redistribute_routes')):
                pass
                for l_1_redistribute_route in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6'), 'redistribute_routes'), 'source_protocol'):
                    l_1_redistribute_route_cli = missing
                    _loop_vars = {}
                    pass
                    l_1_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_1_redistribute_route, 'source_protocol'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if (environment.getattr(l_1_redistribute_route, 'source_protocol') == 'ospfv3'):
                        pass
                        if t_6(environment.getattr(l_1_redistribute_route, 'ospf_route_type')):
                            pass
                            l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' match ', environment.getattr(l_1_redistribute_route, 'ospf_route_type'), ))
                            _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if (environment.getattr(l_1_redistribute_route, 'source_protocol') == 'bgp'):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    elif t_6(environment.getattr(l_1_redistribute_route, 'include_leaked'), True):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' include leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if t_6(environment.getattr(l_1_redistribute_route, 'route_map')):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' route-map ', environment.getattr(l_1_redistribute_route, 'route_map'), ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    elif (environment.getattr(l_1_redistribute_route, 'source_protocol') in ['connected', 'static', 'isis', 'user', 'dynamic']):
                        pass
                        if t_6(environment.getattr(l_1_redistribute_route, 'rcf')):
                            pass
                            l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' rcf ', environment.getattr(l_1_redistribute_route, 'rcf'), ))
                            _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    yield '      '
                    yield str((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli))
                    yield '\n'
                l_1_redistribute_route = l_1_redistribute_route_cli = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast')):
            pass
            yield '   !\n   address-family ipv6 multicast\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                pass
                yield '      bgp missing-policy direction in action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                pass
                yield '      bgp missing-policy direction out action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'bgp'), 'additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths receive\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
            l_1_neighbor = missing
            for l_1_network in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'networks'), 'prefix'):
                l_1_network_cli = missing
                _loop_vars = {}
                pass
                l_1_network_cli = str_join(('network ', environment.getattr(l_1_network, 'prefix'), ))
                _loop_vars['network_cli'] = l_1_network_cli
                if t_6(environment.getattr(l_1_network, 'route_map')):
                    pass
                    l_1_network_cli = str_join(((undefined(name='network_cli') if l_1_network_cli is missing else l_1_network_cli), ' route-map ', environment.getattr(l_1_network, 'route_map'), ))
                    _loop_vars['network_cli'] = l_1_network_cli
                yield '      '
                yield str((undefined(name='network_cli') if l_1_network_cli is missing else l_1_network_cli))
                yield '\n'
            l_1_network = l_1_network_cli = missing
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'redistribute')):
                pass
                l_0_redistribute_var = environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'redistribute')
                context.vars['redistribute_var'] = l_0_redistribute_var
                context.exported_vars.add('redistribute_var')
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'enabled'), True):
                    pass
                    l_0_redistribute_conn = 'redistribute connected'
                    context.vars['redistribute_conn'] = l_0_redistribute_conn
                    context.exported_vars.add('redistribute_conn')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'route_map')):
                        pass
                        l_0_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'connected'), 'route_map'), ))
                        context.vars['redistribute_conn'] = l_0_redistribute_conn
                        context.exported_vars.add('redistribute_conn')
                    yield '      '
                    yield str((undefined(name='redistribute_conn') if l_0_redistribute_conn is missing else l_0_redistribute_conn))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'enabled'), True):
                    pass
                    l_0_redistribute_isis = 'redistribute isis'
                    context.vars['redistribute_isis'] = l_0_redistribute_isis
                    context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'isis_level')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'isis_level'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'include_leaked'), True):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' include leaked', ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'route_map')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'route_map'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'rcf')):
                        pass
                        l_0_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'isis'), 'rcf'), ))
                        context.vars['redistribute_isis'] = l_0_redistribute_isis
                        context.exported_vars.add('redistribute_isis')
                    yield '      '
                    yield str((undefined(name='redistribute_isis') if l_0_redistribute_isis is missing else l_0_redistribute_isis))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf = 'redistribute ospf'
                    context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                    context.exported_vars.add('redistribute_ospf')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'route_map')):
                        pass
                        l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'route_map'), ))
                        context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                        context.exported_vars.add('redistribute_ospf')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf = 'redistribute ospf match internal'
                    context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                    context.exported_vars.add('redistribute_ospf')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'route_map')):
                        pass
                        l_0_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_internal'), 'route_map'), ))
                        context.vars['redistribute_ospf'] = l_0_redistribute_ospf
                        context.exported_vars.add('redistribute_ospf')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf') if l_0_redistribute_ospf is missing else l_0_redistribute_ospf))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3 = 'redistribute ospfv3'
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'route_map'), ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3 = 'redistribute ospfv3 match internal'
                    context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                    context.exported_vars.add('redistribute_ospfv3')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map'), ))
                        context.vars['redistribute_ospfv3'] = l_0_redistribute_ospfv3
                        context.exported_vars.add('redistribute_ospfv3')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3') if l_0_redistribute_ospfv3 is missing else l_0_redistribute_ospfv3))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3_match = 'redistribute ospfv3 match external'
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_external'), 'route_map'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospfv3_match = 'redistribute ospfv3 match nssa-external'
                    context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                    context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                        context.vars['redistribute_ospfv3_match'] = l_0_redistribute_ospfv3_match
                        context.exported_vars.add('redistribute_ospfv3_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3_match') if l_0_redistribute_ospfv3_match is missing else l_0_redistribute_ospfv3_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf_match = 'redistribute ospf match external'
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_external'), 'route_map'), ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'enabled'), True):
                    pass
                    l_0_redistribute_ospf_match = 'redistribute ospf match nssa-external'
                    context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                    context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type')):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type'), ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map')):
                        pass
                        l_0_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map'), ))
                        context.vars['redistribute_ospf_match'] = l_0_redistribute_ospf_match
                        context.exported_vars.add('redistribute_ospf_match')
                    yield '      '
                    yield str((undefined(name='redistribute_ospf_match') if l_0_redistribute_ospf_match is missing else l_0_redistribute_ospf_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'enabled'), True):
                    pass
                    l_0_redistribute_static = 'redistribute static'
                    context.vars['redistribute_static'] = l_0_redistribute_static
                    context.exported_vars.add('redistribute_static')
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'route_map')):
                        pass
                        l_0_redistribute_static = str_join(((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_0_redistribute_var is missing else l_0_redistribute_var), 'static'), 'route_map'), ))
                        context.vars['redistribute_static'] = l_0_redistribute_static
                        context.exported_vars.add('redistribute_static')
                    yield '      '
                    yield str((undefined(name='redistribute_static') if l_0_redistribute_static is missing else l_0_redistribute_static))
                    yield '\n'
            elif t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'redistribute_routes')):
                pass
                for l_1_redistribute_route in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_multicast'), 'redistribute_routes'), 'source_protocol'):
                    l_1_redistribute_route_cli = missing
                    _loop_vars = {}
                    pass
                    l_1_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_1_redistribute_route, 'source_protocol'), ))
                    _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if (environment.getattr(l_1_redistribute_route, 'source_protocol') in ['ospf', 'ospfv3']):
                        pass
                        if t_6(environment.getattr(l_1_redistribute_route, 'ospf_route_type')):
                            pass
                            l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' match ', environment.getattr(l_1_redistribute_route, 'ospf_route_type'), ))
                            _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if t_6(environment.getattr(l_1_redistribute_route, 'include_leaked'), True):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' include leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    if t_6(environment.getattr(l_1_redistribute_route, 'route_map')):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' route-map ', environment.getattr(l_1_redistribute_route, 'route_map'), ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    elif ((environment.getattr(l_1_redistribute_route, 'source_protocol') == 'isis') and t_6(environment.getattr(l_1_redistribute_route, 'rcf'))):
                        pass
                        l_1_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli), ' rcf ', environment.getattr(l_1_redistribute_route, 'rcf'), ))
                        _loop_vars['redistribute_route_cli'] = l_1_redistribute_route_cli
                    yield '      '
                    yield str((undefined(name='redistribute_route_cli') if l_1_redistribute_route_cli is missing else l_1_redistribute_route_cli))
                    yield '\n'
                l_1_redistribute_route = l_1_redistribute_route_cli = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_sr_te')):
            pass
            yield '   !\n   address-family ipv6 sr-te\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_sr_te'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_ipv6_sr_te'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
            l_1_neighbor = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state')):
            pass
            yield '   !\n   address-family link-state\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                pass
                yield '      bgp missing-policy direction in action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                pass
                yield '      bgp missing-policy direction out action '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(l_1_peer_group, 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(l_1_peer_group, 'missing_policy'), 'direction_out_action'))
                    yield '\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'missing_policy'), 'direction_out_action'))
                    yield '\n'
            l_1_neighbor = missing
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection')):
                pass
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection'), 'roles'), 'producer'), True):
                    pass
                    yield '      path-selection\n'
                if (t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection'), 'roles'), 'consumer'), True) or t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection'), 'roles'), 'propagator'), True)):
                    pass
                    l_0_path_selection_roles = 'path-selection role'
                    context.vars['path_selection_roles'] = l_0_path_selection_roles
                    context.exported_vars.add('path_selection_roles')
                    if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection'), 'roles'), 'consumer'), True):
                        pass
                        l_0_path_selection_roles = str_join(((undefined(name='path_selection_roles') if l_0_path_selection_roles is missing else l_0_path_selection_roles), ' consumer', ))
                        context.vars['path_selection_roles'] = l_0_path_selection_roles
                        context.exported_vars.add('path_selection_roles')
                    if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_link_state'), 'path_selection'), 'roles'), 'propagator'), True):
                        pass
                        l_0_path_selection_roles = str_join(((undefined(name='path_selection_roles') if l_0_path_selection_roles is missing else l_0_path_selection_roles), ' propagator', ))
                        context.vars['path_selection_roles'] = l_0_path_selection_roles
                        context.exported_vars.add('path_selection_roles')
                    yield '      '
                    yield str((undefined(name='path_selection_roles') if l_0_path_selection_roles is missing else l_0_path_selection_roles))
                    yield '\n'
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection')):
            pass
            yield '   !\n   address-family path-selection\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send')):
                pass
                if (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send') == 'disabled'):
                    pass
                    yield '      no bgp additional-paths send\n'
                elif (t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send') == 'ecmp')):
                    pass
                    yield '      bgp additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send_limit'))
                    yield '\n'
                elif (environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send') == 'limit'):
                    pass
                    if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send_limit')):
                        pass
                        yield '      bgp additional-paths send limit '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send_limit'))
                        yield '\n'
                else:
                    pass
                    yield '      bgp additional-paths send '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'bgp'), 'additional_paths'), 'send'))
                    yield '\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' additional-paths send\n'
                    elif t_6(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit')):
                        pass
                        if (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'ecmp'):
                            pass
                            yield '      neighbor '
                            yield str(environment.getattr(l_1_peer_group, 'name'))
                            yield ' additional-paths send ecmp limit '
                            yield str(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit'))
                            yield '\n'
                        elif (environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send') == 'limit'):
                            pass
                            yield '      neighbor '
                            yield str(environment.getattr(l_1_peer_group, 'name'))
                            yield ' additional-paths send limit '
                            yield str(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send_limit'))
                            yield '\n'
                    else:
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' additional-paths send '
                        yield str(environment.getattr(environment.getattr(l_1_peer_group, 'additional_paths'), 'send'))
                        yield '\n'
            l_1_peer_group = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_path_selection'), 'neighbors'), 'ip_address'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send\n'
                    elif (t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'ecmp')):
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send ecmp limit '
                        yield str(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit'))
                        yield '\n'
                    elif (environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send') == 'limit'):
                        pass
                        if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit')):
                            pass
                            yield '      neighbor '
                            yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                            yield ' additional-paths send limit '
                            yield str(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send_limit'))
                            yield '\n'
                    else:
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                        yield ' additional-paths send '
                        yield str(environment.getattr(environment.getattr(l_1_neighbor, 'additional_paths'), 'send'))
                        yield '\n'
            l_1_neighbor = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_rtc')):
            pass
            yield '   !\n   address-family rt-membership\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_rtc'), 'peer_groups'), 'name'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_7(environment.getattr(l_1_peer_group, 'default_route_target')):
                    pass
                    if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_route_target'), 'only'), True):
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' default-route-target only\n'
                    else:
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_1_peer_group, 'name'))
                        yield ' default-route-target\n'
                if t_7(environment.getattr(environment.getattr(l_1_peer_group, 'default_route_target'), 'encoding_origin_as_omit')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' default-route-target encoding origin-as omit\n'
            l_1_peer_group = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4')):
            pass
            yield '   !\n   address-family vpn-ipv4\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'peer_groups'), 'name'):
                l_1_peer_group_default_route_cli = resolve('peer_group_default_route_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_peer_group, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_peer_group, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer_group, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_peer_group, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'enabled'), True):
                    pass
                    l_1_peer_group_default_route_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' default-route', ))
                    _loop_vars['peer_group_default_route_cli'] = l_1_peer_group_default_route_cli
                    if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'rcf')):
                        pass
                        l_1_peer_group_default_route_cli = str_join(((undefined(name='peer_group_default_route_cli') if l_1_peer_group_default_route_cli is missing else l_1_peer_group_default_route_cli), ' rcf ', environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'rcf'), ))
                        _loop_vars['peer_group_default_route_cli'] = l_1_peer_group_default_route_cli
                    elif t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'route_map')):
                        pass
                        l_1_peer_group_default_route_cli = str_join(((undefined(name='peer_group_default_route_cli') if l_1_peer_group_default_route_cli is missing else l_1_peer_group_default_route_cli), ' route-map ', environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'route_map'), ))
                        _loop_vars['peer_group_default_route_cli'] = l_1_peer_group_default_route_cli
                    yield '      '
                    yield str((undefined(name='peer_group_default_route_cli') if l_1_peer_group_default_route_cli is missing else l_1_peer_group_default_route_cli))
                    yield '\n'
            l_1_peer_group = l_1_peer_group_default_route_cli = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'neighbors'), 'ip_address'):
                l_1_neighbor_default_route_cli = resolve('neighbor_default_route_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'enabled'), True):
                    pass
                    l_1_neighbor_default_route_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' default-route', ))
                    _loop_vars['neighbor_default_route_cli'] = l_1_neighbor_default_route_cli
                    if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'rcf')):
                        pass
                        l_1_neighbor_default_route_cli = str_join(((undefined(name='neighbor_default_route_cli') if l_1_neighbor_default_route_cli is missing else l_1_neighbor_default_route_cli), ' rcf ', environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'rcf'), ))
                        _loop_vars['neighbor_default_route_cli'] = l_1_neighbor_default_route_cli
                    elif t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'route_map')):
                        pass
                        l_1_neighbor_default_route_cli = str_join(((undefined(name='neighbor_default_route_cli') if l_1_neighbor_default_route_cli is missing else l_1_neighbor_default_route_cli), ' route-map ', environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'route_map'), ))
                        _loop_vars['neighbor_default_route_cli'] = l_1_neighbor_default_route_cli
                    yield '      '
                    yield str((undefined(name='neighbor_default_route_cli') if l_1_neighbor_default_route_cli is missing else l_1_neighbor_default_route_cli))
                    yield '\n'
            l_1_neighbor = l_1_neighbor_default_route_cli = missing
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'neighbor_default_encapsulation_mpls_next_hop_self'), 'source_interface')):
                pass
                yield '      neighbor default encapsulation mpls next-hop-self source-interface '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'neighbor_default_encapsulation_mpls_next_hop_self'), 'source_interface'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'domain_identifier')):
                pass
                yield '      domain identifier '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'domain_identifier'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv4'), 'route'), 'import_match_failure_action'), 'discard'):
                pass
                yield '      route import match-failure action discard\n'
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6')):
            pass
            yield '   !\n   address-family vpn-ipv6\n'
            for l_1_peer_group in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'peer_groups'), 'name'):
                l_1_peer_group_default_route_cli = resolve('peer_group_default_route_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_peer_group, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_peer_group, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' activate\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_peer_group, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_peer_group, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_peer_group, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_peer_group, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_peer_group, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_peer_group, 'name'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_peer_group, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'enabled'), True):
                    pass
                    l_1_peer_group_default_route_cli = str_join(('neighbor ', environment.getattr(l_1_peer_group, 'name'), ' default-route', ))
                    _loop_vars['peer_group_default_route_cli'] = l_1_peer_group_default_route_cli
                    if t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'rcf')):
                        pass
                        l_1_peer_group_default_route_cli = str_join(((undefined(name='peer_group_default_route_cli') if l_1_peer_group_default_route_cli is missing else l_1_peer_group_default_route_cli), ' rcf ', environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'rcf'), ))
                        _loop_vars['peer_group_default_route_cli'] = l_1_peer_group_default_route_cli
                    elif t_6(environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'route_map')):
                        pass
                        l_1_peer_group_default_route_cli = str_join(((undefined(name='peer_group_default_route_cli') if l_1_peer_group_default_route_cli is missing else l_1_peer_group_default_route_cli), ' route-map ', environment.getattr(environment.getattr(l_1_peer_group, 'default_route'), 'route_map'), ))
                        _loop_vars['peer_group_default_route_cli'] = l_1_peer_group_default_route_cli
                    yield '      '
                    yield str((undefined(name='peer_group_default_route_cli') if l_1_peer_group_default_route_cli is missing else l_1_peer_group_default_route_cli))
                    yield '\n'
            l_1_peer_group = l_1_peer_group_default_route_cli = missing
            for l_1_neighbor in t_3(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'neighbors'), 'ip_address'):
                l_1_neighbor_default_route_cli = resolve('neighbor_default_route_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'activate'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                elif t_6(environment.getattr(l_1_neighbor, 'activate'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' activate\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(l_1_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_1_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf in '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_in'))
                    yield '\n'
                if t_6(environment.getattr(l_1_neighbor, 'rcf_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' rcf out '
                    yield str(environment.getattr(l_1_neighbor, 'rcf_out'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'enabled'), True):
                    pass
                    l_1_neighbor_default_route_cli = str_join(('neighbor ', environment.getattr(l_1_neighbor, 'ip_address'), ' default-route', ))
                    _loop_vars['neighbor_default_route_cli'] = l_1_neighbor_default_route_cli
                    if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'rcf')):
                        pass
                        l_1_neighbor_default_route_cli = str_join(((undefined(name='neighbor_default_route_cli') if l_1_neighbor_default_route_cli is missing else l_1_neighbor_default_route_cli), ' rcf ', environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'rcf'), ))
                        _loop_vars['neighbor_default_route_cli'] = l_1_neighbor_default_route_cli
                    elif t_6(environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'route_map')):
                        pass
                        l_1_neighbor_default_route_cli = str_join(((undefined(name='neighbor_default_route_cli') if l_1_neighbor_default_route_cli is missing else l_1_neighbor_default_route_cli), ' route-map ', environment.getattr(environment.getattr(l_1_neighbor, 'default_route'), 'route_map'), ))
                        _loop_vars['neighbor_default_route_cli'] = l_1_neighbor_default_route_cli
                    yield '      '
                    yield str((undefined(name='neighbor_default_route_cli') if l_1_neighbor_default_route_cli is missing else l_1_neighbor_default_route_cli))
                    yield '\n'
            l_1_neighbor = l_1_neighbor_default_route_cli = missing
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'neighbor_default_encapsulation_mpls_next_hop_self'), 'source_interface')):
                pass
                yield '      neighbor default encapsulation mpls next-hop-self source-interface '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'neighbor_default_encapsulation_mpls_next_hop_self'), 'source_interface'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'domain_identifier')):
                pass
                yield '      domain identifier '
                yield str(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'domain_identifier'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'address_family_vpn_ipv6'), 'route'), 'import_match_failure_action'), 'discard'):
                pass
                yield '      route import match-failure action discard\n'
        for l_1_vrf in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'vrfs'), 'name'):
            l_1_paths_cli = l_0_paths_cli
            l_1_redistribute_var = l_0_redistribute_var
            l_1_redistribute_conn = l_0_redistribute_conn
            l_1_redistribute_isis = l_0_redistribute_isis
            l_1_redistribute_ospf = l_0_redistribute_ospf
            l_1_redistribute_ospf_match = l_0_redistribute_ospf_match
            l_1_redistribute_ospfv3 = l_0_redistribute_ospfv3
            l_1_redistribute_ospfv3_match = l_0_redistribute_ospfv3_match
            l_1_redistribute_static = l_0_redistribute_static
            l_1_redistribute_rip = l_0_redistribute_rip
            l_1_redistribute_host = l_0_redistribute_host
            l_1_redistribute_dynamic = l_0_redistribute_dynamic
            l_1_redistribute_bgp = l_0_redistribute_bgp
            l_1_redistribute_user = l_0_redistribute_user
            l_1_redistribute_dhcp = l_0_redistribute_dhcp
            _loop_vars = {}
            pass
            yield '   !\n   vrf '
            yield str(environment.getattr(l_1_vrf, 'name'))
            yield '\n'
            if t_6(environment.getattr(l_1_vrf, 'rd')):
                pass
                yield '      rd '
                yield str(environment.getattr(l_1_vrf, 'rd'))
                yield '\n'
            if t_6(environment.getattr(l_1_vrf, 'default_route_exports')):
                pass
                for l_2_default_route_export in t_3(environment.getattr(l_1_vrf, 'default_route_exports'), 'address_family'):
                    l_2_vrf_default_route_export_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_vrf_default_route_export_cli = str_join(('default-route export ', environment.getattr(l_2_default_route_export, 'address_family'), ))
                    _loop_vars['vrf_default_route_export_cli'] = l_2_vrf_default_route_export_cli
                    if t_6(environment.getattr(l_2_default_route_export, 'always'), True):
                        pass
                        l_2_vrf_default_route_export_cli = str_join(((undefined(name='vrf_default_route_export_cli') if l_2_vrf_default_route_export_cli is missing else l_2_vrf_default_route_export_cli), ' always', ))
                        _loop_vars['vrf_default_route_export_cli'] = l_2_vrf_default_route_export_cli
                    if t_6(environment.getattr(l_2_default_route_export, 'rcf')):
                        pass
                        l_2_vrf_default_route_export_cli = str_join(((undefined(name='vrf_default_route_export_cli') if l_2_vrf_default_route_export_cli is missing else l_2_vrf_default_route_export_cli), ' rcf ', environment.getattr(l_2_default_route_export, 'rcf'), ))
                        _loop_vars['vrf_default_route_export_cli'] = l_2_vrf_default_route_export_cli
                    elif t_6(environment.getattr(l_2_default_route_export, 'route_map')):
                        pass
                        l_2_vrf_default_route_export_cli = str_join(((undefined(name='vrf_default_route_export_cli') if l_2_vrf_default_route_export_cli is missing else l_2_vrf_default_route_export_cli), ' route-map ', environment.getattr(l_2_default_route_export, 'route_map'), ))
                        _loop_vars['vrf_default_route_export_cli'] = l_2_vrf_default_route_export_cli
                    yield '      '
                    yield str((undefined(name='vrf_default_route_export_cli') if l_2_vrf_default_route_export_cli is missing else l_2_vrf_default_route_export_cli))
                    yield '\n'
                l_2_default_route_export = l_2_vrf_default_route_export_cli = missing
            if t_6(environment.getattr(environment.getattr(l_1_vrf, 'route_targets'), 'import')):
                pass
                for l_2_address_family in environment.getattr(environment.getattr(l_1_vrf, 'route_targets'), 'import'):
                    _loop_vars = {}
                    pass
                    for l_3_route_target in environment.getattr(l_2_address_family, 'route_targets'):
                        _loop_vars = {}
                        pass
                        yield '      route-target import '
                        yield str(environment.getattr(l_2_address_family, 'address_family'))
                        yield ' '
                        yield str(l_3_route_target)
                        yield '\n'
                    l_3_route_target = missing
                    if (environment.getattr(l_2_address_family, 'address_family') in ['evpn', 'vpn-ipv4', 'vpn-ipv6']):
                        pass
                        if t_6(environment.getattr(l_2_address_family, 'rcf')):
                            pass
                            if (t_6(environment.getattr(l_2_address_family, 'vpn_route_filter_rcf')) and (environment.getattr(l_2_address_family, 'address_family') in ['vpn-ipv4', 'vpn-ipv6'])):
                                pass
                                yield '      route-target import '
                                yield str(environment.getattr(l_2_address_family, 'address_family'))
                                yield ' rcf '
                                yield str(environment.getattr(l_2_address_family, 'rcf'))
                                yield ' vpn-route filter-rcf '
                                yield str(environment.getattr(l_2_address_family, 'vpn_route_filter_rcf'))
                                yield '\n'
                            else:
                                pass
                                yield '      route-target import '
                                yield str(environment.getattr(l_2_address_family, 'address_family'))
                                yield ' rcf '
                                yield str(environment.getattr(l_2_address_family, 'rcf'))
                                yield '\n'
                        if t_6(environment.getattr(l_2_address_family, 'route_map')):
                            pass
                            yield '      route-target import '
                            yield str(environment.getattr(l_2_address_family, 'address_family'))
                            yield ' route-map '
                            yield str(environment.getattr(l_2_address_family, 'route_map'))
                            yield '\n'
                l_2_address_family = missing
            if t_6(environment.getattr(environment.getattr(l_1_vrf, 'route_targets'), 'export')):
                pass
                for l_2_address_family in environment.getattr(environment.getattr(l_1_vrf, 'route_targets'), 'export'):
                    _loop_vars = {}
                    pass
                    for l_3_route_target in environment.getattr(l_2_address_family, 'route_targets'):
                        _loop_vars = {}
                        pass
                        yield '      route-target export '
                        yield str(environment.getattr(l_2_address_family, 'address_family'))
                        yield ' '
                        yield str(l_3_route_target)
                        yield '\n'
                    l_3_route_target = missing
                    if (environment.getattr(l_2_address_family, 'address_family') in ['evpn', 'vpn-ipv4', 'vpn-ipv6']):
                        pass
                        if t_6(environment.getattr(l_2_address_family, 'rcf')):
                            pass
                            if (t_6(environment.getattr(l_2_address_family, 'vrf_route_filter_rcf')) and (environment.getattr(l_2_address_family, 'address_family') in ['vpn-ipv4', 'vpn-ipv6'])):
                                pass
                                yield '      route-target export '
                                yield str(environment.getattr(l_2_address_family, 'address_family'))
                                yield ' rcf '
                                yield str(environment.getattr(l_2_address_family, 'rcf'))
                                yield ' vrf-route filter-rcf '
                                yield str(environment.getattr(l_2_address_family, 'vrf_route_filter_rcf'))
                                yield '\n'
                            else:
                                pass
                                yield '      route-target export '
                                yield str(environment.getattr(l_2_address_family, 'address_family'))
                                yield ' rcf '
                                yield str(environment.getattr(l_2_address_family, 'rcf'))
                                yield '\n'
                        if t_6(environment.getattr(l_2_address_family, 'route_map')):
                            pass
                            yield '      route-target export '
                            yield str(environment.getattr(l_2_address_family, 'address_family'))
                            yield ' route-map '
                            yield str(environment.getattr(l_2_address_family, 'route_map'))
                            yield '\n'
                l_2_address_family = missing
            if t_6(environment.getattr(l_1_vrf, 'router_id')):
                pass
                yield '      router-id '
                yield str(environment.getattr(l_1_vrf, 'router_id'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(l_1_vrf, 'updates'), 'wait_for_convergence'), True):
                pass
                yield '      update wait-for-convergence\n'
            if t_6(environment.getattr(environment.getattr(l_1_vrf, 'updates'), 'wait_install'), True):
                pass
                yield '      update wait-install\n'
            if t_6(environment.getattr(l_1_vrf, 'timers')):
                pass
                yield '      timers bgp '
                yield str(environment.getattr(l_1_vrf, 'timers'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(l_1_vrf, 'graceful_restart'), 'enabled'), True):
                pass
                if t_6(environment.getattr(environment.getattr(l_1_vrf, 'graceful_restart'), 'restart_time')):
                    pass
                    yield '      graceful-restart restart-time '
                    yield str(environment.getattr(environment.getattr(l_1_vrf, 'graceful_restart'), 'restart_time'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_vrf, 'graceful_restart'), 'stalepath_time')):
                    pass
                    yield '      graceful-restart stalepath-time '
                    yield str(environment.getattr(environment.getattr(l_1_vrf, 'graceful_restart'), 'stalepath_time'))
                    yield '\n'
                yield '      graceful-restart\n'
            if t_6(environment.getattr(environment.getattr(l_1_vrf, 'maximum_paths'), 'paths')):
                pass
                l_1_paths_cli = str_join(('maximum-paths ', environment.getattr(environment.getattr(l_1_vrf, 'maximum_paths'), 'paths'), ))
                _loop_vars['paths_cli'] = l_1_paths_cli
                if t_6(environment.getattr(environment.getattr(l_1_vrf, 'maximum_paths'), 'ecmp')):
                    pass
                    l_1_paths_cli = str_join(((undefined(name='paths_cli') if l_1_paths_cli is missing else l_1_paths_cli), ' ecmp ', environment.getattr(environment.getattr(l_1_vrf, 'maximum_paths'), 'ecmp'), ))
                    _loop_vars['paths_cli'] = l_1_paths_cli
                yield '      '
                yield str((undefined(name='paths_cli') if l_1_paths_cli is missing else l_1_paths_cli))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'install'), True):
                pass
                yield '      bgp additional-paths install\n'
            elif t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'install_ecmp_primary'), True):
                pass
                yield '      bgp additional-paths install ecmp-primary\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'receive'), True):
                pass
                yield '      bgp additional-paths receive\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'send')):
                pass
                if (environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'send') == 'disabled'):
                    pass
                    yield '      no bgp additional-paths send\n'
                elif (t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'send') == 'ecmp')):
                    pass
                    yield '      bgp additional-paths send ecmp limit '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'send_limit'))
                    yield '\n'
                elif (environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'send') == 'limit'):
                    pass
                    if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'send_limit')):
                        pass
                        yield '      bgp additional-paths send limit '
                        yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'send_limit'))
                        yield '\n'
                else:
                    pass
                    yield '      bgp additional-paths send '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'additional_paths'), 'send'))
                    yield '\n'
            if t_6(environment.getattr(l_1_vrf, 'listen_ranges')):
                pass
                def t_10(fiter):
                    for l_2_listen_range in fiter:
                        if ((t_6(environment.getattr(l_2_listen_range, 'peer_group')) and t_6(environment.getattr(l_2_listen_range, 'prefix'))) and (t_6(environment.getattr(l_2_listen_range, 'peer_filter')) or t_6(environment.getattr(l_2_listen_range, 'remote_as')))):
                            yield l_2_listen_range
                for l_2_listen_range in t_10(t_3(environment.getattr(l_1_vrf, 'listen_ranges'), 'peer_group')):
                    l_2_listen_range_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_listen_range_cli = str_join(('bgp listen range ', environment.getattr(l_2_listen_range, 'prefix'), ))
                    _loop_vars['listen_range_cli'] = l_2_listen_range_cli
                    if t_6(environment.getattr(l_2_listen_range, 'peer_id_include_router_id'), True):
                        pass
                        l_2_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_2_listen_range_cli is missing else l_2_listen_range_cli), ' peer-id include router-id', ))
                        _loop_vars['listen_range_cli'] = l_2_listen_range_cli
                    l_2_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_2_listen_range_cli is missing else l_2_listen_range_cli), ' peer-group ', environment.getattr(l_2_listen_range, 'peer_group'), ))
                    _loop_vars['listen_range_cli'] = l_2_listen_range_cli
                    if t_6(environment.getattr(l_2_listen_range, 'peer_filter')):
                        pass
                        l_2_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_2_listen_range_cli is missing else l_2_listen_range_cli), ' peer-filter ', environment.getattr(l_2_listen_range, 'peer_filter'), ))
                        _loop_vars['listen_range_cli'] = l_2_listen_range_cli
                    elif t_6(environment.getattr(l_2_listen_range, 'remote_as')):
                        pass
                        l_2_listen_range_cli = str_join(((undefined(name='listen_range_cli') if l_2_listen_range_cli is missing else l_2_listen_range_cli), ' remote-as ', environment.getattr(l_2_listen_range, 'remote_as'), ))
                        _loop_vars['listen_range_cli'] = l_2_listen_range_cli
                    yield '      '
                    yield str((undefined(name='listen_range_cli') if l_2_listen_range_cli is missing else l_2_listen_range_cli))
                    yield '\n'
                l_2_listen_range = l_2_listen_range_cli = missing
            for l_2_neighbor in t_3(environment.getattr(l_1_vrf, 'neighbors'), 'ip_address'):
                l_2_remove_private_as_cli = resolve('remove_private_as_cli')
                l_2_allowas_in_cli = resolve('allowas_in_cli')
                l_2_neighbor_rib_in_pre_policy_retain_cli = resolve('neighbor_rib_in_pre_policy_retain_cli')
                l_2_neighbor_ebgp_multihop_cli = resolve('neighbor_ebgp_multihop_cli')
                l_2_hide_passwords = resolve('hide_passwords')
                l_2_neighbor_default_originate_cli = resolve('neighbor_default_originate_cli')
                l_2_maximum_routes_cli = resolve('maximum_routes_cli')
                l_2_remove_private_as_ingress_cli = resolve('remove_private_as_ingress_cli')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_2_neighbor, 'peer_group')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' peer group '
                    yield str(environment.getattr(l_2_neighbor, 'peer_group'))
                    yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'remote_as')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' remote-as '
                    yield str(environment.getattr(l_2_neighbor, 'remote_as'))
                    yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'next_hop_self'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' next-hop-self\n'
                if t_6(environment.getattr(l_2_neighbor, 'next_hop_peer'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' next-hop-peer\n'
                if t_6(environment.getattr(l_2_neighbor, 'shutdown'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' shutdown\n'
                if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as'), 'enabled'), True):
                    pass
                    l_2_remove_private_as_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' remove-private-as', ))
                    _loop_vars['remove_private_as_cli'] = l_2_remove_private_as_cli
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as'), 'all'), True):
                        pass
                        l_2_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_2_remove_private_as_cli is missing else l_2_remove_private_as_cli), ' all', ))
                        _loop_vars['remove_private_as_cli'] = l_2_remove_private_as_cli
                        if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as'), 'replace_as'), True):
                            pass
                            l_2_remove_private_as_cli = str_join(((undefined(name='remove_private_as_cli') if l_2_remove_private_as_cli is missing else l_2_remove_private_as_cli), ' replace-as', ))
                            _loop_vars['remove_private_as_cli'] = l_2_remove_private_as_cli
                    yield '      '
                    yield str((undefined(name='remove_private_as_cli') if l_2_remove_private_as_cli is missing else l_2_remove_private_as_cli))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as'), 'enabled'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' remove-private-as\n'
                if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'as_path'), 'prepend_own_disabled'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' as-path prepend-own disabled\n'
                if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'as_path'), 'remote_as_replace_out'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' as-path remote-as replace out\n'
                if t_6(environment.getattr(l_2_neighbor, 'local_as')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' local-as '
                    yield str(environment.getattr(l_2_neighbor, 'local_as'))
                    yield ' no-prepend replace-as\n'
                if t_6(environment.getattr(l_2_neighbor, 'weight')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' weight '
                    yield str(environment.getattr(l_2_neighbor, 'weight'))
                    yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'passive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' passive\n'
                if t_6(environment.getattr(l_2_neighbor, 'update_source')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' update-source '
                    yield str(environment.getattr(l_2_neighbor, 'update_source'))
                    yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'bfd'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' bfd\n'
                    if ((t_6(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'interval')) and t_6(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'min_rx'))) and t_6(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'multiplier'))):
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' bfd interval '
                        yield str(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'interval'))
                        yield ' min-rx '
                        yield str(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'min_rx'))
                        yield ' multiplier '
                        yield str(environment.getattr(environment.getattr(l_2_neighbor, 'bfd_timers'), 'multiplier'))
                        yield '\n'
                elif (t_6(environment.getattr(l_2_neighbor, 'bfd'), False) and t_6(environment.getattr(l_2_neighbor, 'peer_group'))):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' bfd\n'
                if t_6(environment.getattr(l_2_neighbor, 'description')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' description '
                    yield str(environment.getattr(l_2_neighbor, 'description'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'allowas_in'), 'enabled'), True):
                    pass
                    l_2_allowas_in_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' allowas-in', ))
                    _loop_vars['allowas_in_cli'] = l_2_allowas_in_cli
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'allowas_in'), 'times')):
                        pass
                        l_2_allowas_in_cli = str_join(((undefined(name='allowas_in_cli') if l_2_allowas_in_cli is missing else l_2_allowas_in_cli), ' ', environment.getattr(environment.getattr(l_2_neighbor, 'allowas_in'), 'times'), ))
                        _loop_vars['allowas_in_cli'] = l_2_allowas_in_cli
                    yield '      '
                    yield str((undefined(name='allowas_in_cli') if l_2_allowas_in_cli is missing else l_2_allowas_in_cli))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'rib_in_pre_policy_retain'), 'enabled'), True):
                    pass
                    l_2_neighbor_rib_in_pre_policy_retain_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' rib-in pre-policy retain', ))
                    _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_2_neighbor_rib_in_pre_policy_retain_cli
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'rib_in_pre_policy_retain'), 'all'), True):
                        pass
                        l_2_neighbor_rib_in_pre_policy_retain_cli = str_join(((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_2_neighbor_rib_in_pre_policy_retain_cli is missing else l_2_neighbor_rib_in_pre_policy_retain_cli), ' all', ))
                        _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_2_neighbor_rib_in_pre_policy_retain_cli
                    yield '      '
                    yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_2_neighbor_rib_in_pre_policy_retain_cli is missing else l_2_neighbor_rib_in_pre_policy_retain_cli))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(l_2_neighbor, 'rib_in_pre_policy_retain'), 'enabled'), False):
                    pass
                    l_2_neighbor_rib_in_pre_policy_retain_cli = str_join(('no neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' rib-in pre-policy retain', ))
                    _loop_vars['neighbor_rib_in_pre_policy_retain_cli'] = l_2_neighbor_rib_in_pre_policy_retain_cli
                    yield '      '
                    yield str((undefined(name='neighbor_rib_in_pre_policy_retain_cli') if l_2_neighbor_rib_in_pre_policy_retain_cli is missing else l_2_neighbor_rib_in_pre_policy_retain_cli))
                    yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'ebgp_multihop')):
                    pass
                    l_2_neighbor_ebgp_multihop_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' ebgp-multihop', ))
                    _loop_vars['neighbor_ebgp_multihop_cli'] = l_2_neighbor_ebgp_multihop_cli
                    if t_8(environment.getattr(l_2_neighbor, 'ebgp_multihop')):
                        pass
                        l_2_neighbor_ebgp_multihop_cli = str_join(((undefined(name='neighbor_ebgp_multihop_cli') if l_2_neighbor_ebgp_multihop_cli is missing else l_2_neighbor_ebgp_multihop_cli), ' ', environment.getattr(l_2_neighbor, 'ebgp_multihop'), ))
                        _loop_vars['neighbor_ebgp_multihop_cli'] = l_2_neighbor_ebgp_multihop_cli
                    yield '      '
                    yield str((undefined(name='neighbor_ebgp_multihop_cli') if l_2_neighbor_ebgp_multihop_cli is missing else l_2_neighbor_ebgp_multihop_cli))
                    yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'route_reflector_client'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' route-reflector-client\n'
                elif t_6(environment.getattr(l_2_neighbor, 'route_reflector_client'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' route-reflector-client\n'
                if t_6(environment.getattr(l_2_neighbor, 'timers')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' timers '
                    yield str(environment.getattr(l_2_neighbor, 'timers'))
                    yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'route_map_in')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_2_neighbor, 'route_map_in'))
                    yield ' in\n'
                if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'receive'), True):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' additional-paths receive\n'
                if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '      no neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' additional-paths send\n'
                    elif (t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send') == 'ecmp')):
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' additional-paths send ecmp limit '
                        yield str(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit'))
                        yield '\n'
                    elif (environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send') == 'limit'):
                        pass
                        if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit')):
                            pass
                            yield '      neighbor '
                            yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                            yield ' additional-paths send limit '
                            yield str(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit'))
                            yield '\n'
                    else:
                        pass
                        yield '      neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' additional-paths send '
                        yield str(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send'))
                        yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'route_map_out')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' route-map '
                    yield str(environment.getattr(l_2_neighbor, 'route_map_out'))
                    yield ' out\n'
                if t_6(environment.getattr(l_2_neighbor, 'password')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' password 7 '
                    yield str(t_2(environment.getattr(l_2_neighbor, 'password'), (undefined(name='hide_passwords') if l_2_hide_passwords is missing else l_2_hide_passwords)))
                    yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'default_originate')):
                    pass
                    l_2_neighbor_default_originate_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' default-originate', ))
                    _loop_vars['neighbor_default_originate_cli'] = l_2_neighbor_default_originate_cli
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'default_originate'), 'route_map')):
                        pass
                        l_2_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_2_neighbor_default_originate_cli is missing else l_2_neighbor_default_originate_cli), ' route-map ', environment.getattr(environment.getattr(l_2_neighbor, 'default_originate'), 'route_map'), ))
                        _loop_vars['neighbor_default_originate_cli'] = l_2_neighbor_default_originate_cli
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'default_originate'), 'always'), True):
                        pass
                        l_2_neighbor_default_originate_cli = str_join(((undefined(name='neighbor_default_originate_cli') if l_2_neighbor_default_originate_cli is missing else l_2_neighbor_default_originate_cli), ' always', ))
                        _loop_vars['neighbor_default_originate_cli'] = l_2_neighbor_default_originate_cli
                    yield '      '
                    yield str((undefined(name='neighbor_default_originate_cli') if l_2_neighbor_default_originate_cli is missing else l_2_neighbor_default_originate_cli))
                    yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'send_community'), 'all'):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' send-community\n'
                elif t_6(environment.getattr(l_2_neighbor, 'send_community')):
                    pass
                    yield '      neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' send-community '
                    yield str(environment.getattr(l_2_neighbor, 'send_community'))
                    yield '\n'
                if t_6(environment.getattr(l_2_neighbor, 'maximum_routes')):
                    pass
                    l_2_maximum_routes_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' maximum-routes ', environment.getattr(l_2_neighbor, 'maximum_routes'), ))
                    _loop_vars['maximum_routes_cli'] = l_2_maximum_routes_cli
                    if t_6(environment.getattr(l_2_neighbor, 'maximum_routes_warning_limit')):
                        pass
                        l_2_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_2_maximum_routes_cli is missing else l_2_maximum_routes_cli), ' warning-limit ', environment.getattr(l_2_neighbor, 'maximum_routes_warning_limit'), ))
                        _loop_vars['maximum_routes_cli'] = l_2_maximum_routes_cli
                    if t_6(environment.getattr(l_2_neighbor, 'maximum_routes_warning_only'), True):
                        pass
                        l_2_maximum_routes_cli = str_join(((undefined(name='maximum_routes_cli') if l_2_maximum_routes_cli is missing else l_2_maximum_routes_cli), ' warning-only', ))
                        _loop_vars['maximum_routes_cli'] = l_2_maximum_routes_cli
                    yield '      '
                    yield str((undefined(name='maximum_routes_cli') if l_2_maximum_routes_cli is missing else l_2_maximum_routes_cli))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as_ingress'), 'enabled'), True):
                    pass
                    l_2_remove_private_as_ingress_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' remove-private-as ingress', ))
                    _loop_vars['remove_private_as_ingress_cli'] = l_2_remove_private_as_ingress_cli
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as_ingress'), 'replace_as'), True):
                        pass
                        l_2_remove_private_as_ingress_cli = str_join(((undefined(name='remove_private_as_ingress_cli') if l_2_remove_private_as_ingress_cli is missing else l_2_remove_private_as_ingress_cli), ' replace-as', ))
                        _loop_vars['remove_private_as_ingress_cli'] = l_2_remove_private_as_ingress_cli
                    yield '      '
                    yield str((undefined(name='remove_private_as_ingress_cli') if l_2_remove_private_as_ingress_cli is missing else l_2_remove_private_as_ingress_cli))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(l_2_neighbor, 'remove_private_as_ingress'), 'enabled'), False):
                    pass
                    yield '      no neighbor '
                    yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                    yield ' remove-private-as ingress\n'
            l_2_neighbor = l_2_remove_private_as_cli = l_2_allowas_in_cli = l_2_neighbor_rib_in_pre_policy_retain_cli = l_2_neighbor_ebgp_multihop_cli = l_2_hide_passwords = l_2_neighbor_default_originate_cli = l_2_maximum_routes_cli = l_2_remove_private_as_ingress_cli = missing
            for l_2_network in t_3(environment.getattr(l_1_vrf, 'networks'), 'prefix'):
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_2_network, 'route_map')):
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_2_network, 'prefix'))
                    yield ' route-map '
                    yield str(environment.getattr(l_2_network, 'route_map'))
                    yield '\n'
                else:
                    pass
                    yield '      network '
                    yield str(environment.getattr(l_2_network, 'prefix'))
                    yield '\n'
            l_2_network = missing
            if t_6(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'redistribute_internal'), True):
                pass
                yield '      bgp redistribute-internal\n'
            elif t_6(environment.getattr(environment.getattr(l_1_vrf, 'bgp'), 'redistribute_internal'), False):
                pass
                yield '      no bgp redistribute-internal\n'
            for l_2_aggregate_address in t_3(environment.getattr(l_1_vrf, 'aggregate_addresses'), 'prefix'):
                l_2_aggregate_address_cli = missing
                _loop_vars = {}
                pass
                l_2_aggregate_address_cli = str_join(('aggregate-address ', environment.getattr(l_2_aggregate_address, 'prefix'), ))
                _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_6(environment.getattr(l_2_aggregate_address, 'as_set'), True):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' as-set', ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_6(environment.getattr(l_2_aggregate_address, 'summary_only'), True):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' summary-only', ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_6(environment.getattr(l_2_aggregate_address, 'attribute_map')):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' attribute-map ', environment.getattr(l_2_aggregate_address, 'attribute_map'), ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_6(environment.getattr(l_2_aggregate_address, 'match_map')):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' match-map ', environment.getattr(l_2_aggregate_address, 'match_map'), ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                if t_6(environment.getattr(l_2_aggregate_address, 'advertise_only'), True):
                    pass
                    l_2_aggregate_address_cli = str_join(((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli), ' advertise-only', ))
                    _loop_vars['aggregate_address_cli'] = l_2_aggregate_address_cli
                yield '      '
                yield str((undefined(name='aggregate_address_cli') if l_2_aggregate_address_cli is missing else l_2_aggregate_address_cli))
                yield '\n'
            l_2_aggregate_address = l_2_aggregate_address_cli = missing
            if t_6(environment.getattr(l_1_vrf, 'redistribute')):
                pass
                l_1_redistribute_var = environment.getattr(l_1_vrf, 'redistribute')
                _loop_vars['redistribute_var'] = l_1_redistribute_var
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'enabled'), True):
                    pass
                    l_1_redistribute_conn = 'redistribute connected'
                    _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' include leaked', ))
                        _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'route_map')):
                        pass
                        l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'route_map'), ))
                        _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'rcf')):
                        pass
                        l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'rcf'), ))
                        _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                    yield '      '
                    yield str((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'enabled'), True):
                    pass
                    l_1_redistribute_isis = 'redistribute isis'
                    _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'isis_level')):
                        pass
                        l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'isis_level'), ))
                        _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' include leaked', ))
                        _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'route_map')):
                        pass
                        l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'route_map'), ))
                        _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'rcf')):
                        pass
                        l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'rcf'), ))
                        _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                    yield '      '
                    yield str((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'enabled'), True):
                    pass
                    l_1_redistribute_ospf = 'redistribute ospf'
                    _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' include leaked', ))
                        _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'route_map')):
                        pass
                        l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'route_map'), ))
                        _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                    yield '      '
                    yield str((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'enabled'), True):
                    pass
                    l_1_redistribute_ospf = 'redistribute ospf match internal'
                    _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' include leaked', ))
                        _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'route_map')):
                        pass
                        l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'route_map'), ))
                        _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                    yield '      '
                    yield str((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'enabled'), True):
                    pass
                    l_1_redistribute_ospf_match = 'redistribute ospf match external'
                    _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' include leaked', ))
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'route_map')):
                        pass
                        l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'route_map'), ))
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                    yield '      '
                    yield str((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'enabled'), True):
                    pass
                    l_1_redistribute_ospf_match = 'redistribute ospf match nssa-external'
                    _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type')):
                        pass
                        l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type'), ))
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' include leaked', ))
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map')):
                        pass
                        l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map'), ))
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                    yield '      '
                    yield str((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'enabled'), True):
                    pass
                    l_1_redistribute_ospfv3 = 'redistribute ospfv3'
                    _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' include leaked', ))
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'route_map')):
                        pass
                        l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'route_map'), ))
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3))
                    yield '\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'enabled'), True):
                    pass
                    l_1_redistribute_ospfv3 = 'redistribute ospfv3 match internal'
                    _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' include leaked', ))
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map')):
                        pass
                        l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map'), ))
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'enabled'), True):
                    pass
                    l_1_redistribute_ospfv3_match = 'redistribute ospfv3 match external'
                    _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' include leaked', ))
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'route_map')):
                        pass
                        l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'route_map'), ))
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                    pass
                    l_1_redistribute_ospfv3_match = 'redistribute ospfv3 match nssa-external'
                    _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type')):
                        pass
                        l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type'), ))
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' include leaked', ))
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                        pass
                        l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                    yield '      '
                    yield str((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'enabled'), True):
                    pass
                    l_1_redistribute_static = 'redistribute static'
                    _loop_vars['redistribute_static'] = l_1_redistribute_static
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'include_leaked'), True):
                        pass
                        l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' include leaked', ))
                        _loop_vars['redistribute_static'] = l_1_redistribute_static
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'route_map')):
                        pass
                        l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'route_map'), ))
                        _loop_vars['redistribute_static'] = l_1_redistribute_static
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'rcf')):
                        pass
                        l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'rcf'), ))
                        _loop_vars['redistribute_static'] = l_1_redistribute_static
                    yield '      '
                    yield str((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'rip'), 'enabled'), True):
                    pass
                    l_1_redistribute_rip = 'redistribute rip'
                    _loop_vars['redistribute_rip'] = l_1_redistribute_rip
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'rip'), 'route_map')):
                        pass
                        l_1_redistribute_rip = str_join(((undefined(name='redistribute_rip') if l_1_redistribute_rip is missing else l_1_redistribute_rip), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'rip'), 'route_map'), ))
                        _loop_vars['redistribute_rip'] = l_1_redistribute_rip
                    yield '      '
                    yield str((undefined(name='redistribute_rip') if l_1_redistribute_rip is missing else l_1_redistribute_rip))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'enabled'), True):
                    pass
                    l_1_redistribute_host = 'redistribute attached-host'
                    _loop_vars['redistribute_host'] = l_1_redistribute_host
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'route_map')):
                        pass
                        l_1_redistribute_host = str_join(((undefined(name='redistribute_host') if l_1_redistribute_host is missing else l_1_redistribute_host), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'route_map'), ))
                        _loop_vars['redistribute_host'] = l_1_redistribute_host
                    yield '      '
                    yield str((undefined(name='redistribute_host') if l_1_redistribute_host is missing else l_1_redistribute_host))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'enabled'), True):
                    pass
                    l_1_redistribute_dynamic = 'redistribute dynamic'
                    _loop_vars['redistribute_dynamic'] = l_1_redistribute_dynamic
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'route_map')):
                        pass
                        l_1_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_1_redistribute_dynamic is missing else l_1_redistribute_dynamic), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'route_map'), ))
                        _loop_vars['redistribute_dynamic'] = l_1_redistribute_dynamic
                    elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'rcf')):
                        pass
                        l_1_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_1_redistribute_dynamic is missing else l_1_redistribute_dynamic), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'rcf'), ))
                        _loop_vars['redistribute_dynamic'] = l_1_redistribute_dynamic
                    yield '      '
                    yield str((undefined(name='redistribute_dynamic') if l_1_redistribute_dynamic is missing else l_1_redistribute_dynamic))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'bgp'), 'enabled'), True):
                    pass
                    l_1_redistribute_bgp = 'redistribute bgp leaked'
                    _loop_vars['redistribute_bgp'] = l_1_redistribute_bgp
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'bgp'), 'route_map')):
                        pass
                        l_1_redistribute_bgp = str_join(((undefined(name='redistribute_bgp') if l_1_redistribute_bgp is missing else l_1_redistribute_bgp), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'bgp'), 'route_map'), ))
                        _loop_vars['redistribute_bgp'] = l_1_redistribute_bgp
                    yield '      '
                    yield str((undefined(name='redistribute_bgp') if l_1_redistribute_bgp is missing else l_1_redistribute_bgp))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'user'), 'enabled'), True):
                    pass
                    l_1_redistribute_user = 'redistribute user'
                    _loop_vars['redistribute_user'] = l_1_redistribute_user
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'user'), 'rcf')):
                        pass
                        l_1_redistribute_user = str_join(((undefined(name='redistribute_user') if l_1_redistribute_user is missing else l_1_redistribute_user), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'user'), 'rcf'), ))
                        _loop_vars['redistribute_user'] = l_1_redistribute_user
                    yield '      '
                    yield str((undefined(name='redistribute_user') if l_1_redistribute_user is missing else l_1_redistribute_user))
                    yield '\n'
            elif t_6(environment.getattr(l_1_vrf, 'redistribute_routes')):
                pass
                for l_2_redistribute_route in t_3(environment.getattr(l_1_vrf, 'redistribute_routes'), 'source_protocol'):
                    l_2_redistribute_route_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_2_redistribute_route, 'source_protocol'), ))
                    _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                    if (environment.getattr(l_2_redistribute_route, 'source_protocol') in ['ospf', 'ospfv3']):
                        pass
                        if t_6(environment.getattr(l_2_redistribute_route, 'ospf_route_type')):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' match ', environment.getattr(l_2_redistribute_route, 'ospf_route_type'), ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                    if (environment.getattr(l_2_redistribute_route, 'source_protocol') == 'bgp'):
                        pass
                        l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                    elif t_6(environment.getattr(l_2_redistribute_route, 'include_leaked'), True):
                        pass
                        l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' include leaked', ))
                        _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                    if t_6(environment.getattr(l_2_redistribute_route, 'route_map')):
                        pass
                        l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' route-map ', environment.getattr(l_2_redistribute_route, 'route_map'), ))
                        _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                    elif (environment.getattr(l_2_redistribute_route, 'source_protocol') in ['connected', 'static', 'isis', 'user', 'dynamic']):
                        pass
                        if t_6(environment.getattr(l_2_redistribute_route, 'rcf')):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' rcf ', environment.getattr(l_2_redistribute_route, 'rcf'), ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                    yield '      '
                    yield str((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli))
                    yield '\n'
                l_2_redistribute_route = l_2_redistribute_route_cli = missing
            for l_2_neighbor_interface in t_3(environment.getattr(l_1_vrf, 'neighbor_interfaces'), 'name'):
                _loop_vars = {}
                pass
                if (t_6(environment.getattr(l_2_neighbor_interface, 'peer_group')) and t_6(environment.getattr(l_2_neighbor_interface, 'remote_as'))):
                    pass
                    yield '      neighbor interface '
                    yield str(environment.getattr(l_2_neighbor_interface, 'name'))
                    yield ' peer-group '
                    yield str(environment.getattr(l_2_neighbor_interface, 'peer_group'))
                    yield ' remote-as '
                    yield str(environment.getattr(l_2_neighbor_interface, 'remote_as'))
                    yield '\n'
                elif (t_6(environment.getattr(l_2_neighbor_interface, 'peer_group')) and t_6(environment.getattr(l_2_neighbor_interface, 'peer_filter'))):
                    pass
                    yield '      neighbor interface '
                    yield str(environment.getattr(l_2_neighbor_interface, 'name'))
                    yield ' peer-group '
                    yield str(environment.getattr(l_2_neighbor_interface, 'peer_group'))
                    yield ' peer-filter '
                    yield str(environment.getattr(l_2_neighbor_interface, 'peer_filter'))
                    yield '\n'
            l_2_neighbor_interface = missing
            if t_6(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4')):
                pass
                yield '      !\n      address-family flow-spec ipv4\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv4'), 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_6(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                l_2_neighbor = missing
            if t_6(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6')):
                pass
                yield '      !\n      address-family flow-spec ipv6\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_flow_spec_ipv6'), 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_6(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                l_2_neighbor = missing
            if t_6(environment.getattr(l_1_vrf, 'address_family_ipv4')):
                pass
                yield '      !\n      address-family ipv4\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'install'), True):
                    pass
                    yield '         bgp additional-paths install\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'install_ecmp_primary'), True):
                    pass
                    yield '         bgp additional-paths install ecmp-primary\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'receive'), True):
                    pass
                    yield '         bgp additional-paths receive\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '         no bgp additional-paths send\n'
                    elif (t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send') == 'ecmp')):
                        pass
                        yield '         bgp additional-paths send ecmp limit '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send_limit'))
                        yield '\n'
                    elif (environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send') == 'limit'):
                        pass
                        if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send_limit')):
                            pass
                            yield '         bgp additional-paths send limit '
                            yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send_limit'))
                            yield '\n'
                    else:
                        pass
                        yield '         bgp additional-paths send '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'additional_paths'), 'send'))
                        yield '\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'neighbors'), 'ip_address'):
                    l_2_ipv6_originate_cli = resolve('ipv6_originate_cli')
                    _loop_vars = {}
                    pass
                    if t_6(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'receive'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' additional-paths receive\n'
                    if t_6(environment.getattr(l_2_neighbor, 'route_map_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_in'))
                        yield ' in\n'
                    if t_6(environment.getattr(l_2_neighbor, 'route_map_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_out'))
                        yield ' out\n'
                    if t_6(environment.getattr(l_2_neighbor, 'rcf_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' rcf in '
                        yield str(environment.getattr(l_2_neighbor, 'rcf_in'))
                        yield '\n'
                    if t_6(environment.getattr(l_2_neighbor, 'rcf_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' rcf out '
                        yield str(environment.getattr(l_2_neighbor, 'rcf_out'))
                        yield '\n'
                    if t_6(environment.getattr(l_2_neighbor, 'prefix_list_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' prefix-list '
                        yield str(environment.getattr(l_2_neighbor, 'prefix_list_in'))
                        yield ' in\n'
                    if t_6(environment.getattr(l_2_neighbor, 'prefix_list_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' prefix-list '
                        yield str(environment.getattr(l_2_neighbor, 'prefix_list_out'))
                        yield ' out\n'
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send')):
                        pass
                        if (environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send') == 'disabled'):
                            pass
                            yield '         no neighbor '
                            yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                            yield ' additional-paths send\n'
                        elif (t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send') == 'ecmp')):
                            pass
                            yield '         neighbor '
                            yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                            yield ' additional-paths send ecmp limit '
                            yield str(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit'))
                            yield '\n'
                        elif (environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send') == 'limit'):
                            pass
                            if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit')):
                                pass
                                yield '         neighbor '
                                yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                                yield ' additional-paths send limit '
                                yield str(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit'))
                                yield '\n'
                        else:
                            pass
                            yield '         neighbor '
                            yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                            yield ' additional-paths send '
                            yield str(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send'))
                            yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr(l_2_neighbor, 'next_hop'), 'address_family_ipv6'), 'enabled')):
                        pass
                        if environment.getattr(environment.getattr(environment.getattr(l_2_neighbor, 'next_hop'), 'address_family_ipv6'), 'enabled'):
                            pass
                            l_2_ipv6_originate_cli = str_join(('neighbor ', environment.getattr(l_2_neighbor, 'ip_address'), ' next-hop address-family ipv6', ))
                            _loop_vars['ipv6_originate_cli'] = l_2_ipv6_originate_cli
                            if t_6(environment.getattr(environment.getattr(environment.getattr(l_2_neighbor, 'next_hop'), 'address_family_ipv6'), 'originate'), True):
                                pass
                                l_2_ipv6_originate_cli = str_join(((undefined(name='ipv6_originate_cli') if l_2_ipv6_originate_cli is missing else l_2_ipv6_originate_cli), ' originate', ))
                                _loop_vars['ipv6_originate_cli'] = l_2_ipv6_originate_cli
                            yield '         '
                            yield str((undefined(name='ipv6_originate_cli') if l_2_ipv6_originate_cli is missing else l_2_ipv6_originate_cli))
                            yield '\n'
                        else:
                            pass
                            yield '         no neighbor '
                            yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                            yield ' next-hop address-family ipv6\n'
                l_2_neighbor = l_2_ipv6_originate_cli = missing
                for l_2_network in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'networks'), 'prefix'):
                    l_2_network_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_network_cli = str_join(('network ', environment.getattr(l_2_network, 'prefix'), ))
                    _loop_vars['network_cli'] = l_2_network_cli
                    if t_6(environment.getattr(l_2_network, 'route_map')):
                        pass
                        l_2_network_cli = str_join(((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli), ' route-map ', environment.getattr(l_2_network, 'route_map'), ))
                        _loop_vars['network_cli'] = l_2_network_cli
                    yield '         '
                    yield str((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli))
                    yield '\n'
                l_2_network = l_2_network_cli = missing
                if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'redistribute_internal'), True):
                    pass
                    yield '         bgp redistribute-internal\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'bgp'), 'redistribute_internal'), False):
                    pass
                    yield '         no bgp redistribute-internal\n'
                if t_6(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'redistribute')):
                    pass
                    l_1_redistribute_var = environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'redistribute')
                    _loop_vars['redistribute_var'] = l_1_redistribute_var
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'enabled'), True):
                        pass
                        l_1_redistribute_host = 'redistribute attached-host'
                        _loop_vars['redistribute_host'] = l_1_redistribute_host
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'route_map')):
                            pass
                            l_1_redistribute_host = str_join(((undefined(name='redistribute_host') if l_1_redistribute_host is missing else l_1_redistribute_host), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'route_map'), ))
                            _loop_vars['redistribute_host'] = l_1_redistribute_host
                        yield '         '
                        yield str((undefined(name='redistribute_host') if l_1_redistribute_host is missing else l_1_redistribute_host))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'bgp'), 'enabled'), True):
                        pass
                        l_1_redistribute_bgp = 'redistribute bgp leaked'
                        _loop_vars['redistribute_bgp'] = l_1_redistribute_bgp
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'bgp'), 'route_map')):
                            pass
                            l_1_redistribute_bgp = str_join(((undefined(name='redistribute_bgp') if l_1_redistribute_bgp is missing else l_1_redistribute_bgp), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'bgp'), 'route_map'), ))
                            _loop_vars['redistribute_bgp'] = l_1_redistribute_bgp
                        yield '         '
                        yield str((undefined(name='redistribute_bgp') if l_1_redistribute_bgp is missing else l_1_redistribute_bgp))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'enabled'), True):
                        pass
                        l_1_redistribute_conn = 'redistribute connected'
                        _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' include leaked', ))
                            _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'route_map')):
                            pass
                            l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'route_map'), ))
                            _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'rcf')):
                            pass
                            l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'rcf'), ))
                            _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        yield '         '
                        yield str((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'enabled'), True):
                        pass
                        l_1_redistribute_dynamic = 'redistribute dynamic'
                        _loop_vars['redistribute_dynamic'] = l_1_redistribute_dynamic
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'route_map')):
                            pass
                            l_1_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_1_redistribute_dynamic is missing else l_1_redistribute_dynamic), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'route_map'), ))
                            _loop_vars['redistribute_dynamic'] = l_1_redistribute_dynamic
                        elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'rcf')):
                            pass
                            l_1_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_1_redistribute_dynamic is missing else l_1_redistribute_dynamic), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'rcf'), ))
                            _loop_vars['redistribute_dynamic'] = l_1_redistribute_dynamic
                        yield '         '
                        yield str((undefined(name='redistribute_dynamic') if l_1_redistribute_dynamic is missing else l_1_redistribute_dynamic))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'user'), 'enabled'), True):
                        pass
                        l_1_redistribute_user = 'redistribute user'
                        _loop_vars['redistribute_user'] = l_1_redistribute_user
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'user'), 'rcf')):
                            pass
                            l_1_redistribute_user = str_join(((undefined(name='redistribute_user') if l_1_redistribute_user is missing else l_1_redistribute_user), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'user'), 'rcf'), ))
                            _loop_vars['redistribute_user'] = l_1_redistribute_user
                        yield '         '
                        yield str((undefined(name='redistribute_user') if l_1_redistribute_user is missing else l_1_redistribute_user))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'enabled'), True):
                        pass
                        l_1_redistribute_isis = 'redistribute isis'
                        _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'isis_level')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'isis_level'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' include leaked', ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'route_map')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'route_map'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'rcf')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'rcf'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        yield '         '
                        yield str((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf = 'redistribute ospf'
                        _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' include leaked', ))
                            _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'route_map')):
                            pass
                            l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'route_map'), ))
                            _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        yield '         '
                        yield str((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf))
                        yield '\n'
                    elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf = 'redistribute ospf match internal'
                        _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' include leaked', ))
                            _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'route_map')):
                            pass
                            l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'route_map'), ))
                            _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        yield '         '
                        yield str((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3 = 'redistribute ospfv3'
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' include leaked', ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3))
                        yield '\n'
                    elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3 = 'redistribute ospfv3 match internal'
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' include leaked', ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3_match = 'redistribute ospfv3 match external'
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' include leaked', ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3_match = 'redistribute ospfv3 match nssa-external'
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' include leaked', ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf_match = 'redistribute ospf match external'
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' include leaked', ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf_match = 'redistribute ospf match nssa-external'
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type')):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type'), ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' include leaked', ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'rip'), 'enabled'), True):
                        pass
                        l_1_redistribute_rip = 'redistribute rip'
                        _loop_vars['redistribute_rip'] = l_1_redistribute_rip
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'rip'), 'route_map')):
                            pass
                            l_1_redistribute_rip = str_join(((undefined(name='redistribute_rip') if l_1_redistribute_rip is missing else l_1_redistribute_rip), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'rip'), 'route_map'), ))
                            _loop_vars['redistribute_rip'] = l_1_redistribute_rip
                        yield '         '
                        yield str((undefined(name='redistribute_rip') if l_1_redistribute_rip is missing else l_1_redistribute_rip))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'enabled'), True):
                        pass
                        l_1_redistribute_static = 'redistribute static'
                        _loop_vars['redistribute_static'] = l_1_redistribute_static
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' include leaked', ))
                            _loop_vars['redistribute_static'] = l_1_redistribute_static
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'route_map')):
                            pass
                            l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'route_map'), ))
                            _loop_vars['redistribute_static'] = l_1_redistribute_static
                        elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'rcf')):
                            pass
                            l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'rcf'), ))
                            _loop_vars['redistribute_static'] = l_1_redistribute_static
                        yield '         '
                        yield str((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static))
                        yield '\n'
                elif t_6(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'redistribute_routes')):
                    pass
                    for l_2_redistribute_route in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4'), 'redistribute_routes'), 'source_protocol'):
                        l_2_redistribute_route_cli = missing
                        _loop_vars = {}
                        pass
                        l_2_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_2_redistribute_route, 'source_protocol'), ))
                        _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if (environment.getattr(l_2_redistribute_route, 'source_protocol') in ['ospf', 'ospfv3']):
                            pass
                            if t_6(environment.getattr(l_2_redistribute_route, 'ospf_route_type')):
                                pass
                                l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' match ', environment.getattr(l_2_redistribute_route, 'ospf_route_type'), ))
                                _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if (environment.getattr(l_2_redistribute_route, 'source_protocol') == 'bgp'):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' leaked', ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        elif (t_6(environment.getattr(l_2_redistribute_route, 'include_leaked'), True) and (environment.getattr(l_2_redistribute_route, 'source_protocol') in ['connected', 'isis', 'ospf', 'ospfv3', 'static'])):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' include leaked', ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if t_6(environment.getattr(l_2_redistribute_route, 'route_map')):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' route-map ', environment.getattr(l_2_redistribute_route, 'route_map'), ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        elif (environment.getattr(l_2_redistribute_route, 'source_protocol') in ['connected', 'static', 'isis', 'user', 'dynamic']):
                            pass
                            if t_6(environment.getattr(l_2_redistribute_route, 'rcf')):
                                pass
                                l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' rcf ', environment.getattr(l_2_redistribute_route, 'rcf'), ))
                                _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        yield '         '
                        yield str((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli))
                        yield '\n'
                    l_2_redistribute_route = l_2_redistribute_route_cli = missing
            if t_6(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast')):
                pass
                yield '      !\n      address-family ipv4 multicast\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'bgp'), 'additional_paths'), 'receive'), True):
                    pass
                    yield '         bgp additional-paths receive\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_6(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'receive'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' additional-paths receive\n'
                    if t_6(environment.getattr(l_2_neighbor, 'route_map_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_in'))
                        yield ' in\n'
                    if t_6(environment.getattr(l_2_neighbor, 'route_map_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_out'))
                        yield ' out\n'
                l_2_neighbor = missing
                for l_2_network in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'networks'), 'prefix'):
                    l_2_network_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_network_cli = str_join(('network ', environment.getattr(l_2_network, 'prefix'), ))
                    _loop_vars['network_cli'] = l_2_network_cli
                    if t_6(environment.getattr(l_2_network, 'route_map')):
                        pass
                        l_2_network_cli = str_join(((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli), ' route-map ', environment.getattr(l_2_network, 'route_map'), ))
                        _loop_vars['network_cli'] = l_2_network_cli
                    yield '         '
                    yield str((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli))
                    yield '\n'
                l_2_network = l_2_network_cli = missing
                if t_6(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'redistribute')):
                    pass
                    l_1_redistribute_var = environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'redistribute')
                    _loop_vars['redistribute_var'] = l_1_redistribute_var
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'enabled'), True):
                        pass
                        l_1_redistribute_host = 'redistribute attached-host'
                        _loop_vars['redistribute_host'] = l_1_redistribute_host
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'route_map')):
                            pass
                            l_1_redistribute_host = str_join(((undefined(name='redistribute_host') if l_1_redistribute_host is missing else l_1_redistribute_host), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'route_map'), ))
                            _loop_vars['redistribute_host'] = l_1_redistribute_host
                        yield '         '
                        yield str((undefined(name='redistribute_host') if l_1_redistribute_host is missing else l_1_redistribute_host))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'enabled'), True):
                        pass
                        l_1_redistribute_conn = 'redistribute connected'
                        _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'route_map')):
                            pass
                            l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'route_map'), ))
                            _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        yield '         '
                        yield str((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'enabled'), True):
                        pass
                        l_1_redistribute_isis = 'redistribute isis'
                        _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'isis_level')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'isis_level'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' include leaked', ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'route_map')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'route_map'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'rcf')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'rcf'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        yield '         '
                        yield str((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf = 'redistribute ospf'
                        _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'route_map')):
                            pass
                            l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'route_map'), ))
                            _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        yield '         '
                        yield str((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf))
                        yield '\n'
                    elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf = 'redistribute ospf match internal'
                        _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'route_map')):
                            pass
                            l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'route_map'), ))
                            _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        yield '         '
                        yield str((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3 = 'redistribute ospfv3'
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3))
                        yield '\n'
                    elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3 = 'redistribute ospfv3 match internal'
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3_match = 'redistribute ospfv3 match external'
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3_match = 'redistribute ospfv3 match nssa-external'
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf_match = 'redistribute ospf match external'
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf_match = 'redistribute ospf match nssa-external'
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type')):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type'), ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'enabled'), True):
                        pass
                        l_1_redistribute_static = 'redistribute static'
                        _loop_vars['redistribute_static'] = l_1_redistribute_static
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'route_map')):
                            pass
                            l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'route_map'), ))
                            _loop_vars['redistribute_static'] = l_1_redistribute_static
                        yield '         '
                        yield str((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static))
                        yield '\n'
                elif t_6(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'redistribute_routes')):
                    pass
                    for l_2_redistribute_route in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv4_multicast'), 'redistribute_routes'), 'source_protocol'):
                        l_2_redistribute_route_cli = missing
                        _loop_vars = {}
                        pass
                        l_2_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_2_redistribute_route, 'source_protocol'), ))
                        _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if (environment.getattr(l_2_redistribute_route, 'source_protocol') in ['ospf', 'ospfv3']):
                            pass
                            if t_6(environment.getattr(l_2_redistribute_route, 'ospf_route_type')):
                                pass
                                l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' match ', environment.getattr(l_2_redistribute_route, 'ospf_route_type'), ))
                                _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if t_6(environment.getattr(l_2_redistribute_route, 'include_leaked'), True):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' include leaked', ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if t_6(environment.getattr(l_2_redistribute_route, 'route_map')):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' route-map ', environment.getattr(l_2_redistribute_route, 'route_map'), ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        elif (environment.getattr(l_2_redistribute_route, 'source_protocol') == 'isis'):
                            pass
                            if t_6(environment.getattr(l_2_redistribute_route, 'rcf')):
                                pass
                                l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' rcf ', environment.getattr(l_2_redistribute_route, 'rcf'), ))
                                _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        yield '         '
                        yield str((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli))
                        yield '\n'
                    l_2_redistribute_route = l_2_redistribute_route_cli = missing
            if t_6(environment.getattr(l_1_vrf, 'address_family_ipv6')):
                pass
                yield '      !\n      address-family ipv6\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'install'), True):
                    pass
                    yield '         bgp additional-paths install\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'install_ecmp_primary'), True):
                    pass
                    yield '         bgp additional-paths install ecmp-primary\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'receive'), True):
                    pass
                    yield '         bgp additional-paths receive\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send')):
                    pass
                    if (environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send') == 'disabled'):
                        pass
                        yield '         no bgp additional-paths send\n'
                    elif (t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send') == 'ecmp')):
                        pass
                        yield '         bgp additional-paths send ecmp limit '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send_limit'))
                        yield '\n'
                    elif (environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send') == 'limit'):
                        pass
                        if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send_limit')):
                            pass
                            yield '         bgp additional-paths send limit '
                            yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send_limit'))
                            yield '\n'
                    else:
                        pass
                        yield '         bgp additional-paths send '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'additional_paths'), 'send'))
                        yield '\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_6(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'receive'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' additional-paths receive\n'
                    if t_6(environment.getattr(l_2_neighbor, 'route_map_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_in'))
                        yield ' in\n'
                    if t_6(environment.getattr(l_2_neighbor, 'route_map_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_out'))
                        yield ' out\n'
                    if t_6(environment.getattr(l_2_neighbor, 'rcf_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' rcf in '
                        yield str(environment.getattr(l_2_neighbor, 'rcf_in'))
                        yield '\n'
                    if t_6(environment.getattr(l_2_neighbor, 'rcf_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' rcf out '
                        yield str(environment.getattr(l_2_neighbor, 'rcf_out'))
                        yield '\n'
                    if t_6(environment.getattr(l_2_neighbor, 'prefix_list_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' prefix-list '
                        yield str(environment.getattr(l_2_neighbor, 'prefix_list_in'))
                        yield ' in\n'
                    if t_6(environment.getattr(l_2_neighbor, 'prefix_list_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' prefix-list '
                        yield str(environment.getattr(l_2_neighbor, 'prefix_list_out'))
                        yield ' out\n'
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send')):
                        pass
                        if (environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send') == 'disabled'):
                            pass
                            yield '         no neighbor '
                            yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                            yield ' additional-paths send\n'
                        elif (t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit')) and (environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send') == 'ecmp')):
                            pass
                            yield '         neighbor '
                            yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                            yield ' additional-paths send ecmp limit '
                            yield str(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit'))
                            yield '\n'
                        elif (environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send') == 'limit'):
                            pass
                            if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit')):
                                pass
                                yield '         neighbor '
                                yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                                yield ' additional-paths send limit '
                                yield str(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send_limit'))
                                yield '\n'
                        else:
                            pass
                            yield '         neighbor '
                            yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                            yield ' additional-paths send '
                            yield str(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'send'))
                            yield '\n'
                l_2_neighbor = missing
                for l_2_network in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'networks'), 'prefix'):
                    l_2_network_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_network_cli = str_join(('network ', environment.getattr(l_2_network, 'prefix'), ))
                    _loop_vars['network_cli'] = l_2_network_cli
                    if t_6(environment.getattr(l_2_network, 'route_map')):
                        pass
                        l_2_network_cli = str_join(((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli), ' route-map ', environment.getattr(l_2_network, 'route_map'), ))
                        _loop_vars['network_cli'] = l_2_network_cli
                    yield '         '
                    yield str((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli))
                    yield '\n'
                l_2_network = l_2_network_cli = missing
                if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'redistribute_internal'), True):
                    pass
                    yield '         bgp redistribute-internal\n'
                elif t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'bgp'), 'redistribute_internal'), False):
                    pass
                    yield '         no bgp redistribute-internal\n'
                if t_6(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'redistribute')):
                    pass
                    l_1_redistribute_var = environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'redistribute')
                    _loop_vars['redistribute_var'] = l_1_redistribute_var
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'enabled'), True):
                        pass
                        l_1_redistribute_host = 'redistribute attached-host'
                        _loop_vars['redistribute_host'] = l_1_redistribute_host
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'route_map')):
                            pass
                            l_1_redistribute_host = str_join(((undefined(name='redistribute_host') if l_1_redistribute_host is missing else l_1_redistribute_host), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'attached_host'), 'route_map'), ))
                            _loop_vars['redistribute_host'] = l_1_redistribute_host
                        yield '         '
                        yield str((undefined(name='redistribute_host') if l_1_redistribute_host is missing else l_1_redistribute_host))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'bgp'), 'enabled'), True):
                        pass
                        l_1_redistribute_bgp = 'redistribute bgp leaked'
                        _loop_vars['redistribute_bgp'] = l_1_redistribute_bgp
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'bgp'), 'route_map')):
                            pass
                            l_1_redistribute_bgp = str_join(((undefined(name='redistribute_bgp') if l_1_redistribute_bgp is missing else l_1_redistribute_bgp), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'bgp'), 'route_map'), ))
                            _loop_vars['redistribute_bgp'] = l_1_redistribute_bgp
                        yield '         '
                        yield str((undefined(name='redistribute_bgp') if l_1_redistribute_bgp is missing else l_1_redistribute_bgp))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dhcp'), 'enabled'), True):
                        pass
                        l_1_redistribute_dhcp = 'redistribute dhcp'
                        _loop_vars['redistribute_dhcp'] = l_1_redistribute_dhcp
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dhcp'), 'route_map')):
                            pass
                            l_1_redistribute_dhcp = str_join(((undefined(name='redistribute_dhcp') if l_1_redistribute_dhcp is missing else l_1_redistribute_dhcp), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dhcp'), 'route_map'), ))
                            _loop_vars['redistribute_dhcp'] = l_1_redistribute_dhcp
                        yield '         '
                        yield str((undefined(name='redistribute_dhcp') if l_1_redistribute_dhcp is missing else l_1_redistribute_dhcp))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'enabled'), True):
                        pass
                        l_1_redistribute_conn = 'redistribute connected'
                        _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' include leaked', ))
                            _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'route_map')):
                            pass
                            l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'route_map'), ))
                            _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'rcf')):
                            pass
                            l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'rcf'), ))
                            _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        yield '         '
                        yield str((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'enabled'), True):
                        pass
                        l_1_redistribute_dynamic = 'redistribute dynamic'
                        _loop_vars['redistribute_dynamic'] = l_1_redistribute_dynamic
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'route_map')):
                            pass
                            l_1_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_1_redistribute_dynamic is missing else l_1_redistribute_dynamic), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'route_map'), ))
                            _loop_vars['redistribute_dynamic'] = l_1_redistribute_dynamic
                        elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'rcf')):
                            pass
                            l_1_redistribute_dynamic = str_join(((undefined(name='redistribute_dynamic') if l_1_redistribute_dynamic is missing else l_1_redistribute_dynamic), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'dynamic'), 'rcf'), ))
                            _loop_vars['redistribute_dynamic'] = l_1_redistribute_dynamic
                        yield '         '
                        yield str((undefined(name='redistribute_dynamic') if l_1_redistribute_dynamic is missing else l_1_redistribute_dynamic))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'user'), 'enabled'), True):
                        pass
                        l_1_redistribute_user = 'redistribute user'
                        _loop_vars['redistribute_user'] = l_1_redistribute_user
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'user'), 'rcf')):
                            pass
                            l_1_redistribute_user = str_join(((undefined(name='redistribute_user') if l_1_redistribute_user is missing else l_1_redistribute_user), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'user'), 'rcf'), ))
                            _loop_vars['redistribute_user'] = l_1_redistribute_user
                        yield '         '
                        yield str((undefined(name='redistribute_user') if l_1_redistribute_user is missing else l_1_redistribute_user))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'enabled'), True):
                        pass
                        l_1_redistribute_isis = 'redistribute isis'
                        _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'isis_level')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'isis_level'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' include leaked', ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'route_map')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'route_map'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'rcf')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'rcf'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        yield '         '
                        yield str((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3 = 'redistribute ospfv3'
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' include leaked', ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3))
                        yield '\n'
                    elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3 = 'redistribute ospfv3 match internal'
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' include leaked', ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3_match = 'redistribute ospfv3 match external'
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' include leaked', ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3_match = 'redistribute ospfv3 match nssa-external'
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' include leaked', ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'enabled'), True):
                        pass
                        l_1_redistribute_static = 'redistribute static'
                        _loop_vars['redistribute_static'] = l_1_redistribute_static
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' include leaked', ))
                            _loop_vars['redistribute_static'] = l_1_redistribute_static
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'route_map')):
                            pass
                            l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'route_map'), ))
                            _loop_vars['redistribute_static'] = l_1_redistribute_static
                        elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'rcf')):
                            pass
                            l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'rcf'), ))
                            _loop_vars['redistribute_static'] = l_1_redistribute_static
                        yield '         '
                        yield str((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static))
                        yield '\n'
                elif t_6(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'redistribute_routes')):
                    pass
                    for l_2_redistribute_route in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6'), 'redistribute_routes'), 'source_protocol'):
                        l_2_redistribute_route_cli = missing
                        _loop_vars = {}
                        pass
                        l_2_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_2_redistribute_route, 'source_protocol'), ))
                        _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if (environment.getattr(l_2_redistribute_route, 'source_protocol') == 'ospfv3'):
                            pass
                            if t_6(environment.getattr(l_2_redistribute_route, 'ospf_route_type')):
                                pass
                                l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' match ', environment.getattr(l_2_redistribute_route, 'ospf_route_type'), ))
                                _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if (environment.getattr(l_2_redistribute_route, 'source_protocol') == 'bgp'):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' leaked', ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        elif (t_6(environment.getattr(l_2_redistribute_route, 'include_leaked'), True) and (environment.getattr(l_2_redistribute_route, 'source_protocol') in ['connected', 'isis', 'ospfv3', 'static'])):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' include leaked', ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if t_6(environment.getattr(l_2_redistribute_route, 'route_map')):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' route-map ', environment.getattr(l_2_redistribute_route, 'route_map'), ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        elif (environment.getattr(l_2_redistribute_route, 'source_protocol') in ['connected', 'static', 'isis', 'user', 'dynamic']):
                            pass
                            if t_6(environment.getattr(l_2_redistribute_route, 'rcf')):
                                pass
                                l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' rcf ', environment.getattr(l_2_redistribute_route, 'rcf'), ))
                                _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        yield '         '
                        yield str((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli))
                        yield '\n'
                    l_2_redistribute_route = l_2_redistribute_route_cli = missing
            if t_6(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast')):
                pass
                yield '      !\n      address-family ipv6 multicast\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action')):
                    pass
                    yield '         bgp missing-policy direction in action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_in_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action')):
                    pass
                    yield '         bgp missing-policy direction out action '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'bgp'), 'missing_policy'), 'direction_out_action'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'bgp'), 'additional_paths'), 'receive'), True):
                    pass
                    yield '         bgp additional-paths receive\n'
                for l_2_neighbor in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'neighbors'), 'ip_address'):
                    _loop_vars = {}
                    pass
                    if t_6(environment.getattr(l_2_neighbor, 'activate'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' activate\n'
                    if t_6(environment.getattr(environment.getattr(l_2_neighbor, 'additional_paths'), 'receive'), True):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' additional-paths receive\n'
                    if t_6(environment.getattr(l_2_neighbor, 'route_map_in')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_in'))
                        yield ' in\n'
                    if t_6(environment.getattr(l_2_neighbor, 'route_map_out')):
                        pass
                        yield '         neighbor '
                        yield str(environment.getattr(l_2_neighbor, 'ip_address'))
                        yield ' route-map '
                        yield str(environment.getattr(l_2_neighbor, 'route_map_out'))
                        yield ' out\n'
                l_2_neighbor = missing
                for l_2_network in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'networks'), 'prefix'):
                    l_2_network_cli = missing
                    _loop_vars = {}
                    pass
                    l_2_network_cli = str_join(('network ', environment.getattr(l_2_network, 'prefix'), ))
                    _loop_vars['network_cli'] = l_2_network_cli
                    if t_6(environment.getattr(l_2_network, 'route_map')):
                        pass
                        l_2_network_cli = str_join(((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli), ' route-map ', environment.getattr(l_2_network, 'route_map'), ))
                        _loop_vars['network_cli'] = l_2_network_cli
                    yield '         '
                    yield str((undefined(name='network_cli') if l_2_network_cli is missing else l_2_network_cli))
                    yield '\n'
                l_2_network = l_2_network_cli = missing
                if t_6(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'redistribute')):
                    pass
                    l_1_redistribute_var = environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'redistribute')
                    _loop_vars['redistribute_var'] = l_1_redistribute_var
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'enabled'), True):
                        pass
                        l_1_redistribute_conn = 'redistribute connected'
                        _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'route_map')):
                            pass
                            l_1_redistribute_conn = str_join(((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'connected'), 'route_map'), ))
                            _loop_vars['redistribute_conn'] = l_1_redistribute_conn
                        yield '         '
                        yield str((undefined(name='redistribute_conn') if l_1_redistribute_conn is missing else l_1_redistribute_conn))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'enabled'), True):
                        pass
                        l_1_redistribute_isis = 'redistribute isis'
                        _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'isis_level')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'isis_level'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'include_leaked'), True):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' include leaked', ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'route_map')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'route_map'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        elif t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'rcf')):
                            pass
                            l_1_redistribute_isis = str_join(((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis), ' rcf ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'isis'), 'rcf'), ))
                            _loop_vars['redistribute_isis'] = l_1_redistribute_isis
                        yield '         '
                        yield str((undefined(name='redistribute_isis') if l_1_redistribute_isis is missing else l_1_redistribute_isis))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf = 'redistribute ospf'
                        _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'route_map')):
                            pass
                            l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'route_map'), ))
                            _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        yield '         '
                        yield str((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf))
                        yield '\n'
                    elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf = 'redistribute ospf match internal'
                        _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'route_map')):
                            pass
                            l_1_redistribute_ospf = str_join(((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_internal'), 'route_map'), ))
                            _loop_vars['redistribute_ospf'] = l_1_redistribute_ospf
                        yield '         '
                        yield str((undefined(name='redistribute_ospf') if l_1_redistribute_ospf is missing else l_1_redistribute_ospf))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3 = 'redistribute ospfv3'
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3))
                        yield '\n'
                    elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3 = 'redistribute ospfv3 match internal'
                        _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3 = str_join(((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_internal'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3'] = l_1_redistribute_ospfv3
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3') if l_1_redistribute_ospfv3 is missing else l_1_redistribute_ospfv3))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3_match = 'redistribute ospfv3 match external'
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospfv3_match = 'redistribute ospfv3 match nssa-external'
                        _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'nssa_type'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospfv3_match = str_join(((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospfv3_match'] = l_1_redistribute_ospfv3_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospfv3_match') if l_1_redistribute_ospfv3_match is missing else l_1_redistribute_ospfv3_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf_match = 'redistribute ospf match external'
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'enabled'), True):
                        pass
                        l_1_redistribute_ospf_match = 'redistribute ospf match nssa-external'
                        _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type')):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'nssa_type'), ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map')):
                            pass
                            l_1_redistribute_ospf_match = str_join(((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'ospf'), 'match_nssa_external'), 'route_map'), ))
                            _loop_vars['redistribute_ospf_match'] = l_1_redistribute_ospf_match
                        yield '         '
                        yield str((undefined(name='redistribute_ospf_match') if l_1_redistribute_ospf_match is missing else l_1_redistribute_ospf_match))
                        yield '\n'
                    if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'enabled'), True):
                        pass
                        l_1_redistribute_static = 'redistribute static'
                        _loop_vars['redistribute_static'] = l_1_redistribute_static
                        if t_6(environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'route_map')):
                            pass
                            l_1_redistribute_static = str_join(((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static), ' route-map ', environment.getattr(environment.getattr((undefined(name='redistribute_var') if l_1_redistribute_var is missing else l_1_redistribute_var), 'static'), 'route_map'), ))
                            _loop_vars['redistribute_static'] = l_1_redistribute_static
                        yield '         '
                        yield str((undefined(name='redistribute_static') if l_1_redistribute_static is missing else l_1_redistribute_static))
                        yield '\n'
                elif t_6(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'redistribute_routes')):
                    pass
                    for l_2_redistribute_route in t_3(environment.getattr(environment.getattr(l_1_vrf, 'address_family_ipv6_multicast'), 'redistribute_routes'), 'source_protocol'):
                        l_2_redistribute_route_cli = missing
                        _loop_vars = {}
                        pass
                        l_2_redistribute_route_cli = str_join(('redistribute ', environment.getattr(l_2_redistribute_route, 'source_protocol'), ))
                        _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if (environment.getattr(l_2_redistribute_route, 'source_protocol') in ['ospf', 'ospfv3']):
                            pass
                            if t_6(environment.getattr(l_2_redistribute_route, 'ospf_route_type')):
                                pass
                                l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' match ', environment.getattr(l_2_redistribute_route, 'ospf_route_type'), ))
                                _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if t_6(environment.getattr(l_2_redistribute_route, 'include_leaked'), True):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' include leaked', ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        if t_6(environment.getattr(l_2_redistribute_route, 'route_map')):
                            pass
                            l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' route-map ', environment.getattr(l_2_redistribute_route, 'route_map'), ))
                            _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        elif (environment.getattr(l_2_redistribute_route, 'source_protocol') == 'isis'):
                            pass
                            if t_6(environment.getattr(l_2_redistribute_route, 'rcf')):
                                pass
                                l_2_redistribute_route_cli = str_join(((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli), ' rcf ', environment.getattr(l_2_redistribute_route, 'rcf'), ))
                                _loop_vars['redistribute_route_cli'] = l_2_redistribute_route_cli
                        yield '         '
                        yield str((undefined(name='redistribute_route_cli') if l_2_redistribute_route_cli is missing else l_2_redistribute_route_cli))
                        yield '\n'
                    l_2_redistribute_route = l_2_redistribute_route_cli = missing
            if t_6(environment.getattr(l_1_vrf, 'evpn_multicast'), True):
                pass
                yield '      evpn multicast\n'
                if t_6(environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_gateway_dr_election'), 'algorithm')):
                    pass
                    if (environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_gateway_dr_election'), 'algorithm') == 'preference'):
                        pass
                        if t_6(environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_gateway_dr_election'), 'preference_value')):
                            pass
                            yield '         gateway dr election algorithm preference '
                            yield str(environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_gateway_dr_election'), 'preference_value'))
                            yield '\n'
                    else:
                        pass
                        yield '         gateway dr election algorithm '
                        yield str(environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_gateway_dr_election'), 'algorithm'))
                        yield '\n'
                if (t_6(environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_address_family'), 'ipv4')) and t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_address_family'), 'ipv4'), 'transit'), True)):
                    pass
                    yield '         address-family ipv4\n'
                    if t_6(environment.getattr(environment.getattr(environment.getattr(l_1_vrf, 'evpn_multicast_address_family'), 'ipv4'), 'transit'), True):
                        pass
                        yield '            transit\n'
            if t_6(environment.getattr(l_1_vrf, 'eos_cli')):
                pass
                yield '      !\n      '
                yield str(t_4(environment.getattr(l_1_vrf, 'eos_cli'), 6, False))
                yield '\n'
        l_1_vrf = l_1_paths_cli = l_1_redistribute_var = l_1_redistribute_conn = l_1_redistribute_isis = l_1_redistribute_ospf = l_1_redistribute_ospf_match = l_1_redistribute_ospfv3 = l_1_redistribute_ospfv3_match = l_1_redistribute_static = l_1_redistribute_rip = l_1_redistribute_host = l_1_redistribute_dynamic = l_1_redistribute_bgp = l_1_redistribute_user = l_1_redistribute_dhcp = missing
        for l_1_session_tracker in t_3(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'session_trackers'), 'name'):
            _loop_vars = {}
            pass
            yield '   session tracker '
            yield str(environment.getattr(l_1_session_tracker, 'name'))
            yield '\n'
            if t_6(environment.getattr(l_1_session_tracker, 'recovery_delay')):
                pass
                yield '      recovery delay '
                yield str(environment.getattr(l_1_session_tracker, 'recovery_delay'))
                yield ' seconds\n'
        l_1_session_tracker = missing
        if t_6(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'eos_cli')):
            pass
            yield '   !\n   '
            yield str(t_4(environment.getattr((undefined(name='router_bgp') if l_0_router_bgp is missing else l_0_router_bgp), 'eos_cli'), 3, False))
            yield '\n'

blocks = {}
debug_info = '7=85&9=88&10=90&11=93&13=95&14=98&16=100&19=103&22=106&24=109&27=112&29=115&32=118&33=120&34=123&35=125&37=128&38=130&39=132&41=135&42=137&45=141&47=143&48=145&49=148&50=150&52=154&54=156&55=158&56=161&58=163&59=166&63=169&64=172&66=174&68=177&69=179&70=182&71=184&75=187&76=189&77=192&78=194&80=198&82=200&83=202&84=205&85=207&87=211&89=213&90=217&92=220&95=223&98=226&99=228&101=231&102=234&103=236&104=238&105=241&108=246&111=248&113=250&112=254&114=258&115=260&116=262&118=264&119=266&120=268&121=270&122=272&124=275&127=278&130=281&132=284&133=287&135=289&136=301&137=303&138=306&140=310&141=313&143=315&144=318&146=320&147=323&149=325&150=328&152=330&153=332&154=334&155=336&156=338&157=340&160=343&161=345&162=348&164=350&165=353&167=355&168=358&170=360&171=363&173=367&174=370&176=374&177=377&179=379&180=382&182=386&183=389&184=391&187=394&190=402&191=405&193=409&194=411&195=413&196=415&198=418&200=420&201=422&202=424&203=426&205=429&206=431&207=433&208=436&210=438&211=441&213=445&214=448&216=452&217=455&219=457&220=460&222=464&223=467&225=471&226=474&228=478&229=481&231=485&232=488&234=492&235=495&237=501&238=503&239=505&240=507&242=509&243=511&245=514&247=516&248=519&249=521&250=524&252=528&253=530&254=532&255=534&257=536&258=538&260=541&262=543&263=545&264=550&265=552&266=554&267=556&268=558&269=560&270=562&271=564&273=566&274=568&276=570&277=572&280=574&281=577&285=580&286=582&287=584&288=586&290=589&292=591&293=593&294=595&295=597&297=600&298=602&299=605&302=608&303=619&304=622&306=626&307=629&309=633&310=636&312=638&313=641&315=643&316=646&318=648&319=650&320=652&321=654&322=656&323=658&326=661&327=663&328=666&330=668&331=671&333=673&334=676&336=678&337=681&339=685&340=688&342=692&343=695&345=697&346=700&348=704&349=707&350=709&353=712&355=720&356=723&358=725&359=728&361=732&362=734&363=736&364=738&366=741&368=743&369=745&370=747&371=749&373=752&374=754&375=756&376=759&378=761&379=764&381=768&382=771&384=775&385=778&386=780&387=783&389=785&390=788&392=792&393=795&395=799&396=802&398=806&399=809&401=813&402=816&404=822&405=825&407=829&408=831&409=833&410=835&412=837&413=839&415=842&417=844&418=847&419=849&420=852&422=856&423=858&424=860&425=862&427=864&428=866&430=869&432=871&433=873&434=878&435=880&436=882&437=884&438=886&439=888&440=890&441=892&443=894&444=896&446=898&447=900&450=902&451=905&455=908&456=910&457=912&458=914&460=917&462=919&463=921&464=923&465=925&467=928&468=930&469=933&472=936&474=939&477=942&478=946&479=948&480=950&482=952&483=954&485=956&486=958&488=960&489=962&491=964&492=966&494=969&496=972&497=974&498=977&499=979&500=982&501=984&503=987&504=989&505=992&506=994&508=998&510=1000&511=1002&512=1005&513=1007&515=1010&516=1012&518=1015&519=1017&520=1020&521=1022&523=1026&525=1028&526=1030&527=1033&528=1035&530=1038&531=1040&533=1044&534=1046&535=1048&536=1051&537=1053&539=1056&540=1058&542=1062&544=1064&545=1066&546=1069&547=1071&549=1074&550=1076&552=1080&554=1082&555=1084&556=1087&557=1089&559=1092&560=1094&562=1097&563=1099&565=1103&567=1105&568=1107&569=1110&570=1112&572=1115&573=1117&575=1121&576=1123&577=1125&578=1128&579=1130&581=1133&582=1135&584=1139&586=1141&587=1143&588=1146&589=1148&591=1151&592=1153&594=1157&596=1159&597=1161&598=1164&599=1166&601=1169&602=1171&604=1174&605=1176&607=1180&609=1182&610=1184&611=1187&612=1189&614=1192&615=1194&616=1197&617=1199&619=1203&621=1205&622=1207&623=1210&624=1212&626=1216&628=1218&629=1220&630=1223&631=1225&633=1229&635=1231&636=1233&637=1236&638=1238&639=1241&640=1243&642=1247&644=1249&645=1251&646=1254&647=1256&649=1260&651=1262&652=1264&653=1267&654=1269&656=1273&658=1275&659=1277&660=1281&661=1283&662=1285&663=1287&666=1289&667=1291&668=1293&669=1295&671=1297&672=1299&673=1301&674=1303&675=1305&678=1308&681=1311&682=1314&683=1317&684=1323&685=1326&689=1333&690=1335&692=1339&693=1341&694=1344&696=1346&697=1349&699=1353&700=1357&702=1360&703=1364&705=1367&706=1371&708=1374&709=1378&711=1383&712=1387&714=1392&715=1396&717=1401&718=1405&720=1408&721=1412&723=1415&725=1418&730=1421&731=1423&733=1427&734=1430&735=1432&736=1435&738=1437&739=1440&741=1442&744=1445&747=1448&748=1451&750=1453&751=1456&753=1459&754=1461&761=1467&763=1471&764=1473&765=1476&767=1478&768=1481&770=1485&771=1489&773=1492&774=1496&776=1499&777=1503&779=1506&780=1510&782=1515&783=1519&785=1524&786=1528&788=1533&789=1537&791=1540&792=1544&794=1548&795=1550&797=1553&802=1556&805=1559&808=1562&811=1565&813=1568&816=1571&817=1573&819=1576&820=1579&821=1581&822=1583&823=1586&826=1591&828=1593&830=1596&832=1599&834=1602&835=1605&836=1607&837=1610&839=1612&842=1615&843=1617&844=1620&845=1622&847=1626&849=1628&850=1630&851=1633&852=1636&853=1638&854=1639&855=1641&856=1642&857=1644&860=1646&861=1649&864=1651&865=1656&866=1659&867=1661&868=1664&870=1666&871=1669&873=1671&874=1674&876=1678&877=1681&879=1685&880=1688&882=1692&883=1695&885=1699&886=1701&887=1703&888=1705&889=1707&890=1709&892=1712&894=1714&895=1716&896=1719&897=1721&898=1724&899=1728&900=1730&901=1733&904=1740&907=1744&908=1746&909=1748&910=1750&912=1753&914=1755&915=1758&918=1761&919=1766&920=1769&921=1771&922=1774&924=1776&925=1779&927=1781&928=1784&930=1788&931=1791&933=1795&934=1798&936=1802&937=1805&939=1809&940=1811&941=1813&942=1815&943=1817&944=1819&946=1822&948=1824&949=1826&950=1829&951=1831&952=1834&953=1838&954=1840&955=1843&958=1850&961=1854&962=1856&963=1858&964=1860&966=1863&969=1866&970=1869&972=1871&973=1874&975=1876&978=1879&981=1882&982=1884&983=1887&984=1889&986=1893&988=1895&990=1898&991=1900&992=1903&993=1905&995=1908&996=1910&998=1913&999=1915&1001=1918&1002=1921&1005=1923&1006=1925&1007=1928&1008=1930&1010=1934&1012=1936&1015=1939&1017=1943&1018=1945&1019=1948&1021=1950&1022=1953&1027=1956&1030=1959&1031=1962&1033=1964&1034=1967&1036=1969&1037=1972&1038=1975&1039=1977&1040=1980&1043=1983&1044=1986&1045=1989&1050=1992&1053=1995&1054=1998&1056=2000&1057=2003&1059=2005&1060=2008&1061=2011&1062=2013&1063=2016&1066=2019&1067=2022&1068=2025&1073=2028&1076=2031&1078=2034&1081=2037&1084=2040&1085=2042&1087=2045&1088=2048&1089=2050&1090=2052&1091=2055&1094=2060&1097=2062&1098=2068&1099=2071&1100=2073&1101=2076&1103=2078&1104=2081&1106=2083&1107=2086&1109=2090&1110=2093&1112=2097&1113=2100&1115=2104&1116=2107&1118=2111&1119=2114&1121=2118&1122=2121&1124=2125&1125=2127&1126=2129&1127=2131&1129=2133&1130=2135&1132=2138&1134=2140&1135=2142&1136=2145&1138=2149&1139=2151&1140=2153&1141=2155&1142=2157&1145=2161&1147=2163&1148=2165&1150=2167&1151=2170&1155=2172&1156=2174&1157=2176&1158=2178&1160=2181&1163=2184&1164=2190&1165=2193&1166=2195&1167=2198&1169=2200&1170=2203&1172=2205&1173=2208&1175=2212&1176=2215&1178=2219&1179=2222&1181=2226&1182=2229&1184=2233&1185=2236&1187=2240&1188=2243&1190=2247&1191=2249&1192=2251&1193=2253&1195=2255&1196=2257&1198=2260&1200=2262&1201=2264&1202=2267&1204=2271&1205=2273&1206=2275&1207=2277&1208=2279&1211=2283&1213=2285&1214=2287&1216=2289&1217=2292&1221=2294&1222=2296&1223=2298&1224=2300&1225=2302&1227=2305&1229=2310&1233=2313&1234=2316&1235=2319&1237=2326&1240=2329&1242=2332&1245=2335&1246=2337&1247=2340&1248=2342&1249=2345&1250=2347&1252=2351&1254=2353&1255=2355&1256=2358&1257=2360&1259=2364&1261=2366&1262=2368&1263=2371&1264=2373&1266=2376&1267=2378&1268=2381&1269=2383&1271=2387&1273=2389&1274=2391&1275=2394&1276=2396&1277=2399&1278=2401&1280=2405&1282=2407&1283=2409&1284=2412&1285=2414&1287=2418&1289=2420&1290=2422&1291=2425&1292=2427&1294=2430&1295=2432&1297=2435&1298=2437&1299=2440&1300=2442&1302=2446&1304=2448&1305=2450&1306=2453&1307=2455&1309=2458&1310=2460&1312=2464&1313=2466&1314=2468&1315=2471&1316=2473&1318=2476&1319=2478&1321=2482&1323=2484&1324=2486&1325=2489&1326=2491&1328=2494&1329=2496&1331=2500&1332=2502&1333=2504&1334=2507&1335=2509&1337=2512&1338=2514&1340=2518&1342=2520&1343=2522&1344=2525&1345=2527&1347=2530&1348=2532&1350=2536&1352=2538&1353=2540&1354=2543&1355=2545&1357=2548&1358=2550&1360=2553&1361=2555&1363=2559&1365=2561&1366=2563&1367=2566&1368=2568&1370=2571&1371=2573&1373=2577&1375=2579&1376=2581&1377=2584&1378=2586&1380=2589&1381=2591&1383=2594&1384=2596&1386=2600&1388=2602&1389=2604&1390=2607&1391=2609&1393=2613&1395=2615&1396=2617&1397=2620&1398=2622&1400=2625&1401=2627&1402=2630&1403=2632&1405=2636&1407=2638&1408=2640&1409=2644&1410=2646&1411=2648&1412=2650&1415=2652&1416=2654&1417=2656&1418=2658&1420=2660&1421=2662&1422=2664&1423=2666&1424=2668&1427=2671&1432=2674&1435=2677&1438=2680&1439=2682&1440=2687&1441=2689&1442=2691&1443=2693&1444=2695&1445=2697&1446=2699&1447=2701&1449=2703&1450=2705&1452=2707&1453=2709&1456=2711&1457=2714&1461=2717&1464=2720&1465=2722&1467=2725&1468=2728&1469=2730&1470=2732&1471=2735&1474=2740&1477=2742&1480=2745&1483=2748&1484=2750&1485=2753&1486=2756&1487=2758&1488=2759&1489=2761&1490=2763&1492=2764&1493=2766&1496=2768&1497=2771&1500=2773&1501=2777&1502=2780&1504=2785&1506=2787&1507=2790&1509=2792&1510=2795&1512=2797&1513=2800&1515=2804&1516=2807&1518=2811&1519=2814&1521=2818&1522=2821&1524=2825&1525=2828&1527=2832&1528=2834&1529=2837&1530=2839&1531=2842&1532=2846&1533=2848&1534=2851&1537=2858&1540=2862&1541=2865&1543=2867&1544=2870&1546=2872&1547=2875&1548=2879&1549=2882&1551=2886&1552=2888&1553=2890&1554=2892&1556=2895&1558=2897&1559=2899&1560=2904&1561=2906&1562=2908&1563=2910&1564=2912&1565=2914&1566=2916&1567=2918&1569=2920&1570=2922&1572=2924&1573=2926&1576=2928&1577=2931&1581=2934&1582=2937&1584=2939&1585=2942&1588=2945&1589=2949&1590=2952&1592=2957&1594=2959&1595=2962&1597=2964&1598=2967&1600=2969&1601=2972&1603=2976&1604=2979&1606=2983&1607=2986&1609=2990&1610=2993&1612=2997&1613=3000&1615=3004&1616=3006&1617=3009&1618=3011&1619=3014&1620=3018&1621=3020&1622=3023&1625=3030&1628=3034&1629=3037&1631=3039&1632=3042&1634=3044&1635=3047&1636=3051&1637=3054&1639=3058&1640=3060&1641=3062&1642=3064&1644=3067&1646=3069&1647=3071&1648=3076&1649=3078&1650=3080&1651=3082&1652=3084&1653=3086&1654=3088&1655=3090&1657=3092&1658=3094&1660=3096&1661=3098&1664=3100&1665=3103&1669=3106&1670=3109&1672=3111&1673=3114&1676=3117&1677=3119&1678=3123&1679=3125&1680=3127&1682=3130&1685=3133&1686=3135&1687=3139&1688=3141&1689=3143&1691=3146&1694=3149&1697=3152&1698=3155&1700=3157&1703=3160&1704=3162&1705=3166&1706=3168&1707=3170&1709=3173&1712=3176&1713=3178&1714=3181&1715=3184&1721=3187&1724=3190&1727=3193&1728=3196&1729=3199&1730=3201&1731=3204&1733=3206&1734=3209&1736=3211&1737=3214&1739=3218&1740=3221&1743=3226&1744=3229&1745=3232&1746=3234&1747=3237&1749=3239&1750=3242&1752=3244&1753=3247&1755=3251&1756=3254&1759=3259&1760=3261&1761=3264&1762=3266&1763=3269&1764=3271&1766=3275&1768=3277&1769=3279&1770=3282&1771=3284&1773=3288&1775=3290&1776=3292&1777=3295&1778=3297&1780=3300&1781=3302&1783=3305&1784=3307&1785=3310&1786=3312&1788=3316&1790=3318&1791=3320&1792=3323&1793=3325&1795=3329&1796=3331&1797=3333&1798=3336&1799=3338&1801=3342&1803=3344&1804=3346&1805=3349&1806=3351&1808=3355&1809=3357&1810=3359&1811=3362&1812=3364&1814=3368&1816=3370&1817=3372&1818=3375&1819=3377&1821=3381&1823=3383&1824=3385&1825=3388&1826=3390&1828=3393&1829=3395&1831=3399&1833=3401&1834=3403&1835=3406&1836=3408&1838=3412&1840=3414&1841=3416&1842=3419&1843=3421&1845=3424&1846=3426&1848=3430&1850=3432&1851=3434&1852=3437&1853=3439&1855=3443&1857=3445&1858=3447&1859=3451&1860=3453&1861=3455&1862=3457&1865=3459&1866=3461&1868=3463&1869=3465&1870=3467&1871=3469&1873=3472&1878=3475&1881=3478&1882=3481&1883=3484&1884=3486&1885=3489&1887=3491&1888=3494&1890=3498&1891=3501&1894=3506&1895=3509&1896=3512&1897=3514&1898=3517&1900=3519&1901=3522&1903=3526&1904=3529&1909=3534&1912=3537&1914=3540&1917=3543&1920=3546&1921=3548&1923=3551&1924=3554&1925=3556&1926=3558&1927=3561&1930=3566&1933=3568&1934=3572&1935=3575&1936=3577&1937=3580&1939=3582&1940=3585&1942=3587&1943=3590&1945=3594&1946=3597&1948=3601&1949=3604&1951=3608&1952=3611&1954=3615&1955=3618&1957=3622&1958=3625&1960=3629&1961=3631&1962=3634&1964=3638&1965=3640&1966=3642&1967=3644&1968=3646&1971=3650&1973=3652&1974=3654&1976=3656&1977=3659&1982=3662&1983=3666&1984=3669&1985=3671&1986=3674&1988=3676&1989=3679&1991=3681&1992=3684&1994=3688&1995=3691&1997=3695&1998=3698&2000=3702&2001=3705&2003=3709&2004=3712&2006=3716&2007=3719&2009=3723&2010=3725&2011=3728&2013=3732&2014=3734&2015=3736&2016=3738&2017=3740&2020=3744&2022=3746&2023=3748&2025=3750&2026=3753&2031=3756&2032=3759&2033=3762&2035=3769&2038=3772&2040=3775&2043=3778&2044=3780&2045=3783&2046=3785&2047=3788&2048=3790&2050=3794&2052=3796&2053=3798&2054=3801&2055=3803&2057=3807&2059=3809&2060=3811&2061=3814&2062=3816&2064=3820&2066=3822&2067=3824&2068=3827&2069=3829&2071=3832&2072=3834&2073=3837&2074=3839&2076=3843&2078=3845&2079=3847&2080=3850&2081=3852&2082=3855&2083=3857&2085=3861&2087=3863&2088=3865&2089=3868&2090=3870&2092=3874&2094=3876&2095=3878&2096=3881&2097=3883&2099=3886&2100=3888&2102=3891&2103=3893&2104=3896&2105=3898&2107=3902&2109=3904&2110=3906&2111=3909&2112=3911&2114=3914&2115=3916&2117=3920&2118=3922&2119=3924&2120=3927&2121=3929&2123=3932&2124=3934&2126=3938&2128=3940&2129=3942&2130=3945&2131=3947&2133=3950&2134=3952&2136=3956&2138=3958&2139=3960&2140=3963&2141=3965&2143=3968&2144=3970&2146=3973&2147=3975&2149=3979&2151=3981&2152=3983&2153=3986&2154=3988&2156=3991&2157=3993&2158=3996&2159=3998&2161=4002&2163=4004&2164=4006&2165=4010&2166=4012&2167=4014&2168=4016&2171=4018&2172=4020&2173=4022&2174=4024&2176=4026&2177=4028&2178=4030&2179=4032&2180=4034&2183=4037&2188=4040&2191=4043&2192=4046&2194=4048&2195=4051&2197=4053&2200=4056&2201=4059&2202=4062&2203=4064&2204=4067&2206=4069&2207=4072&2210=4075&2211=4078&2212=4081&2214=4083&2215=4086&2217=4088&2218=4091&2220=4095&2221=4098&2224=4103&2225=4107&2226=4109&2227=4111&2229=4114&2231=4117&2232=4119&2233=4122&2234=4124&2235=4127&2236=4129&2238=4133&2240=4135&2241=4137&2242=4140&2243=4142&2245=4145&2246=4147&2248=4150&2249=4152&2250=4155&2251=4157&2253=4161&2255=4163&2256=4165&2257=4168&2258=4170&2260=4174&2261=4176&2262=4178&2263=4181&2264=4183&2266=4187&2268=4189&2269=4191&2270=4194&2271=4196&2273=4200&2274=4202&2275=4204&2276=4207&2277=4209&2279=4213&2281=4215&2282=4217&2283=4220&2284=4222&2286=4226&2288=4228&2289=4230&2290=4233&2291=4235&2293=4238&2294=4240&2296=4244&2298=4246&2299=4248&2300=4251&2301=4253&2303=4257&2305=4259&2306=4261&2307=4264&2308=4266&2310=4269&2311=4271&2313=4275&2315=4277&2316=4279&2317=4282&2318=4284&2320=4288&2322=4290&2323=4292&2324=4296&2325=4298&2326=4300&2327=4302&2330=4304&2331=4306&2333=4308&2334=4310&2335=4312&2336=4314&2338=4317&2343=4320&2346=4323&2347=4326&2348=4329&2349=4331&2350=4334&2352=4336&2353=4339&2355=4343&2356=4346&2359=4351&2360=4354&2361=4357&2362=4359&2363=4362&2365=4364&2366=4367&2368=4371&2369=4374&2374=4379&2377=4382&2378=4385&2380=4387&2381=4390&2383=4392&2384=4395&2385=4398&2386=4400&2387=4403&2389=4405&2390=4408&2392=4412&2393=4415&2396=4420&2397=4423&2398=4426&2400=4428&2401=4431&2403=4435&2404=4438&2407=4443&2408=4445&2411=4448&2412=4450&2413=4453&2414=4455&2416=4458&2417=4460&2419=4464&2424=4466&2427=4469&2430=4472&2431=4474&2433=4477&2434=4480&2435=4482&2436=4484&2437=4487&2440=4492&2443=4494&2444=4497&2445=4500&2446=4502&2447=4505&2449=4507&2450=4510&2452=4512&2453=4514&2454=4517&2455=4519&2456=4521&2457=4524&2458=4528&2459=4531&2462=4538&2466=4543&2467=4546&2468=4549&2469=4551&2470=4554&2472=4556&2473=4559&2475=4561&2476=4563&2477=4566&2478=4568&2479=4571&2480=4575&2481=4577&2482=4580&2485=4587&2491=4592&2494=4595&2495=4598&2496=4601&2497=4603&2498=4606&2500=4608&2501=4610&2502=4613&2504=4618&2507=4620&2508=4623&2513=4626&2516=4629&2517=4633&2518=4636&2519=4638&2520=4641&2522=4643&2523=4646&2525=4650&2526=4653&2528=4657&2529=4660&2531=4664&2532=4667&2534=4671&2535=4673&2536=4675&2537=4677&2538=4679&2539=4681&2541=4684&2544=4687&2545=4691&2546=4694&2547=4696&2548=4699&2550=4701&2551=4704&2553=4708&2554=4711&2556=4715&2557=4718&2559=4722&2560=4725&2562=4729&2563=4731&2564=4733&2565=4735&2566=4737&2567=4739&2569=4742&2572=4745&2573=4748&2575=4750&2576=4753&2578=4755&2583=4758&2586=4761&2587=4765&2588=4768&2589=4770&2590=4773&2592=4775&2593=4778&2595=4782&2596=4785&2598=4789&2599=4792&2601=4796&2602=4799&2604=4803&2605=4805&2606=4807&2607=4809&2608=4811&2609=4813&2611=4816&2614=4819&2615=4823&2616=4826&2617=4828&2618=4831&2620=4833&2621=4836&2623=4840&2624=4843&2626=4847&2627=4850&2629=4854&2630=4857&2632=4861&2633=4863&2634=4865&2635=4867&2636=4869&2637=4871&2639=4874&2642=4877&2643=4880&2645=4882&2646=4885&2648=4887&2653=4890&2655=4909&2656=4911&2657=4914&2659=4916&2660=4918&2661=4922&2662=4924&2663=4926&2665=4928&2666=4930&2667=4932&2668=4934&2670=4937&2673=4940&2674=4942&2675=4945&2676=4949&2678=4954&2679=4956&2680=4958&2681=4961&2683=4970&2686=4974&2687=4977&2692=4982&2693=4984&2694=4987&2695=4991&2697=4996&2698=4998&2699=5000&2700=5003&2702=5012&2705=5016&2706=5019&2711=5024&2712=5027&2714=5029&2717=5032&2720=5035&2721=5038&2723=5040&2724=5042&2725=5045&2727=5047&2728=5050&2732=5053&2733=5055&2734=5057&2735=5059&2737=5062&2739=5064&2741=5067&2744=5070&2747=5073&2748=5075&2750=5078&2751=5081&2752=5083&2753=5085&2754=5088&2757=5093&2760=5095&2762=5097&2761=5101&2763=5105&2764=5107&2765=5109&2767=5111&2768=5113&2769=5115&2770=5117&2771=5119&2773=5122&2776=5125&2777=5136&2778=5139&2780=5143&2781=5146&2783=5150&2784=5153&2786=5155&2787=5158&2789=5160&2790=5163&2792=5165&2793=5167&2794=5169&2795=5171&2796=5173&2797=5175&2800=5178&2801=5180&2802=5183&2804=5185&2805=5188&2807=5190&2808=5193&2810=5195&2811=5198&2813=5202&2814=5205&2816=5209&2817=5212&2819=5214&2820=5217&2822=5221&2823=5224&2824=5226&2827=5229&2829=5237&2830=5240&2832=5242&2833=5245&2835=5249&2836=5251&2837=5253&2838=5255&2840=5258&2842=5260&2843=5262&2844=5264&2845=5266&2847=5269&2848=5271&2849=5273&2850=5276&2852=5278&2853=5280&2854=5282&2855=5284&2857=5287&2859=5289&2860=5292&2861=5294&2862=5297&2864=5299&2865=5302&2867=5306&2868=5309&2870=5313&2871=5316&2873=5318&2874=5320&2875=5323&2876=5325&2877=5328&2878=5332&2879=5334&2880=5337&2883=5344&2886=5348&2887=5351&2889=5355&2890=5358&2892=5362&2893=5364&2894=5366&2895=5368&2897=5370&2898=5372&2900=5375&2902=5377&2903=5380&2904=5382&2905=5385&2907=5389&2908=5391&2909=5393&2910=5395&2912=5397&2913=5399&2915=5402&2917=5404&2918=5406&2919=5408&2920=5410&2922=5413&2923=5415&2924=5418&2927=5421&2928=5424&2929=5427&2931=5434&2934=5437&2936=5440&2939=5443&2940=5447&2941=5449&2942=5451&2944=5453&2945=5455&2947=5457&2948=5459&2950=5461&2951=5463&2953=5465&2954=5467&2956=5470&2958=5473&2959=5475&2960=5477&2961=5479&2962=5481&2963=5483&2965=5485&2966=5487&2967=5489&2968=5491&2970=5494&2972=5496&2973=5498&2974=5500&2975=5502&2977=5504&2978=5506&2980=5508&2981=5510&2982=5512&2983=5514&2985=5517&2987=5519&2988=5521&2989=5523&2990=5525&2992=5527&2993=5529&2995=5532&2996=5534&2997=5536&2998=5538&2999=5540&3001=5542&3002=5544&3004=5547&3006=5549&3007=5551&3008=5553&3009=5555&3011=5557&3012=5559&3014=5562&3016=5564&3017=5566&3018=5568&3019=5570&3021=5572&3022=5574&3024=5576&3025=5578&3027=5581&3029=5583&3030=5585&3031=5587&3032=5589&3034=5591&3035=5593&3037=5596&3038=5598&3039=5600&3040=5602&3041=5604&3043=5606&3044=5608&3046=5611&3048=5613&3049=5615&3050=5617&3051=5619&3053=5621&3054=5623&3056=5626&3058=5628&3059=5630&3060=5632&3061=5634&3063=5636&3064=5638&3066=5640&3067=5642&3069=5645&3071=5647&3072=5649&3073=5651&3074=5653&3076=5655&3077=5657&3078=5659&3079=5661&3081=5664&3083=5666&3084=5668&3085=5670&3086=5672&3088=5675&3090=5677&3091=5679&3092=5681&3093=5683&3095=5686&3097=5688&3098=5690&3099=5692&3100=5694&3101=5696&3102=5698&3104=5701&3106=5703&3107=5705&3108=5707&3109=5709&3111=5712&3113=5714&3114=5716&3115=5718&3116=5720&3118=5723&3120=5725&3121=5727&3122=5731&3123=5733&3124=5735&3125=5737&3128=5739&3129=5741&3130=5743&3131=5745&3133=5747&3134=5749&3135=5751&3136=5753&3137=5755&3140=5758&3143=5761&3144=5764&3145=5767&3146=5773&3147=5776&3150=5783&3153=5786&3154=5789&3156=5791&3157=5794&3159=5796&3160=5799&3161=5802&3165=5805&3168=5808&3169=5811&3171=5813&3172=5816&3174=5818&3175=5821&3176=5824&3180=5827&3183=5830&3185=5833&3188=5836&3189=5839&3191=5841&3192=5844&3194=5846&3197=5849&3198=5851&3200=5854&3201=5857&3202=5859&3203=5861&3204=5864&3207=5869&3210=5871&3211=5875&3212=5878&3214=5880&3215=5883&3217=5885&3218=5888&3220=5892&3221=5895&3223=5899&3224=5902&3226=5906&3227=5909&3229=5913&3230=5916&3232=5920&3233=5923&3235=5927&3236=5929&3237=5932&3238=5934&3239=5937&3240=5941&3241=5943&3242=5946&3245=5953&3248=5957&3249=5959&3250=5961&3251=5963&3252=5965&3254=5968&3256=5973&3260=5976&3261=5980&3262=5982&3263=5984&3265=5987&3267=5990&3269=5993&3272=5996&3273=5998&3274=6000&3275=6002&3276=6004&3277=6006&3279=6009&3281=6011&3282=6013&3283=6015&3284=6017&3286=6020&3288=6022&3289=6024&3290=6026&3291=6028&3293=6030&3294=6032&3295=6034&3296=6036&3298=6039&3300=6041&3301=6043&3302=6045&3303=6047&3304=6049&3305=6051&3307=6054&3309=6056&3310=6058&3311=6060&3312=6062&3314=6065&3316=6067&3317=6069&3318=6071&3319=6073&3321=6075&3322=6077&3324=6079&3325=6081&3326=6083&3327=6085&3329=6088&3331=6090&3332=6092&3333=6094&3334=6096&3336=6098&3337=6100&3339=6103&3340=6105&3341=6107&3342=6109&3343=6111&3345=6113&3346=6115&3348=6118&3350=6120&3351=6122&3352=6124&3353=6126&3355=6128&3356=6130&3358=6133&3359=6135&3360=6137&3361=6139&3362=6141&3364=6143&3365=6145&3367=6148&3369=6150&3370=6152&3371=6154&3372=6156&3374=6158&3375=6160&3377=6163&3379=6165&3380=6167&3381=6169&3382=6171&3384=6173&3385=6175&3387=6177&3388=6179&3390=6182&3392=6184&3393=6186&3394=6188&3395=6190&3397=6192&3398=6194&3400=6197&3402=6199&3403=6201&3404=6203&3405=6205&3407=6207&3408=6209&3410=6211&3411=6213&3413=6216&3415=6218&3416=6220&3417=6222&3418=6224&3420=6227&3422=6229&3423=6231&3424=6233&3425=6235&3427=6237&3428=6239&3429=6241&3430=6243&3432=6246&3434=6248&3435=6250&3436=6254&3437=6256&3438=6258&3439=6260&3442=6262&3443=6264&3444=6266&3445=6268&3447=6270&3448=6272&3449=6274&3450=6276&3451=6278&3454=6281&3458=6284&3461=6287&3462=6290&3464=6292&3465=6295&3467=6297&3470=6300&3471=6303&3472=6306&3474=6308&3475=6311&3477=6313&3478=6316&3480=6320&3481=6323&3484=6328&3485=6332&3486=6334&3487=6336&3489=6339&3491=6342&3492=6344&3493=6346&3494=6348&3495=6350&3496=6352&3498=6355&3500=6357&3501=6359&3502=6361&3503=6363&3505=6366&3507=6368&3508=6370&3509=6372&3510=6374&3512=6376&3513=6378&3515=6380&3516=6382&3517=6384&3518=6386&3520=6389&3522=6391&3523=6393&3524=6395&3525=6397&3527=6400&3528=6402&3529=6404&3530=6406&3531=6408&3533=6411&3535=6413&3536=6415&3537=6417&3538=6419&3540=6422&3541=6424&3542=6426&3543=6428&3544=6430&3546=6433&3548=6435&3549=6437&3550=6439&3551=6441&3553=6444&3555=6446&3556=6448&3557=6450&3558=6452&3560=6454&3561=6456&3563=6459&3565=6461&3566=6463&3567=6465&3568=6467&3570=6470&3572=6472&3573=6474&3574=6476&3575=6478&3577=6480&3578=6482&3580=6485&3582=6487&3583=6489&3584=6491&3585=6493&3587=6496&3589=6498&3590=6500&3591=6504&3592=6506&3593=6508&3594=6510&3597=6512&3598=6514&3600=6516&3601=6518&3602=6520&3603=6522&3604=6524&3607=6527&3611=6530&3614=6533&3616=6536&3619=6539&3620=6542&3622=6544&3623=6547&3625=6549&3628=6552&3629=6554&3631=6557&3632=6560&3633=6562&3634=6564&3635=6567&3638=6572&3641=6574&3642=6577&3643=6580&3645=6582&3646=6585&3648=6587&3649=6590&3651=6594&3652=6597&3654=6601&3655=6604&3657=6608&3658=6611&3660=6615&3661=6618&3663=6622&3664=6625&3666=6629&3667=6631&3668=6634&3669=6636&3670=6639&3671=6643&3672=6645&3673=6648&3676=6655&3680=6660&3681=6664&3682=6666&3683=6668&3685=6671&3687=6674&3689=6677&3692=6680&3693=6682&3694=6684&3695=6686&3696=6688&3697=6690&3699=6693&3701=6695&3702=6697&3703=6699&3704=6701&3706=6704&3708=6706&3709=6708&3710=6710&3711=6712&3713=6715&3715=6717&3716=6719&3717=6721&3718=6723&3720=6725&3721=6727&3722=6729&3723=6731&3725=6734&3727=6736&3728=6738&3729=6740&3730=6742&3731=6744&3732=6746&3734=6749&3736=6751&3737=6753&3738=6755&3739=6757&3741=6760&3743=6762&3744=6764&3745=6766&3746=6768&3748=6770&3749=6772&3751=6774&3752=6776&3753=6778&3754=6780&3756=6783&3758=6785&3759=6787&3760=6789&3761=6791&3763=6793&3764=6795&3766=6798&3767=6800&3768=6802&3769=6804&3770=6806&3772=6808&3773=6810&3775=6813&3777=6815&3778=6817&3779=6819&3780=6821&3782=6823&3783=6825&3785=6828&3787=6830&3788=6832&3789=6834&3790=6836&3792=6838&3793=6840&3795=6842&3796=6844&3798=6847&3800=6849&3801=6851&3802=6853&3803=6855&3805=6857&3806=6859&3807=6861&3808=6863&3810=6866&3812=6868&3813=6870&3814=6874&3815=6876&3816=6878&3817=6880&3820=6882&3821=6884&3822=6886&3823=6888&3825=6890&3826=6892&3827=6894&3828=6896&3829=6898&3832=6901&3836=6904&3839=6907&3840=6910&3842=6912&3843=6915&3845=6917&3848=6920&3849=6923&3850=6926&3852=6928&3853=6931&3855=6933&3856=6936&3858=6940&3859=6943&3862=6948&3863=6952&3864=6954&3865=6956&3867=6959&3869=6962&3870=6964&3871=6966&3872=6968&3873=6970&3874=6972&3876=6975&3878=6977&3879=6979&3880=6981&3881=6983&3883=6985&3884=6987&3886=6989&3887=6991&3888=6993&3889=6995&3891=6998&3893=7000&3894=7002&3895=7004&3896=7006&3898=7009&3899=7011&3900=7013&3901=7015&3902=7017&3904=7020&3906=7022&3907=7024&3908=7026&3909=7028&3911=7031&3912=7033&3913=7035&3914=7037&3915=7039&3917=7042&3919=7044&3920=7046&3921=7048&3922=7050&3924=7053&3926=7055&3927=7057&3928=7059&3929=7061&3931=7063&3932=7065&3934=7068&3936=7070&3937=7072&3938=7074&3939=7076&3941=7079&3943=7081&3944=7083&3945=7085&3946=7087&3948=7089&3949=7091&3951=7094&3953=7096&3954=7098&3955=7100&3956=7102&3958=7105&3960=7107&3961=7109&3962=7113&3963=7115&3964=7117&3965=7119&3968=7121&3969=7123&3971=7125&3972=7127&3973=7129&3974=7131&3975=7133&3978=7136&3982=7139&3984=7142&3985=7144&3986=7146&3987=7149&3990=7154&3993=7156&3996=7159&4001=7162&4003=7165&4007=7168&4008=7172&4009=7174&4010=7177&4013=7180&4015=7183'