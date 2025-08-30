from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/agents.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_agents = resolve('agents')
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
    if t_2((undefined(name='agents') if l_0_agents is missing else l_0_agents)):
        pass
        yield '\n### Agents\n'
        for l_1_agent in t_1((undefined(name='agents') if l_0_agents is missing else l_0_agents), 'name'):
            _loop_vars = {}
            pass
            yield '\n#### Agent '
            yield str(environment.getattr(l_1_agent, 'name'))
            yield '\n'
            if t_2(environment.getattr(l_1_agent, 'environment_variables')):
                pass
                yield '\n##### Environment Variables\n\n| Name | Value |\n| ---- | ----- |\n'
                for l_2_envvar in environment.getattr(l_1_agent, 'environment_variables'):
                    _loop_vars = {}
                    pass
                    yield '| '
                    yield str(environment.getattr(l_2_envvar, 'name'))
                    yield ' | '
                    yield str(environment.getattr(l_2_envvar, 'value'))
                    yield ' |\n'
                l_2_envvar = missing
            if ((t_2(environment.getattr(l_1_agent, 'shutdown')) or t_2(environment.getattr(l_1_agent, 'shutdown_supervisor_active'))) or t_2(environment.getattr(l_1_agent, 'shutdown_supervisor_standby'))):
                pass
                yield '\n##### Shutdown\n\n| Setting | Value |\n| ------- | ----- |\n'
                if t_2(environment.getattr(l_1_agent, 'shutdown')):
                    pass
                    yield '| Shutdown | '
                    yield str(environment.getattr(l_1_agent, 'shutdown'))
                    yield ' |\n'
                if t_2(environment.getattr(l_1_agent, 'shutdown_supervisor_active')):
                    pass
                    yield '| Shutdown on Active Supervisor | '
                    yield str(environment.getattr(l_1_agent, 'shutdown_supervisor_active'))
                    yield ' |\n'
                if t_2(environment.getattr(l_1_agent, 'shutdown_supervisor_standby')):
                    pass
                    yield '| Shutdown on Standby Supervisor | '
                    yield str(environment.getattr(l_1_agent, 'shutdown_supervisor_standby'))
                    yield ' |\n'
        l_1_agent = missing
        yield '\n#### Agents Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/agents.j2', 'documentation/agents.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=24&10=27&12=31&13=33&19=36&20=40&23=45&29=48&30=51&32=53&33=56&35=58&36=61&44=65'