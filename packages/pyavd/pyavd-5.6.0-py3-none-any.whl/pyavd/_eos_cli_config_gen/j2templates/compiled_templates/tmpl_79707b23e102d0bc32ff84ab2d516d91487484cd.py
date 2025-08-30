from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ptp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ptp = resolve('ptp')
    l_0_ptp_free_running = resolve('ptp_free_running')
    try:
        t_1 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_1((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp)):
        pass
        yield '!\n'
        if t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'clock_identity')):
            pass
            yield 'ptp clock-identity '
            yield str(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'clock_identity'))
            yield '\n'
        if t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'domain')):
            pass
            yield 'ptp domain '
            yield str(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'domain'))
            yield '\n'
        if t_1(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'free_running'), 'enabled'), True):
            pass
            l_0_ptp_free_running = 'ptp free-running'
            context.vars['ptp_free_running'] = l_0_ptp_free_running
            context.exported_vars.add('ptp_free_running')
            if t_1(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'free_running'), 'source_clock_hardware'), True):
                pass
                l_0_ptp_free_running = str_join(((undefined(name='ptp_free_running') if l_0_ptp_free_running is missing else l_0_ptp_free_running), ' source clock hardware', ))
                context.vars['ptp_free_running'] = l_0_ptp_free_running
                context.exported_vars.add('ptp_free_running')
            yield str((undefined(name='ptp_free_running') if l_0_ptp_free_running is missing else l_0_ptp_free_running))
            yield '\n'
        if t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'hold_ptp_time')):
            pass
            yield 'ptp hold-ptp-time '
            yield str(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'hold_ptp_time'))
            yield '\n'
        if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'message_type'), 'event'), 'dscp')):
            pass
            yield 'ptp message-type event dscp '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'message_type'), 'event'), 'dscp'))
            yield ' default\n'
        if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'message_type'), 'general'), 'dscp')):
            pass
            yield 'ptp message-type general dscp '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'message_type'), 'general'), 'dscp'))
            yield ' default\n'
        if t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'mode')):
            pass
            if (t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'mode_one_step'), True) and (environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'mode') in ['boundary', 'e2etransparent'])):
                pass
                yield 'ptp mode '
                yield str(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'mode'))
                yield ' one-step\n'
            else:
                pass
                yield 'ptp mode '
                yield str(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'mode'))
                yield '\n'
        if t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'priority1')):
            pass
            yield 'ptp priority1 '
            yield str(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'priority1'))
            yield '\n'
        if t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'priority2')):
            pass
            yield 'ptp priority2 '
            yield str(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'priority2'))
            yield '\n'
        if t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'profile')):
            pass
            yield 'ptp profile '
            yield str(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'profile'))
            yield '\n'
        if t_1(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'source'), 'ip')):
            pass
            yield 'ptp source ip '
            yield str(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'source'), 'ip'))
            yield '\n'
        if t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'ttl')):
            pass
            yield 'ptp ttl '
            yield str(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'ttl'))
            yield '\n'
        if t_1(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'free_running'), 'enabled'), False):
            pass
            yield 'no ptp free-running\n'
        if t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'forward_v1'), True):
            pass
            yield 'ptp forward-v1\n'
        if t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'forward_unicast'), True):
            pass
            yield 'ptp forward-unicast\n'
        if t_1(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'enabled'), False):
            pass
            yield 'no ptp monitor\n'
        elif t_1(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor')):
            pass
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'threshold'), 'offset_from_master')):
                pass
                yield 'ptp monitor threshold offset-from-master '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'threshold'), 'offset_from_master'))
                yield '\n'
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'threshold'), 'mean_path_delay')):
                pass
                yield 'ptp monitor threshold mean-path-delay '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'threshold'), 'mean_path_delay'))
                yield '\n'
            if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'threshold'), 'drop'), 'mean_path_delay')):
                pass
                yield 'ptp monitor threshold mean-path-delay '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'threshold'), 'drop'), 'mean_path_delay'))
                yield ' nanoseconds drop\n'
            if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'threshold'), 'drop'), 'offset_from_master')):
                pass
                yield 'ptp monitor threshold offset-from-master '
                yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'threshold'), 'drop'), 'offset_from_master'))
                yield ' nanoseconds drop\n'
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'intervals')):
                pass
                if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'intervals'), 'sync')):
                    pass
                    yield 'ptp monitor threshold missing-message sync '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'intervals'), 'sync'))
                    yield ' intervals\n'
                if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'intervals'), 'follow_up')):
                    pass
                    yield 'ptp monitor threshold missing-message follow-up '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'intervals'), 'follow_up'))
                    yield ' intervals\n'
                if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'intervals'), 'announce')):
                    pass
                    yield 'ptp monitor threshold missing-message announce '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'intervals'), 'announce'))
                    yield ' intervals\n'
            if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'sequence_ids'), 'enabled'), False):
                pass
                yield 'no ptp monitor sequence-id\n'
            elif t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'sequence_ids'), 'enabled'), True):
                pass
                yield 'ptp monitor sequence-id\n'
                if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'sequence_ids'), 'sync')):
                    pass
                    yield 'ptp monitor threshold missing-message sync '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'sequence_ids'), 'sync'))
                    yield ' sequence-ids\n'
                if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'sequence_ids'), 'follow_up')):
                    pass
                    yield 'ptp monitor threshold missing-message follow-up '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'sequence_ids'), 'follow_up'))
                    yield ' sequence-ids\n'
                if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'sequence_ids'), 'delay_resp')):
                    pass
                    yield 'ptp monitor threshold missing-message delay-resp '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'sequence_ids'), 'delay_resp'))
                    yield ' sequence-ids\n'
                if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'sequence_ids'), 'announce')):
                    pass
                    yield 'ptp monitor threshold missing-message announce '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ptp') if l_0_ptp is missing else l_0_ptp), 'monitor'), 'missing_message'), 'sequence_ids'), 'announce'))
                    yield ' sequence-ids\n'

blocks = {}
debug_info = '7=19&9=22&10=25&12=27&13=30&15=32&16=34&17=37&18=39&20=42&22=44&23=47&25=49&26=52&28=54&29=57&31=59&32=61&33=64&35=69&38=71&39=74&41=76&42=79&44=81&45=84&47=86&48=89&50=91&51=94&53=96&56=99&59=102&62=105&64=108&65=110&66=113&68=115&69=118&71=120&72=123&74=125&75=128&77=130&78=132&79=135&81=137&82=140&84=142&85=145&88=147&90=150&92=153&93=156&95=158&96=161&98=163&99=166&101=168&102=171'