from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/queue-monitor.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_queue_monitor_length = resolve('queue_monitor_length')
    l_0_queue_monitor_streaming = resolve('queue_monitor_streaming')
    l_0_enabled = resolve('enabled')
    l_0_log = resolve('log')
    l_0_default_high = resolve('default_high')
    l_0_default_low = resolve('default_low')
    l_0_notifying = resolve('notifying')
    l_0_tx_latency = resolve('tx_latency')
    l_0_cpu_high = resolve('cpu_high')
    l_0_cpu_low = resolve('cpu_low')
    l_0_mirror = resolve('mirror')
    l_0_mirror_destination = resolve('mirror_destination')
    l_0_vrf = resolve('vrf')
    l_0_ip_acl = resolve('ip_acl')
    l_0_ipv6_acl = resolve('ipv6_acl')
    l_0_max_connections = resolve('max_connections')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_3 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_4 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if (t_4((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length)) or t_4((undefined(name='queue_monitor_streaming') if l_0_queue_monitor_streaming is missing else l_0_queue_monitor_streaming))):
        pass
        yield '\n## Queue Monitor\n'
        if t_4((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length)):
            pass
            yield '\n### Queue Monitor Length\n'
            l_0_enabled = t_1(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'enabled'), '-')
            context.vars['enabled'] = l_0_enabled
            context.exported_vars.add('enabled')
            l_0_log = t_1(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'log'), '-')
            context.vars['log'] = l_0_log
            context.exported_vars.add('log')
            l_0_default_high = t_1(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'default_thresholds'), 'high'), '-')
            context.vars['default_high'] = l_0_default_high
            context.exported_vars.add('default_high')
            l_0_default_low = t_1(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'default_thresholds'), 'low'), '-')
            context.vars['default_low'] = l_0_default_low
            context.exported_vars.add('default_low')
            l_0_notifying = ('enabled' if t_4(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'notifying'), True) else 'disabled')
            context.vars['notifying'] = l_0_notifying
            context.exported_vars.add('notifying')
            l_0_tx_latency = ('enabled' if t_4(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'tx_latency'), True) else 'disabled')
            context.vars['tx_latency'] = l_0_tx_latency
            context.exported_vars.add('tx_latency')
            l_0_cpu_high = t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'cpu'), 'thresholds'), 'high'), '-')
            context.vars['cpu_high'] = l_0_cpu_high
            context.exported_vars.add('cpu_high')
            l_0_cpu_low = t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'cpu'), 'thresholds'), 'low'), '-')
            context.vars['cpu_low'] = l_0_cpu_low
            context.exported_vars.add('cpu_low')
            l_0_mirror = t_1(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'enabled'), '-')
            context.vars['mirror'] = l_0_mirror
            context.exported_vars.add('mirror')
            l_0_mirror_destination = []
            context.vars['mirror_destination'] = l_0_mirror_destination
            context.exported_vars.add('mirror_destination')
            if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'cpu'), True):
                pass
                context.call(environment.getattr((undefined(name='mirror_destination') if l_0_mirror_destination is missing else l_0_mirror_destination), 'append'), 'Cpu')
            if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'tunnel_mode_gre')):
                pass
                context.call(environment.getattr((undefined(name='mirror_destination') if l_0_mirror_destination is missing else l_0_mirror_destination), 'append'), 'Tunnel')
            if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'ethernet_interfaces')):
                pass
                context.call(environment.getattr((undefined(name='mirror_destination') if l_0_mirror_destination is missing else l_0_mirror_destination), 'extend'), environment.getattr(environment.getattr(environment.getattr((undefined(name='queue_monitor_length') if l_0_queue_monitor_length is missing else l_0_queue_monitor_length), 'mirror'), 'destination'), 'ethernet_interfaces'))
            if (t_3((undefined(name='mirror_destination') if l_0_mirror_destination is missing else l_0_mirror_destination)) == 0):
                pass
                l_0_mirror_destination = ['-']
                context.vars['mirror_destination'] = l_0_mirror_destination
                context.exported_vars.add('mirror_destination')
            yield '\n| Enabled | Logging Interval | Default Thresholds High | Default Thresholds Low | Notifying | TX Latency | CPU Thresholds High | CPU Thresholds Low | Mirroring Enabled | Mirror destinations |\n| ------- | ---------------- | ----------------------- | ---------------------- | --------- | ---------- | ------------------- | ------------------ | ----------------- | ------------------ |\n| '
            yield str((undefined(name='enabled') if l_0_enabled is missing else l_0_enabled))
            yield ' | '
            yield str((undefined(name='log') if l_0_log is missing else l_0_log))
            yield ' | '
            yield str((undefined(name='default_high') if l_0_default_high is missing else l_0_default_high))
            yield ' | '
            yield str((undefined(name='default_low') if l_0_default_low is missing else l_0_default_low))
            yield ' | '
            yield str((undefined(name='notifying') if l_0_notifying is missing else l_0_notifying))
            yield ' | '
            yield str((undefined(name='tx_latency') if l_0_tx_latency is missing else l_0_tx_latency))
            yield ' | '
            yield str((undefined(name='cpu_high') if l_0_cpu_high is missing else l_0_cpu_high))
            yield ' | '
            yield str((undefined(name='cpu_low') if l_0_cpu_low is missing else l_0_cpu_low))
            yield ' | '
            yield str((undefined(name='mirror') if l_0_mirror is missing else l_0_mirror))
            yield ' | '
            yield str(t_2(context.eval_ctx, (undefined(name='mirror_destination') if l_0_mirror_destination is missing else l_0_mirror_destination), ', '))
            yield ' |\n'
        if t_4((undefined(name='queue_monitor_streaming') if l_0_queue_monitor_streaming is missing else l_0_queue_monitor_streaming)):
            pass
            yield '\n### Queue Monitor Streaming\n'
            l_0_enabled = t_1(environment.getattr((undefined(name='queue_monitor_streaming') if l_0_queue_monitor_streaming is missing else l_0_queue_monitor_streaming), 'enable'), '-')
            context.vars['enabled'] = l_0_enabled
            context.exported_vars.add('enabled')
            l_0_vrf = t_1(environment.getattr((undefined(name='queue_monitor_streaming') if l_0_queue_monitor_streaming is missing else l_0_queue_monitor_streaming), 'vrf'), '-')
            context.vars['vrf'] = l_0_vrf
            context.exported_vars.add('vrf')
            l_0_ip_acl = t_1(environment.getattr((undefined(name='queue_monitor_streaming') if l_0_queue_monitor_streaming is missing else l_0_queue_monitor_streaming), 'ip_access_group'), '-')
            context.vars['ip_acl'] = l_0_ip_acl
            context.exported_vars.add('ip_acl')
            l_0_ipv6_acl = t_1(environment.getattr((undefined(name='queue_monitor_streaming') if l_0_queue_monitor_streaming is missing else l_0_queue_monitor_streaming), 'ipv6_access_group'), '-')
            context.vars['ipv6_acl'] = l_0_ipv6_acl
            context.exported_vars.add('ipv6_acl')
            l_0_max_connections = t_1(environment.getattr((undefined(name='queue_monitor_streaming') if l_0_queue_monitor_streaming is missing else l_0_queue_monitor_streaming), 'max_connections'), '-')
            context.vars['max_connections'] = l_0_max_connections
            context.exported_vars.add('max_connections')
            yield '\n| Enabled | IP Access Group | IPv6 Access Group | Max Connections | VRF |\n| ------- | --------------- | ----------------- | --------------- | --- |\n| '
            yield str((undefined(name='enabled') if l_0_enabled is missing else l_0_enabled))
            yield ' | '
            yield str((undefined(name='ip_acl') if l_0_ip_acl is missing else l_0_ip_acl))
            yield ' | '
            yield str((undefined(name='ipv6_acl') if l_0_ipv6_acl is missing else l_0_ipv6_acl))
            yield ' | '
            yield str((undefined(name='max_connections') if l_0_max_connections is missing else l_0_max_connections))
            yield ' | '
            yield str((undefined(name='vrf') if l_0_vrf is missing else l_0_vrf))
            yield ' |\n'
        yield '\n### Queue Monitor Configuration\n\n```eos\n'
        template = environment.get_template('eos/queue-monitor-length.j2', 'documentation/queue-monitor.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'cpu_high': l_0_cpu_high, 'cpu_low': l_0_cpu_low, 'default_high': l_0_default_high, 'default_low': l_0_default_low, 'enabled': l_0_enabled, 'ip_acl': l_0_ip_acl, 'ipv6_acl': l_0_ipv6_acl, 'log': l_0_log, 'max_connections': l_0_max_connections, 'mirror': l_0_mirror, 'mirror_destination': l_0_mirror_destination, 'notifying': l_0_notifying, 'tx_latency': l_0_tx_latency, 'vrf': l_0_vrf}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        template = environment.get_template('eos/queue-monitor-streaming.j2', 'documentation/queue-monitor.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'cpu_high': l_0_cpu_high, 'cpu_low': l_0_cpu_low, 'default_high': l_0_default_high, 'default_low': l_0_default_low, 'enabled': l_0_enabled, 'ip_acl': l_0_ip_acl, 'ipv6_acl': l_0_ipv6_acl, 'log': l_0_log, 'max_connections': l_0_max_connections, 'mirror': l_0_mirror, 'mirror_destination': l_0_mirror_destination, 'notifying': l_0_notifying, 'tx_latency': l_0_tx_latency, 'vrf': l_0_vrf}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=51&10=54&13=57&14=60&15=63&16=66&17=69&18=72&19=75&20=78&21=81&22=84&23=87&24=89&26=90&27=92&29=93&30=95&32=96&33=98&38=102&40=122&43=125&44=128&45=131&46=134&47=137&51=141&57=152&58=158'