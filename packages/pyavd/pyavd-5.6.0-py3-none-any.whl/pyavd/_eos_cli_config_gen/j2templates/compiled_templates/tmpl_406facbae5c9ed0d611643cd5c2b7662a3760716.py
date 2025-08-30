from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/flow-tracking.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_flow_tracking = resolve('flow_tracking')
    l_0_encapsulation = resolve('encapsulation')
    l_0_hardware_offload_protocols = resolve('hardware_offload_protocols')
    l_0_namespace = resolve('namespace')
    l_0_tracker_ns = resolve('tracker_ns')
    l_0_low_tracking = resolve('low_tracking')
    try:
        t_1 = environment.filters['arista.avd.natural_sort']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.natural_sort' found.")
    try:
        t_2 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_3 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_4 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_4(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware')):
        pass
        yield '!\nflow tracking hardware\n'
        l_1_loop = missing
        for l_1_tracker, l_1_loop in LoopContext(t_1(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'trackers')), undefined):
            _loop_vars = {}
            pass
            if (not environment.getattr(l_1_loop, 'first')):
                pass
                yield '   !\n'
            yield '   tracker '
            yield str(environment.getattr(l_1_tracker, 'name'))
            yield '\n'
            if t_4(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout')):
                pass
                yield '      record export on inactive timeout '
                yield str(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout'))
                yield '\n'
            if t_4(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval')):
                pass
                yield '      record export on interval '
                yield str(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval'))
                yield '\n'
            if t_4(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'mpls'), True):
                pass
                yield '      record export mpls\n'
            l_2_loop = missing
            for l_2_exporter, l_2_loop in LoopContext(t_1(environment.getattr(l_1_tracker, 'exporters'), 'name'), undefined):
                l_2_collector_cli = resolve('collector_cli')
                _loop_vars = {}
                pass
                if (not environment.getattr(l_2_loop, 'first')):
                    pass
                    yield '      !\n'
                yield '      exporter '
                yield str(environment.getattr(l_2_exporter, 'name'))
                yield '\n'
                if t_4(environment.getattr(l_2_exporter, 'collectors')):
                    pass
                    for l_3_collector in t_1(environment.getattr(l_2_exporter, 'collectors')):
                        l_3_collector_cli = l_2_collector_cli
                        _loop_vars = {}
                        pass
                        l_3_collector_cli = str_join(('collector ', environment.getattr(l_3_collector, 'host'), ))
                        _loop_vars['collector_cli'] = l_3_collector_cli
                        if t_4(environment.getattr(l_3_collector, 'port')):
                            pass
                            l_3_collector_cli = str_join(((undefined(name='collector_cli') if l_3_collector_cli is missing else l_3_collector_cli), ' port ', environment.getattr(l_3_collector, 'port'), ))
                            _loop_vars['collector_cli'] = l_3_collector_cli
                        yield '         '
                        yield str((undefined(name='collector_cli') if l_3_collector_cli is missing else l_3_collector_cli))
                        yield '\n'
                    l_3_collector = l_3_collector_cli = missing
                elif t_4(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host')):
                    pass
                    l_2_collector_cli = str_join(('collector ', environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host'), ))
                    _loop_vars['collector_cli'] = l_2_collector_cli
                    if t_4(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'port')):
                        pass
                        l_2_collector_cli = str_join(((undefined(name='collector_cli') if l_2_collector_cli is missing else l_2_collector_cli), ' port ', environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'port'), ))
                        _loop_vars['collector_cli'] = l_2_collector_cli
                    yield '         '
                    yield str((undefined(name='collector_cli') if l_2_collector_cli is missing else l_2_collector_cli))
                    yield '\n'
                if t_4(environment.getattr(environment.getattr(l_2_exporter, 'format'), 'ipfix_version')):
                    pass
                    yield '         format ipfix version '
                    yield str(environment.getattr(environment.getattr(l_2_exporter, 'format'), 'ipfix_version'))
                    yield '\n'
                if t_4(environment.getattr(l_2_exporter, 'local_interface')):
                    pass
                    yield '         local interface '
                    yield str(environment.getattr(l_2_exporter, 'local_interface'))
                    yield '\n'
                if t_4(environment.getattr(l_2_exporter, 'template_interval')):
                    pass
                    yield '         template interval '
                    yield str(environment.getattr(l_2_exporter, 'template_interval'))
                    yield '\n'
            l_2_loop = l_2_exporter = l_2_collector_cli = missing
            if t_4(environment.getattr(l_1_tracker, 'table_size')):
                pass
                yield '      flow table size '
                yield str(environment.getattr(l_1_tracker, 'table_size'))
                yield ' entries\n'
        l_1_loop = l_1_tracker = missing
        if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'record'), 'format_ipfix_standard_timestamps_counters'), True):
            pass
            yield '   record format ipfix standard timestamps counters\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'shutdown'), False):
            pass
            yield '   no shutdown\n'
    if t_4(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled')):
        pass
        yield '!\nflow tracking sampled\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'encapsulation')):
            pass
            l_0_encapsulation = 'encapsulation'
            context.vars['encapsulation'] = l_0_encapsulation
            context.exported_vars.add('encapsulation')
            if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'encapsulation'), 'ipv4_ipv6'), True):
                pass
                l_0_encapsulation = str_join(((undefined(name='encapsulation') if l_0_encapsulation is missing else l_0_encapsulation), ' ipv4 ipv6', ))
                context.vars['encapsulation'] = l_0_encapsulation
                context.exported_vars.add('encapsulation')
                if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'encapsulation'), 'mpls'), True):
                    pass
                    l_0_encapsulation = str_join(((undefined(name='encapsulation') if l_0_encapsulation is missing else l_0_encapsulation), ' mpls', ))
                    context.vars['encapsulation'] = l_0_encapsulation
                    context.exported_vars.add('encapsulation')
            yield '   '
            yield str((undefined(name='encapsulation') if l_0_encapsulation is missing else l_0_encapsulation))
            yield '\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'sample')):
            pass
            yield '   sample '
            yield str(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'sample'))
            yield '\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload')):
            pass
            l_0_hardware_offload_protocols = []
            context.vars['hardware_offload_protocols'] = l_0_hardware_offload_protocols
            context.exported_vars.add('hardware_offload_protocols')
            if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'ipv4'), True):
                pass
                context.call(environment.getattr((undefined(name='hardware_offload_protocols') if l_0_hardware_offload_protocols is missing else l_0_hardware_offload_protocols), 'append'), 'ipv4')
            if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'ipv6'), True):
                pass
                context.call(environment.getattr((undefined(name='hardware_offload_protocols') if l_0_hardware_offload_protocols is missing else l_0_hardware_offload_protocols), 'append'), 'ipv6')
            if (t_3((undefined(name='hardware_offload_protocols') if l_0_hardware_offload_protocols is missing else l_0_hardware_offload_protocols)) > 0):
                pass
                yield '   hardware offload '
                yield str(t_2(context.eval_ctx, (undefined(name='hardware_offload_protocols') if l_0_hardware_offload_protocols is missing else l_0_hardware_offload_protocols), ' '))
                yield '\n'
            if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'threshold_minimum')):
                pass
                yield '   hardware offload threshold minimum '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'threshold_minimum'))
                yield ' samples\n'
        l_1_loop = missing
        for l_1_tracker, l_1_loop in LoopContext(t_1(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'trackers')), undefined):
            _loop_vars = {}
            pass
            if (not environment.getattr(l_1_loop, 'first')):
                pass
                yield '   !\n'
            yield '   tracker '
            yield str(environment.getattr(l_1_tracker, 'name'))
            yield '\n'
            if t_4(environment.getattr(l_1_tracker, 'table_size')):
                pass
                yield '      flow table size '
                yield str(environment.getattr(l_1_tracker, 'table_size'))
                yield ' entries\n'
            if t_4(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout')):
                pass
                yield '      record export on inactive timeout '
                yield str(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout'))
                yield '\n'
            if t_4(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval')):
                pass
                yield '      record export on interval '
                yield str(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval'))
                yield '\n'
            if t_4(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'mpls'), True):
                pass
                yield '      record export mpls\n'
            l_2_loop = missing
            for l_2_exporter, l_2_loop in LoopContext(t_1(environment.getattr(l_1_tracker, 'exporters'), 'name'), undefined):
                l_2_collector_cli = resolve('collector_cli')
                _loop_vars = {}
                pass
                if (not environment.getattr(l_2_loop, 'first')):
                    pass
                    yield '      !\n'
                yield '      exporter '
                yield str(environment.getattr(l_2_exporter, 'name'))
                yield '\n'
                if t_4(environment.getattr(l_2_exporter, 'collectors')):
                    pass
                    for l_3_collector in t_1(environment.getattr(l_2_exporter, 'collectors')):
                        l_3_collector_cli = l_2_collector_cli
                        _loop_vars = {}
                        pass
                        l_3_collector_cli = str_join(('collector ', environment.getattr(l_3_collector, 'host'), ))
                        _loop_vars['collector_cli'] = l_3_collector_cli
                        if t_4(environment.getattr(l_3_collector, 'port')):
                            pass
                            l_3_collector_cli = str_join(((undefined(name='collector_cli') if l_3_collector_cli is missing else l_3_collector_cli), ' port ', environment.getattr(l_3_collector, 'port'), ))
                            _loop_vars['collector_cli'] = l_3_collector_cli
                        yield '         '
                        yield str((undefined(name='collector_cli') if l_3_collector_cli is missing else l_3_collector_cli))
                        yield '\n'
                    l_3_collector = l_3_collector_cli = missing
                elif t_4(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host')):
                    pass
                    l_2_collector_cli = str_join(('collector ', environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host'), ))
                    _loop_vars['collector_cli'] = l_2_collector_cli
                    if t_4(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'port')):
                        pass
                        l_2_collector_cli = str_join(((undefined(name='collector_cli') if l_2_collector_cli is missing else l_2_collector_cli), ' port ', environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'port'), ))
                        _loop_vars['collector_cli'] = l_2_collector_cli
                    yield '         '
                    yield str((undefined(name='collector_cli') if l_2_collector_cli is missing else l_2_collector_cli))
                    yield '\n'
                if t_4(environment.getattr(environment.getattr(l_2_exporter, 'format'), 'ipfix_version')):
                    pass
                    yield '         format ipfix version '
                    yield str(environment.getattr(environment.getattr(l_2_exporter, 'format'), 'ipfix_version'))
                    yield '\n'
                if t_4(environment.getattr(l_2_exporter, 'local_interface')):
                    pass
                    yield '         local interface '
                    yield str(environment.getattr(l_2_exporter, 'local_interface'))
                    yield '\n'
                if t_4(environment.getattr(l_2_exporter, 'template_interval')):
                    pass
                    yield '         template interval '
                    yield str(environment.getattr(l_2_exporter, 'template_interval'))
                    yield '\n'
            l_2_loop = l_2_exporter = l_2_collector_cli = missing
        l_1_loop = l_1_tracker = missing
        if t_4(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'shutdown'), False):
            pass
            yield '   no shutdown\n'
    if t_4(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop')):
        pass
        yield '!\nflow tracking mirror-on-drop\n'
        l_0_tracker_ns = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), tracker_exclamation=False)
        context.vars['tracker_ns'] = l_0_tracker_ns
        context.exported_vars.add('tracker_ns')
        if (t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'encapsulation'), 'ipv4_ipv6'), True) or t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='low_tracking') if l_0_low_tracking is missing else l_0_low_tracking), 'mirror_on_drop'), 'encapsulation'), 'mpls'), True)):
            pass
            if not isinstance(l_0_tracker_ns, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_tracker_ns['tracker_exclamation'] = True
            l_0_encapsulation = 'encapsulation'
            context.vars['encapsulation'] = l_0_encapsulation
            context.exported_vars.add('encapsulation')
            if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'encapsulation'), 'ipv4_ipv6'), True):
                pass
                l_0_encapsulation = str_join(((undefined(name='encapsulation') if l_0_encapsulation is missing else l_0_encapsulation), ' ipv4 ipv6', ))
                context.vars['encapsulation'] = l_0_encapsulation
                context.exported_vars.add('encapsulation')
            if t_4(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'encapsulation'), 'mpls'), True):
                pass
                l_0_encapsulation = str_join(((undefined(name='encapsulation') if l_0_encapsulation is missing else l_0_encapsulation), ' mpls', ))
                context.vars['encapsulation'] = l_0_encapsulation
                context.exported_vars.add('encapsulation')
            yield '   '
            yield str((undefined(name='encapsulation') if l_0_encapsulation is missing else l_0_encapsulation))
            yield '\n'
        if t_4(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'sample_limit')):
            pass
            if not isinstance(l_0_tracker_ns, Namespace):
                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
            l_0_tracker_ns['tracker_exclamation'] = True
            yield '   sample limit '
            yield str(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'sample_limit'))
            yield ' pps\n'
        l_1_loop = missing
        for l_1_tracker, l_1_loop in LoopContext(t_1(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'trackers')), undefined):
            l_1_exporter_ns = missing
            _loop_vars = {}
            pass
            if ((not environment.getattr(l_1_loop, 'first')) or (environment.getattr((undefined(name='tracker_ns') if l_0_tracker_ns is missing else l_0_tracker_ns), 'tracker_exclamation') == True)):
                pass
                yield '   !\n'
            l_1_exporter_ns = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), exporter_exclamation=False, _loop_vars=_loop_vars)
            _loop_vars['exporter_ns'] = l_1_exporter_ns
            yield '   tracker '
            yield str(environment.getattr(l_1_tracker, 'name'))
            yield '\n'
            if t_4(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout')):
                pass
                if not isinstance(l_1_exporter_ns, Namespace):
                    raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                l_1_exporter_ns['exporter_exclamation'] = True
                yield '      record export on inactive timeout '
                yield str(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout'))
                yield '\n'
            if t_4(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval')):
                pass
                if not isinstance(l_1_exporter_ns, Namespace):
                    raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                l_1_exporter_ns['exporter_exclamation'] = True
                yield '      record export on interval '
                yield str(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval'))
                yield '\n'
            l_2_loop = missing
            for l_2_exporter, l_2_loop in LoopContext(t_1(environment.getattr(l_1_tracker, 'exporters'), 'name'), undefined):
                _loop_vars = {}
                pass
                if ((not environment.getattr(l_2_loop, 'first')) or (environment.getattr((undefined(name='exporter_ns') if l_1_exporter_ns is missing else l_1_exporter_ns), 'exporter_exclamation') == True)):
                    pass
                    yield '      !\n'
                yield '      exporter '
                yield str(environment.getattr(l_2_exporter, 'name'))
                yield '\n'
                if t_4(environment.getattr(l_2_exporter, 'format')):
                    pass
                    yield '         format '
                    yield str(environment.getattr(l_2_exporter, 'format'))
                    yield '\n'
                for l_3_collector in t_1(environment.getattr(l_2_exporter, 'collectors')):
                    l_3_collector_cli = missing
                    _loop_vars = {}
                    pass
                    l_3_collector_cli = str_join(('collector ', environment.getattr(l_3_collector, 'host'), ))
                    _loop_vars['collector_cli'] = l_3_collector_cli
                    if t_4(environment.getattr(l_3_collector, 'port')):
                        pass
                        l_3_collector_cli = str_join(((undefined(name='collector_cli') if l_3_collector_cli is missing else l_3_collector_cli), ' port ', environment.getattr(l_3_collector, 'port'), ))
                        _loop_vars['collector_cli'] = l_3_collector_cli
                    yield '         '
                    yield str((undefined(name='collector_cli') if l_3_collector_cli is missing else l_3_collector_cli))
                    yield '\n'
                l_3_collector = l_3_collector_cli = missing
                if t_4(environment.getattr(l_2_exporter, 'dscp')):
                    pass
                    yield '         dscp '
                    yield str(environment.getattr(l_2_exporter, 'dscp'))
                    yield '\n'
                if t_4(environment.getattr(l_2_exporter, 'local_interface')):
                    pass
                    yield '         local interface '
                    yield str(environment.getattr(l_2_exporter, 'local_interface'))
                    yield '\n'
                if t_4(environment.getattr(l_2_exporter, 'template_interval')):
                    pass
                    yield '         template interval '
                    yield str(environment.getattr(l_2_exporter, 'template_interval'))
                    yield '\n'
            l_2_loop = l_2_exporter = missing
        l_1_loop = l_1_tracker = l_1_exporter_ns = missing
        if t_4(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'shutdown'), False):
            pass
            yield '   no shutdown\n'

blocks = {}
debug_info = '8=41&11=45&12=48&15=52&16=54&17=57&19=59&20=62&22=64&25=68&26=72&29=76&31=78&32=80&33=84&34=86&35=88&37=91&39=94&40=96&41=98&42=100&44=103&46=105&47=108&49=110&50=113&52=115&53=118&56=121&57=124&60=127&63=130&68=133&71=136&72=138&73=141&74=143&75=146&76=148&79=152&81=154&82=157&84=159&85=161&86=164&87=166&89=167&90=169&92=170&93=173&95=175&96=178&99=181&100=184&103=188&104=190&105=193&107=195&108=198&110=200&111=203&113=205&116=209&117=213&120=217&122=219&123=221&124=225&125=227&126=229&128=232&130=235&131=237&132=239&133=241&135=244&137=246&138=249&140=251&141=254&143=256&144=259&148=263&153=266&156=269&157=272&158=276&159=277&160=280&161=282&163=285&164=287&166=291&168=293&169=297&170=299&172=302&173=306&176=309&177=312&178=314&179=318&180=320&182=322&183=326&184=328&186=331&187=334&190=338&191=340&192=343&194=345&195=349&196=351&197=353&199=356&201=359&202=362&204=364&205=367&207=369&208=372&212=376'