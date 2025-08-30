from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/port-channel.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_port_channel = resolve('port_channel')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['replace']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'replace' found.")
    try:
        t_3 = environment.filters['upper']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'upper' found.")
    try:
        t_4 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_4((undefined(name='port_channel') if l_0_port_channel is missing else l_0_port_channel)):
        pass
        yield '\n## Port-Channel\n\n### Port-Channel Summary\n'
        if t_4(environment.getattr((undefined(name='port_channel') if l_0_port_channel is missing else l_0_port_channel), 'load_balance_sand_profile')):
            pass
            yield '\nPort-Channel load balance Sand platform profile: '
            yield str(environment.getattr((undefined(name='port_channel') if l_0_port_channel is missing else l_0_port_channel), 'load_balance_sand_profile'))
            yield '\n'
        if t_4(environment.getattr((undefined(name='port_channel') if l_0_port_channel is missing else l_0_port_channel), 'load_balance_trident_udf')):
            pass
            yield '\n#### Port-channel Load-balance Trident UDF Eth-type Headers\n\n| Eth-Type | IP Protocol | Header | Offset | Mask |\n| -------- | ----------- | ------ | ------ | ---- |\n'
            for l_1_udf_field in environment.getattr((undefined(name='port_channel') if l_0_port_channel is missing else l_0_port_channel), 'load_balance_trident_udf'):
                _loop_vars = {}
                pass
                yield '| '
                yield str(t_2(context.eval_ctx, environment.getattr(l_1_udf_field, 'eth_type'), 'ip', 'IP'))
                yield ' | '
                yield str(t_3(t_1(environment.getattr(l_1_udf_field, 'ip_protocol'), '-')))
                yield ' | '
                yield str(t_2(context.eval_ctx, environment.getattr(l_1_udf_field, 'header'), '_', ' '))
                yield ' | '
                yield str(environment.getattr(l_1_udf_field, 'offset'))
                yield ' | '
                yield str(t_1(environment.getattr(l_1_udf_field, 'mask'), '-'))
                yield ' |\n'
            l_1_udf_field = missing
        yield '\n### Port-channel Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/port-channel.j2', 'documentation/port-channel.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=36&12=39&14=42&16=44&22=47&23=51&30=63'