from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/vxlan-interface.j2'

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
        t_4 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_5 = environment.filters['string']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'string' found.")
    try:
        t_6 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    l_0_vxlan_config = t_1(environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'vxlan1'), environment.getattr((undefined(name='vxlan_interface') if l_0_vxlan_interface is missing else l_0_vxlan_interface), 'Vxlan1'))
    context.vars['vxlan_config'] = l_0_vxlan_config
    context.exported_vars.add('vxlan_config')
    if t_6((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config)):
        pass
        yield '\n### VXLAN Interface\n\n#### VXLAN Interface Summary\n\n| Setting | Value |\n| ------- | ----- |\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'source_interface')):
            pass
            yield '| Source Interface | '
            yield str(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'source_interface'))
            yield ' |\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'controller_client'), 'enabled')):
            pass
            yield '| Controller Client | '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'controller_client'), 'enabled'))
            yield ' |\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'mlag_source_interface')):
            pass
            yield '| MLAG Source Interface | '
            yield str(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'mlag_source_interface'))
            yield ' |\n'
        yield '| UDP port | '
        yield str(t_1(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'udp_port'), '4789'))
        yield ' |\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vtep_to_vtep_bridging'), True):
            pass
            yield '| Vtep-to-Vtep Bridging | '
            yield str(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vtep_to_vtep_bridging'))
            yield ' |\n'
        if (t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'encapsulations'), 'ipv4'), True) or t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'encapsulations'), 'ipv6'), True)):
            pass
            l_0_tmp_encapsulations = []
            context.vars['tmp_encapsulations'] = l_0_tmp_encapsulations
            context.exported_vars.add('tmp_encapsulations')
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'encapsulations'), 'ipv4'), True):
                pass
                context.call(environment.getattr((undefined(name='tmp_encapsulations') if l_0_tmp_encapsulations is missing else l_0_tmp_encapsulations), 'append'), 'ipv4')
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'encapsulations'), 'ipv6'), True):
                pass
                context.call(environment.getattr((undefined(name='tmp_encapsulations') if l_0_tmp_encapsulations is missing else l_0_tmp_encapsulations), 'append'), 'ipv6')
            yield '| Vxlan Encapsulation | '
            yield str(t_4(context.eval_ctx, (undefined(name='tmp_encapsulations') if l_0_tmp_encapsulations is missing else l_0_tmp_encapsulations), ', '))
            yield ' |\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'virtual_router_encapsulation_mac_address')):
            pass
            yield '| EVPN MLAG Shared Router MAC | '
            yield str(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'virtual_router_encapsulation_mac_address'))
            yield ' |\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'flood_vtep_learned_data_plane'), True):
            pass
            yield '| VXLAN flood-lists learning from data-plane | Enabled |\n'
        elif t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'flood_vtep_learned_data_plane'), False):
            pass
            yield '| VXLAN flood-lists learning from data-plane | Disabled |\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'dscp_propagation_encapsulation'), True):
            pass
            yield '| Qos dscp propagation encapsulation | Enabled |\n'
        elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'dscp_propagation_encapsulation'), False):
            pass
            yield '| Qos dscp propagation encapsulation | Disabled |\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'ecn_propagation'), True):
            pass
            yield '| Qos ECN propagation | Enabled |\n'
        elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'ecn_propagation'), False):
            pass
            yield '| Qos ECN propagation | Disabled |\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'dscp_ecn'), 'rewrite_bridged_enabled'), True):
            pass
            yield '| Qos DHCP ECN rewrite bridged | Enabled |\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'map_dscp_to_traffic_class_decapsulation'), True):
            pass
            yield '| Qos map dscp to traffic-class decapsulation | Enabled |\n'
        elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'qos'), 'map_dscp_to_traffic_class_decapsulation'), False):
            pass
            yield '| Qos map dscp to traffic-class decapsulation | Disabled |\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn')):
            pass
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'interval')):
                pass
                yield '| Remote VTEPs EVPN BFD transmission rate | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'interval'))
                yield 'ms |\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'min_rx')):
                pass
                yield '| Remote VTEPs EVPN BFD expected minimum incoming rate (min-rx) | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'min_rx'))
                yield 'ms |\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'multiplier')):
                pass
                yield '| Remote VTEPs EVPN BFD multiplier | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'multiplier'))
                yield ' |\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'prefix_list')):
                pass
                yield '| Remote VTEPs EVPN BFD prefix-list | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'bfd_vtep_evpn'), 'prefix_list'))
                yield ' |\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'multicast'), 'headend_replication'), True):
            pass
            yield '| Multicast headend-replication | Enabled |\n'
        elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'multicast'), 'headend_replication'), False):
            pass
            yield '| Multicast headend-replication | Disabled |\n'
        if (t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlans')) or t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlan_range'))):
            pass
            yield '\n##### VLAN to VNI, Flood List and Multicast Group Mappings\n\n| VLAN | VNI | Flood List | Multicast Group |\n| ---- | --- | ---------- | --------------- |\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlan_range')):
                pass
                yield '| '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlan_range'), 'vlans'))
                yield ' | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlan_range'), 'vnis'))
                yield ' | - | - |\n'
            l_0_range_vlans = t_3(t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlan_range'), 'vlans'), []))
            context.vars['range_vlans'] = l_0_range_vlans
            context.exported_vars.add('range_vlans')
            for l_1_vlan in t_2(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vlans'), 'id'):
                l_1_vlan_vni = resolve('vlan_vni')
                l_1_multicast_group = l_1_flood_list = missing
                _loop_vars = {}
                pass
                if (t_5(environment.getattr(l_1_vlan, 'id')) not in (undefined(name='range_vlans') if l_0_range_vlans is missing else l_0_range_vlans)):
                    pass
                    l_1_vlan_vni = t_1(environment.getattr(l_1_vlan, 'vni'), '-')
                    _loop_vars['vlan_vni'] = l_1_vlan_vni
                l_1_multicast_group = t_1(environment.getattr(l_1_vlan, 'multicast_group'), '-')
                _loop_vars['multicast_group'] = l_1_multicast_group
                l_1_flood_list = []
                _loop_vars['flood_list'] = l_1_flood_list
                if t_6(environment.getattr(l_1_vlan, 'flood_vteps')):
                    pass
                    context.call(environment.getattr((undefined(name='flood_list') if l_1_flood_list is missing else l_1_flood_list), 'extend'), environment.getattr(l_1_vlan, 'flood_vteps'), _loop_vars=_loop_vars)
                if t_6(environment.getattr(l_1_vlan, 'flood_group')):
                    pass
                    context.call(environment.getattr((undefined(name='flood_list') if l_1_flood_list is missing else l_1_flood_list), 'append'), environment.getattr(l_1_vlan, 'flood_group'), _loop_vars=_loop_vars)
                l_1_flood_list = t_4(context.eval_ctx, ((undefined(name='flood_list') if l_1_flood_list is missing else l_1_flood_list) or ['-']), '<br/>')
                _loop_vars['flood_list'] = l_1_flood_list
                yield '| '
                yield str(environment.getattr(l_1_vlan, 'id'))
                yield ' | '
                yield str(t_1((undefined(name='vlan_vni') if l_1_vlan_vni is missing else l_1_vlan_vni), '-'))
                yield ' | '
                yield str((undefined(name='flood_list') if l_1_flood_list is missing else l_1_flood_list))
                yield ' | '
                yield str((undefined(name='multicast_group') if l_1_multicast_group is missing else l_1_multicast_group))
                yield ' |\n'
            l_1_vlan = l_1_vlan_vni = l_1_multicast_group = l_1_flood_list = missing
        if t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vrfs')):
            pass
            yield '\n##### VRF to VNI and Multicast Group Mappings\n\n| VRF | VNI | Overlay Multicast Group to Encap Mappings |\n| --- | --- | ----------------------------------------- |\n'
            for l_1_vrf in t_2(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'vrfs'), 'name'):
                l_1_vrf_vni = l_1_multicast_groups_mappings = missing
                _loop_vars = {}
                pass
                l_1_vrf_vni = t_1(environment.getattr(l_1_vrf, 'vni'), '-')
                _loop_vars['vrf_vni'] = l_1_vrf_vni
                l_1_multicast_groups_mappings = []
                _loop_vars['multicast_groups_mappings'] = l_1_multicast_groups_mappings
                if t_6(environment.getattr(l_1_vrf, 'multicast_group')):
                    pass
                    context.call(environment.getattr((undefined(name='multicast_groups_mappings') if l_1_multicast_groups_mappings is missing else l_1_multicast_groups_mappings), 'append'), str_join(('default -> ', environment.getattr(l_1_vrf, 'multicast_group'), )), _loop_vars=_loop_vars)
                if t_6(environment.getattr(l_1_vrf, 'multicast_group_encap_range')):
                    pass
                    context.call(environment.getattr((undefined(name='multicast_groups_mappings') if l_1_multicast_groups_mappings is missing else l_1_multicast_groups_mappings), 'append'), str_join(('dynamic -> ', environment.getattr(l_1_vrf, 'multicast_group_encap_range'), )), _loop_vars=_loop_vars)
                for l_2_multicast_group in t_2(environment.getattr(l_1_vrf, 'multicast_groups'), 'overlay_group'):
                    _loop_vars = {}
                    pass
                    context.call(environment.getattr((undefined(name='multicast_groups_mappings') if l_1_multicast_groups_mappings is missing else l_1_multicast_groups_mappings), 'append'), str_join((environment.getattr(l_2_multicast_group, 'overlay_group'), ' -> ', environment.getattr(l_2_multicast_group, 'encap'), )), _loop_vars=_loop_vars)
                l_2_multicast_group = missing
                if (not (undefined(name='multicast_groups_mappings') if l_1_multicast_groups_mappings is missing else l_1_multicast_groups_mappings)):
                    pass
                    context.call(environment.getattr((undefined(name='multicast_groups_mappings') if l_1_multicast_groups_mappings is missing else l_1_multicast_groups_mappings), 'append'), '-', _loop_vars=_loop_vars)
                yield '| '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield ' | '
                yield str((undefined(name='vrf_vni') if l_1_vrf_vni is missing else l_1_vrf_vni))
                yield ' | '
                yield str(t_4(context.eval_ctx, (undefined(name='multicast_groups_mappings') if l_1_multicast_groups_mappings is missing else l_1_multicast_groups_mappings), '<br/>'))
                yield ' |\n'
            l_1_vrf = l_1_vrf_vni = l_1_multicast_groups_mappings = missing
        if t_6(environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'flood_vteps')):
            pass
            yield '\n##### Default Flood List\n\n| Default Flood List |\n| ------------------ |\n| '
            yield str(t_4(context.eval_ctx, environment.getattr(environment.getattr((undefined(name='vxlan_config') if l_0_vxlan_config is missing else l_0_vxlan_config), 'vxlan'), 'flood_vteps'), '<br/>'))
            yield ' |\n'
        yield '\n#### VXLAN Interface Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/vxlan-interface.j2', 'documentation/vxlan-interface.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'range_vlans': l_0_range_vlans, 'tmp_encapsulations': l_0_tmp_encapsulations, 'vxlan_config': l_0_vxlan_config}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '8=51&9=54&17=57&18=60&20=62&21=65&23=67&24=70&26=73&27=75&28=78&30=80&31=82&32=85&33=87&35=88&36=90&38=92&40=94&41=97&43=99&45=102&48=105&50=108&53=111&55=114&58=117&61=120&63=123&66=126&67=128&68=131&70=133&71=136&73=138&74=141&76=143&77=146&80=148&82=151&85=154&91=157&92=160&94=164&95=167&96=172&97=174&99=176&100=178&101=180&102=182&104=183&105=185&107=186&108=189&111=198&117=201&118=205&119=207&120=209&121=211&123=212&124=214&126=215&127=218&129=220&130=222&132=224&135=231&141=234&147=237'