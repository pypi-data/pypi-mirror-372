from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/management-ssh.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_management_ssh = resolve('management_ssh')
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
        t_4 = environment.filters['selectattr']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'selectattr' found.")
    try:
        t_5 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_5((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh)):
        pass
        yield '!\nmanagement ssh\n'
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'access_groups')):
            pass
            for l_1_access_group in t_2(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'access_groups')):
                l_1_acl_cli = missing
                _loop_vars = {}
                pass
                l_1_acl_cli = str_join(('ip access-group ', environment.getattr(l_1_access_group, 'name'), ))
                _loop_vars['acl_cli'] = l_1_acl_cli
                if t_5(environment.getattr(l_1_access_group, 'vrf')):
                    pass
                    l_1_acl_cli = str_join(((undefined(name='acl_cli') if l_1_acl_cli is missing else l_1_acl_cli), ' vrf ', environment.getattr(l_1_access_group, 'vrf'), ))
                    _loop_vars['acl_cli'] = l_1_acl_cli
                l_1_acl_cli = str_join(((undefined(name='acl_cli') if l_1_acl_cli is missing else l_1_acl_cli), ' in', ))
                _loop_vars['acl_cli'] = l_1_acl_cli
                yield '   '
                yield str((undefined(name='acl_cli') if l_1_acl_cli is missing else l_1_acl_cli))
                yield '\n'
            l_1_access_group = l_1_acl_cli = missing
        for l_1_vrf in t_4(context, t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'vrfs'), []), 'ip_access_group_in', 'arista.avd.defined'):
            _loop_vars = {}
            pass
            yield '   ip access-group '
            yield str(environment.getattr(l_1_vrf, 'ip_access_group_in'))
            yield ' vrf '
            yield str(environment.getattr(l_1_vrf, 'name'))
            yield ' in\n'
        l_1_vrf = missing
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'ip_access_group_in')):
            pass
            yield '   ip access-group '
            yield str(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'ip_access_group_in'))
            yield ' in\n'
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'ipv6_access_groups')):
            pass
            for l_1_ipv6_access_group in t_2(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'ipv6_access_groups')):
                l_1_ipv6_acl_cli = missing
                _loop_vars = {}
                pass
                l_1_ipv6_acl_cli = str_join(('ipv6 access-group ', environment.getattr(l_1_ipv6_access_group, 'name'), ))
                _loop_vars['ipv6_acl_cli'] = l_1_ipv6_acl_cli
                if t_5(environment.getattr(l_1_ipv6_access_group, 'vrf')):
                    pass
                    l_1_ipv6_acl_cli = str_join(((undefined(name='ipv6_acl_cli') if l_1_ipv6_acl_cli is missing else l_1_ipv6_acl_cli), ' vrf ', environment.getattr(l_1_ipv6_access_group, 'vrf'), ))
                    _loop_vars['ipv6_acl_cli'] = l_1_ipv6_acl_cli
                l_1_ipv6_acl_cli = str_join(((undefined(name='ipv6_acl_cli') if l_1_ipv6_acl_cli is missing else l_1_ipv6_acl_cli), ' in', ))
                _loop_vars['ipv6_acl_cli'] = l_1_ipv6_acl_cli
                yield '   '
                yield str((undefined(name='ipv6_acl_cli') if l_1_ipv6_acl_cli is missing else l_1_ipv6_acl_cli))
                yield '\n'
            l_1_ipv6_access_group = l_1_ipv6_acl_cli = missing
        for l_1_vrf in t_4(context, t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'vrfs'), []), 'ipv6_access_group_in', 'arista.avd.defined'):
            _loop_vars = {}
            pass
            yield '   ipv6 access-group '
            yield str(environment.getattr(l_1_vrf, 'ipv6_access_group_in'))
            yield ' vrf '
            yield str(environment.getattr(l_1_vrf, 'name'))
            yield ' in\n'
        l_1_vrf = missing
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'ipv6_access_group_in')):
            pass
            yield '   ipv6 access-group '
            yield str(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'ipv6_access_group_in'))
            yield ' in\n'
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'idle_timeout')):
            pass
            yield '   idle-timeout '
            yield str(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'idle_timeout'))
            yield '\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'authentication'), 'protocols')):
            pass
            yield '   authentication protocol '
            yield str(t_3(context.eval_ctx, environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'authentication'), 'protocols'), ' '))
            yield '\n'
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'cipher')):
            pass
            yield '   cipher '
            yield str(t_3(context.eval_ctx, environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'cipher'), ' '))
            yield '\n'
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'key_exchange')):
            pass
            yield '   key-exchange '
            yield str(t_3(context.eval_ctx, environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'key_exchange'), ' '))
            yield '\n'
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'mac')):
            pass
            yield '   mac '
            yield str(t_3(context.eval_ctx, environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'mac'), ' '))
            yield '\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'hostkey'), 'server')):
            pass
            yield '   hostkey server '
            yield str(t_3(context.eval_ctx, environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'hostkey'), 'server'), ' '))
            yield '\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'connection'), 'per_host')):
            pass
            yield '   connection per-host '
            yield str(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'connection'), 'per_host'))
            yield '\n'
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'fips_restrictions'), True):
            pass
            yield '   fips restrictions\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'hostkey'), 'client_strict_checking'), True):
            pass
            yield '   hostkey client strict-checking\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'connection'), 'limit')):
            pass
            yield '   connection limit '
            yield str(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'connection'), 'limit'))
            yield '\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'authentication'), 'empty_passwords')):
            pass
            yield '   authentication empty-passwords '
            yield str(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'authentication'), 'empty_passwords'))
            yield '\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'client_alive'), 'interval')):
            pass
            yield '   client-alive interval '
            yield str(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'client_alive'), 'interval'))
            yield '\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'client_alive'), 'count_max')):
            pass
            yield '   client-alive count-max '
            yield str(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'client_alive'), 'count_max'))
            yield '\n'
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'enable'), False):
            pass
            yield '   shutdown\n'
        elif t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'enable'), True):
            pass
            yield '   no shutdown\n'
        if t_5(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'log_level')):
            pass
            yield '   log-level '
            yield str(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'log_level'))
            yield '\n'
        if t_5(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'hostkey'), 'server_cert')):
            pass
            yield '   hostkey server cert '
            yield str(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'hostkey'), 'server_cert'))
            yield '\n'
        for l_1_vrf in t_2(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'vrfs'), 'name'):
            _loop_vars = {}
            pass
            yield '   !\n   vrf '
            yield str(environment.getattr(l_1_vrf, 'name'))
            yield '\n'
            if t_5(environment.getattr(l_1_vrf, 'enable'), True):
                pass
                yield '      no shutdown\n'
            elif t_5(environment.getattr(l_1_vrf, 'enable'), False):
                pass
                yield '      shutdown\n'
        l_1_vrf = missing

blocks = {}
debug_info = '7=42&10=45&11=47&12=51&13=53&14=55&16=57&17=60&20=63&21=67&23=72&24=75&26=77&27=79&28=83&29=85&30=87&32=89&33=92&36=95&37=99&39=104&40=107&42=109&43=112&45=114&46=117&48=119&49=122&51=124&52=127&54=129&55=132&57=134&58=137&60=139&61=142&63=144&66=147&69=150&70=153&72=155&73=158&75=160&76=163&78=165&79=168&81=170&83=173&86=176&87=179&89=181&90=184&92=186&94=190&95=192&97=195'