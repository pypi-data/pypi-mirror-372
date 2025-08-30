from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/load-balance.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_load_balance = resolve('load_balance')
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
    if t_3((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance)):
        pass
        yield '\n## Load Balance\n'
        if t_3(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'policies')):
            pass
            yield '\n### Load Balance Profiles\n'
            for l_1_profile in t_2(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'policies'), 'sand_profiles'), 'name'):
                _loop_vars = {}
                pass
                yield '\n#### '
                yield str(environment.getattr(l_1_profile, 'name'))
                yield '\n'
                if t_3(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp')):
                    pass
                    yield '\n##### UDP Fields Settings\n\n| Setting | Value |\n| ------- | ----- |\n| Destination Port | '
                    yield str(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'dst_port'))
                    yield ' |\n'
                    if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match')):
                        pass
                        yield '| Match Payload Bits | '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match'), 'payload_bits'))
                        yield ' |\n| Match Pattern | '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match'), 'pattern'))
                        yield ' |\n| Match Hash Payload Bytes | '
                        yield str(environment.getattr(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'match'), 'hash_payload_bytes'))
                        yield ' |\n'
                    if t_3(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'payload_bytes')):
                        pass
                        yield '| UDP Payload | '
                        yield str(environment.getattr(environment.getattr(environment.getattr(l_1_profile, 'fields'), 'udp'), 'payload_bytes'))
                        yield ' |\n'
            l_1_profile = missing
        if t_3(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster')):
            pass
            yield '\n### Load Balance Cluster\n\n| Setting | Value |\n| ------- | ----- |\n'
            if t_3(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'forwarding_type')):
                pass
                yield '| Forwarding Type | '
                yield str(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'forwarding_type'))
                yield ' |\n'
            if t_3(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'destination_grouping')):
                pass
                if (environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'destination_grouping') != 'prefix length'):
                    pass
                    yield '| Destination Grouping | '
                    yield str(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'destination_grouping'))
                    yield ' |\n'
                elif t_3(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'prefix_length')):
                    pass
                    yield '| Destination Grouping | '
                    yield str(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'destination_grouping'))
                    yield ' '
                    yield str(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'prefix_length'))
                    yield ' |\n'
            if t_3(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'load_balance_method_flow_round_robin')):
                pass
                yield '| Load-balance Method Flow Round-robin | '
                yield str(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'load_balance_method_flow_round_robin'))
                yield ' |\n'
            if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'flow'), 'monitor')):
                pass
                yield '| Flow Monitor | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'flow'), 'monitor'))
                yield ' |\n'
            if t_3(environment.getattr(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'flow'), 'source_learning_aging_timeout')):
                pass
                yield '| Flow Source Learning Aging Timeout | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'flow'), 'source_learning_aging_timeout'))
                yield ' seconds |\n'
            if t_3(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'port_groups')):
                pass
                yield '\n#### Host Port Groups\n\n| Port Group | Interface | Flow Limit | Flow Warning | Balance Factor | Exhaustion Action DSCP | Exhaustion Action Traffic-class |\n| ---------- | --------- | ---------- | ------------ | -------------- | ---------------------- | ------------------------------- |\n'
                for l_1_port_group in t_2(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'port_groups'), 'group'):
                    l_1_interface = l_1_flow_limit = l_1_flow_warning = l_1_balance_factor = l_1_exhaustion_action_dscp = l_1_exhaustion_action_traffic_class = missing
                    _loop_vars = {}
                    pass
                    l_1_interface = t_1(environment.getattr(l_1_port_group, 'interface'), '-')
                    _loop_vars['interface'] = l_1_interface
                    l_1_flow_limit = t_1(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'limit'), '-')
                    _loop_vars['flow_limit'] = l_1_flow_limit
                    l_1_flow_warning = t_1(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'warning'), '-')
                    _loop_vars['flow_warning'] = l_1_flow_warning
                    l_1_balance_factor = t_1(environment.getattr(l_1_port_group, 'balance_factor'), '-')
                    _loop_vars['balance_factor'] = l_1_balance_factor
                    l_1_exhaustion_action_dscp = t_1(environment.getattr(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'exhaustion_action'), 'dscp'), '-')
                    _loop_vars['exhaustion_action_dscp'] = l_1_exhaustion_action_dscp
                    l_1_exhaustion_action_traffic_class = t_1(environment.getattr(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'exhaustion_action'), 'traffic_class'), '-')
                    _loop_vars['exhaustion_action_traffic_class'] = l_1_exhaustion_action_traffic_class
                    yield '| '
                    yield str(environment.getattr(l_1_port_group, 'group'))
                    yield ' | '
                    yield str((undefined(name='interface') if l_1_interface is missing else l_1_interface))
                    yield ' | '
                    yield str((undefined(name='flow_limit') if l_1_flow_limit is missing else l_1_flow_limit))
                    yield ' | '
                    yield str((undefined(name='flow_warning') if l_1_flow_warning is missing else l_1_flow_warning))
                    yield ' | '
                    yield str((undefined(name='balance_factor') if l_1_balance_factor is missing else l_1_balance_factor))
                    yield ' | '
                    yield str((undefined(name='exhaustion_action_dscp') if l_1_exhaustion_action_dscp is missing else l_1_exhaustion_action_dscp))
                    yield ' | '
                    yield str((undefined(name='exhaustion_action_traffic_class') if l_1_exhaustion_action_traffic_class is missing else l_1_exhaustion_action_traffic_class))
                    yield ' |\n'
                l_1_port_group = l_1_interface = l_1_flow_limit = l_1_flow_warning = l_1_balance_factor = l_1_exhaustion_action_dscp = l_1_exhaustion_action_traffic_class = missing
        yield '\n### Load Balance Configuration\n\n```eos\n'
        template = environment.get_template('eos/load-balance.j2', 'documentation/load-balance.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        template = environment.get_template('eos/load-balance-cluster.j2', 'documentation/load-balance.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=30&10=33&13=36&15=40&16=42&22=45&23=47&24=50&25=52&26=54&28=56&29=59&34=62&40=65&41=68&43=70&44=72&45=75&46=77&47=80&50=84&51=87&53=89&54=92&56=94&57=97&59=99&65=102&66=106&67=108&68=110&69=112&70=114&71=116&72=119&80=135&81=141'