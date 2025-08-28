## Command Line Usage

You can use the package directly from the command line with the following commands:

```powershell
# Show help and usage
python -m qrngtools --help

# Generate a random bit
python -m qrngtools --type bit

# Generate a string of 16 random bits
python -m qrngtools --type bits --length 16

# Generate a random integer in [0, 1000)
python -m qrngtools --type int --max 1000

# Generate a random float in [0, 1)
python -m qrngtools --type float

# Generate a random string of length 12
python -m qrngtools --type string --length 12

# Generate 8 random bytes
python -m qrngtools --type bytes --length 8

# Generate a random boolean value
python -m qrngtools --type bool

# Pick a random element from a sequence
python -m qrngtools --type choice --seq A B C D

# Pick 2 unique random elements from a sequence
python -m qrngtools --type sample --seq A B C D --k 2

# Generate a random UUID
python -m qrngtools --type uuid

# Generate a 3x3 matrix of random floats
python -m qrngtools --type matrix --rows 3 --cols 3

# Generate a random permutation of a sequence
python -m qrngtools --type permutation --seq A B C D

# Generate a list of 10 random bits
python -m qrngtools --type bit_array --length 10

# Generate a list of 10 random floats
python -m qrngtools --type float_array --length 10

# Add --with-source to any command to show the randomness source
python -m qrngtools --type int --max 1000 --with-source
```

# qrngtools

Quantum random number generation using IBM Quantum (Qiskit) and AerSimulator.

## 1. Environment Setup (Recommended)

Create and activate a clean Python environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2. Install the Package

Install from PyPI:

```powershell
pip install qrngtools
```

## 3. (Optional) Set Up IBM Quantum Cloud Backend

Set your IBM Quantum API token as an environment variable:

**Windows PowerShell:**

```powershell
$env:IBM_QUANTUM_TOKEN="your_token_here"
```

**Windows Command Prompt:**

```cmd
set IBM_QUANTUM_TOKEN=your_token_here
```

If the token is set and the IBM provider is available, the package will use the IBM Quantum cloud backend. Otherwise, it defaults to AerSimulator (local quantum simulation).

## 4. Usage

Import and use the API functions:

```python
from qrngtools import get_random_bit, get_random_bits, get_random_int, get_random_float, get_random_string

# By default, functions return only the random value
print(get_random_bit())      # 0 or 1
print(get_random_bits(8))    # e.g. '01101001'
print(get_random_int(100))   # random int in [0, 100)
print(get_random_float())    # random float in [0, 1)
print(get_random_string(10)) # e.g. 'aB3kLmP9Qz'

# To get the randomness source as well, pass with_source=True
bit, source = get_random_bit(with_source=True)
print(bit, source)           # e.g. 1, 'quantum' or 'system'
```

## 5. CLI Usage

Generate a quantum random integer from the command line:

```powershell
python -m qrngtools
```

## 6. Fallback

If Qiskit or AerSimulator is unavailable, the package automatically falls back to system randomness.
