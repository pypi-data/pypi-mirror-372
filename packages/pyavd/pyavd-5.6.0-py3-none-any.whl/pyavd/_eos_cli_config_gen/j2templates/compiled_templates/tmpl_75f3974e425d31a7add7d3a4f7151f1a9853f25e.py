from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/mpls-rsvp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_mpls = resolve('mpls')
    l_0_auth = resolve('auth')
    l_0_fast_reroute = resolve('fast_reroute')
    l_0_with_neighbor_ipv4_address = resolve('with_neighbor_ipv4_address')
    l_0_with_neighbor_ipv6_address = resolve('with_neighbor_ipv6_address')
    l_0_sorted_ip_addresses = resolve('sorted_ip_addresses')
    l_0_graceful_restart = resolve('graceful_restart')
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
    if t_5(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp')):
        pass
        yield '\n### MPLS RSVP\n\n#### MPLS RSVP Summary\n\n| Setting | Value |\n| ------- | ----- |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'refresh')):
            pass
            if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'refresh'), 'interval')):
                pass
                yield '| Refresh interval | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'refresh'), 'interval'))
                yield ' |\n'
            if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'refresh'), 'method')):
                pass
                yield '| Refresh method  | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'refresh'), 'method'))
                yield ' |\n'
        if (t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hello'), 'interval')) and t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hello'), 'multiplier'))):
            pass
            yield '| Hello interval | '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hello'), 'interval'))
            yield ' |\n| Timeout multiplier | '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hello'), 'multiplier'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'authentication')):
            pass
            l_0_auth = environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'authentication')
            context.vars['auth'] = l_0_auth
            context.exported_vars.add('auth')
            yield '| Authentication type | '
            yield str(t_1(environment.getattr((undefined(name='auth') if l_0_auth is missing else l_0_auth), 'type'), '-'))
            yield ' |\n| Authentication sequence-number window | '
            yield str(t_1(environment.getattr((undefined(name='auth') if l_0_auth is missing else l_0_auth), 'sequence_number_window'), '-'))
            yield ' |\n| Authentication active index | '
            yield str(t_1(environment.getattr((undefined(name='auth') if l_0_auth is missing else l_0_auth), 'active_index'), '-'))
            yield ' |\n'
        if (t_5(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'ip_access_group')) or t_5(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'ipv6_access_group'))):
            pass
            yield '| IPv4 access-group | '
            yield str(t_1(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'ip_access_group'), '-'))
            yield ' |\n| IPv6 access-group | '
            yield str(t_1(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'ipv6_access_group'), '-'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'srlg'), 'strict'), True):
            pass
            yield '| SRLG strict | Enabled |\n'
        elif t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'srlg'), 'enabled'), True):
            pass
            yield '| SRLG | Enabled |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'label_local_termination')):
            pass
            yield '| Label local-termination | '
            yield str(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'label_local_termination'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'preemption_method'), 'preemption')):
            pass
            yield '| Preemption method | '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'preemption_method'), 'preemption'))
            yield ' |\n'
            if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'preemption_method'), 'timer')):
                pass
                yield '| Preemption timer | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'preemption_method'), 'timer'))
                yield ' |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'mtu_signaling')):
            pass
            yield '| MTU signaling | Enabled |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'fast_reroute')):
            pass
            l_0_fast_reroute = environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'fast_reroute')
            context.vars['fast_reroute'] = l_0_fast_reroute
            context.exported_vars.add('fast_reroute')
            yield '| Fast reroute mode | '
            yield str(t_1(environment.getattr((undefined(name='fast_reroute') if l_0_fast_reroute is missing else l_0_fast_reroute), 'mode'), '-'))
            yield ' |\n| Fast reroute reversion | '
            yield str(t_1(environment.getattr((undefined(name='fast_reroute') if l_0_fast_reroute is missing else l_0_fast_reroute), 'reversion'), '-'))
            yield ' |\n| Fast reroute  bypass tunnel optimization interval | '
            yield str(t_1(environment.getattr((undefined(name='fast_reroute') if l_0_fast_reroute is missing else l_0_fast_reroute), 'bypass_tunnel_optimization_interval'), '-'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hitless_restart'), 'enabled'), True):
            pass
            yield '| Hitless restart | Active |\n| Hitless restart recovery timer | '
            yield str(t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hitless_restart'), 'timer_recovery'), '-'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'p2mp'), 'enabled')):
            pass
            yield '| P2MP | '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'p2mp'), 'enabled'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'shutdown')):
            pass
            yield '| Shutdown | '
            yield str(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'shutdown'))
            yield ' |\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'neighbors')):
            pass
            yield '\n##### RSVP Neighbor Authentication\n\n| Neighbor IP | Index | Type |\n| ----------- | ----- | ---- |\n'
            l_0_with_neighbor_ipv4_address = t_2(t_4(context, environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'neighbors'), 'ip_address', 'arista.avd.defined'), 'ip_address')
            context.vars['with_neighbor_ipv4_address'] = l_0_with_neighbor_ipv4_address
            context.exported_vars.add('with_neighbor_ipv4_address')
            l_0_with_neighbor_ipv6_address = t_2(t_4(context, environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'neighbors'), 'ipv6_address', 'arista.avd.defined'), 'ipv6_address')
            context.vars['with_neighbor_ipv6_address'] = l_0_with_neighbor_ipv6_address
            context.exported_vars.add('with_neighbor_ipv6_address')
            l_0_sorted_ip_addresses = (t_3(context.eval_ctx, (undefined(name='with_neighbor_ipv4_address') if l_0_with_neighbor_ipv4_address is missing else l_0_with_neighbor_ipv4_address)) + t_3(context.eval_ctx, (undefined(name='with_neighbor_ipv6_address') if l_0_with_neighbor_ipv6_address is missing else l_0_with_neighbor_ipv6_address)))
            context.vars['sorted_ip_addresses'] = l_0_sorted_ip_addresses
            context.exported_vars.add('sorted_ip_addresses')
            for l_1_neighbor in (undefined(name='sorted_ip_addresses') if l_0_sorted_ip_addresses is missing else l_0_sorted_ip_addresses):
                _loop_vars = {}
                pass
                if t_5(environment.getattr(l_1_neighbor, 'ip_address')):
                    pass
                    yield '| '
                    yield str(environment.getattr(l_1_neighbor, 'ip_address'))
                    yield ' | '
                    yield str(t_1(environment.getattr(environment.getattr(l_1_neighbor, 'authentication'), 'index'), '-'))
                    yield ' | '
                    yield str(t_1(environment.getattr(environment.getattr(l_1_neighbor, 'authentication'), 'type'), '-'))
                    yield ' |\n'
                elif t_5(environment.getattr(l_1_neighbor, 'ipv6_address')):
                    pass
                    yield '| '
                    yield str(environment.getattr(l_1_neighbor, 'ipv6_address'))
                    yield ' | '
                    yield str(t_1(environment.getattr(environment.getattr(l_1_neighbor, 'authentication'), 'index'), '-'))
                    yield ' | '
                    yield str(t_1(environment.getattr(environment.getattr(l_1_neighbor, 'authentication'), 'type'), '-'))
                    yield ' |\n'
            l_1_neighbor = missing
        if t_5(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'graceful_restart')):
            pass
            l_0_graceful_restart = environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'graceful_restart')
            context.vars['graceful_restart'] = l_0_graceful_restart
            context.exported_vars.add('graceful_restart')
            yield '\n##### RSVP Graceful Restart\n\n| Role | Recovery timer | Restart timer |\n| ---- | -------------- | ------------- |\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_helper'), 'enabled'), True):
                pass
                yield '| Helper | '
                yield str(t_1(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_helper'), 'timer_recovery'), '-'))
                yield ' | '
                yield str(t_1(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_helper'), 'timer_restart'), '-'))
                yield ' |\n'
            if t_5(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_speaker'), 'enabled'), True):
                pass
                yield '| Speaker | '
                yield str(t_1(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_speaker'), 'timer_recovery'), '-'))
                yield ' | '
                yield str(t_1(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_speaker'), 'timer_restart'), '-'))
                yield ' |\n'

blocks = {}
debug_info = '7=48&15=51&16=53&17=56&19=58&20=61&23=63&24=66&25=68&27=70&28=72&29=76&30=78&31=80&33=82&34=85&35=87&37=89&39=92&42=95&43=98&45=100&46=103&47=105&48=108&51=110&54=113&55=115&56=119&57=121&58=123&60=125&62=128&64=130&65=133&67=135&68=138&70=140&76=143&77=146&78=149&79=152&80=155&81=158&82=164&83=167&87=174&88=176&94=180&95=183&97=187&98=190'