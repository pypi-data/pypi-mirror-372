from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/router-traffic-engineering.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_router_traffic_engineering = resolve('router_traffic_engineering')
    l_0_namespace = resolve('namespace')
    l_0_ns = resolve('ns')
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
    if t_3(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'enabled'), True):
        pass
        yield '!\nrouter traffic-engineering\n'
        if t_3(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'segment_routing')):
            pass
            l_0_ns = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), delimiter=False)
            context.vars['ns'] = l_0_ns
            context.exported_vars.add('ns')
            yield '   segment-routing\n'
            if t_3(environment.getattr(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'segment_routing'), 'colored_tunnel_rib'), True):
                pass
                if not isinstance(l_0_ns, Namespace):
                    raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                l_0_ns['delimiter'] = True
                yield '      rib system-colored-tunnel-rib\n'
            if t_3(environment.getattr(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'segment_routing'), 'policy_endpoints')):
                pass
                for l_1_endpoint in t_1(environment.getattr(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'segment_routing'), 'policy_endpoints'), 'address'):
                    _loop_vars = {}
                    pass
                    for l_2_color in t_1(environment.getattr(l_1_endpoint, 'colors'), 'value'):
                        _loop_vars = {}
                        pass
                        if t_3(environment.getattr((undefined(name='ns') if l_0_ns is missing else l_0_ns), 'delimiter'), True):
                            pass
                            yield '      !\n'
                        if not isinstance(l_0_ns, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_0_ns['delimiter'] = True
                        yield '      policy endpoint '
                        yield str(environment.getattr(l_1_endpoint, 'address'))
                        yield ' color '
                        yield str(environment.getattr(l_2_color, 'value'))
                        yield '\n'
                        if t_3(environment.getattr(l_2_color, 'binding_sid')):
                            pass
                            yield '         binding-sid '
                            yield str(environment.getattr(l_2_color, 'binding_sid'))
                            yield '\n'
                        if t_3(environment.getattr(l_2_color, 'name')):
                            pass
                            yield '         name '
                            yield str(environment.getattr(l_2_color, 'name'))
                            yield '\n'
                        if t_3(environment.getattr(l_2_color, 'description')):
                            pass
                            yield '         description '
                            yield str(environment.getattr(l_2_color, 'description'))
                            yield '\n'
                        if t_3(environment.getattr(l_2_color, 'sbfd_remote_discriminator')):
                            pass
                            yield '         sbfd remote-discriminator '
                            yield str(environment.getattr(l_2_color, 'sbfd_remote_discriminator'))
                            yield '\n'
                        for l_3_pathgroup in t_1(environment.getattr(l_2_color, 'path_group'), 'preference'):
                            _loop_vars = {}
                            pass
                            yield '         !\n         path-group preference '
                            yield str(environment.getattr(l_3_pathgroup, 'preference'))
                            yield '\n'
                            if t_3(environment.getattr(l_3_pathgroup, 'explicit_null')):
                                pass
                                yield '            explicit-null '
                                yield str(environment.getattr(l_3_pathgroup, 'explicit_null'))
                                yield '\n'
                            for l_4_labelstack in t_1(environment.getattr(l_3_pathgroup, 'segment_list'), 'label_stack'):
                                l_4_stack = missing
                                _loop_vars = {}
                                pass
                                l_4_stack = environment.getattr(l_4_labelstack, 'label_stack')
                                _loop_vars['stack'] = l_4_stack
                                if t_3(environment.getattr(l_4_labelstack, 'weight')):
                                    pass
                                    l_4_stack = str_join(((undefined(name='stack') if l_4_stack is missing else l_4_stack), ' weight ', environment.getattr(l_4_labelstack, 'weight'), ))
                                    _loop_vars['stack'] = l_4_stack
                                if t_3(environment.getattr(l_4_labelstack, 'index')):
                                    pass
                                    l_4_stack = str_join(((undefined(name='stack') if l_4_stack is missing else l_4_stack), ' index ', environment.getattr(l_4_labelstack, 'index'), ))
                                    _loop_vars['stack'] = l_4_stack
                                yield '            segment-list label-stack '
                                yield str((undefined(name='stack') if l_4_stack is missing else l_4_stack))
                                yield '\n'
                            l_4_labelstack = l_4_stack = missing
                        l_3_pathgroup = missing
                    l_2_color = missing
                l_1_endpoint = missing
        if t_3(environment.getattr(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'router_id'), 'ipv4')):
            pass
            yield '   router-id ipv4 '
            yield str(environment.getattr(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'router_id'), 'ipv4'))
            yield '\n'
        if t_3(environment.getattr(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'router_id'), 'ipv6')):
            pass
            yield '   router-id ipv6 '
            yield str(environment.getattr(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'router_id'), 'ipv6'))
            yield '\n'
        if t_3(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'twamp_light_sender_profile')):
            pass
            yield '   twamp-light sender profile '
            yield str(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'twamp_light_sender_profile'))
            yield '\n'
        if t_3(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'flex_algos')):
            pass
            yield '   !\n   flex-algo\n'
            l_1_loop = missing
            for l_1_flex_algo, l_1_loop in LoopContext(t_1(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'flex_algos'), 'number'), undefined):
                l_1_admingrp_cli = resolve('admingrp_cli')
                _loop_vars = {}
                pass
                yield '      flex-algo '
                yield str(environment.getattr(l_1_flex_algo, 'number'))
                yield ' '
                yield str(environment.getattr(l_1_flex_algo, 'name'))
                yield '\n'
                if t_3(environment.getattr(l_1_flex_algo, 'priority')):
                    pass
                    yield '         priority '
                    yield str(environment.getattr(l_1_flex_algo, 'priority'))
                    yield '\n'
                if ((t_3(environment.getattr(environment.getattr(l_1_flex_algo, 'administrative_group'), 'include_all')) or t_3(environment.getattr(environment.getattr(l_1_flex_algo, 'administrative_group'), 'include_any'))) or t_3(environment.getattr(environment.getattr(l_1_flex_algo, 'administrative_group'), 'exclude'))):
                    pass
                    l_1_admingrp_cli = 'administrative-group'
                    _loop_vars['admingrp_cli'] = l_1_admingrp_cli
                    if t_3(environment.getattr(environment.getattr(l_1_flex_algo, 'administrative_group'), 'include_all')):
                        pass
                        l_1_admingrp_cli = str_join(((undefined(name='admingrp_cli') if l_1_admingrp_cli is missing else l_1_admingrp_cli), ' include all ', environment.getattr(environment.getattr(l_1_flex_algo, 'administrative_group'), 'include_all'), ))
                        _loop_vars['admingrp_cli'] = l_1_admingrp_cli
                    if t_3(environment.getattr(environment.getattr(l_1_flex_algo, 'administrative_group'), 'include_any')):
                        pass
                        l_1_admingrp_cli = str_join(((undefined(name='admingrp_cli') if l_1_admingrp_cli is missing else l_1_admingrp_cli), ' include any ', environment.getattr(environment.getattr(l_1_flex_algo, 'administrative_group'), 'include_any'), ))
                        _loop_vars['admingrp_cli'] = l_1_admingrp_cli
                    if t_3(environment.getattr(environment.getattr(l_1_flex_algo, 'administrative_group'), 'exclude')):
                        pass
                        l_1_admingrp_cli = str_join(((undefined(name='admingrp_cli') if l_1_admingrp_cli is missing else l_1_admingrp_cli), ' exclude ', environment.getattr(environment.getattr(l_1_flex_algo, 'administrative_group'), 'exclude'), ))
                        _loop_vars['admingrp_cli'] = l_1_admingrp_cli
                    yield '         '
                    yield str((undefined(name='admingrp_cli') if l_1_admingrp_cli is missing else l_1_admingrp_cli))
                    yield '\n'
                if t_3(environment.getattr(l_1_flex_algo, 'metric')):
                    pass
                    yield '         metric '
                    yield str(environment.getattr(l_1_flex_algo, 'metric'))
                    yield '\n'
                if t_3(environment.getattr(l_1_flex_algo, 'srlg_exclude')):
                    pass
                    yield '         srlg exclude '
                    yield str(environment.getattr(l_1_flex_algo, 'srlg_exclude'))
                    yield '\n'
                if t_3(environment.getattr(l_1_flex_algo, 'color')):
                    pass
                    yield '         color '
                    yield str(environment.getattr(l_1_flex_algo, 'color'))
                    yield '\n'
                if (environment.getattr(l_1_loop, 'index') < t_2(t_1(environment.getattr((undefined(name='router_traffic_engineering') if l_0_router_traffic_engineering is missing else l_0_router_traffic_engineering), 'flex_algos'), 'number'))):
                    pass
                    yield '      !\n'
            l_1_loop = l_1_flex_algo = l_1_admingrp_cli = missing

blocks = {}
debug_info = '7=32&10=35&11=37&13=41&14=45&17=47&18=49&19=52&20=55&23=60&24=62&25=66&26=69&28=71&29=74&31=76&32=79&34=81&35=84&37=86&39=90&40=92&41=95&43=97&44=101&45=103&46=105&48=107&49=109&51=112&58=118&59=121&61=123&62=126&64=128&65=131&67=133&70=137&71=142&72=146&73=149&75=151&76=153&77=155&78=157&80=159&81=161&83=163&84=165&86=168&88=170&89=173&91=175&92=178&94=180&95=183&97=185'