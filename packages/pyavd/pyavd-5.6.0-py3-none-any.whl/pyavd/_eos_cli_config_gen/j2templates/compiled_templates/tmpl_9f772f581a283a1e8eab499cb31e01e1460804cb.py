from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/flow-tracking.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_flow_tracking = resolve('flow_tracking')
    l_0_sample_size = resolve('sample_size')
    l_0_min_sample_size = resolve('min_sample_size')
    l_0_hardware_offload_ipv4 = resolve('hardware_offload_ipv4')
    l_0_hardware_offload_ipv6 = resolve('hardware_offload_ipv6')
    l_0_encapsulations_list = resolve('encapsulations_list')
    l_0_encapsulations = resolve('encapsulations')
    l_0_sample_limit_size = resolve('sample_limit_size')
    l_0_namespace = resolve('namespace')
    l_0_ns_count_exporter = resolve('ns_count_exporter')
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
        t_3 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_4 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_5 = environment.filters['list']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'list' found.")
    try:
        t_6 = environment.filters['map']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'map' found.")
    try:
        t_7 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_7((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking)):
        pass
        yield '\n### Flow Tracking\n'
        if t_7(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled')):
            pass
            yield '\n#### Flow Tracking Sampled\n\n| Sample Size | Minimum Sample Size | Hardware Offload for IPv4 | Hardware Offload for IPv6 | Encapsulations |\n| ----------- | ------------------- | ------------------------- | ------------------------- | -------------- |\n'
            l_0_sample_size = t_1(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'sample'), 'default')
            context.vars['sample_size'] = l_0_sample_size
            context.exported_vars.add('sample_size')
            l_0_min_sample_size = t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'threshold_minimum'), 'default')
            context.vars['min_sample_size'] = l_0_min_sample_size
            context.exported_vars.add('min_sample_size')
            l_0_hardware_offload_ipv4 = 'disabled'
            context.vars['hardware_offload_ipv4'] = l_0_hardware_offload_ipv4
            context.exported_vars.add('hardware_offload_ipv4')
            l_0_hardware_offload_ipv6 = 'disabled'
            context.vars['hardware_offload_ipv6'] = l_0_hardware_offload_ipv6
            context.exported_vars.add('hardware_offload_ipv6')
            l_0_encapsulations_list = []
            context.vars['encapsulations_list'] = l_0_encapsulations_list
            context.exported_vars.add('encapsulations_list')
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'encapsulation'), 'ipv4_ipv6'), True):
                pass
                context.call(environment.getattr((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list), 'append'), 'ipv4')
                context.call(environment.getattr((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list), 'append'), 'ipv6')
                if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'encapsulation'), 'mpls'), True):
                    pass
                    context.call(environment.getattr((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list), 'append'), 'mpls')
            l_0_encapsulations = t_3(context.eval_ctx, ((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list) or ['-']), ', ')
            context.vars['encapsulations'] = l_0_encapsulations
            context.exported_vars.add('encapsulations')
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'ipv4'), True):
                pass
                l_0_hardware_offload_ipv4 = 'enabled'
                context.vars['hardware_offload_ipv4'] = l_0_hardware_offload_ipv4
                context.exported_vars.add('hardware_offload_ipv4')
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'hardware_offload'), 'ipv6'), True):
                pass
                l_0_hardware_offload_ipv6 = 'enabled'
                context.vars['hardware_offload_ipv6'] = l_0_hardware_offload_ipv6
                context.exported_vars.add('hardware_offload_ipv6')
            yield '| '
            yield str((undefined(name='sample_size') if l_0_sample_size is missing else l_0_sample_size))
            yield ' | '
            yield str((undefined(name='min_sample_size') if l_0_min_sample_size is missing else l_0_min_sample_size))
            yield ' | '
            yield str((undefined(name='hardware_offload_ipv4') if l_0_hardware_offload_ipv4 is missing else l_0_hardware_offload_ipv4))
            yield ' | '
            yield str((undefined(name='hardware_offload_ipv6') if l_0_hardware_offload_ipv6 is missing else l_0_hardware_offload_ipv6))
            yield ' | '
            yield str((undefined(name='encapsulations') if l_0_encapsulations is missing else l_0_encapsulations))
            yield ' |\n'
            if t_7(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'trackers')):
                pass
                yield '\n##### Trackers Summary\n\n| Tracker Name | Record Export On Inactive Timeout | Record Export On Interval | MPLS | Number of Exporters | Applied On | Table Size |\n| ------------ | --------------------------------- | ------------------------- | ---- | ------------------- | ---------- | ---------- |\n'
                for l_1_tracker in t_2(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'trackers'), 'name'):
                    l_1_dps_interfaces = resolve('dps_interfaces')
                    l_1_ethernet_interfaces = resolve('ethernet_interfaces')
                    l_1_port_channel_interfaces = resolve('port_channel_interfaces')
                    l_1_on_inactive_timeout = l_1_on_interval = l_1_mpls = l_1_count_exporter = l_1_applied_on = l_1_table_size = missing
                    _loop_vars = {}
                    pass
                    l_1_on_inactive_timeout = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout'), '-')
                    _loop_vars['on_inactive_timeout'] = l_1_on_inactive_timeout
                    l_1_on_interval = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval'), '-')
                    _loop_vars['on_interval'] = l_1_on_interval
                    l_1_mpls = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'mpls'), '-')
                    _loop_vars['mpls'] = l_1_mpls
                    l_1_count_exporter = t_4(t_1(environment.getattr(l_1_tracker, 'exporters'), []))
                    _loop_vars['count_exporter'] = l_1_count_exporter
                    l_1_applied_on = []
                    _loop_vars['applied_on'] = l_1_applied_on
                    l_1_table_size = t_1(environment.getattr(l_1_tracker, 'table_size'), '-')
                    _loop_vars['table_size'] = l_1_table_size
                    for l_2_dps_interface in t_1((undefined(name='dps_interfaces') if l_1_dps_interfaces is missing else l_1_dps_interfaces), []):
                        _loop_vars = {}
                        pass
                        if t_7(environment.getattr(environment.getattr(l_2_dps_interface, 'flow_tracker'), 'sampled'), environment.getattr(l_1_tracker, 'name')):
                            pass
                            context.call(environment.getattr((undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), 'append'), environment.getattr(l_2_dps_interface, 'name'), _loop_vars=_loop_vars)
                    l_2_dps_interface = missing
                    for l_2_ethernet_interface in t_1((undefined(name='ethernet_interfaces') if l_1_ethernet_interfaces is missing else l_1_ethernet_interfaces), []):
                        _loop_vars = {}
                        pass
                        if t_7(environment.getattr(environment.getattr(l_2_ethernet_interface, 'flow_tracker'), 'sampled'), environment.getattr(l_1_tracker, 'name')):
                            pass
                            context.call(environment.getattr((undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), 'append'), environment.getattr(l_2_ethernet_interface, 'name'), _loop_vars=_loop_vars)
                    l_2_ethernet_interface = missing
                    for l_2_port_channel_interface in t_1((undefined(name='port_channel_interfaces') if l_1_port_channel_interfaces is missing else l_1_port_channel_interfaces), []):
                        _loop_vars = {}
                        pass
                        if t_7(environment.getattr(environment.getattr(l_2_port_channel_interface, 'flow_tracker'), 'sampled'), environment.getattr(l_1_tracker, 'name')):
                            pass
                            context.call(environment.getattr((undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), 'append'), environment.getattr(l_2_port_channel_interface, 'name'), _loop_vars=_loop_vars)
                    l_2_port_channel_interface = missing
                    yield '| '
                    yield str(environment.getattr(l_1_tracker, 'name'))
                    yield ' | '
                    yield str((undefined(name='on_inactive_timeout') if l_1_on_inactive_timeout is missing else l_1_on_inactive_timeout))
                    yield ' | '
                    yield str((undefined(name='on_interval') if l_1_on_interval is missing else l_1_on_interval))
                    yield ' | '
                    yield str((undefined(name='mpls') if l_1_mpls is missing else l_1_mpls))
                    yield ' | '
                    yield str((undefined(name='count_exporter') if l_1_count_exporter is missing else l_1_count_exporter))
                    yield ' | '
                    yield str(t_3(context.eval_ctx, (undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), '<br>'))
                    yield ' | '
                    yield str((undefined(name='table_size') if l_1_table_size is missing else l_1_table_size))
                    yield ' |\n'
                l_1_tracker = l_1_on_inactive_timeout = l_1_on_interval = l_1_mpls = l_1_count_exporter = l_1_applied_on = l_1_table_size = l_1_dps_interfaces = l_1_ethernet_interfaces = l_1_port_channel_interfaces = missing
                yield '\n##### Exporters Summary\n\n| Tracker Name | Exporter Name | Collector IP/Host | Collector Port | Local Interface |\n| ------------ | ------------- | ----------------- | -------------- | --------------- |\n'
                for l_1_tracker in t_2(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'sampled'), 'trackers'), 'name'):
                    _loop_vars = {}
                    pass
                    for l_2_exporter in t_2(environment.getattr(l_1_tracker, 'exporters'), 'name'):
                        l_2_host = resolve('host')
                        l_2_port = resolve('port')
                        l_2_local_interface = missing
                        _loop_vars = {}
                        pass
                        if t_7(environment.getattr(l_2_exporter, 'collectors')):
                            pass
                            l_2_host = t_3(context.eval_ctx, t_5(context.eval_ctx, t_6(context, t_2(environment.getattr(l_2_exporter, 'collectors')), attribute='host')), '<br>')
                            _loop_vars['host'] = l_2_host
                            l_2_port = t_3(context.eval_ctx, t_5(context.eval_ctx, t_6(context, t_6(context, t_2(environment.getattr(l_2_exporter, 'collectors')), attribute='port'), 'arista.avd.default', '-')), '<br>')
                            _loop_vars['port'] = l_2_port
                        elif t_7(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host')):
                            pass
                            l_2_host = environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host')
                            _loop_vars['host'] = l_2_host
                            l_2_port = t_1(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'port'), '-')
                            _loop_vars['port'] = l_2_port
                        l_2_local_interface = t_1(environment.getattr(l_2_exporter, 'local_interface'), 'No local interface')
                        _loop_vars['local_interface'] = l_2_local_interface
                        yield '| '
                        yield str(environment.getattr(l_1_tracker, 'name'))
                        yield ' | '
                        yield str(environment.getattr(l_2_exporter, 'name'))
                        yield ' | '
                        yield str(t_1((undefined(name='host') if l_2_host is missing else l_2_host), '-'))
                        yield ' | '
                        yield str(t_1((undefined(name='port') if l_2_port is missing else l_2_port), '-'))
                        yield ' | '
                        yield str((undefined(name='local_interface') if l_2_local_interface is missing else l_2_local_interface))
                        yield ' |\n'
                    l_2_exporter = l_2_host = l_2_port = l_2_local_interface = missing
                l_1_tracker = missing
        if t_7(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware')):
            pass
            yield '\n#### Flow Tracking Hardware\n'
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'record'), 'format_ipfix_standard_timestamps_counters'), True):
                pass
                yield '\nSoftware export of IPFIX data records enabled.\n'
            if t_7(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'trackers')):
                pass
                yield '\n##### Trackers Summary\n\n| Tracker Name | Record Export On Inactive Timeout | Record Export On Interval | Number of Exporters | Applied On |\n| ------------ | --------------------------------- | ------------------------- | ------------------- | ---------- |\n'
                for l_1_tracker in t_2(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'trackers'), 'name'):
                    l_1_dps_interfaces = resolve('dps_interfaces')
                    l_1_ethernet_interfaces = resolve('ethernet_interfaces')
                    l_1_port_channel_interfaces = resolve('port_channel_interfaces')
                    l_1_on_inactive_timeout = l_1_on_interval = l_1_count_exporter = l_1_applied_on = missing
                    _loop_vars = {}
                    pass
                    l_1_on_inactive_timeout = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout'), '-')
                    _loop_vars['on_inactive_timeout'] = l_1_on_inactive_timeout
                    l_1_on_interval = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval'), '-')
                    _loop_vars['on_interval'] = l_1_on_interval
                    l_1_count_exporter = t_4(t_1(environment.getattr(l_1_tracker, 'exporters'), []))
                    _loop_vars['count_exporter'] = l_1_count_exporter
                    l_1_applied_on = []
                    _loop_vars['applied_on'] = l_1_applied_on
                    for l_2_dps_interface in t_1((undefined(name='dps_interfaces') if l_1_dps_interfaces is missing else l_1_dps_interfaces), []):
                        _loop_vars = {}
                        pass
                        if t_7(environment.getattr(environment.getattr(l_2_dps_interface, 'flow_tracker'), 'hardware'), environment.getattr(l_1_tracker, 'name')):
                            pass
                            context.call(environment.getattr((undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), 'append'), environment.getattr(l_2_dps_interface, 'name'), _loop_vars=_loop_vars)
                    l_2_dps_interface = missing
                    for l_2_ethernet_interface in t_1((undefined(name='ethernet_interfaces') if l_1_ethernet_interfaces is missing else l_1_ethernet_interfaces), []):
                        _loop_vars = {}
                        pass
                        if t_7(environment.getattr(environment.getattr(l_2_ethernet_interface, 'flow_tracker'), 'hardware'), environment.getattr(l_1_tracker, 'name')):
                            pass
                            context.call(environment.getattr((undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), 'append'), environment.getattr(l_2_ethernet_interface, 'name'), _loop_vars=_loop_vars)
                    l_2_ethernet_interface = missing
                    for l_2_port_channel_interface in t_1((undefined(name='port_channel_interfaces') if l_1_port_channel_interfaces is missing else l_1_port_channel_interfaces), []):
                        _loop_vars = {}
                        pass
                        if t_7(environment.getattr(environment.getattr(l_2_port_channel_interface, 'flow_tracker'), 'hardware'), environment.getattr(l_1_tracker, 'name')):
                            pass
                            context.call(environment.getattr((undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), 'append'), environment.getattr(l_2_port_channel_interface, 'name'), _loop_vars=_loop_vars)
                    l_2_port_channel_interface = missing
                    yield '| '
                    yield str(environment.getattr(l_1_tracker, 'name'))
                    yield ' | '
                    yield str((undefined(name='on_inactive_timeout') if l_1_on_inactive_timeout is missing else l_1_on_inactive_timeout))
                    yield ' | '
                    yield str((undefined(name='on_interval') if l_1_on_interval is missing else l_1_on_interval))
                    yield ' | '
                    yield str((undefined(name='count_exporter') if l_1_count_exporter is missing else l_1_count_exporter))
                    yield ' | '
                    yield str(t_3(context.eval_ctx, (undefined(name='applied_on') if l_1_applied_on is missing else l_1_applied_on), '<br>'))
                    yield ' |\n'
                l_1_tracker = l_1_on_inactive_timeout = l_1_on_interval = l_1_count_exporter = l_1_applied_on = l_1_dps_interfaces = l_1_ethernet_interfaces = l_1_port_channel_interfaces = missing
                yield '\n##### Exporters Summary\n\n| Tracker Name | Exporter Name | Collector IP/Host | Collector Port | Local Interface |\n| ------------ | ------------- | ----------------- | -------------- | --------------- |\n'
                for l_1_tracker in t_2(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'hardware'), 'trackers'), 'name'):
                    _loop_vars = {}
                    pass
                    for l_2_exporter in t_2(environment.getattr(l_1_tracker, 'exporters'), 'name'):
                        l_2_host = resolve('host')
                        l_2_port = resolve('port')
                        l_2_local_interface = missing
                        _loop_vars = {}
                        pass
                        if t_7(environment.getattr(l_2_exporter, 'collectors')):
                            pass
                            l_2_host = t_3(context.eval_ctx, t_5(context.eval_ctx, t_6(context, t_2(environment.getattr(l_2_exporter, 'collectors')), attribute='host')), '<br>')
                            _loop_vars['host'] = l_2_host
                            l_2_port = t_3(context.eval_ctx, t_5(context.eval_ctx, t_6(context, t_6(context, t_2(environment.getattr(l_2_exporter, 'collectors')), attribute='port'), 'arista.avd.default', '-')), '<br>')
                            _loop_vars['port'] = l_2_port
                        elif t_7(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host')):
                            pass
                            l_2_host = environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'host')
                            _loop_vars['host'] = l_2_host
                            l_2_port = t_1(environment.getattr(environment.getattr(l_2_exporter, 'collector'), 'port'), '-')
                            _loop_vars['port'] = l_2_port
                        l_2_local_interface = t_1(environment.getattr(l_2_exporter, 'local_interface'), 'No local interface')
                        _loop_vars['local_interface'] = l_2_local_interface
                        yield '| '
                        yield str(environment.getattr(l_1_tracker, 'name'))
                        yield ' | '
                        yield str(environment.getattr(l_2_exporter, 'name'))
                        yield ' | '
                        yield str(t_1((undefined(name='host') if l_2_host is missing else l_2_host), '-'))
                        yield ' | '
                        yield str(t_1((undefined(name='port') if l_2_port is missing else l_2_port), '-'))
                        yield ' | '
                        yield str((undefined(name='local_interface') if l_2_local_interface is missing else l_2_local_interface))
                        yield ' |\n'
                    l_2_exporter = l_2_host = l_2_port = l_2_local_interface = missing
                l_1_tracker = missing
        if t_7(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop')):
            pass
            yield '\n#### Flow Tracking mirror-on-drop\n\n| Sample Limit Size | Encapsulations |\n| ----------------- | -------------- |\n'
            l_0_sample_limit_size = t_1(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'sample_limit'), 'default')
            context.vars['sample_limit_size'] = l_0_sample_limit_size
            context.exported_vars.add('sample_limit_size')
            l_0_encapsulations_list = []
            context.vars['encapsulations_list'] = l_0_encapsulations_list
            context.exported_vars.add('encapsulations_list')
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'encapsulation'), 'ipv4_ipv6'), True):
                pass
                context.call(environment.getattr((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list), 'append'), 'ipv4, ipv6')
            if t_7(environment.getattr(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'encapsulation'), 'mpls'), True):
                pass
                context.call(environment.getattr((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list), 'append'), 'mpls')
            l_0_encapsulations = t_3(context.eval_ctx, ((undefined(name='encapsulations_list') if l_0_encapsulations_list is missing else l_0_encapsulations_list) or ['-']), ', ')
            context.vars['encapsulations'] = l_0_encapsulations
            context.exported_vars.add('encapsulations')
            yield '| '
            yield str((undefined(name='sample_limit_size') if l_0_sample_limit_size is missing else l_0_sample_limit_size))
            yield ' | '
            yield str((undefined(name='encapsulations') if l_0_encapsulations is missing else l_0_encapsulations))
            yield ' |\n'
            if t_7(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'trackers')):
                pass
                l_0_ns_count_exporter = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), count_exporter=0)
                context.vars['ns_count_exporter'] = l_0_ns_count_exporter
                context.exported_vars.add('ns_count_exporter')
                yield '\n##### Trackers Summary\n\n| Tracker Name | Record Export On Inactive Timeout | Record Export On Interval | Number of Exporters |\n| ------------ | --------------------------------- | ------------------------- | ------------------- |\n'
                for l_1_tracker in t_2(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'trackers'), 'name'):
                    l_1_on_inactive_timeout = l_1_on_interval = missing
                    _loop_vars = {}
                    pass
                    l_1_on_inactive_timeout = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_inactive_timeout'), '-')
                    _loop_vars['on_inactive_timeout'] = l_1_on_inactive_timeout
                    l_1_on_interval = t_1(environment.getattr(environment.getattr(l_1_tracker, 'record_export'), 'on_interval'), '-')
                    _loop_vars['on_interval'] = l_1_on_interval
                    if not isinstance(l_0_ns_count_exporter, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_0_ns_count_exporter['count_exporter'] = t_4(t_1(environment.getattr(l_1_tracker, 'exporters'), []))
                    yield '| '
                    yield str(environment.getattr(l_1_tracker, 'name'))
                    yield ' | '
                    yield str((undefined(name='on_inactive_timeout') if l_1_on_inactive_timeout is missing else l_1_on_inactive_timeout))
                    yield ' | '
                    yield str((undefined(name='on_interval') if l_1_on_interval is missing else l_1_on_interval))
                    yield ' | '
                    yield str(environment.getattr((undefined(name='ns_count_exporter') if l_0_ns_count_exporter is missing else l_0_ns_count_exporter), 'count_exporter'))
                    yield ' |\n'
                l_1_tracker = l_1_on_inactive_timeout = l_1_on_interval = missing
                if (environment.getattr((undefined(name='ns_count_exporter') if l_0_ns_count_exporter is missing else l_0_ns_count_exporter), 'count_exporter') > 0):
                    pass
                    yield '\n##### Exporters Summary\n\n| Tracker Name | Exporter Name |  Local Interface | Template Interval | Collector IP/Host/Sflow | Collector Port | DSCP Value | Format |\n| ------------ | ------------- | ---------------- | ------------------| ----------------------- | -------------- | ---------- | ------ |\n'
                    for l_1_tracker in t_2(environment.getattr(environment.getattr((undefined(name='flow_tracking') if l_0_flow_tracking is missing else l_0_flow_tracking), 'mirror_on_drop'), 'trackers'), 'name'):
                        _loop_vars = {}
                        pass
                        for l_2_exporter in t_2(environment.getattr(l_1_tracker, 'exporters'), 'name'):
                            l_2_current_exporter_collector_hosts = l_2_current_exporter_collector_ports = missing
                            _loop_vars = {}
                            pass
                            l_2_current_exporter_collector_hosts = t_5(context.eval_ctx, t_6(context, t_2(environment.getattr(l_2_exporter, 'collectors')), attribute='host'))
                            _loop_vars['current_exporter_collector_hosts'] = l_2_current_exporter_collector_hosts
                            l_2_current_exporter_collector_ports = t_5(context.eval_ctx, t_6(context, t_6(context, t_2(environment.getattr(l_2_exporter, 'collectors')), attribute='port'), 'arista.avd.default', '-'))
                            _loop_vars['current_exporter_collector_ports'] = l_2_current_exporter_collector_ports
                            yield '| '
                            yield str(environment.getattr(l_1_tracker, 'name'))
                            yield ' | '
                            yield str(environment.getattr(l_2_exporter, 'name'))
                            yield ' | '
                            yield str(t_1(environment.getattr(l_2_exporter, 'local_interface'), '-'))
                            yield ' | '
                            yield str(t_1(environment.getattr(l_2_exporter, 'template_interval'), '-'))
                            yield ' | '
                            yield str(t_3(context.eval_ctx, (undefined(name='current_exporter_collector_hosts') if l_2_current_exporter_collector_hosts is missing else l_2_current_exporter_collector_hosts), '<br>'))
                            yield ' | '
                            yield str(t_3(context.eval_ctx, (undefined(name='current_exporter_collector_ports') if l_2_current_exporter_collector_ports is missing else l_2_current_exporter_collector_ports), '<br>'))
                            yield ' | '
                            yield str(t_1(environment.getattr(l_2_exporter, 'dscp'), '-'))
                            yield ' | '
                            yield str(t_1(environment.getattr(l_2_exporter, 'format'), '-'))
                            yield ' |\n'
                        l_2_exporter = l_2_current_exporter_collector_hosts = l_2_current_exporter_collector_ports = missing
                    l_1_tracker = missing
        yield '\n#### Flow Tracking Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/flow-tracking.j2', 'documentation/flow-tracking.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'encapsulations': l_0_encapsulations, 'encapsulations_list': l_0_encapsulations_list, 'hardware_offload_ipv4': l_0_hardware_offload_ipv4, 'hardware_offload_ipv6': l_0_hardware_offload_ipv6, 'min_sample_size': l_0_min_sample_size, 'ns_count_exporter': l_0_ns_count_exporter, 'sample_limit_size': l_0_sample_limit_size, 'sample_size': l_0_sample_size}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=63&10=66&16=69&17=72&18=75&19=78&20=81&21=84&22=86&23=87&24=88&25=90&28=91&29=94&30=96&32=99&33=101&35=105&36=115&42=118&43=125&44=127&45=129&46=131&47=133&48=135&49=137&50=140&51=142&54=144&55=147&56=149&59=151&60=154&61=156&64=159&71=175&72=178&73=184&74=186&75=188&76=190&77=192&78=194&80=196&81=199&86=211&89=214&93=217&99=220&100=227&101=229&102=231&103=233&104=235&105=238&106=240&109=242&110=245&111=247&114=249&115=252&116=254&119=257&126=269&127=272&128=278&129=280&130=282&131=284&132=286&133=288&135=290&136=293&141=305&147=308&148=311&149=314&150=316&152=317&153=319&155=320&156=324&157=328&158=330&165=334&166=338&167=340&168=344&169=346&171=355&177=358&178=361&179=365&180=367&181=370&191=389'