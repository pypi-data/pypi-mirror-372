from clarity_cli.outputs import CliOutput

out = CliOutput()


class StopCommand(Exception):
    def __init__(self, *args):
        out.error(*args)
        exit(1)


class UnAuthenticated(Exception):
    def __init__(self, *args):
        raise StopCommand(f"You need to login first. Run {CliOutput.bold('clarity login')}")
