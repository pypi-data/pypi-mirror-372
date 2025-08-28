
import math
import os
import secrets
from typing import Optional

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    from qiskit_ibm_provider import IBMProvider
    QISKIT_AVAILABLE = True
except ImportError as e:
    print(f"Qiskit import error: {e}")
    QISKIT_AVAILABLE = False


TOKEN_ENV_VAR = "IBM_QUANTUM_TOKEN"


class QuantumRNG:
    def __init__(self):
        self.backend = None
        self.service = None
        self._setup_backend()


    def _setup_backend(self):
        if not QISKIT_AVAILABLE:
            print("Qiskit not available. Using system randomness.")
            self.backend = None
            return

        # Prefer AerSimulator by default
        try:
            self.backend = AerSimulator()
            print("Using local AerSimulator backend.")
        except Exception as e:
            print(f"AerSimulator not available: {e}. Using system randomness.")
            self.backend = None

        # Allow IBM Quantum cloud only if user provides token and package is installed
        token = os.environ.get(TOKEN_ENV_VAR)
        if token:
            try:
                provider = IBMProvider(token=token)
                self.backend = provider.get_backend("ibm_brisbane")
                print(f"Using IBM Quantum cloud backend: {self.backend.name}")
            except Exception as e:
                print(f"Could not use IBM Quantum cloud backend: {e}. Continuing with AerSimulator.")



    def get_random_bit(self):
        if self.backend:
            qc = QuantumCircuit(1, 1)
            qc.h(0)
            qc.measure(0, 0)
            tqc = transpile(qc, self.backend)
            job = self.backend.run(tqc, shots=1)
            result = job.result()
            counts = result.get_counts()
            return int(list(counts.keys())[0]), "quantum"
        else:
            return secrets.randbits(1), "system"


    def get_random_bits(self, n: int):
        if self.backend:
            qc = QuantumCircuit(1, 1)
            qc.h(0)
            qc.measure(0, 0)
            tqc = transpile(qc, self.backend)
            job = self.backend.run(tqc, shots=n)
            result = job.result()
            counts = result.get_counts()
            bits = ""
            for k, v in counts.items():
                bits += k * v
            return bits[:n], "quantum"
        else:
            return ''.join(str(secrets.randbits(1)) for _ in range(n)), "system"


    def get_random_int(self, max_val: int):
        n_bits = max_val.bit_length()
        while True:
            bits, source = self.get_random_bits(n_bits)
            val = int(bits, 2)
            if val < max_val:
                return val, source


    def get_random_float(self):
        bits, source = self.get_random_bits(53)
        val = int(bits, 2)
        return val / (1 << 53), source


    def get_random_bytes(self, n: int):
        """Return n random bytes."""
        bits, source = self.get_random_bits(n * 8)
        return int(bits, 2).to_bytes(n, 'big'), source


    def get_random_bool(self):
        """Return a random boolean value."""
        bit, source = self.get_random_bits(1)
        return bool(bit), source


    def get_random_choice(self, seq):
        """Return a random element from a sequence."""
        idx, source = self.get_random_int(len(seq))
        return seq[idx], source


    def get_random_sample(self, seq, k):
        """Return k unique random elements from a sequence."""
        seq = list(seq)
        result = []
        sources = []
        while len(result) < k and seq:
            choice, source = self.get_random_choice(seq)
            result.append(choice)
            sources.append(source)
            seq.remove(choice)
        return result, sources[0] if sources else "system"


    def get_random_string(self, length: int, charset: Optional[str] = None):
        """Return a random string of given length from charset."""
        if charset is None:
            charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        chars = []
        sources = []
        for _ in range(length):
            c, source = self.get_random_choice(charset)
            chars.append(c)
            sources.append(source)
        return ''.join(chars), sources[0] if sources else "system"


    def get_random_uuid(self):
        """Return a random UUID string."""
        import uuid
        random_bytes, source = self.get_random_bytes(16)
        return str(uuid.UUID(bytes=random_bytes)), source


    def get_random_matrix(self, rows: int, cols: int):
        """Return a matrix of quantum random floats."""
        matrix = []
        sources = []
        for _ in range(rows):
            row = []
            for _ in range(cols):
                val, source = self.get_float()
                row.append(val)
                sources.append(source)
            matrix.append(row)
        return matrix, sources[0] if sources else "system"


    def get_random_permutation(self, seq):
        """Return a random permutation of a sequence."""
        seq = list(seq)
        result = []
        sources = []
        while seq:
            choice, source = self.get_random_choice(seq)
            result.append(choice)
            sources.append(source)
            seq.remove(choice)
        return result, sources[0] if sources else "system"


    def get_random_bit_array(self, n: int):
        """Return a list of n random bits."""
        bits, source = self.get_random_bits(n)
        return [int(b) for b in bits], source



    def get_random_source(self):
        """Return the current randomness source: 'quantum' or 'system'."""
        return "quantum" if self.backend else "system"

_rng = QuantumRNG()



