from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/ptp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ptp = resolve('ptp')
    l_0_clock_id = resolve('clock_id')
    l_0_sip = resolve('sip')
    l_0_pri1 = resolve('pri1')
    l_0_pri2 = resolve('pri2')
    l_0_ttl = resolve('ttl')
    l_0_domain = resolve('domain')
    l_0_mode = resolve('mode')
    l_0_forward_unicast = resolve('forward_unicast')
    l_0_forward_v1 = resolve('forward_v1')
    l_0_free_running = resolve('free_running')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_2((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp)):
        pass
        yield '\n### PTP\n'
        if t_2(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'profile')):
            pass
            yield '\nPTP Profile: '
            yield str(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'profile'))
            yield '\n'
        yield '\n#### PTP Summary\n\n| Clock ID | Source IP | Priority 1 | Priority 2 | TTL | Domain | Mode | Forward V1 | Forward Unicast | Free Running Enabled |\n| -------- | --------- | ---------- | ---------- | --- | ------ | ---- | ---------- | --------------- | -------------------- |\n'
        l_0_clock_id = t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'clock_identity'), '-')
        context.vars['clock_id'] = l_0_clock_id
        context.exported_vars.add('clock_id')
        l_0_sip = t_1(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'source'), 'ip'), '-')
        context.vars['sip'] = l_0_sip
        context.exported_vars.add('sip')
        l_0_pri1 = t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'priority1'), '-')
        context.vars['pri1'] = l_0_pri1
        context.exported_vars.add('pri1')
        l_0_pri2 = t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'priority2'), '-')
        context.vars['pri2'] = l_0_pri2
        context.exported_vars.add('pri2')
        l_0_ttl = t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'ttl'), '-')
        context.vars['ttl'] = l_0_ttl
        context.exported_vars.add('ttl')
        l_0_domain = t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'domain'), '-')
        context.vars['domain'] = l_0_domain
        context.exported_vars.add('domain')
        l_0_mode = t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'mode'), '-')
        context.vars['mode'] = l_0_mode
        context.exported_vars.add('mode')
        l_0_forward_unicast = t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'forward_unicast'), '-')
        context.vars['forward_unicast'] = l_0_forward_unicast
        context.exported_vars.add('forward_unicast')
        l_0_forward_v1 = t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'forward_v1'), '-')
        context.vars['forward_v1'] = l_0_forward_v1
        context.exported_vars.add('forward_v1')
        l_0_free_running = t_1(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'free_running'), 'enabled'), '-')
        context.vars['free_running'] = l_0_free_running
        context.exported_vars.add('free_running')
        if t_2(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'free_running'), 'source_clock_hardware'), True):
            pass
            l_0_free_running = str_join(((undefined(name='free_running') if l_0_free_running is missing else l_0_free_running), ' (Hardware)', ))
            context.vars['free_running'] = l_0_free_running
            context.exported_vars.add('free_running')
        yield '| '
        yield str((undefined(name='clock_id') if l_0_clock_id is missing else l_0_clock_id))
        yield ' | '
        yield str((undefined(name='sip') if l_0_sip is missing else l_0_sip))
        yield ' | '
        yield str((undefined(name='pri1') if l_0_pri1 is missing else l_0_pri1))
        yield ' | '
        yield str((undefined(name='pri2') if l_0_pri2 is missing else l_0_pri2))
        yield ' | '
        yield str((undefined(name='ttl') if l_0_ttl is missing else l_0_ttl))
        yield ' | '
        yield str((undefined(name='domain') if l_0_domain is missing else l_0_domain))
        yield ' | '
        yield str((undefined(name='mode') if l_0_mode is missing else l_0_mode))
        yield ' | '
        yield str((undefined(name='forward_v1') if l_0_forward_v1 is missing else l_0_forward_v1))
        yield ' | '
        yield str((undefined(name='forward_unicast') if l_0_forward_unicast is missing else l_0_forward_unicast))
        yield ' | '
        yield str((undefined(name='free_running') if l_0_free_running is missing else l_0_free_running))
        yield ' |\n\n#### PTP Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/ptp.j2', 'documentation/ptp.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'clock_id': l_0_clock_id, 'domain': l_0_domain, 'forward_unicast': l_0_forward_unicast, 'forward_v1': l_0_forward_v1, 'free_running': l_0_free_running, 'mode': l_0_mode, 'pri1': l_0_pri1, 'pri2': l_0_pri2, 'sip': l_0_sip, 'ttl': l_0_ttl}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=34&10=37&12=40&19=43&20=46&21=49&22=52&23=55&24=58&25=61&26=64&27=67&28=70&29=73&30=75&32=79&37=99'