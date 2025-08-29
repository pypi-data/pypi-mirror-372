import stix2

from faker import Faker

fake = Faker()

from stix_traverser import ObjectTraverser


def test_object_traverser():
    test_object = stix2.IPv4Address(value=fake.ipv4())

    traverser = ObjectTraverser(test_object)

    assert not traverser.a
    assert not traverser.a.b.c

    assert traverser.value == test_object.value
    assert traverser.id == test_object.id

def test_object_refs_traverser():
    test_mac = stix2.MACAddress(value=fake.mac_address())
    test_ip = stix2.IPv4Address(value=fake.ipv4(), resolves_to_refs=[test_mac])

    env = stix2.Environment(store=stix2.MemoryStore())
    env.add(test_ip)
    env.add(test_mac)

    stix = ObjectTraverser(obj=test_ip, env=env)

    assert not stix.a
    assert not stix.a.b.c

    assert stix.value == test_ip.value
    assert stix.id == test_ip.id
    assert stix.resolves_to_refs() == [test_mac]

    assert stix.MACAddress() == [test_mac]
    assert stix.MACAddress[0]() == test_mac

    assert stix.MACAddress[0].value == test_mac.value

    assert not stix.MACAddress[1]
    assert not stix.MACAddress[1]()
    assert not stix.MACAddress[1].a
    assert not stix.MACAddress[1].a()
    assert not stix.MACAddress[1].a.b.c

    assert not stix.MACAddress[1][2]
    assert not stix.MACAddress[1].a[2]
    assert not stix.MACAddress[1].a[2]()
