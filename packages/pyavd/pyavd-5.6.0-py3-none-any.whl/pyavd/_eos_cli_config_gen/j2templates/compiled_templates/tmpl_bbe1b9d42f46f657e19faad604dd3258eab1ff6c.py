from jinja2.runtime import LoopContext, Macro, Markup, Namespace, TemplateNotFound, TemplateReference, TemplateRuntimeError, Undefined, escape, identity, internalcode, markup_join, missing, str_join
name = 'eos-intended-config.j2'

def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    concat = environment.concat
    cond_expr_undefined = Undefined
    if 0: yield None
    l_0_eos_cli_config_gen_configuration = resolve('eos_cli_config_gen_configuration')
    l_0_hide_passwords = missing
    try:
        t_1 = environment.filters['arista.avd.default']
    except KeyError:
        @internalcode
        def t_1(*unused):
            raise TemplateRuntimeError("No filter named 'arista.avd.default' found.")
    pass
    l_0_hide_passwords = t_1(environment.getattr((undefined(name='eos_cli_config_gen_configuration') if l_0_eos_cli_config_gen_configuration is missing else l_0_eos_cli_config_gen_configuration), 'hide_passwords'), False)
    context.vars['hide_passwords'] = l_0_hide_passwords
    context.exported_vars.add('hide_passwords')
    template = environment.get_template('eos/rancid-content-type.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/config-comment.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/boot.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/enable-password.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/aaa-root.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/local-users.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/address-locking.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/agents.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/hardware.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/service-routing-configuration-bgp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/prompt.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/terminal.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/aliases.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/logging-event-storm-control.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/daemon-terminattr.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/daemons.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/dhcp-relay.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-dhcp-relay.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-dhcp-relay.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/dhcp-servers.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-dhcp-snooping.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/switchport-default.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/vlan-internal-order.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/errdisable.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/event-monitor.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/flow-tracking.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/hardware-access-list-update-default-result-permit.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-igmp-snooping.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/logging-event-congestion-drops.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/load-interval.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/transceiver-qsfp-default-mode.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/platform-sfe-interface.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/interface-defaults.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/service-routing-protocols-model.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/kernel.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/l2-protocol-forwarding.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/lacp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/queue-monitor-length.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/monitor-layer1.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/load-balance.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/link-tracking-groups.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/lldp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/logging.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/match-list-input.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/mcs-client.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-virtual-router-mac-address-mlag-peer.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/monitor-server-radius.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/monitor-twamp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-name-server-groups.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/platform-trident.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-nat-part1.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/hostname.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-domain-lookup.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-name-servers.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/dns-domain.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/domain-list.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/aaa-server-groups-ldap.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/trackers.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/poe.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/switchport-port-security.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ptp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/qos-profiles.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/radius-proxy.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/redundancy.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-adaptive-virtual-topology.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-internet-exit.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-l2-vpn.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-path-selection.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-service-insertion.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/platform.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/sflow.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/snmp-server.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/hardware-speed-groups.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/spanning-tree.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/sync-e.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/service-unsupported-transceiver.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/transceiver.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/port-channel.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/system-l1.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/tap-aggregation.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/clock.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/vlans.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/vrfs.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/bgp-groups.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/queue-monitor-streaming.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/banners.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-accounts.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-api-http.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-console.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-cvx.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-defaults.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-api-gnmi.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-api-models.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-security.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/radius-server.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/aaa-server-groups-radius.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/tacacs-servers.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/aaa-server-groups-tacacs-plus.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/aaa.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/cvx.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/dot1x.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/monitor-telemetry-influx.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-security.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/mac-security.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/port-channel-interfaces.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/dps-interfaces.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ethernet-interfaces.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/loopback-interfaces.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-interfaces.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/tunnel-interfaces.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/vlan-interfaces.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/vxlan-interface.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/tcam-profile.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/application-traffic-recognition.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/load-balance-cluster.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/monitor-connectivity.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/mac-address-table-aging-time.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/mac-address-table-static-entries.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/event-handlers.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-segment-security.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/interface-groups.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/interface-profiles.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-virtual-router-mac-address.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/virtual-source-nat-vrfs.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-access-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-standard-access-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/access-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-access-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/class-maps-pbr.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/standard-access-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-routing.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-icmp-redirect.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-hardware.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-routing-vrfs.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-icmp-redirect.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/as-path.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-community-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/community-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-extcommunity-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-extcommunity-lists-regexp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/dynamic-prefix-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/prefix-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-prefix-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-unicast-routing.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-hardware.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-unicast-routing-vrfs.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-neighbors.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/mac-access-lists.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/system.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/mac-address-table-notification.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/maintenance.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/monitor-sessions.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/monitor-session-default-encapsulation-gre.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/mlag-configuration.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/static-routes.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/arp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-static-routes.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/mpls.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-nat-part2.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-client-source-interfaces.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ntp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/patch-panel.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/policy-maps-pbr.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/monitor-telemetry-postcard-policy.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/qos.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/class-maps.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/policy-maps-copp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/policy-maps-qos.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/priority-flow-control.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-radius-source-interfaces.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/roles.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/route-maps.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/peer-filters.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-bfd.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-bgp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-general.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-traffic-engineering.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-igmp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-isis.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-multicast.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-ospf.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ipv6-router-ospf.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-pim-sparse-mode.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/router-msdp.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/stun.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/ip-tacacs-source-interfaces.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/traffic-policies.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/platform-apply.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/platform-headroom-pool.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/vmtracer-sessions.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/dot1x_part2.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-ssh.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/management-tech-support.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/eos-cli.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()
    template = environment.get_template('eos/end.j2', 'eos-intended-config.j2')
    gen = template.root_render_func(template.new_context(context.get_all(), True, {'hide_passwords': l_0_hide_passwords}))
    try:
        for event in gen:
            yield event
    finally: gen.close()

blocks = {}
debug_info = '8=19&9=22&10=28&12=34&14=40&16=46&18=52&20=58&22=64&24=70&26=76&28=82&30=88&32=94&34=100&36=106&38=112&40=118&42=124&44=130&46=136&48=142&50=148&52=154&54=160&56=166&58=172&60=178&62=184&64=190&66=196&68=202&70=208&72=214&74=220&76=226&78=232&80=238&82=244&84=250&86=256&88=262&90=268&92=274&94=280&96=286&98=292&100=298&102=304&104=310&106=316&108=322&110=328&112=334&114=340&116=346&118=352&120=358&122=364&124=370&126=376&128=382&130=388&132=394&134=400&136=406&138=412&140=418&142=424&144=430&146=436&148=442&150=448&152=454&154=460&156=466&158=472&160=478&162=484&164=490&166=496&168=502&170=508&172=514&174=520&176=526&178=532&180=538&182=544&184=550&186=556&188=562&190=568&192=574&194=580&196=586&198=592&200=598&202=604&204=610&206=616&208=622&210=628&212=634&214=640&216=646&218=652&220=658&222=664&224=670&226=676&228=682&230=688&232=694&234=700&236=706&238=712&240=718&242=724&244=730&246=736&248=742&250=748&252=754&254=760&256=766&258=772&260=778&262=784&264=790&266=796&268=802&270=808&272=814&274=820&276=826&278=832&280=838&282=844&284=850&286=856&288=862&290=868&292=874&294=880&296=886&298=892&300=898&302=904&304=910&306=916&308=922&310=928&311=934&313=940&315=946&317=952&319=958&321=964&323=970&325=976&327=982&329=988&331=994&333=1000&335=1006&337=1012&339=1018&341=1024&343=1030&345=1036&347=1042&349=1048&351=1054&353=1060&355=1066&357=1072&359=1078&361=1084&363=1090&365=1096&367=1102&369=1108&371=1114&373=1120&375=1126&377=1132&379=1138&381=1144&383=1150&385=1156&387=1162&389=1168&391=1174&393=1180&395=1186'