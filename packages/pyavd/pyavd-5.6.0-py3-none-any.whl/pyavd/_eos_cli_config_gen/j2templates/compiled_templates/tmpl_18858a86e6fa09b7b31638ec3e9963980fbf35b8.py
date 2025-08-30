from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/load-balance.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_load_balance = resolve('load_balance')
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
    if t_2(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'policies')):
        pass
        yield '!\nload-balance policies\n'
        l_1_loop = missing
        for l_1_profile, l_1_loop in LoopContext(t_1(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'policies'), 'sand_profiles'), 'name'), undefined):
            _loop_vars = {}
            pass
            if (not environment.getattr(l_1_loop, 'first')):
                pass
                yield '   !\n'
            yield '   load-balance sand profile '
            yield str(environment.getattr(l_1_profile, 'name'))
            yield '\n'
            if t_2(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp')):
                pass
                yield '      fields udp dst-port '
                yield str(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'dst_port'))
                yield '\n'
                if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match')):
                    pass
                    yield '         match payload bits '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match'), 'payload_bits'))
                    yield ' pattern '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match'), 'pattern'))
                    yield ' hash payload bytes '
                    yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match'), 'hash_payload_bytes'))
                    yield '\n'
                if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'payload_bytes')):
                    pass
                    yield '         payload bytes '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'payload_bytes'))
                    yield '\n'
        l_1_loop = l_1_profile = missing

blocks = {}
debug_info = '7=24&10=28&11=31&14=35&15=37&16=40&17=42&18=45&20=51&21=54'