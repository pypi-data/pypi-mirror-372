import numpy as np

def print_tau_style(derivatives, freqs, f_name):

    with open(f_name, 'w') as f:
        f.truncate(0)

        for freq, ((idx, _, _), pars) in zip(freqs, derivatives):

            f.write(("Vibration: {:d} Energy (cm-1): {} Rank (k), order (q) "
                     "and derivatives up to 3rd order\n").format(idx, freq))

            for (k, q), Bkq_dq in pars.items():
                f.write(f"{k:^ d} {q:^ d}  {0: 14.9f}  {0: 14.9f}  {Bkq_dq: 14.9f}\n")


def read_tau_style(f_name: str):
    """
    Reads CFP_polynomials.dat and extracts coupling values and mode energies

    Parameters
    ----------
    f_name : str
        CFP_polynomials file name

    Returns
    -------
    np.ndarray
        Polynomial coefficients a, b, c for each mode (3, n_modes)
    list
        Mode energies
    """

    freqs = []
    derivatives = []

    with open(f_name, 'r') as f:

        for line in f:
            if "Vibration:" in line:
                freqs.append(float(line.split()[4]))
                tmp = []
                for _ in range(27):
                    line = next(f)
                    tmp.append(float(line.split()[-1]))
                derivatives.append(tmp)

    freqs = np.array(freqs)
    derivatives = np.array(derivatives)

    return derivatives, freqs
