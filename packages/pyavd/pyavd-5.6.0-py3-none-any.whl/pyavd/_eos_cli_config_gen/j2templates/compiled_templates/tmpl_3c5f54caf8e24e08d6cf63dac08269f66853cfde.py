from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/ip-hardware.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_hardware = resolve('ip_hardware')
    try:
        t_1 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if (t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_hardware') if l_0_ip_hardware is missing else l_0_ip_hardware), 'fib'), 'optimize'), 'prefixes'), 'profile')) or t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_hardware') if l_0_ip_hardware is missing else l_0_ip_hardware), 'fib'), 'load_balance_distribution'), 'dynamic'))):
        pass
        yield '\n## IP Hardware FIB\n\n### IP Hardware FIB Summary\n\n'
        if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_hardware') if l_0_ip_hardware is missing else l_0_ip_hardware), 'fib'), 'optimize'), 'prefixes'), 'profile')):
            pass
            yield 'IP hardware FIB optimize prefixes profile: '
            yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_hardware') if l_0_ip_hardware is missing else l_0_ip_hardware), 'fib'), 'optimize'), 'prefixes'), 'profile'))
            yield '\n'
        if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_hardware') if l_0_ip_hardware is missing else l_0_ip_hardware), 'fib'), 'load_balance_distribution'), 'dynamic'), 'enabled'), True):
            pass
            yield 'IP hardware FIB dynamic load balancing: Enabled\n'
        if t_1(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_hardware') if l_0_ip_hardware is missing else l_0_ip_hardware), 'fib'), 'load_balance_distribution'), 'dynamic'), 'flow_set_size')):
            pass
            yield 'IP hardware FIB dynamic load balancing flow-set-size: '
            yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr((undefined(name='ip_hardware') if l_0_ip_hardware is missing else l_0_ip_hardware), 'fib'), 'load_balance_distribution'), 'dynamic'), 'flow_set_size'))
            yield '\n'
        yield '\n### IP Hardware FIB Configuration\n\n```eos\n'
        template = environment.get_template('eos/ip-hardware.j2', 'documentation/ip-hardware.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=18&13=21&14=24&16=26&19=29&20=32&26=35'