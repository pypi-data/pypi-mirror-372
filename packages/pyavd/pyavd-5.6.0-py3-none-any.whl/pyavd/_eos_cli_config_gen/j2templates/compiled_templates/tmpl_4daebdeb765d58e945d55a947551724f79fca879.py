from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/platform-sfe-interface.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_platform = resolve('platform')
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
    if t_2(environment.getattr(environment.getattr((undefined(name='platform') if l_0_platform is missing else l_0_platform), 'sfe'), 'interface')):
        pass
        yield '!\nplatform sfe interface\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='platform') if l_0_platform is missing else l_0_platform), 'sfe'), 'interface'), 'interface_profile')):
            pass
            yield '   interface profile '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='platform') if l_0_platform is missing else l_0_platform), 'sfe'), 'interface'), 'interface_profile'))
            yield '\n'
        l_1_loop = missing
        for l_1_profile_data, l_1_loop in LoopContext(t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='platform') if l_0_platform is missing else l_0_platform), 'sfe'), 'interface'), 'profiles'), 'name'), undefined):
            _loop_vars = {}
            pass
            yield '   !\n   profile '
            yield str(environment.getattr(l_1_profile_data, 'name'))
            yield '\n'
            l_2_loop = missing
            for l_2_interface_data, l_2_loop in LoopContext(t_1(environment.getattr(l_1_profile_data, 'interfaces'), 'name'), undefined):
                _loop_vars = {}
                pass
                yield '      interface '
                yield str(environment.getattr(l_2_interface_data, 'name'))
                yield '\n'
                if t_2(environment.getattr(environment.getattr(l_2_interface_data, 'rx_queue'), 'count')):
                    pass
                    yield '         rx-queue count '
                    yield str(environment.getattr(environment.getattr(l_2_interface_data, 'rx_queue'), 'count'))
                    yield '\n'
                if t_2(environment.getattr(environment.getattr(l_2_interface_data, 'rx_queue'), 'worker')):
                    pass
                    yield '         rx-queue worker '
                    yield str(environment.getattr(environment.getattr(l_2_interface_data, 'rx_queue'), 'worker'))
                    yield '\n'
                if t_2(environment.getattr(environment.getattr(l_2_interface_data, 'rx_queue'), 'mode')):
                    pass
                    yield '         rx-queue mode '
                    yield str(environment.getattr(environment.getattr(l_2_interface_data, 'rx_queue'), 'mode'))
                    yield '\n'
                if (not environment.getattr(l_2_loop, 'last')):
                    pass
                    yield '      !\n'
            l_2_loop = l_2_interface_data = missing
        l_1_loop = l_1_profile_data = missing

blocks = {}
debug_info = '7=24&11=27&12=30&14=33&17=37&18=40&19=44&20=46&21=49&23=51&24=54&26=56&27=59&29=61'