from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/monitor-twamp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_monitor_twamp = resolve('monitor_twamp')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_3 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_3(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light')):
        pass
        yield '\n### Monitor TWAMP\n\n#### TWAMP-light Summary\n'
        if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'reflector_defaults'), 'listen_port')):
            pass
            yield '\n- Reflector Default Listen Port is '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'reflector_defaults'), 'listen_port'))
            yield '\n'
        if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_defaults'), 'destination_port')):
            pass
            yield '\n- Sender Default Destination Port is '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_defaults'), 'destination_port'))
            yield '\n'
        if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_defaults'), 'source_port')):
            pass
            yield '\n- Sender Default Source Port is '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_defaults'), 'source_port'))
            yield '\n'
        if t_3(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_profiles')):
            pass
            yield '\n#### TWAMP-light Sender Profiles\n\n| Profile Name | Measurement Interval(seconds) | Measurement Samples | Significance Value(microseconds) | Significance Offset(microseconds) |\n| ------------ | ----------------------------- | ------------------- | -------------------------------- | --------------------------------- |\n'
            for l_1_profile in t_2(environment.getattr(environment.getattr((undefined(name='monitor_twamp') if l_0_monitor_twamp is missing else l_0_monitor_twamp), 'twamp_light'), 'sender_profiles'), 'name'):
                l_1_profile_interval = l_1_profile_samples = l_1_profile_sig_value = l_1_profile_sig_offset = missing
                _loop_vars = {}
                pass
                l_1_profile_interval = t_1(environment.getattr(l_1_profile, 'measurement_interval'), '-')
                _loop_vars['profile_interval'] = l_1_profile_interval
                l_1_profile_samples = t_1(environment.getattr(l_1_profile, 'measurement_samples'), '-')
                _loop_vars['profile_samples'] = l_1_profile_samples
                l_1_profile_sig_value = t_1(environment.getattr(environment.getattr(l_1_profile, 'significance'), 'value'), '-')
                _loop_vars['profile_sig_value'] = l_1_profile_sig_value
                l_1_profile_sig_offset = t_1(environment.getattr(environment.getattr(l_1_profile, 'significance'), 'offset'), '-')
                _loop_vars['profile_sig_offset'] = l_1_profile_sig_offset
                yield '| '
                yield str(environment.getattr(l_1_profile, 'name'))
                yield ' | '
                yield str((undefined(name='profile_interval') if l_1_profile_interval is missing else l_1_profile_interval))
                yield ' | '
                yield str((undefined(name='profile_samples') if l_1_profile_samples is missing else l_1_profile_samples))
                yield ' | '
                yield str((undefined(name='profile_sig_value') if l_1_profile_sig_value is missing else l_1_profile_sig_value))
                yield ' | '
                yield str((undefined(name='profile_sig_offset') if l_1_profile_sig_offset is missing else l_1_profile_sig_offset))
                yield ' |\n'
            l_1_profile = l_1_profile_interval = l_1_profile_samples = l_1_profile_sig_value = l_1_profile_sig_offset = missing
        yield '\n#### Monitor TWAMP configuration\n\n```eos\n'
        template = environment.get_template('eos/monitor-twamp.j2', 'documentation/monitor-twamp.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=30&12=33&14=36&16=38&18=41&20=43&22=46&24=48&30=51&31=55&32=57&33=59&34=61&35=64&42=76'