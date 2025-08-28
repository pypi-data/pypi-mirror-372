from rori.command import CommandK8s, CommandSsh


def test_can_instantiate_kubernetex_context():
    command = CommandK8s()
    assert command.port_from is None
    assert command.port_to is None
    assert hasattr(command, "context")
    assert hasattr(command, "namespace")
    assert hasattr(command, "pod")
    assert hasattr(command, "service")
    assert command.executable == "kubectl"
    assert command.type_ == "kubernetes"


def test_can_instantiate_ssh_context():
    command = CommandSsh()
    assert command.port_from is None
    assert command.port_to is None
    # assert hasattr(command, 'user')
    # assert hasattr(command, 'host')
    assert command.executable == "ssh"
    assert command.type_ == "ssh"
