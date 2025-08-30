from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/monitor-twamp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_monitor_twamp = resolve('monitor_twamp')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_3((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp)):
        pass
        yield '!\nmonitor twamp\n'
        if t_3(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light')):
            pass
            yield '   twamp-light\n'
            if t_3(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'reflector_defaults')):
                pass
                yield '      reflector defaults\n'
                if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'reflector_defaults'), 'listen_port')):
                    pass
                    yield '         listen port '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'reflector_defaults'), 'listen_port'))
                    yield '\n'
                yield '      !\n'
            if (t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_defaults'), 'destination_port')) or t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_defaults'), 'source_port'))):
                pass
                yield '      sender defaults\n'
                if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_defaults'), 'destination_port')):
                    pass
                    yield '         destination port '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_defaults'), 'destination_port'))
                    yield '\n'
                if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_defaults'), 'source_port')):
                    pass
                    yield '         source port '
                    yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_defaults'), 'source_port'))
                    yield '\n'
                yield '      !\n'
            l_1_loop = missing
            for l_1_sender_profile, l_1_loop in LoopContext(t_1(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_profiles'), 'name'), undefined):
                _loop_vars = {}
                pass
                yield '      sender profile '
                yield str(environment.getattr(l_1_sender_profile, 'name'))
                yield '\n'
                if t_3(environment.getattr(l_1_sender_profile, 'measurement_interval')):
                    pass
                    yield '         measurement interval '
                    yield str(environment.getattr(l_1_sender_profile, 'measurement_interval'))
                    yield ' seconds\n'
                if t_3(environment.getattr(l_1_sender_profile, 'measurement_samples')):
                    pass
                    yield '         measurement samples '
                    yield str(environment.getattr(l_1_sender_profile, 'measurement_samples'))
                    yield '\n'
                if t_3(environment.getattr(l_1_sender_profile, 'significance')):
                    pass
                    yield '         significance '
                    yield str(environment.getattr(environment.getattr(l_1_sender_profile, 'significance'), 'value'))
                    yield ' microseconds offset '
                    yield str(environment.getattr(environment.getattr(l_1_sender_profile, 'significance'), 'offset'))
                    yield ' microseconds\n'
                if (environment.getattr(l_1_loop, 'index') < t_2(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_profiles'))):
                    pass
                    yield '      !\n'
            l_1_loop = l_1_sender_profile = missing

blocks = {}
debug_info = '6=30&9=33&11=36&13=39&14=42&18=45&20=48&21=51&23=53&24=56&28=60&29=64&30=66&31=69&33=71&34=74&36=76&37=79&39=83'