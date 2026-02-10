import pytest
from src.cleaner import is_private_ip

def test_is_private_ip_success():
    # Test avec des IPs privées (RFC 1918)
    assert is_private_ip("192.168.1.1") is True
    assert is_private_ip("10.0.0.50") is True
    assert is_private_ip("172.16.0.100") is True

def test_is_private_ip_public():
    # Test avec des IPs publiques (Google, Cloudflare)
    assert is_private_ip("8.8.8.8") is False
    assert is_private_ip("1.1.1.1") is False

def test_is_private_ip_invalid():
    # Test avec des données corrompues (Sécurité : gestion des erreurs)
    assert is_private_ip("not-an-ip") is False
    assert is_private_ip(None) is False
    assert is_private_ip("999.999.999.999") is False