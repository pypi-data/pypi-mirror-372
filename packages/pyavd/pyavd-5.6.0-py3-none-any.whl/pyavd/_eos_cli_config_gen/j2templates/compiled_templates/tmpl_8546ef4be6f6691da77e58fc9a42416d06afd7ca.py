from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/aaa-accounting.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_aaa_accounting = resolve('aaa_accounting')
    l_0_methods_list = resolve('methods_list')
    l_0_namespace = resolve('namespace')
    l_0_logging_namespace = resolve('logging_namespace')
    l_0_aaa_accounting_logging = resolve('aaa_accounting_logging')
    l_0_aaa_accounting_group = resolve('aaa_accounting_group')
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    try:
        t_2 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_2(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_2((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting)):
        pass
        yield '\n### AAA Accounting\n\n#### AAA Accounting Summary\n\n| Type | Commands | Record type | Groups | Logging |\n| ---- | -------- | ----------- | ------ | ------- |\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'type')):
            pass
            if (environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'type') == 'none'):
                pass
                yield '| Exec - Console | - | none | - | - |\n'
            elif t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'methods')):
                pass
                l_0_methods_list = []
                context.vars['methods_list'] = l_0_methods_list
                context.exported_vars.add('methods_list')
                l_0_logging_namespace = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), method_logging=False)
                context.vars['logging_namespace'] = l_0_logging_namespace
                context.exported_vars.add('logging_namespace')
                for l_1_method in environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'methods'):
                    _loop_vars = {}
                    pass
                    if (t_2(environment.getattr(l_1_method, 'group')) and (environment.getattr(l_1_method, 'method') == 'group')):
                        pass
                        context.call(environment.getattr((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list), 'append'), environment.getattr(l_1_method, 'group'), _loop_vars=_loop_vars)
                    elif (environment.getattr(l_1_method, 'method') == 'logging'):
                        pass
                        if not isinstance(l_0_logging_namespace, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_0_logging_namespace['method_logging'] = True
                l_1_method = missing
                if ((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list) == []):
                    pass
                    context.call(environment.getattr((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list), 'append'), '-')
                yield '| Exec - Console | - | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'type'))
                yield ' | '
                yield str(context.call(environment.getattr(', ', 'join'), (undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list)))
                yield ' | '
                yield str(environment.getattr((undefined(name='logging_namespace') if l_0_logging_namespace is missing else l_0_logging_namespace), 'method_logging'))
                yield ' |\n'
            elif (t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'logging')) or t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'group'))):
                pass
                l_0_aaa_accounting_logging = t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'logging'), '-')
                context.vars['aaa_accounting_logging'] = l_0_aaa_accounting_logging
                context.exported_vars.add('aaa_accounting_logging')
                l_0_aaa_accounting_group = t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'group'), '-')
                context.vars['aaa_accounting_group'] = l_0_aaa_accounting_group
                context.exported_vars.add('aaa_accounting_group')
                yield '| Exec - Console | - | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'type'))
                yield ' | '
                yield str((undefined(name='aaa_accounting_group') if l_0_aaa_accounting_group is missing else l_0_aaa_accounting_group))
                yield ' | '
                yield str((undefined(name='aaa_accounting_logging') if l_0_aaa_accounting_logging is missing else l_0_aaa_accounting_logging))
                yield ' |\n'
        if t_2(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'commands'), 'console')):
            pass
            for l_1_command_console in environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'commands'), 'console'):
                l_1_methods_list = l_0_methods_list
                l_1_logging_namespace = l_0_logging_namespace
                l_1_group = resolve('group')
                l_1_logging = resolve('logging')
                _loop_vars = {}
                pass
                if (t_2(environment.getattr(l_1_command_console, 'type')) and t_2(environment.getattr(l_1_command_console, 'commands'))):
                    pass
                    if (environment.getattr(l_1_command_console, 'type') == 'none'):
                        pass
                        yield '| Commands - Console | '
                        yield str(environment.getattr(l_1_command_console, 'commands'))
                        yield ' | none | - | - |\n'
                    elif t_2(environment.getattr(l_1_command_console, 'methods')):
                        pass
                        l_1_methods_list = []
                        _loop_vars['methods_list'] = l_1_methods_list
                        l_1_logging_namespace = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), method_logging=False, _loop_vars=_loop_vars)
                        _loop_vars['logging_namespace'] = l_1_logging_namespace
                        for l_2_method in environment.getattr(l_1_command_console, 'methods'):
                            _loop_vars = {}
                            pass
                            if (t_2(environment.getattr(l_2_method, 'group')) and (environment.getattr(l_2_method, 'method') == 'group')):
                                pass
                                context.call(environment.getattr((undefined(name='methods_list') if l_1_methods_list is missing else l_1_methods_list), 'append'), environment.getattr(l_2_method, 'group'), _loop_vars=_loop_vars)
                            elif (environment.getattr(l_2_method, 'method') == 'logging'):
                                pass
                                if not isinstance(l_1_logging_namespace, Namespace):
                                    raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                                l_1_logging_namespace['method_logging'] = True
                        l_2_method = missing
                        if ((undefined(name='methods_list') if l_1_methods_list is missing else l_1_methods_list) == []):
                            pass
                            context.call(environment.getattr((undefined(name='methods_list') if l_1_methods_list is missing else l_1_methods_list), 'append'), '-', _loop_vars=_loop_vars)
                        yield '| Commands - Console | '
                        yield str(environment.getattr(l_1_command_console, 'commands'))
                        yield ' | '
                        yield str(environment.getattr(l_1_command_console, 'type'))
                        yield ' | '
                        yield str(context.call(environment.getattr(', ', 'join'), (undefined(name='methods_list') if l_1_methods_list is missing else l_1_methods_list), _loop_vars=_loop_vars))
                        yield ' | '
                        yield str(environment.getattr((undefined(name='logging_namespace') if l_1_logging_namespace is missing else l_1_logging_namespace), 'method_logging'))
                        yield ' |\n'
                    elif (t_2(environment.getattr(l_1_command_console, 'group')) or t_2(environment.getattr(l_1_command_console, 'logging'))):
                        pass
                        l_1_group = t_1(environment.getattr(l_1_command_console, 'group'), ' - ')
                        _loop_vars['group'] = l_1_group
                        l_1_logging = t_1(environment.getattr(l_1_command_console, 'logging'), 'False')
                        _loop_vars['logging'] = l_1_logging
                        yield '| Commands - Console | '
                        yield str(environment.getattr(l_1_command_console, 'commands'))
                        yield ' | '
                        yield str(environment.getattr(l_1_command_console, 'type'))
                        yield ' | '
                        yield str((undefined(name='group') if l_1_group is missing else l_1_group))
                        yield ' | '
                        yield str((undefined(name='logging') if l_1_logging is missing else l_1_logging))
                        yield ' |\n'
            l_1_command_console = l_1_methods_list = l_1_logging_namespace = l_1_group = l_1_logging = missing
        if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'type')):
            pass
            if (environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'type') == 'none'):
                pass
                yield '| Exec - Default | - | none | - | - |\n'
            elif t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'methods')):
                pass
                l_0_methods_list = []
                context.vars['methods_list'] = l_0_methods_list
                context.exported_vars.add('methods_list')
                l_0_logging_namespace = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), method_logging=False)
                context.vars['logging_namespace'] = l_0_logging_namespace
                context.exported_vars.add('logging_namespace')
                for l_1_method in environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'methods'):
                    _loop_vars = {}
                    pass
                    if (t_2(environment.getattr(l_1_method, 'group')) and (environment.getattr(l_1_method, 'method') == 'group')):
                        pass
                        context.call(environment.getattr((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list), 'append'), environment.getattr(l_1_method, 'group'), _loop_vars=_loop_vars)
                    elif (environment.getattr(l_1_method, 'method') == 'logging'):
                        pass
                        if not isinstance(l_0_logging_namespace, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_0_logging_namespace['method_logging'] = True
                l_1_method = missing
                if ((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list) == []):
                    pass
                    context.call(environment.getattr((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list), 'append'), '-')
                yield '| Exec - Default | - | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'type'))
                yield ' | '
                yield str(context.call(environment.getattr(', ', 'join'), (undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list)))
                yield ' | '
                yield str(environment.getattr((undefined(name='logging_namespace') if l_0_logging_namespace is missing else l_0_logging_namespace), 'method_logging'))
                yield ' |\n'
            elif (t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'logging')) or t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'group'))):
                pass
                l_0_aaa_accounting_logging = t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'logging'), '-')
                context.vars['aaa_accounting_logging'] = l_0_aaa_accounting_logging
                context.exported_vars.add('aaa_accounting_logging')
                l_0_aaa_accounting_group = t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'group'), '-')
                context.vars['aaa_accounting_group'] = l_0_aaa_accounting_group
                context.exported_vars.add('aaa_accounting_group')
                yield '| Exec - Default | - | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'type'))
                yield ' | '
                yield str((undefined(name='aaa_accounting_group') if l_0_aaa_accounting_group is missing else l_0_aaa_accounting_group))
                yield ' | '
                yield str((undefined(name='aaa_accounting_logging') if l_0_aaa_accounting_logging is missing else l_0_aaa_accounting_logging))
                yield ' |\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'type')):
            pass
            if (environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'type') == 'none'):
                pass
                yield '| System - Default | - | none | - | - |\n'
            elif t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'methods')):
                pass
                l_0_methods_list = []
                context.vars['methods_list'] = l_0_methods_list
                context.exported_vars.add('methods_list')
                l_0_logging_namespace = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), method_logging=False)
                context.vars['logging_namespace'] = l_0_logging_namespace
                context.exported_vars.add('logging_namespace')
                for l_1_method in environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'methods'):
                    _loop_vars = {}
                    pass
                    if (t_2(environment.getattr(l_1_method, 'group')) and (environment.getattr(l_1_method, 'method') == 'group')):
                        pass
                        context.call(environment.getattr((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list), 'append'), environment.getattr(l_1_method, 'group'), _loop_vars=_loop_vars)
                    elif (environment.getattr(l_1_method, 'method') == 'logging'):
                        pass
                        if not isinstance(l_0_logging_namespace, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_0_logging_namespace['method_logging'] = True
                l_1_method = missing
                if ((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list) == []):
                    pass
                    context.call(environment.getattr((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list), 'append'), '-')
                yield '| System - Default | - | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'type'))
                yield ' | '
                yield str(context.call(environment.getattr(', ', 'join'), (undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list)))
                yield ' | '
                yield str(environment.getattr((undefined(name='logging_namespace') if l_0_logging_namespace is missing else l_0_logging_namespace), 'method_logging'))
                yield ' |\n'
            elif t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'group')):
                pass
                yield '| System - Default | - | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'type'))
                yield ' | '
                yield str(t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'group'), '-'))
                yield ' | - |\n'
        if t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'type')):
            pass
            if (environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'type') == 'none'):
                pass
                yield '| Dot1x - Default | - | none | - | - |\n'
            elif t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'methods')):
                pass
                l_0_methods_list = []
                context.vars['methods_list'] = l_0_methods_list
                context.exported_vars.add('methods_list')
                l_0_logging_namespace = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), method_logging=False)
                context.vars['logging_namespace'] = l_0_logging_namespace
                context.exported_vars.add('logging_namespace')
                for l_1_method in environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'methods'):
                    l_1_method_group_cli = resolve('method_group_cli')
                    _loop_vars = {}
                    pass
                    if (t_2(environment.getattr(l_1_method, 'group')) and (environment.getattr(l_1_method, 'method') == 'group')):
                        pass
                        l_1_method_group_cli = environment.getattr(l_1_method, 'group')
                        _loop_vars['method_group_cli'] = l_1_method_group_cli
                        if t_2(environment.getattr(l_1_method, 'multicast')):
                            pass
                            l_1_method_group_cli = str_join(((undefined(name='method_group_cli') if l_1_method_group_cli is missing else l_1_method_group_cli), '(multicast)', ))
                            _loop_vars['method_group_cli'] = l_1_method_group_cli
                        context.call(environment.getattr((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list), 'append'), (undefined(name='method_group_cli') if l_1_method_group_cli is missing else l_1_method_group_cli), _loop_vars=_loop_vars)
                    elif (environment.getattr(l_1_method, 'method') == 'logging'):
                        pass
                        if not isinstance(l_0_logging_namespace, Namespace):
                            raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                        l_0_logging_namespace['method_logging'] = True
                l_1_method = l_1_method_group_cli = missing
                if ((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list) == []):
                    pass
                    context.call(environment.getattr((undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list), 'append'), '-')
                yield '| Dot1x - Default | - | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'type'))
                yield ' | '
                yield str(context.call(environment.getattr(', ', 'join'), (undefined(name='methods_list') if l_0_methods_list is missing else l_0_methods_list)))
                yield ' | '
                yield str(environment.getattr((undefined(name='logging_namespace') if l_0_logging_namespace is missing else l_0_logging_namespace), 'method_logging'))
                yield ' |\n'
            elif t_2(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'group')):
                pass
                yield '| Dot1x - Default | - | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'type'))
                yield ' | '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'group'))
                yield ' | - |\n'
        if t_2(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'commands'), 'default')):
            pass
            for l_1_command_default in environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'commands'), 'default'):
                l_1_methods_list = l_0_methods_list
                l_1_logging_namespace = l_0_logging_namespace
                _loop_vars = {}
                pass
                if t_2(environment.getattr(l_1_command_default, 'type'), 'none'):
                    pass
                    yield '| Commands - Default | '
                    yield str(environment.getattr(l_1_command_default, 'commands'))
                    yield ' | none | - | - |\n'
                elif (t_2(environment.getattr(l_1_command_default, 'type')) and t_2(environment.getattr(l_1_command_default, 'methods'))):
                    pass
                    l_1_methods_list = []
                    _loop_vars['methods_list'] = l_1_methods_list
                    l_1_logging_namespace = context.call((undefined(name='namespace') if l_0_namespace is missing else l_0_namespace), method_logging=False, _loop_vars=_loop_vars)
                    _loop_vars['logging_namespace'] = l_1_logging_namespace
                    for l_2_method in environment.getattr(l_1_command_default, 'methods'):
                        _loop_vars = {}
                        pass
                        if (t_2(environment.getattr(l_2_method, 'group')) and (environment.getattr(l_2_method, 'method') == 'group')):
                            pass
                            context.call(environment.getattr((undefined(name='methods_list') if l_1_methods_list is missing else l_1_methods_list), 'append'), environment.getattr(l_2_method, 'group'), _loop_vars=_loop_vars)
                        elif (environment.getattr(l_2_method, 'method') == 'logging'):
                            pass
                            if not isinstance(l_1_logging_namespace, Namespace):
                                raise TemplateRuntimeError("cannot assign attribute on non-namespace object")
                            l_1_logging_namespace['method_logging'] = True
                    l_2_method = missing
                    if ((undefined(name='methods_list') if l_1_methods_list is missing else l_1_methods_list) == []):
                        pass
                        context.call(environment.getattr((undefined(name='methods_list') if l_1_methods_list is missing else l_1_methods_list), 'append'), '-', _loop_vars=_loop_vars)
                    yield '| Commands - Default | '
                    yield str(environment.getattr(l_1_command_default, 'commands'))
                    yield ' | '
                    yield str(environment.getattr(l_1_command_default, 'type'))
                    yield ' | '
                    yield str(context.call(environment.getattr(', ', 'join'), (undefined(name='methods_list') if l_1_methods_list is missing else l_1_methods_list), _loop_vars=_loop_vars))
                    yield ' | '
                    yield str(environment.getattr((undefined(name='logging_namespace') if l_1_logging_namespace is missing else l_1_logging_namespace), 'method_logging'))
                    yield ' |\n'
                elif (t_2(environment.getattr(l_1_command_default, 'type')) and (t_2(environment.getattr(l_1_command_default, 'logging')) or t_2(environment.getattr(l_1_command_default, 'group')))):
                    pass
                    yield '| Commands - Default | '
                    yield str(environment.getattr(l_1_command_default, 'commands'))
                    yield ' | '
                    yield str(environment.getattr(l_1_command_default, 'type'))
                    yield ' | '
                    yield str(t_1(environment.getattr(l_1_command_default, 'group'), '-'))
                    yield ' | '
                    yield str(t_1(environment.getattr(l_1_command_default, 'logging'), '-'))
                    yield ' |\n'
            l_1_command_default = l_1_methods_list = l_1_logging_namespace = missing
        yield '\n#### AAA Accounting Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/aaa-accounting.j2', 'documentation/aaa-accounting.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {'aaa_accounting_group': l_0_aaa_accounting_group, 'aaa_accounting_logging': l_0_aaa_accounting_logging, 'logging_namespace': l_0_logging_namespace, 'methods_list': l_0_methods_list}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=29&15=32&16=34&18=37&19=39&20=42&21=45&22=48&23=50&24=51&25=55&28=57&29=59&31=61&32=67&33=69&34=72&35=76&38=82&39=84&40=91&41=93&42=96&43=98&44=100&45=102&46=104&47=107&48=109&49=110&50=114&53=116&54=118&56=120&57=128&58=130&59=132&60=135&65=144&66=146&68=149&69=151&70=154&71=157&72=160&73=162&74=163&75=167&78=169&79=171&81=173&82=179&83=181&84=184&85=188&88=194&89=196&91=199&92=201&93=204&94=207&95=210&96=212&97=213&98=217&101=219&102=221&104=223&105=229&106=232&109=236&110=238&112=241&113=243&114=246&115=249&116=253&117=255&118=257&119=259&121=261&122=262&123=266&126=268&127=270&129=272&130=278&131=281&134=285&135=287&136=292&137=295&138=297&139=299&140=301&141=303&142=306&143=308&144=309&145=313&148=315&149=317&151=319&152=327&153=330&161=340'