def get_random_bit(with_source=False):
    """Return a single quantum random bit (0 or 1). If with_source=True, return (value, source)."""
    val, source = _rng.get_random_bit()
    return (val, source) if with_source else val

def get_random_bits(n: int, with_source=False):
    """Return a string of n quantum random bits. If with_source=True, return (value, source)."""
    val, source = _rng.get_random_bits(n)
    return (val, source) if with_source else val

def get_random_int(max_val: int, with_source=False):
    """Return a quantum random integer in [0, max_val). If with_source=True, return (value, source)."""
    val, source = _rng.get_random_int(max_val)
    return (val, source) if with_source else val

def get_random_float(with_source=False):
    """Return a quantum random float in [0, 1). If with_source=True, return (value, source)."""
    val, source = _rng.get_random_float()
    return (val, source) if with_source else val

def get_random_bytes(n: int, with_source=False):
    """Return n quantum random bytes. If with_source=True, return (value, source)."""
    val, source = _rng.get_random_bytes(n)
    return (val, source) if with_source else val

def get_random_bool(with_source=False):
    """Return a quantum random boolean value. If with_source=True, return (value, source)."""
    val, source = _rng.get_random_bool()
    return (val, source) if with_source else val

def get_random_choice(seq, with_source=False):
    """Return a quantum random element from a sequence. If with_source=True, return (value, source)."""
    val, source = _rng.get_random_choice(seq)
    return (val, source) if with_source else val

def get_random_sample(seq, k, with_source=False):
    """Return k unique quantum random elements from a sequence. If with_source=True, return (value, source)."""
    val, source = _rng.get_random_sample(seq, k)
    return (val, source) if with_source else val

def get_random_string(length: int, charset: Optional[str] = None, with_source=False):
    """Return a quantum random string of given length from charset. If with_source=True, return (value, source)."""
    val, source = _rng.get_random_string(length, charset)
    return (val, source) if with_source else val

def get_random_uuid(with_source=False):
    """Return a quantum random UUID string. If with_source=True, return (value, source)."""
    val, source = _rng.get_random_uuid()
    return (val, source) if with_source else val


def get_random_bit_array(n: int, with_source=False):
    """Return a list of n quantum random bits. If with_source=True, return (value, source)."""
    val, source = _rng.get_random_bit_array(n)
    return (val, source) if with_source else val

def get_random_coin(with_source=False):
    """Return 'heads' or 'tails' as a quantum random coin flip. If with_source=True, return (value, source)."""
    bit, source = get_random_bit(with_source=True)
    result = 'heads' if bit == 0 else 'tails'
    return (result, source) if with_source else result

def get_random_dice(with_source=False, sides=6):
    """Return a quantum random dice roll in [1, sides]. If with_source=True, return (value, source)."""

    val, source = get_random_int(sides, with_source=True)
    result = val + 1
    return (result, source) if with_source else result

def _is_prime(n, k=5):
    """Miller-Rabin primality test."""
    if n == 2 or n == 3:
        return True
    if n < 2 or n % 2 == 0:
        return False
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    import random
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def get_random_prime(bits: int, with_source=False):
    """Generate a random prime number of the given bit length using quantum randomness."""
    if bits < 2:
        raise ValueError("Bit length must be >= 2")
    while True:
        candidate, source = get_random_bits(bits, with_source=True)
        n = int(candidate, 2) | 1  # Ensure odd
        if _is_prime(n):
            return (n, source) if with_source else n

def get_random_otp(length=6, charset='0123456789', with_source=False):
    """Return a quantum random OTP of given length and charset. If with_source=True, return (value, source)."""
    return get_random_string(length, charset, with_source=with_source)

def get_random_gauss(mu=0.0, sigma=1.0, with_source=False):
    """Return a quantum random float based on the Gaussian distribution N(mu, sigma^2). If with_source=True, return (value, source)."""
    # Use Box-Muller transform with quantum random floats
    u1, source1 = get_random_float(with_source=True)
    u2, source2 = get_random_float(with_source=True)
    z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    value = mu + z0 * sigma
    source = source1 if source1 == 'quantum' or source2 == 'quantum' else 'system'
    return (value, source) if with_source else value

def get_random_float_array(n, with_source=False):
    """Return a list of n quantum random floats. If with_source=True, return (value, source)."""
    arr = []
    sources = []
    for _ in range(n):
        val, source = get_random_float(with_source=True)
        arr.append(val)
        sources.append(source)
    return (arr, sources[0] if sources else "system") if with_source else arr

def get_random_matrix(rows, cols, with_source=False):
    """Return a matrix (list of lists) of quantum random floats. If with_source=True, return (value, source)."""
    matrix = []
    sources = []
    for _ in range(rows):
        row = []
        for _ in range(cols):
            val, source = get_random_float(with_source=True)
            row.append(val)
            sources.append(source)
        matrix.append(row)
    return (matrix, sources[0] if sources else "system") if with_source else matrix