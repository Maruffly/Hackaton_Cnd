import pandas as pd
import ipaddress
import os

def is_private_ip(ip):
    """Check if network is private - RFC 1918"""
    try:
        # Convert object to an object : use private property
        return ipaddress.ip_address(ip).is_private
    except:
        return False

def is_multicast_broadcast(ip):
    try:
        addr = ipaddress.ip_address(ip)
        # Check if this is multicast or broadcast
        return addr.is_multicast or ip == "255.255.255.255"
    except:
        return False

def get_stats(chunk):
    return {
        "total_lines": len(chunk),
        "false_positives": int(chunk['is_false_positive'].sum()),
        "reconnaissance": int(chunk['is_scan'].sum()),
        "lateral_movement": int(chunk['is_lateral'].sum()),
        "noise_broadcast": int(chunk['is_noise'].sum())
    }