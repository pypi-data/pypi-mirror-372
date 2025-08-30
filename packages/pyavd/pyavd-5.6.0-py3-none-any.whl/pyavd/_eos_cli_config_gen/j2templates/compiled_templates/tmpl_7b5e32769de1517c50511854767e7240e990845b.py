from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/platform-trident.j2'

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
    if t_2((undefined(name='platform') if l_0_platform is missing else l_0_platform)):
        pass
        for l_1_profile in t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='platform') if l_0_platform is missing else l_0_platform), 'trident'), 'mmu'), 'queue_profiles'), 'name'):
            l_1_ingress_reserved = resolve('ingress_reserved')
            l_1_ingress_headroom = resolve('ingress_headroom')
            _loop_vars = {}
            pass
            yield '!\nplatform trident mmu queue profile '
            yield str(environment.getattr(l_1_profile, 'name'))
            yield '\n'
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'reserved'), 'memory')):
                pass
                l_1_ingress_reserved = 'ingress reserved '
                _loop_vars['ingress_reserved'] = l_1_ingress_reserved
                if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'reserved'), 'unit')):
                    pass
                    l_1_ingress_reserved = str_join(((undefined(name='ingress_reserved') if l_1_ingress_reserved is missing else l_1_ingress_reserved), environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'reserved'), 'unit'), ' ', ))
                    _loop_vars['ingress_reserved'] = l_1_ingress_reserved
                l_1_ingress_reserved = str_join(((undefined(name='ingress_reserved') if l_1_ingress_reserved is missing else l_1_ingress_reserved), environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'reserved'), 'memory'), ))
                _loop_vars['ingress_reserved'] = l_1_ingress_reserved
                yield '    '
                yield str((undefined(name='ingress_reserved') if l_1_ingress_reserved is missing else l_1_ingress_reserved))
                yield '\n'
            if t_2(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'threshold')):
                pass
                yield '    ingress threshold '
                yield str(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'threshold'))
                yield '\n'
            if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'headroom'), 'memory')):
                pass
                l_1_ingress_headroom = 'ingress headroom '
                _loop_vars['ingress_headroom'] = l_1_ingress_headroom
                if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'headroom'), 'unit')):
                    pass
                    l_1_ingress_headroom = str_join(((undefined(name='ingress_headroom') if l_1_ingress_headroom is missing else l_1_ingress_headroom), environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'headroom'), 'unit'), ' ', ))
                    _loop_vars['ingress_headroom'] = l_1_ingress_headroom
                l_1_ingress_headroom = str_join(((undefined(name='ingress_headroom') if l_1_ingress_headroom is missing else l_1_ingress_headroom), environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'headroom'), 'memory'), ))
                _loop_vars['ingress_headroom'] = l_1_ingress_headroom
                yield '    '
                yield str((undefined(name='ingress_headroom') if l_1_ingress_headroom is missing else l_1_ingress_headroom))
                yield '\n'
            if t_2(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'resume')):
                pass
                yield '    ingress resume '
                yield str(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'resume'))
                yield '\n'
            for l_2_priority_group in t_1(environment.getattr(environment.getattr(l_1_profile, 'ingress'), 'priority_groups'), 'id'):
                l_2_priority_group_reserved = resolve('priority_group_reserved')
                _loop_vars = {}
                pass
                if t_2(environment.getattr(environment.getattr(l_2_priority_group, 'reserved'), 'memory')):
                    pass
                    l_2_priority_group_reserved = str_join(('ingress priority-group ', environment.getattr(l_2_priority_group, 'id'), ' reserved ', ))
                    _loop_vars['priority_group_reserved'] = l_2_priority_group_reserved
                    if t_2(environment.getattr(environment.getattr(l_2_priority_group, 'reserved'), 'unit')):
                        pass
                        l_2_priority_group_reserved = str_join(((undefined(name='priority_group_reserved') if l_2_priority_group_reserved is missing else l_2_priority_group_reserved), environment.getattr(environment.getattr(l_2_priority_group, 'reserved'), 'unit'), ' ', ))
                        _loop_vars['priority_group_reserved'] = l_2_priority_group_reserved
                    l_2_priority_group_reserved = str_join(((undefined(name='priority_group_reserved') if l_2_priority_group_reserved is missing else l_2_priority_group_reserved), environment.getattr(environment.getattr(l_2_priority_group, 'reserved'), 'memory'), ))
                    _loop_vars['priority_group_reserved'] = l_2_priority_group_reserved
                    yield '    '
                    yield str((undefined(name='priority_group_reserved') if l_2_priority_group_reserved is missing else l_2_priority_group_reserved))
                    yield '\n'
                if t_2(environment.getattr(l_2_priority_group, 'threshold')):
                    pass
                    yield '    ingress priority-group '
                    yield str(environment.getattr(l_2_priority_group, 'id'))
                    yield ' threshold '
                    yield str(environment.getattr(l_2_priority_group, 'threshold'))
                    yield '\n'
            l_2_priority_group = l_2_priority_group_reserved = missing
            for l_2_queue in t_1(environment.getattr(l_1_profile, 'unicast_queues'), 'id'):
                l_2_reserved_cli = resolve('reserved_cli')
                _loop_vars = {}
                pass
                if t_2(environment.getattr(l_2_queue, 'reserved')):
                    pass
                    l_2_reserved_cli = str_join(('egress unicast queue ', environment.getattr(l_2_queue, 'id'), ' reserved', ))
                    _loop_vars['reserved_cli'] = l_2_reserved_cli
                    if t_2(environment.getattr(l_2_queue, 'unit')):
                        pass
                        l_2_reserved_cli = str_join(((undefined(name='reserved_cli') if l_2_reserved_cli is missing else l_2_reserved_cli), ' ', environment.getattr(l_2_queue, 'unit'), ))
                        _loop_vars['reserved_cli'] = l_2_reserved_cli
                    l_2_reserved_cli = str_join(((undefined(name='reserved_cli') if l_2_reserved_cli is missing else l_2_reserved_cli), ' ', environment.getattr(l_2_queue, 'reserved'), ))
                    _loop_vars['reserved_cli'] = l_2_reserved_cli
                    yield '    '
                    yield str((undefined(name='reserved_cli') if l_2_reserved_cli is missing else l_2_reserved_cli))
                    yield '\n'
                if t_2(environment.getattr(l_2_queue, 'threshold')):
                    pass
                    yield '    egress unicast queue '
                    yield str(environment.getattr(l_2_queue, 'id'))
                    yield ' threshold '
                    yield str(environment.getattr(l_2_queue, 'threshold'))
                    yield '\n'
                if t_2(environment.getattr(l_2_queue, 'drop')):
                    pass
                    yield '    egress unicast queue '
                    yield str(environment.getattr(l_2_queue, 'id'))
                    yield ' drop-precedence '
                    yield str(environment.getattr(environment.getattr(l_2_queue, 'drop'), 'precedence'))
                    yield ' drop-threshold '
                    yield str(environment.getattr(environment.getattr(l_2_queue, 'drop'), 'threshold'))
                    yield '\n'
            l_2_queue = l_2_reserved_cli = missing
            for l_2_queue in t_1(environment.getattr(l_1_profile, 'multicast_queues'), 'id'):
                l_2_reserved_cli = resolve('reserved_cli')
                _loop_vars = {}
                pass
                if t_2(environment.getattr(l_2_queue, 'reserved')):
                    pass
                    l_2_reserved_cli = str_join(('egress multicast queue ', environment.getattr(l_2_queue, 'id'), ' reserved', ))
                    _loop_vars['reserved_cli'] = l_2_reserved_cli
                    if t_2(environment.getattr(l_2_queue, 'unit')):
                        pass
                        l_2_reserved_cli = str_join(((undefined(name='reserved_cli') if l_2_reserved_cli is missing else l_2_reserved_cli), ' ', environment.getattr(l_2_queue, 'unit'), ))
                        _loop_vars['reserved_cli'] = l_2_reserved_cli
                    l_2_reserved_cli = str_join(((undefined(name='reserved_cli') if l_2_reserved_cli is missing else l_2_reserved_cli), ' ', environment.getattr(l_2_queue, 'reserved'), ))
                    _loop_vars['reserved_cli'] = l_2_reserved_cli
                    yield '    '
                    yield str((undefined(name='reserved_cli') if l_2_reserved_cli is missing else l_2_reserved_cli))
                    yield '\n'
                if t_2(environment.getattr(l_2_queue, 'threshold')):
                    pass
                    yield '    egress multicast queue '
                    yield str(environment.getattr(l_2_queue, 'id'))
                    yield ' threshold '
                    yield str(environment.getattr(l_2_queue, 'threshold'))
                    yield '\n'
                if t_2(environment.getattr(l_2_queue, 'drop')):
                    pass
                    yield '    egress multicast queue '
                    yield str(environment.getattr(l_2_queue, 'id'))
                    yield ' drop-precedence '
                    yield str(environment.getattr(environment.getattr(l_2_queue, 'drop'), 'precedence'))
                    yield ' drop-threshold '
                    yield str(environment.getattr(environment.getattr(l_2_queue, 'drop'), 'threshold'))
                    yield '\n'
            l_2_queue = l_2_reserved_cli = missing
        l_1_profile = l_1_ingress_reserved = l_1_ingress_headroom = missing

blocks = {}
debug_info = '7=24&8=26&10=32&11=34&12=36&13=38&14=40&16=42&17=45&19=47&20=50&22=52&23=54&24=56&25=58&27=60&28=63&30=65&31=68&33=70&34=74&35=76&36=78&37=80&39=82&40=85&42=87&43=90&46=95&47=99&48=101&49=103&50=105&52=107&53=110&55=112&56=115&58=119&59=122&62=129&63=133&64=135&65=137&66=139&68=141&69=144&71=146&72=149&74=153&75=156'