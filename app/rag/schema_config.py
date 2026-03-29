"""
Database schema configuration for RAG system.
Contains table descriptions, relationships, and example queries.
"""

from typing import Dict, List, Any

NETWORK_DB_SCHEMA: Dict[str, Any] = {
    # ==== TABLE SCHEMAS ====
    "tables": {
        "devices": {
            "description": "Network devices (routers, switches) with location and vendor info",
            "columns": [
                {"name": "device_id", "type": "INT", "description": "Primary key"},
                {"name": "hostname", "type": "VARCHAR", "description": "Device hostname"},
                {"name": "management_ip", "type": "VARCHAR", "description": "Management IP address"},
                {"name": "vendor", "type": "VARCHAR", "description": "Device vendor (Cisco, Juniper, Arista)"},
                {"name": "device_type", "type": "VARCHAR", "description": "Device type (Router, Switch)"},
                {"name": "location_id", "type": "INT", "description": "Foreign key to locations"},
            ],
            "primary_key": "device_id",
            "foreign_keys": {"location_id": "locations.location_id"},
            "indexes": ["hostname", "location_id"],
        },
        "alerts": {
            "description": "Network alerts and incidents triggered by devices",
            "columns": [
                {"name": "alert_id", "type": "INT", "description": "Primary key"},
                {"name": "device_id", "type": "INT", "description": "Device that triggered alert"},
                {"name": "alert_type", "type": "VARCHAR", "description": "Type of alert (High CPU, Packet Loss, Interface Down)"},
                {"name": "severity", "type": "VARCHAR", "description": "Alert severity (Warning, Critical)"},
                {"name": "message", "type": "VARCHAR", "description": "Alert message"},
                {"name": "triggered_at", "type": "TIMESTAMP", "description": "When alert was triggered"},
            ],
            "primary_key": "alert_id",
            "foreign_keys": {"device_id": "devices.device_id"},
            "indexes": ["device_id", "severity", "triggered_at"],
        },
        "device_health": {
            "description": "CPU, memory, and temperature metrics for devices",
            "columns": [
                {"name": "health_id", "type": "INT", "description": "Primary key"},
                {"name": "device_id", "type": "INT", "description": "Device ID"},
                {"name": "cpu_usage", "type": "FLOAT", "description": "CPU usage percentage"},
                {"name": "memory_usage", "type": "FLOAT", "description": "Memory usage percentage"},
                {"name": "temperature", "type": "INT", "description": "Device temperature in Celsius"},
                {"name": "timestamp", "type": "TIMESTAMP", "description": "Metric timestamp"},
            ],
            "primary_key": "health_id",
            "foreign_keys": {"device_id": "devices.device_id"},
            "indexes": ["device_id", "timestamp"],
        },
        "interfaces": {
            "description": "Network interfaces on devices with IP addresses",
            "columns": [
                {"name": "interface_id", "type": "INT", "description": "Primary key"},
                {"name": "device_id", "type": "INT", "description": "Device ID"},
                {"name": "interface_name", "type": "VARCHAR", "description": "Interface name (Gig0/0, Eth0)"},
                {"name": "interface_ip", "type": "VARCHAR", "description": "Interface IP address"},
                {"name": "status", "type": "VARCHAR", "description": "Interface status (UP, DOWN)"},
                {"name": "speed", "type": "INT", "description": "Interface speed in Mbps"},
            ],
            "primary_key": "interface_id",
            "foreign_keys": {"device_id": "devices.device_id"},
            "indexes": ["device_id", "status"],
        },
        "interface_metrics": {
            "description": "Traffic and utilization metrics for interfaces",
            "columns": [
                {"name": "metric_id", "type": "INT", "description": "Primary key"},
                {"name": "interface_id", "type": "INT", "description": "Interface ID"},
                {"name": "in_traffic", "type": "BIGINT", "description": "Inbound traffic in bytes"},
                {"name": "out_traffic", "type": "BIGINT", "description": "Outbound traffic in bytes"},
                {"name": "utilization", "type": "FLOAT", "description": "Interface utilization percentage"},
                {"name": "timestamp", "type": "TIMESTAMP", "description": "Metric timestamp"},
            ],
            "primary_key": "metric_id",
            "foreign_keys": {"interface_id": "interfaces.interface_id"},
            "indexes": ["interface_id", "timestamp"],
        },
        "bgp_neighbors": {
            "description": "BGP neighbor relationships and states",
            "columns": [
                {"name": "neighbor_id", "type": "INT", "description": "Primary key"},
                {"name": "device_id", "type": "INT", "description": "Device ID"},
                {"name": "neighbor_ip", "type": "VARCHAR", "description": "Neighbor IP address"},
                {"name": "remote_as", "type": "INT", "description": "Remote AS number"},
                {"name": "state", "type": "VARCHAR", "description": "BGP state (ESTABLISHED, IDLE)"},
            ],
            "primary_key": "neighbor_id",
            "foreign_keys": {"device_id": "devices.device_id"},
            "indexes": ["device_id", "state"],
        },
        "isis_instances": {
            "description": "ISIS routing protocol instances on devices",
            "columns": [
                {"name": "instance_id", "type": "INT", "description": "Primary key"},
                {"name": "device_id", "type": "INT", "description": "Device ID"},
                {"name": "instance_name", "type": "VARCHAR", "description": "ISIS instance name"},
                {"name": "system_id", "type": "VARCHAR", "description": "ISIS system ID"},
                {"name": "level_type", "type": "VARCHAR", "description": "ISIS level (L1, L2)"},
            ],
            "primary_key": "instance_id",
            "foreign_keys": {"device_id": "devices.device_id"},
            "indexes": ["device_id"],
        },
        "isis_adjacencies": {
            "description": "ISIS adjacency relationships between interfaces",
            "columns": [
                {"name": "adjacency_id", "type": "INT", "description": "Primary key"},
                {"name": "instance_id", "type": "INT", "description": "ISIS instance ID"},
                {"name": "interface_id", "type": "INT", "description": "Interface ID"},
                {"name": "neighbor_ip", "type": "VARCHAR", "description": "Neighbor IP address"},
                {"name": "level", "type": "VARCHAR", "description": "ISIS level (L1, L2)"},
                {"name": "metric", "type": "INT", "description": "Link metric"},
                {"name": "state", "type": "VARCHAR", "description": "Adjacency state (UP, DOWN)"},
            ],
            "primary_key": "adjacency_id",
            "foreign_keys": {
                "instance_id": "isis_instances.instance_id",
                "interface_id": "interfaces.interface_id",
            },
            "indexes": ["instance_id", "interface_id", "state"],
        },
        "topology_links": {
            "description": "Physical and logical links between devices",
            "columns": [
                {"name": "link_id", "type": "INT", "description": "Primary key"},
                {"name": "device_a", "type": "INT", "description": "First device ID"},
                {"name": "device_b", "type": "INT", "description": "Second device ID"},
                {"name": "interface_a", "type": "VARCHAR", "description": "Interface on device A"},
                {"name": "interface_b", "type": "VARCHAR", "description": "Interface on device B"},
                {"name": "protocol", "type": "VARCHAR", "description": "Protocol (ISIS, BGP, L2)"},
            ],
            "primary_key": "link_id",
            "foreign_keys": {
                "device_a": "devices.device_id",
                "device_b": "devices.device_id",
            },
            "indexes": ["device_a", "device_b", "protocol"],
        },
        "locations": {
            "description": "Data center locations with geographic information",
            "columns": [
                {"name": "location_id", "type": "INT", "description": "Primary key"},
                {"name": "site_name", "type": "VARCHAR", "description": "Site name"},
                {"name": "city", "type": "VARCHAR", "description": "City"},
                {"name": "country", "type": "VARCHAR", "description": "Country"},
            ],
            "primary_key": "location_id",
            "indexes": ["city", "country"],
        },
    },
    
    # ==== COMMON JOIN PATTERNS ====
    "common_joins": [
        {
            "name": "device_location",
            "tables": ["devices", "locations"],
            "condition": "devices.location_id = locations.location_id",
            "description": "Join devices with their location information",
            "example_sql": """
            SELECT d.hostname, d.device_type, l.site_name, l.city
            FROM devices d
            JOIN locations l ON d.location_id = l.location_id
            WHERE l.country = 'India'
            """,
            "use_cases": ["Find devices by location", "devices in a specific city"]
        },
        {
            "name": "device_alerts",
            "tables": ["devices", "alerts"],
            "condition": "devices.device_id = alerts.device_id",
            "description": "Join devices with their alerts",
            "example_sql": """
            SELECT d.hostname, a.alert_type, a.severity, a.triggered_at
            FROM devices d
            LEFT JOIN alerts a ON d.device_id = a.device_id
            WHERE a.severity = 'Critical' AND a.triggered_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """,
            "use_cases": ["Get critical alerts", "alerts by device"]
        },
        {
            "name": "device_health_metrics",
            "tables": ["devices", "device_health"],
            "condition": "devices.device_id = device_health.device_id",
            "description": "Join devices with their health metrics",
            "example_sql": """
            SELECT d.hostname, dh.cpu_usage, dh.memory_usage, dh.temperature, dh.timestamp
            FROM devices d
            JOIN device_health dh ON d.device_id = dh.device_id
            WHERE dh.cpu_usage > 80 OR dh.temperature > 60
            ORDER BY dh.timestamp DESC
            """,
            "use_cases": ["High CPU usage", "temperature monitoring", "memory usage"]
        },
        {
            "name": "device_interfaces",
            "tables": ["devices", "interfaces"],
            "condition": "devices.device_id = interfaces.device_id",
            "description": "Join devices with their interfaces",
            "example_sql": """
            SELECT d.hostname, i.interface_name, i.interface_ip, i.status, i.speed
            FROM devices d
            JOIN interfaces i ON d.device_id = i.device_id
            WHERE i.status = 'DOWN'
            """,
            "use_cases": ["Down interfaces", "interface information", "IP addresses"]
        },
        {
            "name": "interface_traffic",
            "tables": ["interfaces", "interface_metrics"],
            "condition": "interfaces.interface_id = interface_metrics.interface_id",
            "description": "Join interfaces with their traffic metrics",
            "example_sql": """
            SELECT i.interface_name, im.in_traffic, im.out_traffic, im.utilization, im.timestamp
            FROM interfaces i
            JOIN interface_metrics im ON i.interface_id = im.interface_id
            WHERE im.utilization > 80
            ORDER BY im.timestamp DESC
            """,
            "use_cases": ["High utilization", "traffic analysis", "interface metrics"]
        },
        {
            "name": "device_bgp",
            "tables": ["devices", "bgp_neighbors"],
            "condition": "devices.device_id = bgp_neighbors.device_id",
            "description": "Join devices with BGP neighbors",
            "example_sql": """
            SELECT d.hostname, bn.neighbor_ip, bn.remote_as, bn.state
            FROM devices d
            JOIN bgp_neighbors bn ON d.device_id = bn.device_id
            WHERE bn.state = 'ESTABLISHED'
            """,
            "use_cases": ["BGP neighbors", "BGP states", "neighbor relationships"]
        },
        {
            "name": "device_isis",
            "tables": ["devices", "isis_instances"],
            "condition": "devices.device_id = isis_instances.device_id",
            "description": "Join devices with ISIS instances",
            "example_sql": """
            SELECT d.hostname, ii.instance_name, ii.system_id, ii.level_type
            FROM devices d
            JOIN isis_instances ii ON d.device_id = ii.device_id
            """,
            "use_cases": ["ISIS configuration", "routing protocol info"]
        },
        {
            "name": "topology_devices",
            "tables": ["topology_links", "devices"],
            "condition": "topology_links.device_a = devices.device_id OR topology_links.device_b = devices.device_id",
            "description": "Join topology links with devices",
            "example_sql": """
            SELECT d1.hostname as device_a, d2.hostname as device_b, tl.protocol
            FROM topology_links tl
            JOIN devices d1 ON tl.device_a = d1.device_id
            JOIN devices d2 ON tl.device_b = d2.device_id
            WHERE tl.protocol = 'ISIS'
            """,
            "use_cases": ["Network topology", "link information", "protocol analysis"]
        },
        {
            "name": "isis_adjacencies_full",
            "tables": ["isis_adjacencies", "isis_instances", "interfaces"],
            "condition": "isis_adjacencies.instance_id = isis_instances.instance_id AND isis_adjacencies.interface_id = interfaces.interface_id",
            "description": "Join ISIS adjacencies with instances and interfaces",
            "example_sql": """
            SELECT ia.adjacency_id, ii.instance_name, i.interface_name, ia.neighbor_ip, ia.state, ia.metric
            FROM isis_adjacencies ia
            JOIN isis_instances ii ON ia.instance_id = ii.instance_id
            JOIN interfaces i ON ia.interface_id = i.interface_id
            WHERE ia.state = 'UP'
            """,
            "use_cases": ["ISIS adjacency status", "ISIS topology"]
        },
    ],
    
    # ==== EXAMPLE QUERIES ====
    "example_queries": [
        {
            "type": "simple_alert_query",
            "description": "Get all critical alerts triggered in the last 24 hours",
            "sql": "SELECT alert_id, device_id, alert_type, severity, triggered_at FROM alerts WHERE severity = 'Critical' AND triggered_at > DATE_SUB(NOW(), INTERVAL 1 DAY)",
            "tables": ["alerts"],
            "complexity": "simple"
        },
        {
            "type": "device_with_alerts",
            "description": "Find all devices with their critical alerts",
            "sql": "SELECT d.hostname, a.alert_type, a.severity FROM devices d LEFT JOIN alerts a ON d.device_id = a.device_id WHERE a.severity = 'Critical'",
            "tables": ["devices", "alerts"],
            "complexity": "medium"
        },
        {
            "type": "location_alerts",
            "description": "Get critical alerts by location",
            "sql": "SELECT l.city, d.hostname, a.alert_type FROM devices d JOIN locations l ON d.location_id = l.location_id JOIN alerts a ON d.device_id = a.device_id WHERE a.severity = 'Critical'",
            "tables": ["locations", "devices", "alerts"],
            "complexity": "complex"
        },
        {
            "type": "device_health_query",
            "description": "Show devices with high CPU or memory usage",
            "sql": "SELECT d.hostname, dh.cpu_usage, dh.memory_usage FROM devices d JOIN device_health dh ON d.device_id = dh.device_id WHERE dh.cpu_usage > 80 OR dh.memory_usage > 85",
            "tables": ["devices", "device_health"],
            "complexity": "medium"
        },
        {
            "type": "interface_status",
            "description": "Find down interfaces with device information",
            "sql": "SELECT d.hostname, i.interface_name, i.status FROM devices d JOIN interfaces i ON d.device_id = i.device_id WHERE i.status = 'DOWN'",
            "tables": ["devices", "interfaces"],
            "complexity": "medium"
        },
        {
            "type": "topology_query",
            "description": "Show ISIS topology between devices",
            "sql": "SELECT d1.hostname as from_device, d2.hostname as to_device, tl.protocol FROM topology_links tl JOIN devices d1 ON tl.device_a = d1.device_id JOIN devices d2 ON tl.device_b = d2.device_id WHERE tl.protocol = 'ISIS'",
            "tables": ["topology_links", "devices"],
            "complexity": "complex"
        },
        {
            "type": "bgp_neighbors",
            "description": "List BGP neighbors and their states",
            "sql": "SELECT d.hostname, bn.neighbor_ip, bn.remote_as, bn.state FROM devices d JOIN bgp_neighbors bn ON d.device_id = bn.device_id",
            "tables": ["devices", "bgp_neighbors"],
            "complexity": "medium"
        },
    ]
}
