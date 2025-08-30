from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/vxlan-interface.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_vxlan_interface = resolve('vxlan_interface')
    l_0_tmp_encapsulations = resolve('tmp_encapsulations')
    l_0_range_vlans = resolve('range_vlans')
    l_0_vxlan_config = missing
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
        t_3 = environment.filters['arista.avd.range_expand']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.range_expand' found.")
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
        t_6 = environment.filters['string']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'string' found.")
    try:
        t_7 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    l_0_vxlan_config = t_1(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'vxlan1'), environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'))
    context.vars['vxlan_config'] = l_0_vxlan_config
    context.exported_vars.add('vxlan_config')
    if t_7((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config)):
        pass
        yield '!\ninterface Vxlan1\n'
        if t_7(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'description')):
            pass
            yield '   description '
            yield str(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'description'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'source_interface')):
            pass
            yield '   vxlan source-interface '
            yield str(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'source_interface'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'controller_client'), 'enabled'), True):
            pass
            yield '   vxlan controller-client\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'virtual_router_encapsulation_mac_address')):
            pass
            yield '   vxlan virtual-router encapsulation mac-address '
            yield str(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'virtual_router_encapsulation_mac_address'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'udp_port')):
            pass
            yield '   vxlan udp-port '
            yield str(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'udp_port'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vtep_to_vtep_bridging'), True):
            pass
            yield '   vxlan bridging vtep-to-vtep\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'flood_vtep_learned_data_plane'), True):
            pass
            yield '   vxlan flood vtep learned data-plane\n'
        if (t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'encapsulations'), 'ipv4'), True) or t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'encapsulations'), 'ipv6'), True)):
            pass
            l_0_tmp_encapsulations = []
            context.vars['tmp_encapsulations'] = l_0_tmp_encapsulations
            context.exported_vars.add('tmp_encapsulations')
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'encapsulations'), 'ipv4'), True):
                pass
                context.call(environment.getattr((undefined(name='tmp_encapsulations') if l_0_tmp_encapsulations is missing else l_0_tmp_encapsulations), 'append'), 'ipv4')
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'encapsulations'), 'ipv6'), True):
                pass
                context.call(environment.getattr((undefined(name='tmp_encapsulations') if l_0_tmp_encapsulations is missing else l_0_tmp_encapsulations), 'append'), 'ipv6')
            yield '   vxlan encapsulation '
            yield str(t_5(context.eval_ctx, (undefined(name='tmp_encapsulations') if l_0_tmp_encapsulations is missing else l_0_tmp_encapsulations), ' '))
            yield '\n'
        l_0_range_vlans = t_3(t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlan_range'), 'vlans'), []))
        context.vars['range_vlans'] = l_0_range_vlans
        context.exported_vars.add('range_vlans')
        for l_1_vlan in t_2(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlans'), 'id'):
            _loop_vars = {}
            pass
            if (t_7(environment.getattr(l_1_vlan, 'vni')) and (t_6(environment.getattr(l_1_vlan, 'id')) not in (undefined(name='range_vlans') if l_0_range_vlans is missing else l_0_range_vlans))):
                pass
                yield '   vxlan vlan '
                yield str(environment.getattr(l_1_vlan, 'id'))
                yield ' vni '
                yield str(environment.getattr(l_1_vlan, 'vni'))
                yield '\n'
        l_1_vlan = missing
        if t_7(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlan_range')):
            pass
            yield '   vxlan vlan '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlan_range'), 'vlans'))
            yield ' vni '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlan_range'), 'vnis'))
            yield '\n'
        for l_1_vrf in t_2(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vrfs'), 'name'):
            _loop_vars = {}
            pass
            if t_7(environment.getattr(l_1_vrf, 'vni')):
                pass
                yield '   vxlan vrf '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield ' vni '
                yield str(environment.getattr(l_1_vrf, 'vni'))
                yield '\n'
        l_1_vrf = missing
        if t_7(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'mlag_source_interface')):
            pass
            yield '   vxlan mlag source-interface '
            yield str(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'mlag_source_interface'))
            yield '\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn')):
            pass
            if ((t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'interval')) and t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'min_rx'))) and t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'multiplier'))):
                pass
                yield '   bfd vtep evpn interval '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'interval'))
                yield ' min-rx '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'min_rx'))
                yield ' multiplier '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'multiplier'))
                yield '\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'prefix_list')):
                pass
                yield '   bfd vtep evpn prefix-list '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'prefix_list'))
                yield '\n'
        if t_7(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'flood_vteps')):
            pass
            yield '   vxlan flood vtep '
            yield str(t_5(context.eval_ctx, environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'flood_vteps'), ' '))
            yield '\n'
        for l_1_vlan in t_2(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlans'), 'id'):
            _loop_vars = {}
            pass
            if t_7(environment.getattr(l_1_vlan, 'flood_vteps')):
                pass
                yield '   vxlan vlan '
                yield str(environment.getattr(l_1_vlan, 'id'))
                yield ' flood vtep '
                yield str(t_5(context.eval_ctx, environment.getattr(l_1_vlan, 'flood_vteps'), ' '))
                yield '\n'
        l_1_vlan = missing
        for l_1_vlan in t_2(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlans'), 'id'):
            _loop_vars = {}
            pass
            if t_7(environment.getattr(l_1_vlan, 'flood_group')):
                pass
                yield '   vxlan vlan '
                yield str(environment.getattr(l_1_vlan, 'id'))
                yield ' flood group '
                yield str(environment.getattr(l_1_vlan, 'flood_group'))
                yield '\n'
        l_1_vlan = missing
        def t_8(fiter):
            for l_1_vlan in fiter:
                if t_7(environment.getattr(l_1_vlan, 'multicast_group')):
                    yield l_1_vlan
        for l_1_vlan in t_8(t_2(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlans'), 'id')):
            _loop_vars = {}
            pass
            yield '   vxlan vlan '
            yield str(environment.getattr(l_1_vlan, 'id'))
            yield ' multicast group '
            yield str(environment.getattr(l_1_vlan, 'multicast_group'))
            yield '\n'
        l_1_vlan = missing
        for l_1_vrf in t_2(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vrfs'), 'name'):
            _loop_vars = {}
            pass
            if t_7(environment.getattr(l_1_vrf, 'multicast_group')):
                pass
                yield '   vxlan vrf '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield ' multicast group '
                yield str(environment.getattr(l_1_vrf, 'multicast_group'))
                yield '\n'
            if t_7(environment.getattr(l_1_vrf, 'multicast_group_encap_range')):
                pass
                yield '   vxlan vrf '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield ' multicast group encap range '
                yield str(environment.getattr(l_1_vrf, 'multicast_group_encap_range'))
                yield ' delayed\n'
            for l_2_multicast_group in t_2(environment.getattr(l_1_vrf, 'multicast_groups'), 'overlay_group'):
                _loop_vars = {}
                pass
                yield '   vxlan vrf '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield ' multicast group overlay '
                yield str(environment.getattr(l_2_multicast_group, 'overlay_group'))
                yield ' encap '
                yield str(environment.getattr(l_2_multicast_group, 'encap'))
                yield ' immediate\n'
            l_2_multicast_group = missing
        l_1_vrf = missing
        if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'multicast'), 'headend_replication'), True):
            pass
            yield '   vxlan multicast headend-replication\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'ecn_propagation'), True):
            pass
            yield '   vxlan qos ecn propagation\n'
        elif t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'ecn_propagation'), False):
            pass
            yield '   no vxlan qos ecn propagation\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'dscp_ecn'), 'rewrite_bridged_enabled'), True):
            pass
            yield '   vxlan qos dscp ecn rewrite bridged enabled\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'dscp_propagation_encapsulation'), True):
            pass
            yield '   vxlan qos dscp propagation encapsulation\n'
        elif t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'dscp_propagation_encapsulation'), False):
            pass
            yield '   no vxlan qos dscp propagation encapsulation\n'
        if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'map_dscp_to_traffic_class_decapsulation'), True):
            pass
            yield '   vxlan qos map dscp to traffic-class decapsulation\n'
        elif t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'map_dscp_to_traffic_class_decapsulation'), False):
            pass
            yield '   no vxlan qos map dscp to traffic-class decapsulation\n'
        if t_7(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'eos_cli')):
            pass
            yield '   '
            yield str(t_4(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'eos_cli'), 3, False))
            yield '\n'

blocks = {}
debug_info = '8=57&9=60&12=63&13=66&15=68&16=71&18=73&21=76&22=79&24=81&25=84&27=86&30=89&33=92&34=94&35=97&36=99&38=100&39=102&41=104&43=106&44=109&45=112&46=115&49=120&50=123&52=127&53=130&54=133&57=138&58=141&60=143&61=145&64=148&66=154&67=157&70=159&71=162&73=164&74=167&75=170&78=175&79=178&80=181&83=186&84=194&86=199&87=202&88=205&90=209&91=212&93=216&94=220&97=228&100=231&102=234&105=237&108=240&110=243&113=246&115=249&118=252&119=255'