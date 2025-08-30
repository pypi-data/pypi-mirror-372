from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'documentation/ip-virtual-router-mac-address.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_ip_virtual_router_mac_address = resolve('ip_virtual_router_mac_address')
    l_0_ip_virtual_router_mac_address_advertisement_interval = resolve('ip_virtual_router_mac_address_advertisement_interval')
    l_0_ip_virtual_router_mac_address_mlag_peer = resolve('ip_virtual_router_mac_address_mlag_peer')
    try:
        t_1 = environment.tests['arista.avd.defined']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No test named 'arista.avd.defined' found.")
    pass
    if ((t_1((undefined(name='ip_virtual_router_mac_address') if l_0_ip_virtual_router_mac_address is missing else l_0_ip_virtual_router_mac_address)) or t_1((undefined(name='ip_virtual_router_mac_address_advertisement_interval') if l_0_ip_virtual_router_mac_address_advertisement_interval is missing else l_0_ip_virtual_router_mac_address_advertisement_interval))) or t_1((undefined(name='ip_virtual_router_mac_address_mlag_peer') if l_0_ip_virtual_router_mac_address_mlag_peer is missing else l_0_ip_virtual_router_mac_address_mlag_peer), True)):
        pass
        yield '\n### Virtual Router MAC Address\n\n#### Virtual Router MAC Address Summary\n\n'
        if t_1((undefined(name='ip_virtual_router_mac_address') if l_0_ip_virtual_router_mac_address is missing else l_0_ip_virtual_router_mac_address)):
            pass
            yield 'Virtual Router MAC Address: '
            yield str((undefined(name='ip_virtual_router_mac_address') if l_0_ip_virtual_router_mac_address is missing else l_0_ip_virtual_router_mac_address))
            yield '\n'
        if t_1((undefined(name='ip_virtual_router_mac_address_advertisement_interval') if l_0_ip_virtual_router_mac_address_advertisement_interval is missing else l_0_ip_virtual_router_mac_address_advertisement_interval)):
            pass
            yield 'Virtual Router MAC Address Advertisement Interval: '
            yield str((undefined(name='ip_virtual_router_mac_address_advertisement_interval') if l_0_ip_virtual_router_mac_address_advertisement_interval is missing else l_0_ip_virtual_router_mac_address_advertisement_interval))
            yield '\n'
        if t_1((undefined(name='ip_virtual_router_mac_address_mlag_peer') if l_0_ip_virtual_router_mac_address_mlag_peer is missing else l_0_ip_virtual_router_mac_address_mlag_peer), True):
            pass
            yield 'Virtual Router MAC Address MLAG Peer: Enabled\n'
        yield '\n#### Virtual Router MAC Address Device Configuration\n\n```eos\n'
        template = environment.get_template('eos/ip-virtual-router-mac-address.j2', 'documentation/ip-virtual-router-mac-address.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        template = environment.get_template('eos/ip-virtual-router-mac-address-mlag-peer.j2', 'documentation/ip-virtual-router-mac-address.j2')
        gen = template.root_render_func(template.new_context(context.get_all(), True, {}))
        try:
            for event in gen:
                yield event
        finally: gen.close()
        yield '```\n'

blocks = {}
debug_info = '7=20&13=23&14=26&16=28&17=31&19=33&26=37&27=43'