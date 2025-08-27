import numpy as np


def unlog_particles(s):
    return 10 ** ((s / 2**16) * 3.5)


def log_particles(s):
    return (np.log10(s) / 3.5) * 2**16
