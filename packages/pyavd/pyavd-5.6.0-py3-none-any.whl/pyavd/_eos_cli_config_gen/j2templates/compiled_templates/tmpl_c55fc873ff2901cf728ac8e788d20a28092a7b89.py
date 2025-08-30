from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/management-ssh.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_management_ssh = resolve('management_ssh')
    l_0_namespace = resolve('namespace')
    l_0__vrf_default = resolve('_vrf_default')
    l_0__ipv4_acl = resolve('_ipv4_acl')
    l_0__ipv6_acl = resolve('_ipv6_acl')
    l_0_protocols = resolve('protocols')
    l_0_empty_passwords = resolve('empty_passwords')
    l_0__idle_timeout = resolve('_idle_timeout')
    l_0__conn_limit = resolve('_conn_limit')
    l_0__per_host = resolve('_per_host')
    l_0__ciphers = resolve('_ciphers')
    l_0__key_ex = resolve('_key_ex')
    l_0__mac = resolve('_mac')
    l_0__hostkey = resolve('_hostkey')
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
        t_4 = environment.filters['last']
    except KeyError:
        @internalcode
        def t_4(*unused):
            raise TemplateRuntimeError("No filter named 'last' found.")
    try:
        t_5 = environment.filters['list']
    except KeyError:
        @internalcode
        def t_5(*unused):
            raise TemplateRuntimeError("No filter named 'list' found.")
    try:
        t_6 = environment.filters['rejectattr']
    except KeyError:
        @internalcode
        def t_6(*unused):
            raise TemplateRuntimeError("No filter named 'rejectattr' found.")
    try:
        t_7 = environment.filters['selectattr']
    except KeyError:
        @internalcode
        def t_7(*unused):
            raise TemplateRuntimeError("No filter named 'selectattr' found.")
    try:
        t_8 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_8(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_8((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh)):
        pass
        yield '\n### Management SSH\n\n#### VRFs\n\n| VRF | Enabled | IPv4 ACL | IPv6 ACL |\n| --- | ------- | -------- | -------- |\n'
        l_0__vrf_default = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), enable=t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'enable')))
        context.vars['_vrf_default'] = l_0__vrf_default
        if t_8(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'vrfs')):
            pass
            for l_1_vrf in t_2(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'vrfs')):
                l_1__ipv4_acl = l_0__ipv4_acl
                l_1__ipv6_acl = l_0__ipv6_acl
                _loop_vars = {}
                pass
                if (environment.getattr(l_1_vrf, 'name') == 'default'):
                    pass
                    if not isinstance(l_0__vrf_default, Namespace):
                        raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                    l_0__vrf_default['enable'] = t_1(environment.getattr(l_1_vrf, 'enable'), environment.getattr((undefined(name='_vrf_default') if l_0__vrf_default is missing else l_0__vrf_default), 'enable'))
                else:
                    pass
                    if (t_8(environment.getattr(l_1_vrf, 'enable')) and (not t_8(environment.getattr((undefined(name='_vrf_default') if l_0__vrf_default is missing else l_0__vrf_default), 'enable')))):
                        pass
                        if not isinstance(l_0__vrf_default, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_0__vrf_default['enable'] = False
                    l_1__ipv4_acl = t_4(environment, t_5(context.eval_ctx, t_7(context, t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'access_groups'), []), 'vrf', 'arista.avd.defined')))
                    _loop_vars['_ipv4_acl'] = l_1__ipv4_acl
                    l_1__ipv6_acl = t_4(environment, t_5(context.eval_ctx, t_7(context, t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'ipv6_access_groups'), []), 'vrf', 'arista.avd.defined')))
                    _loop_vars['_ipv6_acl'] = l_1__ipv6_acl
                    yield '| '
                    yield str(environment.getattr(l_1_vrf, 'name'))
                    yield ' | '
                    yield str(t_1(environment.getattr(l_1_vrf, 'enable'), '-'))
                    yield ' | '
                    yield str(t_1(environment.getattr(l_1_vrf, 'ip_access_group_in'), environment.getattr((undefined(name='_ipv4_acl') if l_1__ipv4_acl is missing else l_1__ipv4_acl), 'name'), '-'))
                    yield ' | '
                    yield str(t_1(environment.getattr(l_1_vrf, 'ipv6_access_group_in'), environment.getattr((undefined(name='_ipv6_acl') if l_1__ipv6_acl is missing else l_1__ipv6_acl), 'name'), '-'))
                    yield ' |\n'
            l_1_vrf = l_1__ipv4_acl = l_1__ipv6_acl = missing
        l_0__ipv4_acl = t_4(environment, t_5(context.eval_ctx, t_6(context, t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'access_groups'), []), 'vrf', 'arista.avd.defined')))
        context.vars['_ipv4_acl'] = l_0__ipv4_acl
        l_0__ipv6_acl = t_4(environment, t_5(context.eval_ctx, t_6(context, t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'ipv6_access_groups'), []), 'vrf', 'arista.avd.defined')))
        context.vars['_ipv6_acl'] = l_0__ipv6_acl
        yield '| default | '
        yield str(t_1(environment.getattr((undefined(name='_vrf_default') if l_0__vrf_default is missing else l_0__vrf_default), 'enable'), True))
        yield ' | '
        yield str(t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'ip_access_group_in'), environment.getattr((undefined(name='_ipv4_acl') if l_0__ipv4_acl is missing else l_0__ipv4_acl), 'name'), '-'))
        yield ' | '
        yield str(t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'ipv6_access_group_in'), environment.getattr((undefined(name='_ipv6_acl') if l_0__ipv6_acl is missing else l_0__ipv6_acl), 'name'), '-'))
        yield ' |\n'
        if t_8(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'authentication')):
            pass
            yield '\n#### Authentication Settings\n\n| Authentication protocols | Empty passwords |\n| ------------------------ | --------------- |\n'
            if t_8(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'authentication'), 'protocols')):
                pass
                l_0_protocols = t_3(context.eval_ctx, environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'authentication'), 'protocols'), ', ')
                context.vars['protocols'] = l_0_protocols
                context.exported_vars.add('protocols')
            else:
                pass
                l_0_protocols = 'keyboard-interactive, public-key'
                context.vars['protocols'] = l_0_protocols
                context.exported_vars.add('protocols')
            l_0_empty_passwords = t_1(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'authentication'), 'empty_passwords'), 'auto')
            context.vars['empty_passwords'] = l_0_empty_passwords
            context.exported_vars.add('empty_passwords')
            yield '| '
            yield str((undefined(name='protocols') if l_0_protocols is missing else l_0_protocols))
            yield ' | '
            yield str((undefined(name='empty_passwords') if l_0_empty_passwords is missing else l_0_empty_passwords))
            yield ' |\n'
        yield '\n#### Other SSH Settings\n\n| Idle Timeout | Connection Limit | Max from a single Host | Ciphers | Key-exchange methods | MAC algorithms | Hostkey server algorithms |\n| ------------ | ---------------- | ---------------------- | ------- | -------------------- | -------------- | ------------------------- |\n'
        l_0__idle_timeout = t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'idle_timeout'), 'default')
        context.vars['_idle_timeout'] = l_0__idle_timeout
        l_0__conn_limit = t_1(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'connection'), 'limit'), '-')
        context.vars['_conn_limit'] = l_0__conn_limit
        l_0__per_host = t_1(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'connection'), 'per_host'), '-')
        context.vars['_per_host'] = l_0__per_host
        l_0__ciphers = t_3(context.eval_ctx, t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'cipher'), ['default']), ', ')
        context.vars['_ciphers'] = l_0__ciphers
        l_0__key_ex = t_3(context.eval_ctx, t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'key_exchange'), ['default']), ', ')
        context.vars['_key_ex'] = l_0__key_ex
        l_0__mac = t_3(context.eval_ctx, t_1(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'mac'), ['default']), ', ')
        context.vars['_mac'] = l_0__mac
        l_0__hostkey = t_3(context.eval_ctx, t_1(environment.getattr(environment.getattr((undefined(name='management_ssh') if l_0_management_ssh is missing else l_0_management_ssh), 'hostkey'), 'server'), ['default']), ', ')
        context.vars['_hostkey'] = l_0__hostkey
        yield '| '
        yield str((undefined(name='_idle_timeout') if l_0__idle_timeout is missing else l_0__idle_timeout))
        yield ' | '
        yield str((undefined(name='_conn_limit') if l_0__conn_limit is missing else l_0__conn_limit))
        yield ' | '
        yield str((undefined(name='_per_host') if l_0__per_host is missing else l_0__per_host))
        yield ' | '
        yield str((undefined(name='_ciphers') if l_0__ciphers is missing else l_0__ciphers))
        yield ' | '
        yield str((undefined(name='_key_ex') if l_0__key_ex is missing else l_0__key_ex))
        yield ' | '
        yield str((undefined(name='_mac') if l_0__mac is missing else l_0__mac))
        yield ' | '
        yield str((undefined(name='_hostkey') if l_0__hostkey is missing else l_0__hostkey))
        yield ' |\n\n#### Management SSH Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/management-ssh.j2', 'documentation/management-ssh.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'_ciphers': l_0__ciphers, '_conn_limit': l_0__conn_limit, '_hostkey': l_0__hostkey, '_idle_timeout': l_0__idle_timeout, '_ipv4_acl': l_0__ipv4_acl, '_ipv6_acl': l_0__ipv6_acl, '_key_ex': l_0__key_ex, '_mac': l_0__mac, '_per_host': l_0__per_host, '_vrf_default': l_0__vrf_default, 'empty_passwords': l_0_empty_passwords, 'protocols': l_0_protocols}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=73&15=76&16=78&17=80&18=85&19=89&21=92&22=96&24=97&25=99&26=102&30=111&31=113&32=116&33=122&39=125&40=127&42=132&44=135&45=139&52=144&53=146&54=148&55=150&56=152&57=154&58=156&59=159&64=173'