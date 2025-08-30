from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/port-channel.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_port_channel = resolve('port_channel')
    try:
        t_1 = environment.filters['replace']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'replace' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_2(environment.getattr((undefined(name='port_channel') if l_0_port_channel is missing else l_0_port_channel), 'load_balance_trident_udf')):
        pass
        yield '!\n'
        for l_1_udf_field in environment.getattr((undefined(name='port_channel') if l_0_port_channel is missing else l_0_port_channel), 'load_balance_trident_udf'):
            l_1_udf_header_cli = missing
            _loop_vars = {}
            pass
            l_1_udf_header_cli = str_join(('port-channel load-balance trident udf eth-type ', t_1(context.eval_ctx, environment.getattr(l_1_udf_field, 'eth_type'), 'ip', 'IP'), ))
            _loop_vars['udf_header_cli'] = l_1_udf_header_cli
            if t_2(environment.getattr(l_1_udf_field, 'ip_protocol')):
                pass
                l_1_udf_header_cli = str_join(((undefined(name='udf_header_cli') if l_1_udf_header_cli is missing else l_1_udf_header_cli), ' ip-protocol ', environment.getattr(l_1_udf_field, 'ip_protocol'), ))
                _loop_vars['udf_header_cli'] = l_1_udf_header_cli
            l_1_udf_header_cli = str_join(((undefined(name='udf_header_cli') if l_1_udf_header_cli is missing else l_1_udf_header_cli), ' header ', t_1(context.eval_ctx, environment.getattr(l_1_udf_field, 'header'), '_', ' '), ' offset ', environment.getattr(l_1_udf_field, 'offset'), ))
            _loop_vars['udf_header_cli'] = l_1_udf_header_cli
            if t_2(environment.getattr(l_1_udf_field, 'mask')):
                pass
                l_1_udf_header_cli = str_join(((undefined(name='udf_header_cli') if l_1_udf_header_cli is missing else l_1_udf_header_cli), ' mask ', environment.getattr(l_1_udf_field, 'mask'), ))
                _loop_vars['udf_header_cli'] = l_1_udf_header_cli
            yield str((undefined(name='udf_header_cli') if l_1_udf_header_cli is missing else l_1_udf_header_cli))
            yield '\n'
        l_1_udf_field = l_1_udf_header_cli = missing

blocks = {}
debug_info = '7=24&9=27&10=31&11=33&12=35&14=37&15=39&16=41&18=43'