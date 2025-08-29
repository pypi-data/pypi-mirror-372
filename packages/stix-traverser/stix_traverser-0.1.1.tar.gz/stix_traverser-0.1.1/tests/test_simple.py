import stix2
from faker import Faker

from stix_traverser import StixTraverser

fake = Faker()

def test_traverser():
    infra = stix2.Infrastructure(name=fake.hostname())
    test_mac = stix2.MACAddress(value=fake.mac_address())
    test_ip = stix2.IPv4Address(value=fake.ipv4(), resolves_to_refs=[test_mac])
    test_ip2 = stix2.IPv4Address(value=fake.ipv4())
    test_ip3 = stix2.IPv4Address(value=fake.ipv4())
    rel1 = stix2.Relationship(infra, "consist-of", test_mac)
    rel2 = stix2.Relationship(infra, "consist-of", test_ip)
    rel3 = stix2.Relationship(infra, "consist-of", test_ip2)

    stix = StixTraverser(test_mac, test_ip, test_ip2, test_ip3, infra, rel1, rel2, rel3)

    assert stix.IPv4Address[0]() == test_ip
    assert stix.IPv4Address[0].MACAddress[0]() == test_mac
    assert stix.MACAddress[0]() == test_mac
    assert stix.MACAddress[0].Infrastructure[0].name == infra.name

    ips = stix.MACAddress[0].Infrastructure[0].IPv4Address()

    assert test_ip in ips
    assert test_ip2 in ips

    vals = stix.MACAddress[0].Infrastructure.IPv4Address.value()

    assert vals.sort() == [test_ip.value, test_ip2.value].sort()

    vals = stix.MACAddress.Infrastructure.IPv4Address.value()

    assert vals.sort() == [test_ip.value, test_ip2.value].sort()
