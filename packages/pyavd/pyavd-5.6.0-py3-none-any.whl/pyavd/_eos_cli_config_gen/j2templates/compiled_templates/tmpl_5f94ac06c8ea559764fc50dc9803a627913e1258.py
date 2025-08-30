from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/platform-headroom-pool.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_platform = resolve('platform')
    l_0_headroom_pool_limit = resolve('headroom_pool_limit')
    try:
        t_1 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='platform') if l_0_platform is missing else l_0_platform), 'trident'), 'mmu'), 'headroom_pool'), 'limit')):
        pass
        l_0_headroom_pool_limit = 'platform trident mmu headroom-pool limit '
        context.vars['headroom_pool_limit'] = l_0_headroom_pool_limit
        context.exported_vars.add('headroom_pool_limit')
        if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='platform') if l_0_platform is missing else l_0_platform), 'trident'), 'mmu'), 'headroom_pool'), 'unit')):
            pass
            l_0_headroom_pool_limit = str_join(((undefined(name='headroom_pool_limit') if l_0_headroom_pool_limit is missing else l_0_headroom_pool_limit), environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='platform') if l_0_platform is missing else l_0_platform), 'trident'), 'mmu'), 'headroom_pool'), 'unit'), ' ', ))
            context.vars['headroom_pool_limit'] = l_0_headroom_pool_limit
            context.exported_vars.add('headroom_pool_limit')
        l_0_headroom_pool_limit = str_join(((undefined(name='headroom_pool_limit') if l_0_headroom_pool_limit is missing else l_0_headroom_pool_limit), environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='platform') if l_0_platform is missing else l_0_platform), 'trident'), 'mmu'), 'headroom_pool'), 'limit'), ))
        context.vars['headroom_pool_limit'] = l_0_headroom_pool_limit
        context.exported_vars.add('headroom_pool_limit')
        yield '!\n'
        yield str((undefined(name='headroom_pool_limit') if l_0_headroom_pool_limit is missing else l_0_headroom_pool_limit))
        yield '\n'

blocks = {}
debug_info = '7=19&8=21&9=24&10=26&12=29&14=33'