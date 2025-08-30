from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/load-balance-cluster.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_load_balance = resolve('load_balance')
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
    if t_2(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster')):
        pass
        yield '!\nload-balance cluster\n'
        if t_2(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'forwarding_type')):
            pass
            yield '   forwarding type '
            yield str(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'forwarding_type'))
            yield '\n'
        if t_2(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'destination_grouping')):
            pass
            if (environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'destination_grouping') != 'prefix length'):
                pass
                yield '   destination grouping '
                yield str(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'destination_grouping'))
                yield '\n'
            elif t_2(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'prefix_length')):
                pass
                yield '   destination grouping '
                yield str(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'destination_grouping'))
                yield ' '
                yield str(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'prefix_length'))
                yield '\n'
        if t_2(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'load_balance_method_flow_round_robin'), True):
            pass
            yield '   load-balance method flow round-robin\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'flow'), 'monitor'), True):
            pass
            yield '   flow monitor\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'flow'), 'source_learning_aging_timeout')):
            pass
            yield '   !\n   flow source learning\n      aging timeout '
            yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'flow'), 'source_learning_aging_timeout'))
            yield ' seconds\n'
        for l_1_port_group in t_1(environment.getattr(environment.getattr((undefined(name='load_balance') if l_0_load_balance is missing else l_0_load_balance), 'cluster'), 'port_groups'), 'group'):
            l_1_exhaustion_action_cli = resolve('exhaustion_action_cli')
            _loop_vars = {}
            pass
            yield '   !\n   port group host '
            yield str(environment.getattr(l_1_port_group, 'group'))
            yield '\n'
            if t_2(environment.getattr(l_1_port_group, 'interface')):
                pass
                yield '      interface '
                yield str(environment.getattr(l_1_port_group, 'interface'))
                yield '\n'
            if t_2(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'limit')):
                pass
                yield '      flow limit '
                yield str(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'limit'))
                yield '\n'
            if t_2(environment.getattr(l_1_port_group, 'balance_factor')):
                pass
                yield '      balance factor '
                yield str(environment.getattr(l_1_port_group, 'balance_factor'))
                yield '\n'
            if t_2(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'warning')):
                pass
                yield '      flow warning '
                yield str(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'warning'))
                yield '\n'
            if (t_2(environment.getattr(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'exhaustion_action'), 'dscp')) or t_2(environment.getattr(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'exhaustion_action'), 'traffic_class'))):
                pass
                l_1_exhaustion_action_cli = 'flow exhaustion action'
                _loop_vars['exhaustion_action_cli'] = l_1_exhaustion_action_cli
                if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'exhaustion_action'), 'dscp')):
                    pass
                    l_1_exhaustion_action_cli = str_join(((undefined(name='exhaustion_action_cli') if l_1_exhaustion_action_cli is missing else l_1_exhaustion_action_cli), ' dscp ', environment.getattr(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'exhaustion_action'), 'dscp'), ))
                    _loop_vars['exhaustion_action_cli'] = l_1_exhaustion_action_cli
                if t_2(environment.getattr(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'exhaustion_action'), 'traffic_class')):
                    pass
                    l_1_exhaustion_action_cli = str_join(((undefined(name='exhaustion_action_cli') if l_1_exhaustion_action_cli is missing else l_1_exhaustion_action_cli), ' traffic-class ', environment.getattr(environment.getattr(environment.getattr(l_1_port_group, 'flow'), 'exhaustion_action'), 'traffic_class'), ))
                    _loop_vars['exhaustion_action_cli'] = l_1_exhaustion_action_cli
                yield '      '
                yield str((undefined(name='exhaustion_action_cli') if l_1_exhaustion_action_cli is missing else l_1_exhaustion_action_cli))
                yield '\n'
        l_1_port_group = l_1_exhaustion_action_cli = missing

blocks = {}
debug_info = '7=24&10=27&11=30&13=32&14=34&15=37&16=39&17=42&20=46&23=49&26=52&29=55&31=57&33=62&34=64&35=67&37=69&38=72&40=74&41=77&43=79&44=82&46=84&47=86&48=88&49=90&51=92&52=94&54=97'