from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/router-pim-sparse-mode.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_router_pim_sparse_mode = resolve('router_pim_sparse_mode')
    l_0_namespace = resolve('namespace')
    l_0_any_ipv4_ip_addresses = resolve('any_ipv4_ip_addresses')
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
        t_3 = environment.filters['default']
    except KeyError:
        @internalcode
        def t_3(*unused):
            raise TemplateRuntimeError("No filter named 'default' found.")
    try:
        t_4 = environment.filters['join']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'join' found.")
    try:
        t_5 = environment.filters['length']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'length' found.")
    try:
        t_6 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_6((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode)):
        pass
        yield '\n#### Router PIM Sparse Mode\n\n##### IP Sparse Mode Information\n'
        if t_6(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'ipv4')):
            pass
            yield '\nBFD enabled: '
            yield str(t_1(environment.getattr(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'ipv4'), 'bfd'), False))
            yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'ipv4'), 'make_before_break')):
                pass
                yield '\nMake-before-break: '
                yield str(environment.getattr(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'ipv4'), 'make_before_break'))
                yield '\n'
            if t_6(environment.getattr(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'ipv4'), 'rp_addresses')):
                pass
                yield '\n##### IP Rendezvous Information\n\n| Rendezvous Point Address | Group Address | Access Lists | Priority | Hashmask | Override |\n| ------------------------ | ------------- | ------------ | -------- | -------- | -------- |\n'
                for l_1_rp_address in t_2(environment.getattr(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'ipv4'), 'rp_addresses'), 'address'):
                    l_1_rp_groups = l_1_access_lists = l_1_priority = l_1_hashmask = l_1_override = missing
                    _loop_vars = {}
                    pass
                    l_1_rp_groups = t_4(context.eval_ctx, t_1(environment.getattr(l_1_rp_address, 'groups'), ['-']), ', ')
                    _loop_vars['rp_groups'] = l_1_rp_groups
                    l_1_access_lists = t_4(context.eval_ctx, t_1(environment.getattr(l_1_rp_address, 'access_lists'), ['-']), ', ')
                    _loop_vars['access_lists'] = l_1_access_lists
                    l_1_priority = t_1(environment.getattr(l_1_rp_address, 'priority'), '-')
                    _loop_vars['priority'] = l_1_priority
                    l_1_hashmask = t_1(environment.getattr(l_1_rp_address, 'hashmask'), '-')
                    _loop_vars['hashmask'] = l_1_hashmask
                    l_1_override = t_1(environment.getattr(l_1_rp_address, 'override'), '-')
                    _loop_vars['override'] = l_1_override
                    yield '| '
                    yield str(environment.getattr(l_1_rp_address, 'address'))
                    yield ' | '
                    yield str((undefined(name='rp_groups') if l_1_rp_groups is missing else l_1_rp_groups))
                    yield ' | '
                    yield str((undefined(name='access_lists') if l_1_access_lists is missing else l_1_access_lists))
                    yield ' | '
                    yield str((undefined(name='priority') if l_1_priority is missing else l_1_priority))
                    yield ' | '
                    yield str((undefined(name='hashmask') if l_1_hashmask is missing else l_1_hashmask))
                    yield ' | '
                    yield str((undefined(name='override') if l_1_override is missing else l_1_override))
                    yield ' |\n'
                l_1_rp_address = l_1_rp_groups = l_1_access_lists = l_1_priority = l_1_hashmask = l_1_override = missing
            if t_6(environment.getattr(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'ipv4'), 'anycast_rps')):
                pass
                yield '\n##### IP Anycast Information\n\n| IP Anycast Address | Other Rendezvous Point Address | Register Count |\n| ------------------ | ------------------------------ | -------------- |\n'
                for l_1_anycast_rp in t_2(environment.getattr(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'ipv4'), 'anycast_rps'), 'address'):
                    _loop_vars = {}
                    pass
                    for l_2_other_anycast_rp_address in t_2(environment.getattr(l_1_anycast_rp, 'other_anycast_rp_addresses'), 'address'):
                        l_2_register_count = missing
                        _loop_vars = {}
                        pass
                        l_2_register_count = t_1(environment.getattr(l_2_other_anycast_rp_address, 'register_count'), '-')
                        _loop_vars['register_count'] = l_2_register_count
                        yield '| '
                        yield str(environment.getattr(l_1_anycast_rp, 'address'))
                        yield ' | '
                        yield str(environment.getattr(l_2_other_anycast_rp_address, 'address'))
                        yield ' | '
                        yield str((undefined(name='register_count') if l_2_register_count is missing else l_2_register_count))
                        yield ' |\n'
                    l_2_other_anycast_rp_address = l_2_register_count = missing
                l_1_anycast_rp = missing
        if t_6(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'vrfs')):
            pass
            yield '\n##### IP Sparse Mode VRFs\n\n'
            l_0_any_ipv4_ip_addresses = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), present=False)
            context.vars['any_ipv4_ip_addresses'] = l_0_any_ipv4_ip_addresses
            context.exported_vars.add('any_ipv4_ip_addresses')
            yield '| VRF Name | BFD Enabled | Make-before-break |\n| -------- | ----------- | ----------------- |\n'
            for l_1_vrf in t_2(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'vrfs'), 'name'):
                _loop_vars = {}
                pass
                if not isinstance(l_0_any_ipv4_ip_addresses, Namespace):
                    raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                l_0_any_ipv4_ip_addresses['present'] = (environment.getattr((undefined(name='any_ipv4_ip_addresses') if l_0_any_ipv4_ip_addresses is missing else l_0_any_ipv4_ip_addresses), 'present') or (t_6(environment.getattr(environment.getattr(l_1_vrf, 'ipv4'), 'rp_addresses')) and (t_5(environment.getattr(environment.getattr(l_1_vrf, 'ipv4'), 'rp_addresses')) > 0)))
                yield '| '
                yield str(environment.getattr(l_1_vrf, 'name'))
                yield ' | '
                yield str(t_1(environment.getattr(environment.getattr(l_1_vrf, 'ipv4'), 'bfd'), False))
                yield ' | '
                yield str(t_3(environment.getattr(environment.getattr(l_1_vrf, 'ipv4'), 'make_before_break'), '-'))
                yield ' |\n'
            l_1_vrf = missing
            if environment.getattr((undefined(name='any_ipv4_ip_addresses') if l_0_any_ipv4_ip_addresses is missing else l_0_any_ipv4_ip_addresses), 'present'):
                pass
                yield '\n| VRF Name | Rendezvous Point Address | Group Address | Access Lists | Priority | Hashmask | Override |\n| -------- | ------------------------ | ------------- | ------------ | -------- | -------- | -------- |\n'
                for l_1_vrf in t_2(environment.getattr((undefined(name='router_pim_sparse_mode') if l_0_router_pim_sparse_mode is missing else l_0_router_pim_sparse_mode), 'vrfs'), 'name'):
                    _loop_vars = {}
                    pass
                    if t_6(environment.getattr(environment.getattr(l_1_vrf, 'ipv4'), 'rp_addresses')):
                        pass
                        for l_2_rp_address in t_2(environment.getattr(environment.getattr(l_1_vrf, 'ipv4'), 'rp_addresses'), 'address'):
                            l_2_rp_groups = l_2_access_lists = l_2_priority = l_2_hashmask = l_2_override = missing
                            _loop_vars = {}
                            pass
                            l_2_rp_groups = t_4(context.eval_ctx, t_1(environment.getattr(l_2_rp_address, 'groups'), ['-']), ', ')
                            _loop_vars['rp_groups'] = l_2_rp_groups
                            l_2_access_lists = t_4(context.eval_ctx, t_1(environment.getattr(l_2_rp_address, 'access_lists'), ['-']), ', ')
                            _loop_vars['access_lists'] = l_2_access_lists
                            l_2_priority = t_1(environment.getattr(l_2_rp_address, 'priority'), '-')
                            _loop_vars['priority'] = l_2_priority
                            l_2_hashmask = t_1(environment.getattr(l_2_rp_address, 'hashmask'), '-')
                            _loop_vars['hashmask'] = l_2_hashmask
                            l_2_override = t_1(environment.getattr(l_2_rp_address, 'override'), '-')
                            _loop_vars['override'] = l_2_override
                            yield '| '
                            yield str(environment.getattr(l_1_vrf, 'name'))
                            yield ' | '
                            yield str(environment.getattr(l_2_rp_address, 'address'))
                            yield ' | '
                            yield str((undefined(name='rp_groups') if l_2_rp_groups is missing else l_2_rp_groups))
                            yield ' | '
                            yield str((undefined(name='access_lists') if l_2_access_lists is missing else l_2_access_lists))
                            yield ' | '
                            yield str((undefined(name='priority') if l_2_priority is missing else l_2_priority))
                            yield ' | '
                            yield str((undefined(name='hashmask') if l_2_hashmask is missing else l_2_hashmask))
                            yield ' | '
                            yield str((undefined(name='override') if l_2_override is missing else l_2_override))
                            yield ' |\n'
                        l_2_rp_address = l_2_rp_groups = l_2_access_lists = l_2_priority = l_2_hashmask = l_2_override = missing
                l_1_vrf = missing
        yield '\n##### Router Multicast Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/router-pim-sparse-mode.j2', 'documentation/router-pim-sparse-mode.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'any_ipv4_ip_addresses': l_0_any_ipv4_ip_addresses}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=50&12=53&14=56&15=58&17=61&19=63&25=66&26=70&27=72&28=74&29=76&30=78&31=81&34=94&40=97&41=100&42=104&43=107&48=115&52=118&55=122&56=127&57=129&59=136&63=139&64=142&65=144&66=148&67=150&68=152&69=154&70=156&71=159&81=176'