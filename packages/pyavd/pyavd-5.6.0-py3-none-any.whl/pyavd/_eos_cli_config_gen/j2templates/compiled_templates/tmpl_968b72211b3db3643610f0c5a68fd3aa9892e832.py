from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ipv6-router-ospf.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ipv6_router_ospf = resolve('ipv6_router_ospf')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    for l_1_process_id in t_1(environment.getattr((undefined(name='ipv6_router_ospf') if l_0_ipv6_router_ospf is missing else l_0_ipv6_router_ospf), 'process_ids'), 'id'):
        l_1_redistribute_bgp_cli = resolve('redistribute_bgp_cli')
        l_1_redistribute_dhcp_cli = resolve('redistribute_dhcp_cli')
        l_1_redistribute_connected_cli = resolve('redistribute_connected_cli')
        l_1_redistribute_isis_cli = resolve('redistribute_isis_cli')
        l_1_redistribute_ospfv3_cli = resolve('redistribute_ospfv3_cli')
        l_1_redistribute_ospfv3_cli_match = resolve('redistribute_ospfv3_cli_match')
        l_1_redistribute_static_cli = resolve('redistribute_static_cli')
        _loop_vars = {}
        pass
        yield '!\n'
        if t_2(environment.getattr(l_1_process_id, 'vrf')):
            pass
            yield 'ipv6 router ospf '
            yield str(environment.getattr(l_1_process_id, 'id'))
            yield ' vrf '
            yield str(environment.getattr(l_1_process_id, 'vrf'))
            yield '\n'
        else:
            pass
            yield 'ipv6 router ospf '
            yield str(environment.getattr(l_1_process_id, 'id'))
            yield '\n'
        if t_2(environment.getattr(l_1_process_id, 'router_id')):
            pass
            yield '   router-id '
            yield str(environment.getattr(l_1_process_id, 'router_id'))
            yield '\n'
        if t_2(environment.getattr(l_1_process_id, 'auto_cost_reference_bandwidth')):
            pass
            yield '   auto-cost reference-bandwidth '
            yield str(environment.getattr(l_1_process_id, 'auto_cost_reference_bandwidth'))
            yield '\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'bgp'), 'enabled'), True):
            pass
            l_1_redistribute_bgp_cli = 'redistribute bgp'
            _loop_vars['redistribute_bgp_cli'] = l_1_redistribute_bgp_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'bgp'), 'include_leaked'), True):
                pass
                l_1_redistribute_bgp_cli = str_join(((undefined(name='redistribute_bgp_cli') if l_1_redistribute_bgp_cli is missing else l_1_redistribute_bgp_cli), ' include leaked', ))
                _loop_vars['redistribute_bgp_cli'] = l_1_redistribute_bgp_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'bgp'), 'route_map')):
                pass
                l_1_redistribute_bgp_cli = str_join(((undefined(name='redistribute_bgp_cli') if l_1_redistribute_bgp_cli is missing else l_1_redistribute_bgp_cli), ' route-map ', environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'bgp'), 'route_map'), ))
                _loop_vars['redistribute_bgp_cli'] = l_1_redistribute_bgp_cli
            yield '   '
            yield str((undefined(name='redistribute_bgp_cli') if l_1_redistribute_bgp_cli is missing else l_1_redistribute_bgp_cli))
            yield '\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'dhcp'), 'enabled'), True):
            pass
            l_1_redistribute_dhcp_cli = 'redistribute dhcp'
            _loop_vars['redistribute_dhcp_cli'] = l_1_redistribute_dhcp_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'dhcp'), 'route_map')):
                pass
                l_1_redistribute_dhcp_cli = str_join(((undefined(name='redistribute_dhcp_cli') if l_1_redistribute_dhcp_cli is missing else l_1_redistribute_dhcp_cli), ' route-map ', environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'dhcp'), 'route_map'), ))
                _loop_vars['redistribute_dhcp_cli'] = l_1_redistribute_dhcp_cli
            yield '   '
            yield str((undefined(name='redistribute_dhcp_cli') if l_1_redistribute_dhcp_cli is missing else l_1_redistribute_dhcp_cli))
            yield '\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'connected'), 'enabled'), True):
            pass
            l_1_redistribute_connected_cli = 'redistribute connected'
            _loop_vars['redistribute_connected_cli'] = l_1_redistribute_connected_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'connected'), 'include_leaked'), True):
                pass
                l_1_redistribute_connected_cli = str_join(((undefined(name='redistribute_connected_cli') if l_1_redistribute_connected_cli is missing else l_1_redistribute_connected_cli), ' include leaked', ))
                _loop_vars['redistribute_connected_cli'] = l_1_redistribute_connected_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'connected'), 'route_map')):
                pass
                l_1_redistribute_connected_cli = str_join(((undefined(name='redistribute_connected_cli') if l_1_redistribute_connected_cli is missing else l_1_redistribute_connected_cli), ' route-map ', environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'connected'), 'route_map'), ))
                _loop_vars['redistribute_connected_cli'] = l_1_redistribute_connected_cli
            yield '   '
            yield str((undefined(name='redistribute_connected_cli') if l_1_redistribute_connected_cli is missing else l_1_redistribute_connected_cli))
            yield '\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'enabled'), True):
            pass
            l_1_redistribute_isis_cli = 'redistribute isis'
            _loop_vars['redistribute_isis_cli'] = l_1_redistribute_isis_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'include_leaked'), True):
                pass
                l_1_redistribute_isis_cli = str_join(((undefined(name='redistribute_isis_cli') if l_1_redistribute_isis_cli is missing else l_1_redistribute_isis_cli), ' include leaked', ))
                _loop_vars['redistribute_isis_cli'] = l_1_redistribute_isis_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'isis_level')):
                pass
                l_1_redistribute_isis_cli = str_join(((undefined(name='redistribute_isis_cli') if l_1_redistribute_isis_cli is missing else l_1_redistribute_isis_cli), ' ', environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'isis_level'), ))
                _loop_vars['redistribute_isis_cli'] = l_1_redistribute_isis_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'route_map')):
                pass
                l_1_redistribute_isis_cli = str_join(((undefined(name='redistribute_isis_cli') if l_1_redistribute_isis_cli is missing else l_1_redistribute_isis_cli), ' route-map ', environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'isis'), 'route_map'), ))
                _loop_vars['redistribute_isis_cli'] = l_1_redistribute_isis_cli
            yield '   '
            yield str((undefined(name='redistribute_isis_cli') if l_1_redistribute_isis_cli is missing else l_1_redistribute_isis_cli))
            yield '\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'enabled'), True):
            pass
            l_1_redistribute_ospfv3_cli = 'redistribute ospfv3 leaked'
            _loop_vars['redistribute_ospfv3_cli'] = l_1_redistribute_ospfv3_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'route_map')):
                pass
                l_1_redistribute_ospfv3_cli = str_join(((undefined(name='redistribute_ospfv3_cli') if l_1_redistribute_ospfv3_cli is missing else l_1_redistribute_ospfv3_cli), ' route-map ', environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'route_map'), ))
                _loop_vars['redistribute_ospfv3_cli'] = l_1_redistribute_ospfv3_cli
            yield '   '
            yield str((undefined(name='redistribute_ospfv3_cli') if l_1_redistribute_ospfv3_cli is missing else l_1_redistribute_ospfv3_cli))
            yield '\n'
        elif t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_internal'), 'enabled'), True):
            pass
            l_1_redistribute_ospfv3_cli = 'redistribute ospfv3 leaked match internal'
            _loop_vars['redistribute_ospfv3_cli'] = l_1_redistribute_ospfv3_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_internal'), 'route_map')):
                pass
                l_1_redistribute_ospfv3_cli = str_join(((undefined(name='redistribute_ospfv3_cli') if l_1_redistribute_ospfv3_cli is missing else l_1_redistribute_ospfv3_cli), ' route-map ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_internal'), 'route_map'), ))
                _loop_vars['redistribute_ospfv3_cli'] = l_1_redistribute_ospfv3_cli
            yield '   '
            yield str((undefined(name='redistribute_ospfv3_cli') if l_1_redistribute_ospfv3_cli is missing else l_1_redistribute_ospfv3_cli))
            yield '\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_external'), 'enabled'), True):
            pass
            l_1_redistribute_ospfv3_cli_match = 'redistribute ospfv3 leaked match external'
            _loop_vars['redistribute_ospfv3_cli_match'] = l_1_redistribute_ospfv3_cli_match
            if t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_external'), 'route_map')):
                pass
                l_1_redistribute_ospfv3_cli_match = str_join(((undefined(name='redistribute_ospfv3_cli_match') if l_1_redistribute_ospfv3_cli_match is missing else l_1_redistribute_ospfv3_cli_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_external'), 'route_map'), ))
                _loop_vars['redistribute_ospfv3_cli_match'] = l_1_redistribute_ospfv3_cli_match
            yield '   '
            yield str((undefined(name='redistribute_ospfv3_cli_match') if l_1_redistribute_ospfv3_cli_match is missing else l_1_redistribute_ospfv3_cli_match))
            yield '\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_nssa_external'), 'enabled'), True):
            pass
            l_1_redistribute_ospfv3_cli_match = 'redistribute ospfv3 leaked match nssa-external'
            _loop_vars['redistribute_ospfv3_cli_match'] = l_1_redistribute_ospfv3_cli_match
            if t_2(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_nssa_external'), 'route_map')):
                pass
                l_1_redistribute_ospfv3_cli_match = str_join(((undefined(name='redistribute_ospfv3_cli_match') if l_1_redistribute_ospfv3_cli_match is missing else l_1_redistribute_ospfv3_cli_match), ' route-map ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'ospfv3'), 'match_nssa_external'), 'route_map'), ))
                _loop_vars['redistribute_ospfv3_cli_match'] = l_1_redistribute_ospfv3_cli_match
            yield '   '
            yield str((undefined(name='redistribute_ospfv3_cli_match') if l_1_redistribute_ospfv3_cli_match is missing else l_1_redistribute_ospfv3_cli_match))
            yield '\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'static'), 'enabled'), True):
            pass
            l_1_redistribute_static_cli = 'redistribute static'
            _loop_vars['redistribute_static_cli'] = l_1_redistribute_static_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'static'), 'include_leaked'), True):
                pass
                l_1_redistribute_static_cli = str_join(((undefined(name='redistribute_static_cli') if l_1_redistribute_static_cli is missing else l_1_redistribute_static_cli), ' include leaked', ))
                _loop_vars['redistribute_static_cli'] = l_1_redistribute_static_cli
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'static'), 'route_map')):
                pass
                l_1_redistribute_static_cli = str_join(((undefined(name='redistribute_static_cli') if l_1_redistribute_static_cli is missing else l_1_redistribute_static_cli), ' route-map ', environment.getattr(environment.getattr(environment.getattr(l_1_process_id, 'redistribute'), 'static'), 'route_map'), ))
                _loop_vars['redistribute_static_cli'] = l_1_redistribute_static_cli
            yield '   '
            yield str((undefined(name='redistribute_static_cli') if l_1_redistribute_static_cli is missing else l_1_redistribute_static_cli))
            yield '\n'
    l_1_process_id = l_1_redistribute_bgp_cli = l_1_redistribute_dhcp_cli = l_1_redistribute_connected_cli = l_1_redistribute_isis_cli = l_1_redistribute_ospfv3_cli = l_1_redistribute_ospfv3_cli_match = l_1_redistribute_static_cli = missing

blocks = {}
debug_info = '7=24&9=35&10=38&12=45&14=47&15=50&17=52&18=55&20=57&21=59&22=61&23=63&25=65&26=67&28=70&30=72&31=74&32=76&33=78&35=81&37=83&38=85&39=87&40=89&42=91&43=93&45=96&47=98&48=100&49=102&50=104&52=106&53=108&55=110&56=112&58=115&60=117&61=119&62=121&63=123&65=126&66=128&67=130&68=132&69=134&71=137&73=139&74=141&75=143&76=145&78=148&80=150&81=152&82=154&83=156&85=159&87=161&88=163&89=165&90=167&92=169&93=171&95=174'