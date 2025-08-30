from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/banners.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_banners = resolve('banners')
    try:
        t_1 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if (t_1(environment.getattr((undefined(name='banners') if l_0_banners is missing else l_0_banners), 'login')) or t_1(environment.getattr((undefined(name='banners') if l_0_banners is missing else l_0_banners), 'motd'))):
        pass
        yield '\n### Banner\n'
        if t_1(environment.getattr((undefined(name='banners') if l_0_banners is missing else l_0_banners), 'login')):
            pass
            yield '\n#### Login Banner\n\n```text\n'
            yield str(context.call(environment.getattr(environment.getattr((undefined(name='banners') if l_0_banners is missing else l_0_banners), 'login'), 'rstrip')))
            yield '\n```\n'
        if t_1(environment.getattr((undefined(name='banners') if l_0_banners is missing else l_0_banners), 'motd')):
            pass
            yield '\n#### MOTD Banner\n\n```text\n'
            yield str(context.call(environment.getattr(environment.getattr((undefined(name='banners') if l_0_banners is missing else l_0_banners), 'motd'), 'rstrip')))
            yield '\n```\n'

blocks = {}
debug_info = '7=18&10=21&15=24&18=26&23=29'