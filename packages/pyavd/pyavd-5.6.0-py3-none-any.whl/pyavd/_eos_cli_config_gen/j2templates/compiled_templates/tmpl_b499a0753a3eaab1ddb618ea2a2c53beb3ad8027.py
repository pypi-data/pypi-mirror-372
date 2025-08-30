from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/mpls.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_mpls = resolve('mpls')
    l_0_auth = resolve('auth')
    l_0_with_neighbor_ipv4_address = resolve('with_neighbor_ipv4_address')
    l_0_with_neighbor_ipv6_address = resolve('with_neighbor_ipv6_address')
    l_0_sorted_ip_addresses = resolve('sorted_ip_addresses')
    l_0_fast_reroute = resolve('fast_reroute')
    l_0_srlg_cli = resolve('srlg_cli')
    l_0_preemption_cli = resolve('preemption_cli')
    l_0_graceful_restart = resolve('graceful_restart')
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
        t_4 = environment.filters['list']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'list' found.")
    try:
        t_5 = environment.filters['selectattr']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'selectattr' found.")
    try:
        t_6 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_6(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'ip'), True):
        pass
        yield '!\nmpls ip\n'
    if (t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'tunnel'), 'termination'), 'model'), 'ttl')) and t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'tunnel'), 'termination'), 'model'), 'dscp'))):
        pass
        yield 'mpls tunnel termination model ttl '
        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'tunnel'), 'termination'), 'model'), 'ttl'))
        yield ' dscp '
        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'tunnel'), 'termination'), 'model'), 'dscp'))
        yield '\n'
    if (t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'tunnel'), 'termination'), 'php_model'), 'ttl')) and t_6(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'tunnel'), 'termination'), 'php_model'), 'dscp'))):
        pass
        yield 'mpls tunnel termination php model ttl '
        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'tunnel'), 'termination'), 'php_model'), 'ttl'))
        yield ' dscp '
        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'tunnel'), 'termination'), 'php_model'), 'dscp'))
        yield '\n'
    if t_6(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'ldp')):
        pass
        yield '!\nmpls ldp\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'ldp'), 'router_id')):
            pass
            yield '   router-id '
            yield str(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'ldp'), 'router_id'))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'ldp'), 'transport_address_interface')):
            pass
            yield '   transport-address interface '
            yield str(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'ldp'), 'transport_address_interface'))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'ldp'), 'interface_disabled_default'), True):
            pass
            yield '   interface disabled default\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'ldp'), 'shutdown'), True):
            pass
            yield '   shutdown\n'
        elif t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'ldp'), 'shutdown'), False):
            pass
            yield '   no shutdown\n'
    if (t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'icmp'), 'fragmentation_needed_tunneling'), True) or t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'icmp'), 'ttl_exceeded_tunneling'), True)):
        pass
        yield '!\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'icmp'), 'fragmentation_needed_tunneling'), True):
            pass
            yield 'mpls icmp fragmentation-needed tunneling\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'icmp'), 'ttl_exceeded_tunneling'), True):
            pass
            yield 'mpls icmp ttl-exceeded tunneling\n'
    if t_6(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp')):
        pass
        yield '!\nmpls rsvp\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'refresh')):
            pass
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'refresh'), 'interval')):
                pass
                yield '   refresh interval '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'refresh'), 'interval'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'refresh'), 'method')):
                pass
                yield '   refresh method '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'refresh'), 'method'))
                yield '\n'
        if (t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hello'), 'interval')) and t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hello'), 'multiplier'))):
            pass
            yield '   hello interval '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hello'), 'interval'))
            yield ' multiplier '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hello'), 'multiplier'))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'authentication')):
            pass
            l_0_auth = environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'authentication')
            context.vars['auth'] = l_0_auth
            context.exported_vars.add('auth')
            if t_6(environment.getattr((undefined(name='auth') if l_0_auth is missing else l_0_auth), 'type')):
                pass
                yield '   authentication type '
                yield str(environment.getattr((undefined(name='auth') if l_0_auth is missing else l_0_auth), 'type'))
                yield '\n'
            if t_6(environment.getattr((undefined(name='auth') if l_0_auth is missing else l_0_auth), 'sequence_number_window')):
                pass
                yield '   authentication sequence-number window '
                yield str(environment.getattr((undefined(name='auth') if l_0_auth is missing else l_0_auth), 'sequence_number_window'))
                yield '\n'
            for l_1_password_index in t_3(environment.getattr((undefined(name='auth') if l_0_auth is missing else l_0_auth), 'password_indexes'), 'index'):
                l_1_hide_passwords = resolve('hide_passwords')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_password_index, 'password')):
                    pass
                    yield '   authentication index '
                    yield str(environment.getattr(l_1_password_index, 'index'))
                    yield ' password '
                    yield str(t_1(environment.getattr(l_1_password_index, 'password_type'), '7'))
                    yield ' '
                    yield str(t_2(environment.getattr(l_1_password_index, 'password'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)))
                    yield '\n'
            l_1_password_index = l_1_hide_passwords = missing
            if t_6(environment.getattr((undefined(name='auth') if l_0_auth is missing else l_0_auth), 'active_index')):
                pass
                yield '   authentication index '
                yield str(environment.getattr((undefined(name='auth') if l_0_auth is missing else l_0_auth), 'active_index'))
                yield ' active\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'neighbors')):
            pass
            l_0_with_neighbor_ipv4_address = t_3(t_5(context, environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'neighbors'), 'ip_address', 'arista.avd.defined'), 'ip_address')
            context.vars['with_neighbor_ipv4_address'] = l_0_with_neighbor_ipv4_address
            context.exported_vars.add('with_neighbor_ipv4_address')
            l_0_with_neighbor_ipv6_address = t_3(t_5(context, environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'neighbors'), 'ipv6_address', 'arista.avd.defined'), 'ipv6_address')
            context.vars['with_neighbor_ipv6_address'] = l_0_with_neighbor_ipv6_address
            context.exported_vars.add('with_neighbor_ipv6_address')
            l_0_sorted_ip_addresses = (t_4(context.eval_ctx, (undefined(name='with_neighbor_ipv4_address') if l_0_with_neighbor_ipv4_address is missing else l_0_with_neighbor_ipv4_address)) + t_4(context.eval_ctx, (undefined(name='with_neighbor_ipv6_address') if l_0_with_neighbor_ipv6_address is missing else l_0_with_neighbor_ipv6_address)))
            context.vars['sorted_ip_addresses'] = l_0_sorted_ip_addresses
            context.exported_vars.add('sorted_ip_addresses')
            for l_1_neighbor in t_1((undefined(name='sorted_ip_addresses') if l_0_sorted_ip_addresses is missing else l_0_sorted_ip_addresses), []):
                l_1_ip_address = resolve('ip_address')
                _loop_vars = {}
                pass
                if t_6(environment.getattr(l_1_neighbor, 'ip_address')):
                    pass
                    l_1_ip_address = environment.getattr(l_1_neighbor, 'ip_address')
                    _loop_vars['ip_address'] = l_1_ip_address
                else:
                    pass
                    l_1_ip_address = environment.getattr(l_1_neighbor, 'ipv6_address')
                    _loop_vars['ip_address'] = l_1_ip_address
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'authentication'), 'type')):
                    pass
                    yield '   neighbor '
                    yield str((undefined(name='ip_address') if l_1_ip_address is missing else l_1_ip_address))
                    yield ' authentication type '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'authentication'), 'type'))
                    yield '\n'
                if t_6(environment.getattr(environment.getattr(l_1_neighbor, 'authentication'), 'index')):
                    pass
                    yield '   neighbor '
                    yield str((undefined(name='ip_address') if l_1_ip_address is missing else l_1_ip_address))
                    yield ' authentication index '
                    yield str(environment.getattr(environment.getattr(l_1_neighbor, 'authentication'), 'index'))
                    yield ' active\n'
            l_1_neighbor = l_1_ip_address = missing
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'ip_access_group')):
            pass
            yield '   ip access-group '
            yield str(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'ip_access_group'))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'ipv6_access_group')):
            pass
            yield '   ipv6 access-group '
            yield str(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'ipv6_access_group'))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'fast_reroute')):
            pass
            l_0_fast_reroute = environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'fast_reroute')
            context.vars['fast_reroute'] = l_0_fast_reroute
            context.exported_vars.add('fast_reroute')
            if t_6(environment.getattr((undefined(name='fast_reroute') if l_0_fast_reroute is missing else l_0_fast_reroute), 'mode')):
                pass
                yield '   fast-reroute mode '
                yield str(environment.getattr((undefined(name='fast_reroute') if l_0_fast_reroute is missing else l_0_fast_reroute), 'mode'))
                yield '\n'
            if t_6(environment.getattr((undefined(name='fast_reroute') if l_0_fast_reroute is missing else l_0_fast_reroute), 'reversion')):
                pass
                yield '   fast-reroute reversion '
                yield str(environment.getattr((undefined(name='fast_reroute') if l_0_fast_reroute is missing else l_0_fast_reroute), 'reversion'))
                yield '\n'
            if t_6(environment.getattr((undefined(name='fast_reroute') if l_0_fast_reroute is missing else l_0_fast_reroute), 'bypass_tunnel_optimization_interval')):
                pass
                yield '   fast-reroute bypass tunnel optimization interval '
                yield str(environment.getattr((undefined(name='fast_reroute') if l_0_fast_reroute is missing else l_0_fast_reroute), 'bypass_tunnel_optimization_interval'))
                yield ' seconds\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'srlg'), 'enabled'), True):
            pass
            l_0_srlg_cli = 'srlg'
            context.vars['srlg_cli'] = l_0_srlg_cli
            context.exported_vars.add('srlg_cli')
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'srlg'), 'strict'), True):
                pass
                l_0_srlg_cli = str_join(((undefined(name='srlg_cli') if l_0_srlg_cli is missing else l_0_srlg_cli), ' strict', ))
                context.vars['srlg_cli'] = l_0_srlg_cli
                context.exported_vars.add('srlg_cli')
            yield '   '
            yield str((undefined(name='srlg_cli') if l_0_srlg_cli is missing else l_0_srlg_cli))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'label_local_termination')):
            pass
            yield '   label local-termination '
            yield str(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'label_local_termination'))
            yield '\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'preemption_method'), 'preemption')):
            pass
            l_0_preemption_cli = str_join(('preemption method ', environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'preemption_method'), 'preemption'), ))
            context.vars['preemption_cli'] = l_0_preemption_cli
            context.exported_vars.add('preemption_cli')
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'preemption_method'), 'timer')):
                pass
                l_0_preemption_cli = str_join(((undefined(name='preemption_cli') if l_0_preemption_cli is missing else l_0_preemption_cli), ' timer ', environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'preemption_method'), 'timer'), ))
                context.vars['preemption_cli'] = l_0_preemption_cli
                context.exported_vars.add('preemption_cli')
            yield '   '
            yield str((undefined(name='preemption_cli') if l_0_preemption_cli is missing else l_0_preemption_cli))
            yield '\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'mtu_signaling')):
            pass
            yield '   mtu signaling\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hitless_restart'), 'enabled'), True):
            pass
            yield '   !\n   hitless-restart\n'
            if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hitless_restart'), 'timer_recovery')):
                pass
                yield '      timer recovery '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'hitless_restart'), 'timer_recovery'))
                yield ' seconds\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'graceful_restart')):
            pass
            l_0_graceful_restart = environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'graceful_restart')
            context.vars['graceful_restart'] = l_0_graceful_restart
            context.exported_vars.add('graceful_restart')
            if t_6(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_helper'), 'enabled'), True):
                pass
                yield '   !\n   graceful-restart role helper\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_helper'), 'timer_recovery')):
                    pass
                    yield '      timer restart maximum '
                    yield str(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_helper'), 'timer_recovery'))
                    yield ' seconds\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_helper'), 'timer_restart')):
                    pass
                    yield '      timer recovery maximum '
                    yield str(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_helper'), 'timer_restart'))
                    yield ' seconds\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_speaker'), 'enabled'), True):
                pass
                yield '   !\n   graceful-restart role speaker\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_speaker'), 'timer_recovery')):
                    pass
                    yield '      timer restart '
                    yield str(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_speaker'), 'timer_recovery'))
                    yield ' seconds\n'
                if t_6(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_speaker'), 'timer_restart')):
                    pass
                    yield '      timer recovery '
                    yield str(environment.getattr(environment.getattr((undefined(name='graceful_restart') if l_0_graceful_restart is missing else l_0_graceful_restart), 'role_speaker'), 'timer_restart'))
                    yield ' seconds\n'
        if t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'p2mp'), 'enabled'), True):
            pass
            yield '   !\n   p2mp\n'
        elif t_6(environment.getattr(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'p2mp'), 'enabled'), False):
            pass
            yield '   !\n   p2mp\n      disabled\n'
        if t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'shutdown'), True):
            pass
            yield '   shutdown\n'
        elif t_6(environment.getattr(environment.getattr((undefined(name='mpls') if l_0_mpls is missing else l_0_mpls), 'rsvp'), 'shutdown'), False):
            pass
            yield '   no shutdown\n'

blocks = {}
debug_info = '7=56&11=59&12=62&14=66&15=69&17=73&20=76&21=79&23=81&24=84&26=86&29=89&31=92&35=95&37=98&40=101&44=104&47=107&48=109&49=112&51=114&52=117&55=119&56=122&58=126&59=128&60=131&61=134&63=136&64=139&66=141&67=145&68=148&71=155&72=158&75=160&76=162&77=165&78=168&79=171&80=175&81=177&83=181&85=183&86=186&88=190&89=193&93=198&94=201&96=203&97=206&99=208&100=210&101=213&102=216&104=218&105=221&107=223&108=226&111=228&112=230&113=233&114=235&116=239&118=241&119=244&121=246&122=248&123=251&124=253&126=257&128=259&131=262&134=265&135=268&138=270&139=272&140=275&143=278&144=281&146=283&147=286&150=288&153=291&154=294&156=296&157=299&161=301&164=304&169=307&171=310'