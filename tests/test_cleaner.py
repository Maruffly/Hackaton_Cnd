import pytest
from src.cleaner import is_private_ip
from src.cleaner import is_multicast_broadcast

def test_is_private_ip_success():
    # Test with private IPs (RFC 1918)
    assert is_private_ip("192.168.1.1") is True
    assert is_private_ip("10.0.0.50") is True
    assert is_private_ip("172.16.0.100") is True

def test_is_private_ip_public():
    # Test with public IPs (Google, Cloudflare)
    assert is_private_ip("8.8.8.8") is False
    assert is_private_ip("1.1.1.1") is False

def test_is_private_ip_invalid():
    # Test with compromised IPs (Security : error handling)
    assert is_private_ip("not-an-ip") is False
    assert is_private_ip(None) is False
    assert is_private_ip("999.999.999.999") is False

def test_is_multicast_broadcast_noise():
    # FALSE POSITIVE : Have to be detected as noise
    assert is_multicast_broadcast("255.255.255.255") is True
    ## Mutlicast range (224.0.0.0 to 239.255.255.255)
    assert is_multicast_broadcast("224.0.0.1") is True
    assert is_multicast_broadcast("239.255.255.250") is True # SSDP (Discovery)

    # TRUE POSITIVE : Have to be detected as threat
    ## Classical private address (Unicast)
    assert is_multicast_broadcast("192.168.1.1") is False
    assert is_multicast_broadcast("10.0.0.1") is False
    ## Public IPs
    assert is_multicast_broadcast("8.8.8.8") is False
    
    # EDGE CASE : Error handling
    assert is_multicast_broadcast("not_an_ip") is False
    assert is_multicast_broadcast(None) is False