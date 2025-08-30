from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/errdisable.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_errdisable = resolve('errdisable')
    l_0_combined_causes = resolve('combined_causes')
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
        t_3 = environment.filters['unique']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'unique' found.")
    try:
        t_4 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_4((undefined(name='errdisable') if l_0_errdisable is missing else l_0_errdisable)):
        pass
        yield '\n## Errdisable\n\n### Errdisable Summary\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='errdisable') if l_0_errdisable is missing else l_0_errdisable), 'recovery'), 'interval')):
            pass
            yield '\nErrdisable recovery timer interval: '
            yield str(environment.getattr(environment.getattr((undefined(name='errdisable') if l_0_errdisable is missing else l_0_errdisable), 'recovery'), 'interval'))
            yield ' seconds\n'
        if (t_4(environment.getattr(environment.getattr((undefined(name='errdisable') if l_0_errdisable is missing else l_0_errdisable), 'detect'), 'causes')) or t_4(environment.getattr(environment.getattr((undefined(name='errdisable') if l_0_errdisable is missing else l_0_errdisable), 'recovery'), 'causes'))):
            pass
            l_0_combined_causes = t_3(environment, (t_1(environment.getattr(environment.getattr((undefined(name='errdisable') if l_0_errdisable is missing else l_0_errdisable), 'detect'), 'causes'), []) + t_1(environment.getattr(environment.getattr((undefined(name='errdisable') if l_0_errdisable is missing else l_0_errdisable), 'recovery'), 'causes'), [])))
            context.vars['combined_causes'] = l_0_combined_causes
            context.exported_vars.add('combined_causes')
            yield '\n|  Cause | Detection Enabled | Recovery Enabled |\n| ------ | ----------------- | ---------------- |\n'
            for l_1_cause in t_2((undefined(name='combined_causes') if l_0_combined_causes is missing else l_0_combined_causes)):
                l_1_detect_status = resolve('detect_status')
                l_1_recovery_status = resolve('recovery_status')
                _loop_vars = {}
                pass
                if (l_1_cause in t_1(environment.getattr(environment.getattr((undefined(name='errdisable') if l_0_errdisable is missing else l_0_errdisable), 'detect'), 'causes'), [])):
                    pass
                    l_1_detect_status = True
                    _loop_vars['detect_status'] = l_1_detect_status
                else:
                    pass
                    l_1_detect_status = '-'
                    _loop_vars['detect_status'] = l_1_detect_status
                if (l_1_cause in t_1(environment.getattr(environment.getattr((undefined(name='errdisable') if l_0_errdisable is missing else l_0_errdisable), 'recovery'), 'causes'), [])):
                    pass
                    l_1_recovery_status = True
                    _loop_vars['recovery_status'] = l_1_recovery_status
                else:
                    pass
                    l_1_recovery_status = '-'
                    _loop_vars['recovery_status'] = l_1_recovery_status
                yield '| '
                yield str(l_1_cause)
                yield ' | '
                yield str((undefined(name='detect_status') if l_1_detect_status is missing else l_1_detect_status))
                yield ' | '
                yield str((undefined(name='recovery_status') if l_1_recovery_status is missing else l_1_recovery_status))
                yield ' |\n'
            l_1_cause = l_1_detect_status = l_1_recovery_status = missing
        yield '\n```eos\n'
        template = environment.get_template('eos/errdisable.j2', 'documentation/errdisable.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'combined_causes': l_0_combined_causes}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=37&12=40&14=43&16=45&17=47&21=51&22=56&23=58&25=62&27=64&28=66&30=70&32=73&37=81'