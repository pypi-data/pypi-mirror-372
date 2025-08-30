from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos/aaa-accounting.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_aaa_accounting = resolve('aaa_accounting')
    l_0_exec_console_list = resolve('exec_console_list')
    l_0_exec_console_cli = resolve('exec_console_cli')
    l_0_exec_default_list = resolve('exec_default_list')
    l_0_exec_default_cli = resolve('exec_default_cli')
    l_0_system_default_list = resolve('system_default_list')
    l_0_system_default_cli = resolve('system_default_cli')
    l_0_dot1x_default_list = resolve('dot1x_default_list')
    l_0_dot1x_default_cli = resolve('dot1x_default_cli')
    try:
        t_1 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if t_1((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting)):
        pass
        if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'type'), 'none'):
            pass
            yield 'aaa accounting exec console none\n'
        elif (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'type')) and t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'methods'))):
            pass
            l_0_exec_console_list = []
            context.vars['exec_console_list'] = l_0_exec_console_list
            context.exported_vars.add('exec_console_list')
            for l_1_method in environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'methods'):
                l_1_group_cli = resolve('group_cli')
                _loop_vars = {}
                pass
                if (environment.getattr(l_1_method, 'method') == 'logging'):
                    pass
                    context.call(environment.getattr((undefined(name='exec_console_list') if l_0_exec_console_list is missing else l_0_exec_console_list), 'append'), environment.getattr(l_1_method, 'method'), _loop_vars=_loop_vars)
                elif ((environment.getattr(l_1_method, 'method') == 'group') and t_1(environment.getattr(l_1_method, 'group'))):
                    pass
                    l_1_group_cli = str_join(('group ', environment.getattr(l_1_method, 'group'), ))
                    _loop_vars['group_cli'] = l_1_group_cli
                    context.call(environment.getattr((undefined(name='exec_console_list') if l_0_exec_console_list is missing else l_0_exec_console_list), 'append'), (undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli), _loop_vars=_loop_vars)
            l_1_method = l_1_group_cli = missing
            l_0_exec_console_cli = context.call(environment.getattr(' ', 'join'), (undefined(name='exec_console_list') if l_0_exec_console_list is missing else l_0_exec_console_list))
            context.vars['exec_console_cli'] = l_0_exec_console_cli
            context.exported_vars.add('exec_console_cli')
            if (undefined(name='exec_console_cli') if l_0_exec_console_cli is missing else l_0_exec_console_cli):
                pass
                yield 'aaa accounting exec console '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'type'))
                yield ' '
                yield str((undefined(name='exec_console_cli') if l_0_exec_console_cli is missing else l_0_exec_console_cli))
                yield '\n'
        elif (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'type')) and (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'group')) or t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'logging'), True))):
            pass
            l_0_exec_console_cli = str_join(('aaa accounting exec console ', environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'type'), ))
            context.vars['exec_console_cli'] = l_0_exec_console_cli
            context.exported_vars.add('exec_console_cli')
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'group')):
                pass
                l_0_exec_console_cli = str_join(((undefined(name='exec_console_cli') if l_0_exec_console_cli is missing else l_0_exec_console_cli), ' group ', environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'group'), ))
                context.vars['exec_console_cli'] = l_0_exec_console_cli
                context.exported_vars.add('exec_console_cli')
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'console'), 'logging'), True):
                pass
                l_0_exec_console_cli = str_join(((undefined(name='exec_console_cli') if l_0_exec_console_cli is missing else l_0_exec_console_cli), ' logging', ))
                context.vars['exec_console_cli'] = l_0_exec_console_cli
                context.exported_vars.add('exec_console_cli')
            yield str((undefined(name='exec_console_cli') if l_0_exec_console_cli is missing else l_0_exec_console_cli))
            yield '\n'
        if t_1(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'commands'), 'console')):
            pass
            for l_1_command_console in environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'commands'), 'console'):
                l_1_command_console_list = resolve('command_console_list')
                l_1_command_console_cli = resolve('command_console_cli')
                l_1_commands_console_cli = resolve('commands_console_cli')
                _loop_vars = {}
                pass
                if (t_1(environment.getattr(l_1_command_console, 'commands')) and t_1(environment.getattr(l_1_command_console, 'type'))):
                    pass
                    if (environment.getattr(l_1_command_console, 'type') == 'none'):
                        pass
                        yield 'aaa accounting commands '
                        yield str(environment.getattr(l_1_command_console, 'commands'))
                        yield ' console none\n'
                    elif t_1(environment.getattr(l_1_command_console, 'methods')):
                        pass
                        l_1_command_console_list = []
                        _loop_vars['command_console_list'] = l_1_command_console_list
                        for l_2_method in environment.getattr(l_1_command_console, 'methods'):
                            l_2_group_cli = resolve('group_cli')
                            _loop_vars = {}
                            pass
                            if (environment.getattr(l_2_method, 'method') == 'logging'):
                                pass
                                context.call(environment.getattr((undefined(name='command_console_list') if l_1_command_console_list is missing else l_1_command_console_list), 'append'), environment.getattr(l_2_method, 'method'), _loop_vars=_loop_vars)
                            elif ((environment.getattr(l_2_method, 'method') == 'group') and t_1(environment.getattr(l_2_method, 'group'))):
                                pass
                                l_2_group_cli = str_join(('group ', environment.getattr(l_2_method, 'group'), ))
                                _loop_vars['group_cli'] = l_2_group_cli
                                context.call(environment.getattr((undefined(name='command_console_list') if l_1_command_console_list is missing else l_1_command_console_list), 'append'), (undefined(name='group_cli') if l_2_group_cli is missing else l_2_group_cli), _loop_vars=_loop_vars)
                        l_2_method = l_2_group_cli = missing
                        l_1_command_console_cli = context.call(environment.getattr(' ', 'join'), (undefined(name='command_console_list') if l_1_command_console_list is missing else l_1_command_console_list), _loop_vars=_loop_vars)
                        _loop_vars['command_console_cli'] = l_1_command_console_cli
                        if (undefined(name='command_console_cli') if l_1_command_console_cli is missing else l_1_command_console_cli):
                            pass
                            yield 'aaa accounting commands '
                            yield str(environment.getattr(l_1_command_console, 'commands'))
                            yield ' console '
                            yield str(environment.getattr(l_1_command_console, 'type'))
                            yield ' '
                            yield str((undefined(name='command_console_cli') if l_1_command_console_cli is missing else l_1_command_console_cli))
                            yield '\n'
                    elif (t_1(environment.getattr(l_1_command_console, 'group')) or t_1(environment.getattr(l_1_command_console, 'logging'), True)):
                        pass
                        l_1_commands_console_cli = str_join(('aaa accounting commands ', environment.getattr(l_1_command_console, 'commands'), ' console ', environment.getattr(l_1_command_console, 'type'), ))
                        _loop_vars['commands_console_cli'] = l_1_commands_console_cli
                        if t_1(environment.getattr(l_1_command_console, 'group')):
                            pass
                            l_1_commands_console_cli = str_join(((undefined(name='commands_console_cli') if l_1_commands_console_cli is missing else l_1_commands_console_cli), ' group ', environment.getattr(l_1_command_console, 'group'), ))
                            _loop_vars['commands_console_cli'] = l_1_commands_console_cli
                        if t_1(environment.getattr(l_1_command_console, 'logging'), True):
                            pass
                            l_1_commands_console_cli = str_join(((undefined(name='commands_console_cli') if l_1_commands_console_cli is missing else l_1_commands_console_cli), ' logging', ))
                            _loop_vars['commands_console_cli'] = l_1_commands_console_cli
                        yield str((undefined(name='commands_console_cli') if l_1_commands_console_cli is missing else l_1_commands_console_cli))
                        yield '\n'
            l_1_command_console = l_1_command_console_list = l_1_command_console_cli = l_1_commands_console_cli = missing
        if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'type'), 'none'):
            pass
            yield 'aaa accounting exec default none\n'
        elif (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'type')) and t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'methods'))):
            pass
            l_0_exec_default_list = []
            context.vars['exec_default_list'] = l_0_exec_default_list
            context.exported_vars.add('exec_default_list')
            for l_1_method in environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'methods'):
                l_1_group_cli = resolve('group_cli')
                _loop_vars = {}
                pass
                if (environment.getattr(l_1_method, 'method') == 'logging'):
                    pass
                    context.call(environment.getattr((undefined(name='exec_default_list') if l_0_exec_default_list is missing else l_0_exec_default_list), 'append'), environment.getattr(l_1_method, 'method'), _loop_vars=_loop_vars)
                elif ((environment.getattr(l_1_method, 'method') == 'group') and t_1(environment.getattr(l_1_method, 'group'))):
                    pass
                    l_1_group_cli = str_join(('group ', environment.getattr(l_1_method, 'group'), ))
                    _loop_vars['group_cli'] = l_1_group_cli
                    context.call(environment.getattr((undefined(name='exec_default_list') if l_0_exec_default_list is missing else l_0_exec_default_list), 'append'), (undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli), _loop_vars=_loop_vars)
            l_1_method = l_1_group_cli = missing
            l_0_exec_default_cli = context.call(environment.getattr(' ', 'join'), (undefined(name='exec_default_list') if l_0_exec_default_list is missing else l_0_exec_default_list))
            context.vars['exec_default_cli'] = l_0_exec_default_cli
            context.exported_vars.add('exec_default_cli')
            if (undefined(name='exec_default_cli') if l_0_exec_default_cli is missing else l_0_exec_default_cli):
                pass
                yield 'aaa accounting exec default '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'type'))
                yield ' '
                yield str((undefined(name='exec_default_cli') if l_0_exec_default_cli is missing else l_0_exec_default_cli))
                yield '\n'
        elif (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'type')) and (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'group')) or t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'logging'), True))):
            pass
            l_0_exec_default_cli = str_join(('aaa accounting exec default ', environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'type'), ))
            context.vars['exec_default_cli'] = l_0_exec_default_cli
            context.exported_vars.add('exec_default_cli')
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'group')):
                pass
                l_0_exec_default_cli = str_join(((undefined(name='exec_default_cli') if l_0_exec_default_cli is missing else l_0_exec_default_cli), ' group ', environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'group'), ))
                context.vars['exec_default_cli'] = l_0_exec_default_cli
                context.exported_vars.add('exec_default_cli')
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'exec'), 'default'), 'logging'), True):
                pass
                l_0_exec_default_cli = str_join(((undefined(name='exec_default_cli') if l_0_exec_default_cli is missing else l_0_exec_default_cli), ' logging', ))
                context.vars['exec_default_cli'] = l_0_exec_default_cli
                context.exported_vars.add('exec_default_cli')
            yield str((undefined(name='exec_default_cli') if l_0_exec_default_cli is missing else l_0_exec_default_cli))
            yield '\n'
        if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'type'), 'none'):
            pass
            yield 'aaa accounting system default none\n'
        elif (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'type')) and t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'methods'))):
            pass
            l_0_system_default_list = []
            context.vars['system_default_list'] = l_0_system_default_list
            context.exported_vars.add('system_default_list')
            for l_1_method in environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'methods'):
                l_1_group_cli = resolve('group_cli')
                _loop_vars = {}
                pass
                if (environment.getattr(l_1_method, 'method') == 'logging'):
                    pass
                    context.call(environment.getattr((undefined(name='system_default_list') if l_0_system_default_list is missing else l_0_system_default_list), 'append'), environment.getattr(l_1_method, 'method'), _loop_vars=_loop_vars)
                elif ((environment.getattr(l_1_method, 'method') == 'group') and t_1(environment.getattr(l_1_method, 'group'))):
                    pass
                    l_1_group_cli = str_join(('group ', environment.getattr(l_1_method, 'group'), ))
                    _loop_vars['group_cli'] = l_1_group_cli
                    context.call(environment.getattr((undefined(name='system_default_list') if l_0_system_default_list is missing else l_0_system_default_list), 'append'), (undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli), _loop_vars=_loop_vars)
            l_1_method = l_1_group_cli = missing
            l_0_system_default_cli = context.call(environment.getattr(' ', 'join'), (undefined(name='system_default_list') if l_0_system_default_list is missing else l_0_system_default_list))
            context.vars['system_default_cli'] = l_0_system_default_cli
            context.exported_vars.add('system_default_cli')
            if (undefined(name='system_default_cli') if l_0_system_default_cli is missing else l_0_system_default_cli):
                pass
                yield 'aaa accounting system default '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'type'))
                yield ' '
                yield str((undefined(name='system_default_cli') if l_0_system_default_cli is missing else l_0_system_default_cli))
                yield '\n'
        elif (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'type')) and (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'group')) or t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'logging'), True))):
            pass
            l_0_system_default_cli = str_join(('aaa accounting system default ', environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'type'), ))
            context.vars['system_default_cli'] = l_0_system_default_cli
            context.exported_vars.add('system_default_cli')
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'group')):
                pass
                l_0_system_default_cli = str_join(((undefined(name='system_default_cli') if l_0_system_default_cli is missing else l_0_system_default_cli), ' group ', environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'system'), 'default'), 'group'), ))
                context.vars['system_default_cli'] = l_0_system_default_cli
                context.exported_vars.add('system_default_cli')
            yield str((undefined(name='system_default_cli') if l_0_system_default_cli is missing else l_0_system_default_cli))
            yield '\n'
        if (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'type')) and t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'methods'))):
            pass
            l_0_dot1x_default_list = []
            context.vars['dot1x_default_list'] = l_0_dot1x_default_list
            context.exported_vars.add('dot1x_default_list')
            for l_1_method in environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'methods'):
                l_1_group_cli = resolve('group_cli')
                _loop_vars = {}
                pass
                if (environment.getattr(l_1_method, 'method') == 'logging'):
                    pass
                    context.call(environment.getattr((undefined(name='dot1x_default_list') if l_0_dot1x_default_list is missing else l_0_dot1x_default_list), 'append'), environment.getattr(l_1_method, 'method'), _loop_vars=_loop_vars)
                elif ((environment.getattr(l_1_method, 'method') == 'group') and t_1(environment.getattr(l_1_method, 'group'))):
                    pass
                    l_1_group_cli = str_join(('group ', environment.getattr(l_1_method, 'group'), ))
                    _loop_vars['group_cli'] = l_1_group_cli
                    if t_1(environment.getattr(l_1_method, 'multicast'), True):
                        pass
                        l_1_group_cli = str_join(((undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli), ' multicast', ))
                        _loop_vars['group_cli'] = l_1_group_cli
                    context.call(environment.getattr((undefined(name='dot1x_default_list') if l_0_dot1x_default_list is missing else l_0_dot1x_default_list), 'append'), (undefined(name='group_cli') if l_1_group_cli is missing else l_1_group_cli), _loop_vars=_loop_vars)
            l_1_method = l_1_group_cli = missing
            l_0_dot1x_default_cli = context.call(environment.getattr(' ', 'join'), (undefined(name='dot1x_default_list') if l_0_dot1x_default_list is missing else l_0_dot1x_default_list))
            context.vars['dot1x_default_cli'] = l_0_dot1x_default_cli
            context.exported_vars.add('dot1x_default_cli')
            if (undefined(name='dot1x_default_cli') if l_0_dot1x_default_cli is missing else l_0_dot1x_default_cli):
                pass
                yield 'aaa accounting dot1x default '
                yield str(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'type'))
                yield ' '
                yield str((undefined(name='dot1x_default_cli') if l_0_dot1x_default_cli is missing else l_0_dot1x_default_cli))
                yield '\n'
        elif (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'type')) and (t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'group')) or t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'logging'), True))):
            pass
            l_0_dot1x_default_cli = str_join(('aaa accounting dot1x default ', environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'type'), ))
            context.vars['dot1x_default_cli'] = l_0_dot1x_default_cli
            context.exported_vars.add('dot1x_default_cli')
            if t_1(environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'group')):
                pass
                l_0_dot1x_default_cli = str_join(((undefined(name='dot1x_default_cli') if l_0_dot1x_default_cli is missing else l_0_dot1x_default_cli), ' group ', environment.getattr(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'dot1x'), 'default'), 'group'), ))
                context.vars['dot1x_default_cli'] = l_0_dot1x_default_cli
                context.exported_vars.add('dot1x_default_cli')
            yield str((undefined(name='dot1x_default_cli') if l_0_dot1x_default_cli is missing else l_0_dot1x_default_cli))
            yield '\n'
        if t_1(environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'commands'), 'default')):
            pass
            for l_1_command_default in environment.getattr(environment.getattr((undefined(name='aaa_accounting') if l_0_aaa_accounting is missing else l_0_aaa_accounting), 'commands'), 'default'):
                l_1_commands_default_list = resolve('commands_default_list')
                l_1_command_default_cli = resolve('command_default_cli')
                l_1_commands_default_cli = resolve('commands_default_cli')
                _loop_vars = {}
                pass
                if (t_1(environment.getattr(l_1_command_default, 'commands')) and t_1(environment.getattr(l_1_command_default, 'type'))):
                    pass
                    if (environment.getattr(l_1_command_default, 'type') == 'none'):
                        pass
                        yield 'aaa accounting commands '
                        yield str(environment.getattr(l_1_command_default, 'commands'))
                        yield ' default none\n'
                    elif t_1(environment.getattr(l_1_command_default, 'methods')):
                        pass
                        l_1_commands_default_list = []
                        _loop_vars['commands_default_list'] = l_1_commands_default_list
                        for l_2_method in environment.getattr(l_1_command_default, 'methods'):
                            l_2_group_cli = resolve('group_cli')
                            _loop_vars = {}
                            pass
                            if (environment.getattr(l_2_method, 'method') == 'logging'):
                                pass
                                context.call(environment.getattr((undefined(name='commands_default_list') if l_1_commands_default_list is missing else l_1_commands_default_list), 'append'), environment.getattr(l_2_method, 'method'), _loop_vars=_loop_vars)
                            elif ((environment.getattr(l_2_method, 'method') == 'group') and t_1(environment.getattr(l_2_method, 'group'))):
                                pass
                                l_2_group_cli = str_join(('group ', environment.getattr(l_2_method, 'group'), ))
                                _loop_vars['group_cli'] = l_2_group_cli
                                context.call(environment.getattr((undefined(name='commands_default_list') if l_1_commands_default_list is missing else l_1_commands_default_list), 'append'), (undefined(name='group_cli') if l_2_group_cli is missing else l_2_group_cli), _loop_vars=_loop_vars)
                        l_2_method = l_2_group_cli = missing
                        l_1_command_default_cli = context.call(environment.getattr(' ', 'join'), (undefined(name='commands_default_list') if l_1_commands_default_list is missing else l_1_commands_default_list), _loop_vars=_loop_vars)
                        _loop_vars['command_default_cli'] = l_1_command_default_cli
                        if (undefined(name='command_default_cli') if l_1_command_default_cli is missing else l_1_command_default_cli):
                            pass
                            yield 'aaa accounting commands '
                            yield str(environment.getattr(l_1_command_default, 'commands'))
                            yield ' default '
                            yield str(environment.getattr(l_1_command_default, 'type'))
                            yield ' '
                            yield str((undefined(name='command_default_cli') if l_1_command_default_cli is missing else l_1_command_default_cli))
                            yield '\n'
                    elif (t_1(environment.getattr(l_1_command_default, 'group')) or t_1(environment.getattr(l_1_command_default, 'logging'), True)):
                        pass
                        l_1_commands_default_cli = str_join(('aaa accounting commands ', environment.getattr(l_1_command_default, 'commands'), ' default ', environment.getattr(l_1_command_default, 'type'), ))
                        _loop_vars['commands_default_cli'] = l_1_commands_default_cli
                        if t_1(environment.getattr(l_1_command_default, 'group')):
                            pass
                            l_1_commands_default_cli = str_join(((undefined(name='commands_default_cli') if l_1_commands_default_cli is missing else l_1_commands_default_cli), ' group ', environment.getattr(l_1_command_default, 'group'), ))
                            _loop_vars['commands_default_cli'] = l_1_commands_default_cli
                        if t_1(environment.getattr(l_1_command_default, 'logging'), True):
                            pass
                            l_1_commands_default_cli = str_join(((undefined(name='commands_default_cli') if l_1_commands_default_cli is missing else l_1_commands_default_cli), ' logging', ))
                            _loop_vars['commands_default_cli'] = l_1_commands_default_cli
                        yield str((undefined(name='commands_default_cli') if l_1_commands_default_cli is missing else l_1_commands_default_cli))
                        yield '\n'
            l_1_command_default = l_1_commands_default_list = l_1_command_default_cli = l_1_commands_default_cli = missing

blocks = {}
debug_info = '7=26&8=28&10=31&11=33&12=36&13=40&14=42&15=43&16=45&17=47&20=49&21=52&22=55&24=59&25=61&26=64&27=66&29=69&30=71&32=74&34=76&35=78&36=84&37=86&38=89&39=91&40=93&41=95&42=99&43=101&44=102&45=104&46=106&49=108&50=110&51=113&53=119&54=121&55=123&56=125&58=127&59=129&61=131&66=134&68=137&69=139&70=142&71=146&72=148&73=149&74=151&75=153&78=155&79=158&80=161&82=165&83=167&84=170&85=172&87=175&88=177&90=180&92=182&94=185&95=187&96=190&97=194&98=196&99=197&100=199&101=201&104=203&105=206&106=209&108=213&109=215&110=218&111=220&113=223&115=225&116=227&117=230&118=234&119=236&120=237&121=239&122=241&123=243&125=245&128=247&129=250&130=253&132=257&133=259&134=262&135=264&137=267&139=269&140=271&141=277&142=279&143=282&144=284&145=286&146=288&147=292&148=294&149=295&150=297&151=299&154=301&155=303&156=306&158=312&159=314&160=316&161=318&163=320&164=322&166=324'