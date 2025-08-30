from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/ip-name-server-groups.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_name_server_groups = resolve('ip_name_server_groups')
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
    for l_1_name_server_group in t_1((undefined(name='ip_name_server_groups') if l_0_ip_name_server_groups is missing else l_0_ip_name_server_groups), 'name'):
        _loop_vars = {}
        pass
        yield '!\nip name-server group '
        yield str(environment.getattr(l_1_name_server_group, 'name'))
        yield '\n'
        for l_2_server in t_1(t_1(t_1(environment.getattr(l_1_name_server_group, 'name_servers'), 'ip_address'), 'vrf'), 'priority', default_value='0'):
            l_2_name_server_cli = missing
            _loop_vars = {}
            pass
            l_2_name_server_cli = str_join(('name-server vrf ', environment.getattr(l_2_server, 'vrf'), ' ', environment.getattr(l_2_server, 'ip_address'), ))
            _loop_vars['name_server_cli'] = l_2_name_server_cli
            if t_2(environment.getattr(l_2_server, 'priority')):
                pass
                l_2_name_server_cli = str_join(((undefined(name='name_server_cli') if l_2_name_server_cli is missing else l_2_name_server_cli), ' priority ', environment.getattr(l_2_server, 'priority'), ))
                _loop_vars['name_server_cli'] = l_2_name_server_cli
            yield '   '
            yield str((undefined(name='name_server_cli') if l_2_name_server_cli is missing else l_2_name_server_cli))
            yield '\n'
        l_2_server = l_2_name_server_cli = missing
        if t_2(environment.getattr(l_1_name_server_group, 'dns_domain')):
            pass
            yield '   dns domain '
            yield str(environment.getattr(l_1_name_server_group, 'dns_domain'))
            yield '\n'
        for l_2_domain in t_1(environment.getattr(l_1_name_server_group, 'ip_domain_lists')):
            _loop_vars = {}
            pass
            yield '   ip domain-list '
            yield str(l_2_domain)
            yield '\n'
        l_2_domain = missing
        if t_2(environment.getattr(l_1_name_server_group, 'ip_domain_list')):
            pass
            yield '   ip domain-list '
            yield str(environment.getattr(l_1_name_server_group, 'ip_domain_list'))
            yield '\n'
    l_1_name_server_group = missing

blocks = {}
debug_info = '6=24&8=28&9=30&10=34&11=36&12=38&14=41&16=44&17=47&19=49&20=53&22=56&23=59'