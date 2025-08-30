from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ntp.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ntp = resolve('ntp')
    l_0_ntp_int_cli = resolve('ntp_int_cli')
    try:
        t_1 = environment.filters['arista.avd.hide_passwords']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.hide_passwords' found.")
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
    if t_3((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp)):
        pass
        yield '!\n'
        for l_1_authentication_key in t_2(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'authentication_keys'), 'id'):
            l_1_hide_passwords = resolve('hide_passwords')
            l_1_ntp_auth_key_cli = missing
            _loop_vars = {}
            pass
            l_1_ntp_auth_key_cli = str_join(('ntp authentication-key ', environment.getattr(l_1_authentication_key, 'id'), ' ', environment.getattr(l_1_authentication_key, 'hash_algorithm'), ))
            _loop_vars['ntp_auth_key_cli'] = l_1_ntp_auth_key_cli
            if t_3(environment.getattr(l_1_authentication_key, 'key_type')):
                pass
                l_1_ntp_auth_key_cli = str_join(((undefined(name='ntp_auth_key_cli') if l_1_ntp_auth_key_cli is missing else l_1_ntp_auth_key_cli), ' ', environment.getattr(l_1_authentication_key, 'key_type'), ))
                _loop_vars['ntp_auth_key_cli'] = l_1_ntp_auth_key_cli
            l_1_ntp_auth_key_cli = str_join(((undefined(name='ntp_auth_key_cli') if l_1_ntp_auth_key_cli is missing else l_1_ntp_auth_key_cli), ' ', t_1(environment.getattr(l_1_authentication_key, 'key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)), ))
            _loop_vars['ntp_auth_key_cli'] = l_1_ntp_auth_key_cli
            yield str((undefined(name='ntp_auth_key_cli') if l_1_ntp_auth_key_cli is missing else l_1_ntp_auth_key_cli))
            yield '\n'
        l_1_authentication_key = l_1_ntp_auth_key_cli = l_1_hide_passwords = missing
        if t_3(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'trusted_keys')):
            pass
            yield 'ntp trusted-key '
            yield str(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'trusted_keys'))
            yield '\n'
        if t_3(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'authenticate_servers_only'), True):
            pass
            yield 'ntp authenticate servers\n'
        elif t_3(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'authenticate'), True):
            pass
            yield 'ntp authenticate\n'
        if t_3(environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'local_interface'), 'name')):
            pass
            l_0_ntp_int_cli = 'ntp local-interface'
            context.vars['ntp_int_cli'] = l_0_ntp_int_cli
            context.exported_vars.add('ntp_int_cli')
            if (t_3(environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'local_interface'), 'vrf')) and (environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'local_interface'), 'vrf') != 'default')):
                pass
                l_0_ntp_int_cli = str_join(((undefined(name='ntp_int_cli') if l_0_ntp_int_cli is missing else l_0_ntp_int_cli), ' vrf ', environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'local_interface'), 'vrf'), ))
                context.vars['ntp_int_cli'] = l_0_ntp_int_cli
                context.exported_vars.add('ntp_int_cli')
            l_0_ntp_int_cli = str_join(((undefined(name='ntp_int_cli') if l_0_ntp_int_cli is missing else l_0_ntp_int_cli), ' ', environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'local_interface'), 'name'), ))
            context.vars['ntp_int_cli'] = l_0_ntp_int_cli
            context.exported_vars.add('ntp_int_cli')
            yield str((undefined(name='ntp_int_cli') if l_0_ntp_int_cli is missing else l_0_ntp_int_cli))
            yield '\n'
        for l_1_server in t_2(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'servers'), 'name'):
            l_1_hide_passwords = resolve('hide_passwords')
            l_1_ntp_server_cli = missing
            _loop_vars = {}
            pass
            l_1_ntp_server_cli = 'ntp server'
            _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            if (t_3(environment.getattr(l_1_server, 'vrf')) and (environment.getattr(l_1_server, 'vrf') != 'default')):
                pass
                l_1_ntp_server_cli = str_join(((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli), ' vrf ', environment.getattr(l_1_server, 'vrf'), ))
                _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            l_1_ntp_server_cli = str_join(((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli), ' ', environment.getattr(l_1_server, 'name'), ))
            _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            if t_3(environment.getattr(l_1_server, 'preferred'), True):
                pass
                l_1_ntp_server_cli = str_join(((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli), ' prefer', ))
                _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            if t_3(environment.getattr(l_1_server, 'burst'), True):
                pass
                l_1_ntp_server_cli = str_join(((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli), ' burst', ))
                _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            if t_3(environment.getattr(l_1_server, 'iburst'), True):
                pass
                l_1_ntp_server_cli = str_join(((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli), ' iburst', ))
                _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            if t_3(environment.getattr(l_1_server, 'version')):
                pass
                l_1_ntp_server_cli = str_join(((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli), ' version ', environment.getattr(l_1_server, 'version'), ))
                _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            if t_3(environment.getattr(l_1_server, 'minpoll')):
                pass
                l_1_ntp_server_cli = str_join(((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli), ' minpoll ', environment.getattr(l_1_server, 'minpoll'), ))
                _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            if t_3(environment.getattr(l_1_server, 'maxpoll')):
                pass
                l_1_ntp_server_cli = str_join(((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli), ' maxpoll ', environment.getattr(l_1_server, 'maxpoll'), ))
                _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            if t_3(environment.getattr(l_1_server, 'local_interface')):
                pass
                l_1_ntp_server_cli = str_join(((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli), ' local-interface ', environment.getattr(l_1_server, 'local_interface'), ))
                _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            if t_3(environment.getattr(l_1_server, 'key')):
                pass
                l_1_ntp_server_cli = str_join(((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli), ' key ', t_1(environment.getattr(l_1_server, 'key'), (undefined(name='hide_passwords') if l_1_hide_passwords is missing else l_1_hide_passwords)), ))
                _loop_vars['ntp_server_cli'] = l_1_ntp_server_cli
            yield str((undefined(name='ntp_server_cli') if l_1_ntp_server_cli is missing else l_1_ntp_server_cli))
            yield '\n'
        l_1_server = l_1_ntp_server_cli = l_1_hide_passwords = missing
        if t_3(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'serve')):
            pass
            if t_3(environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'serve'), 'serve_all'), True):
                pass
                yield 'ntp serve all\n'
            for l_1_vrf in t_2(environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'serve'), 'vrfs'), sort_key='name', ignore_case=False):
                _loop_vars = {}
                pass
                if t_3(environment.getattr(l_1_vrf, 'serve_all'), True):
                    pass
                    yield 'ntp serve all vrf '
                    yield str(environment.getattr(l_1_vrf, 'name'))
                    yield '\n'
            l_1_vrf = missing
            for l_1_vrf in t_2(environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'serve'), 'vrfs'), sort_key='name', ignore_case=False):
                _loop_vars = {}
                pass
                if t_3(environment.getattr(l_1_vrf, 'access_group')):
                    pass
                    yield 'ntp serve ip access-group '
                    yield str(environment.getattr(l_1_vrf, 'access_group'))
                    yield ' vrf '
                    yield str(environment.getattr(l_1_vrf, 'name'))
                    yield ' in\n'
            l_1_vrf = missing
            if t_3(environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'serve'), 'access_group')):
                pass
                yield 'ntp serve ip access-group '
                yield str(environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'serve'), 'access_group'))
                yield ' in\n'
            for l_1_vrf in t_2(environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'serve'), 'vrfs'), sort_key='name', ignore_case=False):
                _loop_vars = {}
                pass
                if t_3(environment.getattr(l_1_vrf, 'ipv6_access_group')):
                    pass
                    yield 'ntp serve ipv6 access-group '
                    yield str(environment.getattr(l_1_vrf, 'ipv6_access_group'))
                    yield ' vrf '
                    yield str(environment.getattr(l_1_vrf, 'name'))
                    yield ' in\n'
            l_1_vrf = missing
            if t_3(environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'serve'), 'ipv6_access_group')):
                pass
                yield 'ntp serve ipv6 access-group '
                yield str(environment.getattr(environment.getattr((undefined(name='ntp') if l_0_ntp is missing else l_0_ntp), 'serve'), 'ipv6_access_group'))
                yield ' in\n'

blocks = {}
debug_info = '7=31&9=34&10=39&11=41&12=43&14=45&15=47&17=50&18=53&20=55&22=58&25=61&26=63&27=66&28=68&30=71&31=74&33=76&34=81&35=83&36=85&38=87&39=89&40=91&42=93&43=95&45=97&46=99&48=101&49=103&51=105&52=107&54=109&55=111&57=113&58=115&60=117&61=119&63=121&65=124&66=126&69=129&70=132&71=135&74=138&75=141&76=144&79=149&80=152&82=154&83=157&84=160&87=165&88=168'