from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/class-maps.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_class_maps = resolve('class_maps')
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
    if t_2(environment.getattr((undefined(name='class_maps') if l_0_class_maps is missing else l_0_class_maps), 'qos')):
        pass
        yield '\n### QOS Class Maps\n\n#### QOS Class Maps Summary\n\n| Name | Field | Value |\n| ---- | ----- | ----- |\n'
        for l_1_class_map in t_1(environment.getattr((undefined(name='class_maps') if l_0_class_maps is missing else l_0_class_maps), 'qos'), 'name'):
            _loop_vars = {}
            pass
            if t_2(environment.getattr(l_1_class_map, 'cos')):
                pass
                yield '| '
                yield str(environment.getattr(l_1_class_map, 'name'))
                yield ' | cos | '
                yield str(environment.getattr(l_1_class_map, 'cos'))
                yield ' |\n'
            elif t_2(environment.getattr(l_1_class_map, 'vlan')):
                pass
                yield '| '
                yield str(environment.getattr(l_1_class_map, 'name'))
                yield ' | vlan | '
                yield str(environment.getattr(l_1_class_map, 'vlan'))
                yield ' |\n'
            elif t_2(environment.getattr(environment.getattr(l_1_class_map, 'ip'), 'access_group')):
                pass
                yield '| '
                yield str(environment.getattr(l_1_class_map, 'name'))
                yield ' | acl | '
                yield str(environment.getattr(environment.getattr(l_1_class_map, 'ip'), 'access_group'))
                yield ' |\n'
            else:
                pass
                if (t_2(environment.getattr(l_1_class_map, 'dscp')) and t_2(environment.getattr(l_1_class_map, 'ecn'))):
                    pass
                    yield '| '
                    yield str(environment.getattr(l_1_class_map, 'name'))
                    yield ' | dscp<br>ecn | '
                    yield str(environment.getattr(l_1_class_map, 'dscp'))
                    yield '<br>'
                    yield str(environment.getattr(l_1_class_map, 'ecn'))
                    yield ' |\n'
                elif t_2(environment.getattr(l_1_class_map, 'dscp')):
                    pass
                    yield '| '
                    yield str(environment.getattr(l_1_class_map, 'name'))
                    yield ' | dscp | '
                    yield str(environment.getattr(l_1_class_map, 'dscp'))
                    yield ' |\n'
                elif t_2(environment.getattr(l_1_class_map, 'ecn')):
                    pass
                    yield '| '
                    yield str(environment.getattr(l_1_class_map, 'name'))
                    yield ' | ecn | '
                    yield str(environment.getattr(l_1_class_map, 'ecn'))
                    yield ' |\n'
                else:
                    pass
                    yield '| '
                    yield str(environment.getattr(l_1_class_map, 'name'))
                    yield ' | - | - |\n'
        l_1_class_map = missing
        yield '\n#### Class-maps Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/class-maps.j2', 'documentation/class-maps.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        template = environment.get_template('eos/class-maps-pbr.j2', 'documentation/class-maps.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=24&15=27&16=30&17=33&18=37&19=40&20=44&21=47&23=53&24=56&25=62&26=65&27=69&28=72&30=79&38=83&39=89'