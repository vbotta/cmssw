import os

def checked_out_MPS():
    """Checks if MPS is checked out locally or taken from the release."""

    checked_out_packages = os.path.join(os.environ["CMSSW_BASE"], "src", ".git",
                                        "info", "sparse-checkout")
    checked_out = False
    try:
        with open(checked_out_packages, "r") as f:
            package = "/Alignment/MillePedeAlignmentAlgorithm/"
            for line in f:
                if package == line.strip():
                    checked_out = True
                    break
    except IOError as e:
        if e.args != (2, 'No such file or directory'): raise

    return checked_out
