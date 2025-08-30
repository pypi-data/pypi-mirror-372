from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/queue-monitor-length.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_queue_monitor_length = resolve('queue_monitor_length')
    l_0_default_thresholds_cli = resolve('default_thresholds_cli')
    l_0_tunnel_mode_gre = resolve('tunnel_mode_gre')
    l_0_tunnel_config = resolve('tunnel_config')
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
    if t_2(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'enabled'), True):
        pass
        yield '!\nqueue-monitor length\n'
        if t_2(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'notifying'), True):
            pass
            yield 'queue-monitor length notifying\n'
        elif t_2(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'notifying'), False):
            pass
            yield 'no queue-monitor length notifying\n'
        if t_2(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'tx_latency'), True):
            pass
            yield 'queue-monitor length tx-latency\n'
        if t_2(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'default_thresholds'), 'high')):
            pass
            l_0_default_thresholds_cli = 'queue-monitor length default threshold'
            context.vars['default_thresholds_cli'] = l_0_default_thresholds_cli
            context.exported_vars.add('default_thresholds_cli')
            if t_2(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'default_thresholds'), 'low')):
                pass
                l_0_default_thresholds_cli = str_join(((undefined(name='default_thresholds_cli') if l_0_default_thresholds_cli is missing else l_0_default_thresholds_cli), 's ', environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'default_thresholds'), 'high'), ' ', environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'default_thresholds'), 'low'), ))
                context.vars['default_thresholds_cli'] = l_0_default_thresholds_cli
                context.exported_vars.add('default_thresholds_cli')
            else:
                pass
                l_0_default_thresholds_cli = str_join(((undefined(name='default_thresholds_cli') if l_0_default_thresholds_cli is missing else l_0_default_thresholds_cli), ' ', environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'default_thresholds'), 'high'), ))
                context.vars['default_thresholds_cli'] = l_0_default_thresholds_cli
                context.exported_vars.add('default_thresholds_cli')
            yield str((undefined(name='default_thresholds_cli') if l_0_default_thresholds_cli is missing else l_0_default_thresholds_cli))
            yield '\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'cpu'), 'thresholds'), 'high')):
            pass
            if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'cpu'), 'thresholds'), 'low')):
                pass
                yield 'queue-monitor length cpu thresholds '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'cpu'), 'thresholds'), 'high'))
                yield ' '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'cpu'), 'thresholds'), 'low'))
                yield '\n'
            else:
                pass
                yield 'queue-monitor length cpu threshold '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'cpu'), 'thresholds'), 'high'))
                yield '\n'
        if t_2(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'log')):
            pass
            yield '!\nqueue-monitor length log '
            yield str(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'log'))
            yield '\n'
        if (((t_2(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'enabled'), True) or t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'cpu'), True)) or t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'ethernet_interfaces'))) or t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'tunnel_mode_gre'))):
            pass
            yield '!\n'
            if t_2(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'enabled'), True):
                pass
                yield 'queue-monitor length mirror\n'
            if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'cpu'), True):
                pass
                yield 'queue-monitor length mirror destination Cpu\n'
            for l_1_ethernet_interface in t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'ethernet_interfaces')):
                _loop_vars = {}
                pass
                yield 'queue-monitor length mirror destination '
                yield str(l_1_ethernet_interface)
                yield '\n'
            l_1_ethernet_interface = missing
            if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'tunnel_mode_gre')):
                pass
                l_0_tunnel_mode_gre = environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'tunnel_mode_gre')
                context.vars['tunnel_mode_gre'] = l_0_tunnel_mode_gre
                context.exported_vars.add('tunnel_mode_gre')
                l_0_tunnel_config = str_join(('queue-monitor length mirror destination tunnel mode gre source ', environment.getattr((undefined(name='tunnel_mode_gre') if l_0_tunnel_mode_gre is missing else l_0_tunnel_mode_gre), 'source'), ' destination ', environment.getattr((undefined(name='tunnel_mode_gre') if l_0_tunnel_mode_gre is missing else l_0_tunnel_mode_gre), 'destination'), ))
                context.vars['tunnel_config'] = l_0_tunnel_config
                context.exported_vars.add('tunnel_config')
                if t_2(environment.getattr((undefined(name='tunnel_mode_gre') if l_0_tunnel_mode_gre is missing else l_0_tunnel_mode_gre), 'ttl')):
                    pass
                    l_0_tunnel_config = str_join(((undefined(name='tunnel_config') if l_0_tunnel_config is missing else l_0_tunnel_config), ' ttl ', environment.getattr((undefined(name='tunnel_mode_gre') if l_0_tunnel_mode_gre is missing else l_0_tunnel_mode_gre), 'ttl'), ))
                    context.vars['tunnel_config'] = l_0_tunnel_config
                    context.exported_vars.add('tunnel_config')
                if t_2(environment.getattr((undefined(name='tunnel_mode_gre') if l_0_tunnel_mode_gre is missing else l_0_tunnel_mode_gre), 'dscp')):
                    pass
                    l_0_tunnel_config = str_join(((undefined(name='tunnel_config') if l_0_tunnel_config is missing else l_0_tunnel_config), ' dscp ', environment.getattr((undefined(name='tunnel_mode_gre') if l_0_tunnel_mode_gre is missing else l_0_tunnel_mode_gre), 'dscp'), ))
                    context.vars['tunnel_config'] = l_0_tunnel_config
                    context.exported_vars.add('tunnel_config')
                if t_2(environment.getattr((undefined(name='tunnel_mode_gre') if l_0_tunnel_mode_gre is missing else l_0_tunnel_mode_gre), 'protocol')):
                    pass
                    l_0_tunnel_config = str_join(((undefined(name='tunnel_config') if l_0_tunnel_config is missing else l_0_tunnel_config), ' protocol ', environment.getattr((undefined(name='tunnel_mode_gre') if l_0_tunnel_mode_gre is missing else l_0_tunnel_mode_gre), 'protocol'), ))
                    context.vars['tunnel_config'] = l_0_tunnel_config
                    context.exported_vars.add('tunnel_config')
                if t_2(environment.getattr((undefined(name='tunnel_mode_gre') if l_0_tunnel_mode_gre is missing else l_0_tunnel_mode_gre), 'vrf')):
                    pass
                    l_0_tunnel_config = str_join(((undefined(name='tunnel_config') if l_0_tunnel_config is missing else l_0_tunnel_config), ' vrf ', environment.getattr((undefined(name='tunnel_mode_gre') if l_0_tunnel_mode_gre is missing else l_0_tunnel_mode_gre), 'vrf'), ))
                    context.vars['tunnel_config'] = l_0_tunnel_config
                    context.exported_vars.add('tunnel_config')
                yield str((undefined(name='tunnel_config') if l_0_tunnel_config is missing else l_0_tunnel_config))
                yield '\n'

blocks = {}
debug_info = '7=27&10=30&12=33&15=36&18=39&19=41&20=44&21=46&23=51&25=54&27=56&28=58&29=61&31=68&34=70&36=73&38=75&43=78&46=81&49=84&50=88&52=91&53=93&54=96&55=99&56=101&58=104&59=106&61=109&62=111&64=114&65=116&67=119'