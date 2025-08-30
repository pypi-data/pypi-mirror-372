from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/qos.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_qos = resolve('qos')
    l_0_ecn_command = resolve('ecn_command')
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
        t_3 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    try:
        t_4 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_4((undefined(name='qos') if l_0_qos is missing else l_0_qos)):
        pass
        yield '\n### QOS\n\n#### QOS Summary\n'
        if t_4(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'rewrite_dscp'), True):
            pass
            yield '\nQOS rewrite DSCP: **enabled**\n'
        else:
            pass
            yield '\nQOS rewrite DSCP: **disabled**\n'
        if t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'random_detect'), 'ecn'), 'allow_non_ect'), 'enabled')):
            pass
            l_0_ecn_command = 'QOS random-detect ECN is set to allow **non-ect**'
            context.vars['ecn_command'] = l_0_ecn_command
            context.exported_vars.add('ecn_command')
            if t_4(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'random_detect'), 'ecn'), 'allow_non_ect'), 'chip_based'), True):
                pass
                l_0_ecn_command = str_join(((undefined(name='ecn_command') if l_0_ecn_command is missing else l_0_ecn_command), ' **chip-based**', ))
                context.vars['ecn_command'] = l_0_ecn_command
                context.exported_vars.add('ecn_command')
            yield '\n'
            yield str((undefined(name='ecn_command') if l_0_ecn_command is missing else l_0_ecn_command))
            yield '\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'tx_queue'), 'shape_rate_percent_adaptive'), True):
            pass
            yield '\nQOS adaptive transmit queue percentage-based allocation: **enabled**\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'tx_queue'), 'queues')):
            pass
            yield '\n##### QOS Transmit Queue Parameters\n\n| Queue ID | Scheduler Profile Responsive |\n| -------- | ---------------------------- |\n'
            for l_1_queue in t_2(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'tx_queue'), 'queues'), 'id'):
                _loop_vars = {}
                pass
                yield '| '
                yield str(environment.getattr(l_1_queue, 'id'))
                yield ' | '
                yield str(t_1(environment.getattr(l_1_queue, 'scheduler_profile_responsive'), '-'))
                yield ' |\n'
            l_1_queue = missing
        if t_4(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'map')):
            pass
            yield '\n##### QOS Mappings\n'
            if t_4(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'map'), 'cos')):
                pass
                yield '\n| COS to Traffic Class mappings |\n| ----------------------------- |\n'
                for l_1_cos_map in t_2(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'map'), 'cos')):
                    _loop_vars = {}
                    pass
                    yield '| '
                    yield str(t_3(l_1_cos_map, '-'))
                    yield ' |\n'
                l_1_cos_map = missing
            if t_4(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'map'), 'dscp')):
                pass
                yield '\n| DSCP to Traffic Class mappings |\n| ------------------------------ |\n'
                for l_1_dscp_map in t_2(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'map'), 'dscp')):
                    _loop_vars = {}
                    pass
                    yield '| '
                    yield str(t_3(l_1_dscp_map, '-'))
                    yield ' |\n'
                l_1_dscp_map = missing
            if t_4(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'map'), 'exp')):
                pass
                yield '\n| EXP to Traffic Class mappings |\n| ----------------------------- |\n'
                for l_1_exp_map in t_2(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'map'), 'exp')):
                    _loop_vars = {}
                    pass
                    yield '| '
                    yield str(t_3(l_1_exp_map, '-'))
                    yield ' |\n'
                l_1_exp_map = missing
            if t_4(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'map'), 'traffic_class')):
                pass
                yield '\n| Traffic Class to DSCP or COS mappings |\n| ------------------------------------- |\n'
                for l_1_tc_map in t_2(environment.getattr(environment.getattr((undefined(name='qos') if l_0_qos is missing else l_0_qos), 'map'), 'traffic_class')):
                    _loop_vars = {}
                    pass
                    yield '| '
                    yield str(t_3(l_1_tc_map, '-'))
                    yield ' |\n'
                l_1_tc_map = missing
        yield '\n#### QOS Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/qos.j2', 'documentation/qos.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'ecn_command': l_0_ecn_command}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=37&12=40&19=46&20=48&21=51&22=53&25=57&27=59&31=62&37=65&38=69&41=74&44=77&48=80&49=84&52=87&56=90&57=94&60=97&64=100&65=104&68=107&72=110&73=114&81=118'