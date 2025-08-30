from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/management-interfaces.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_management_interfaces = resolve('management_interfaces')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['indent']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'indent' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    for l_1_management_interface in t_1((undefined(name='management_interfaces') if l_0_management_interfaces is missing else l_0_management_interfaces), 'name'):
        l_1_fallback_delay = resolve('fallback_delay')
        l_1_neighbor_cli = resolve('neighbor_cli')
        _loop_vars = {}
        pass
        yield '!\ninterface '
        yield str(environment.getattr(l_1_management_interface, 'name'))
        yield '\n'
        if t_3(environment.getattr(l_1_management_interface, 'description')):
            pass
            yield '   description '
            yield str(environment.getattr(l_1_management_interface, 'description'))
            yield '\n'
        if t_3(environment.getattr(l_1_management_interface, 'shutdown'), True):
            pass
            yield '   shutdown\n'
        elif t_3(environment.getattr(l_1_management_interface, 'shutdown'), False):
            pass
            yield '   no shutdown\n'
        if t_3(environment.getattr(l_1_management_interface, 'mtu')):
            pass
            yield '   mtu '
            yield str(environment.getattr(l_1_management_interface, 'mtu'))
            yield '\n'
        if t_3(environment.getattr(l_1_management_interface, 'mac_address')):
            pass
            yield '   mac-address '
            yield str(environment.getattr(l_1_management_interface, 'mac_address'))
            yield '\n'
        if t_3(environment.getattr(l_1_management_interface, 'speed')):
            pass
            yield '   speed '
            yield str(environment.getattr(l_1_management_interface, 'speed'))
            yield '\n'
        if (t_3(environment.getattr(l_1_management_interface, 'vrf')) and (environment.getattr(l_1_management_interface, 'vrf') != 'default')):
            pass
            yield '   vrf '
            yield str(environment.getattr(l_1_management_interface, 'vrf'))
            yield '\n'
        if t_3(environment.getattr(l_1_management_interface, 'ip_address')):
            pass
            yield '   ip address '
            yield str(environment.getattr(l_1_management_interface, 'ip_address'))
            yield '\n'
        if t_3(environment.getattr(l_1_management_interface, 'ipv6_enable'), True):
            pass
            yield '   ipv6 enable\n'
        if t_3(environment.getattr(l_1_management_interface, 'ipv6_address')):
            pass
            yield '   ipv6 address '
            yield str(environment.getattr(l_1_management_interface, 'ipv6_address'))
            yield '\n'
        if t_3(environment.getattr(environment.getattr(l_1_management_interface, 'lldp'), 'transmit'), False):
            pass
            yield '   no lldp transmit\n'
        if t_3(environment.getattr(environment.getattr(l_1_management_interface, 'lldp'), 'receive'), False):
            pass
            yield '   no lldp receive\n'
        if t_3(environment.getattr(environment.getattr(l_1_management_interface, 'lldp'), 'ztp_vlan')):
            pass
            yield '   lldp tlv transmit ztp vlan '
            yield str(environment.getattr(environment.getattr(l_1_management_interface, 'lldp'), 'ztp_vlan'))
            yield '\n'
        if t_3(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'fallback_delay')):
            pass
            l_1_fallback_delay = str_join(('redundancy fallback-delay ', environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'fallback_delay'), ))
            _loop_vars['fallback_delay'] = l_1_fallback_delay
            if t_3(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'fallback_delay'), 'infinity'):
                pass
                yield '   '
                yield str((undefined(name='fallback_delay') if l_1_fallback_delay is missing else l_1_fallback_delay))
                yield '\n'
            else:
                pass
                yield '   '
                yield str((undefined(name='fallback_delay') if l_1_fallback_delay is missing else l_1_fallback_delay))
                yield ' seconds\n'
        if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'monitor'), 'link_state'), True):
            pass
            yield '   redundancy monitor link-state\n'
        elif t_3(environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'monitor'), 'neighbor')):
            pass
            l_1_neighbor_cli = str_join(('redundancy monitor neighbor ipv6 ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'monitor'), 'neighbor'), 'ipv6_address'), ))
            _loop_vars['neighbor_cli'] = l_1_neighbor_cli
            if t_3(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'monitor'), 'neighbor'), 'interval')):
                pass
                l_1_neighbor_cli = str_join(((undefined(name='neighbor_cli') if l_1_neighbor_cli is missing else l_1_neighbor_cli), ' interval ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'monitor'), 'neighbor'), 'interval'), ' milliseconds', ))
                _loop_vars['neighbor_cli'] = l_1_neighbor_cli
            if t_3(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'monitor'), 'neighbor'), 'multiplier')):
                pass
                l_1_neighbor_cli = str_join(((undefined(name='neighbor_cli') if l_1_neighbor_cli is missing else l_1_neighbor_cli), ' multiplier ', environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'monitor'), 'neighbor'), 'multiplier'), ))
                _loop_vars['neighbor_cli'] = l_1_neighbor_cli
            yield '   '
            yield str((undefined(name='neighbor_cli') if l_1_neighbor_cli is missing else l_1_neighbor_cli))
            yield '\n'
        if t_3(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'supervisor_1')):
            pass
            yield '   redundancy supervisor 1 interface primary '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'supervisor_1'), 'primary_management_interface'))
            yield ' backup '
            yield str(context.call(environment.getattr(' ', 'join'), environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'supervisor_1'), 'backup_management_interfaces'), _loop_vars=_loop_vars))
            yield '\n'
        if t_3(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'supervisor_2')):
            pass
            yield '   redundancy supervisor 2 interface primary '
            yield str(environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'supervisor_2'), 'primary_management_interface'))
            yield ' backup '
            yield str(context.call(environment.getattr(' ', 'join'), environment.getattr(environment.getattr(environment.getattr(l_1_management_interface, 'redundancy'), 'supervisor_2'), 'backup_management_interfaces'), _loop_vars=_loop_vars))
            yield '\n'
        if t_3(environment.getattr(l_1_management_interface, 'eos_cli')):
            pass
            yield '   '
            yield str(t_2(environment.getattr(l_1_management_interface, 'eos_cli'), 3, False))
            yield '\n'
    l_1_management_interface = l_1_fallback_delay = l_1_neighbor_cli = missing

blocks = {}
debug_info = '7=30&9=36&10=38&11=41&13=43&15=46&18=49&19=52&21=54&22=57&24=59&25=62&27=64&28=67&30=69&31=72&33=74&36=77&37=80&39=82&42=85&45=88&46=91&48=93&49=95&50=97&51=100&53=105&56=107&58=110&59=112&60=114&61=116&63=118&64=120&66=123&68=125&69=128&71=132&72=135&74=139&75=142'