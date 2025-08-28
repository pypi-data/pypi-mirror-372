
import argparse
from qrngtools import (
    get_random_bit, get_random_bits, get_random_int, get_random_float,
    get_random_string, get_random_bytes, get_random_bool, get_random_choice,
    get_random_sample, get_random_uuid, get_random_bit_array,
    get_random_coin, get_random_dice, get_random_prime, get_random_otp,
    get_random_gauss, get_random_float_array, get_random_matrix
)

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate quantum random numbers using Qiskit and IBM Quantum.\n"
            "\n"
            "You can generate a variety of quantum random values, including bits, integers, floats, strings, coins, dice, primes, OTPs, arrays, matrices, and more.\n"
            "Advanced options are available for arrays, matrices, and statistical distributions.\n"
            "\n"
            "Examples:\n"
            "  python -m qrngtools --type int --max 100\n"
            "  python -m qrngtools --float-array 5\n"
            "  python -m qrngtools --matrix 3 3\n"
            "  python -m qrngtools --gauss 0 1\n"
            "\n"
        )
    )

    parser.add_argument('--type', choices=[
        'bit', 'bits', 'int', 'float', 'string', 'bytes', 'bool', 'choice', 'sample', 'uuid', 'bit_array', 'coin', 'dice', 'prime', 'otp'
    ], help='Type of quantum random value to generate (e.g., int, float, string, dice, prime, otp, etc.)')
    parser.add_argument('--bits', type=int, help='Bit length for prime number generation (used with --type prime)')
    parser.add_argument('--sides', type=int, help='Number of sides for dice (used with --type dice, default 6)')
    parser.add_argument('--length', type=int, help='Length for string, bits, bytes, array, or OTP (used with --type string, bits, bytes, bit_array, otp)')
    parser.add_argument('--max', type=int, help='Maximum value for integer (used with --type int)')
    parser.add_argument('--seq', nargs='+', help='Sequence to choose/sample from (used with --type choice, sample)')
    parser.add_argument('--k', type=int, help='Number of samples to select (used with --type sample)')
    parser.add_argument('--with-source', action='store_true', help='Show the randomness source (quantum or system)')
    parser.add_argument('--float-array', nargs=1, metavar='N', type=int, help='Generate a quantum random float array of length N')
    parser.add_argument('--matrix', nargs=2, metavar=('ROWS', 'COLS'), type=int, help='Generate a quantum random float matrix of size ROWS x COLS')
    parser.add_argument('--gauss', nargs=2, metavar=('MU', 'SIGMA'), type=float, help='Generate a quantum random Gaussian float with mean MU and standard deviation SIGMA')
    args = parser.parse_args()

    # Dispatch based on CLI options
    if args.float_array:
        n = args.float_array[0]
        arr = get_random_float_array(n)
        print(f"Quantum random float array ({n}): {arr}")
        return
    if args.matrix:
        rows, cols = args.matrix
        matrix = get_random_matrix(rows, cols)
        print(f"Quantum random float matrix ({rows}x{cols}): {matrix}")
        return
    if args.gauss:
        mu, sigma = args.gauss
        val = get_random_gauss(mu, sigma)
        print(f"Quantum random Gaussian float (mu={mu}, sigma={sigma}): {val}")
        return
    if args.type:
        if args.type == 'bit':
            result = get_random_bit(with_source=args.with_source)
        elif args.type == 'bits':
            n = args.length or 8
            result = get_random_bits(n, with_source=args.with_source)
        elif args.type == 'int':
            max_val = args.max or 100
            result = get_random_int(max_val, with_source=args.with_source)
        elif args.type == 'float':
            result = get_random_float(with_source=args.with_source)
        elif args.type == 'string':
            n = args.length or 10
            result = get_random_string(n, with_source=args.with_source)
        elif args.type == 'bytes':
            n = args.length or 8
            result = get_random_bytes(n, with_source=args.with_source)
        elif args.type == 'bool':
            result = get_random_bool(with_source=args.with_source)
        elif args.type == 'choice':
            seq = args.seq or ['A', 'B', 'C']
            result = get_random_choice(seq, with_source=args.with_source)
        elif args.type == 'sample':
            seq = args.seq or ['A', 'B', 'C', 'D']
            k = args.k or 2
            result = get_random_sample(seq, k, with_source=args.with_source)
        elif args.type == 'uuid':
            result = get_random_uuid(with_source=args.with_source)
        elif args.type == 'bit_array':
            n = args.length or 8
            result = get_random_bit_array(n, with_source=args.with_source)
        elif args.type == 'coin':
            result = get_random_coin(with_source=args.with_source)
        elif args.type == 'dice':
            sides = args.sides or 6
            result = get_random_dice(with_source=args.with_source, sides=sides)
        elif args.type == 'prime':
            bits = args.bits or 16
            result = get_random_prime(bits, with_source=args.with_source)
        elif args.type == 'otp':
            n = args.length or 6
            result = get_random_otp(n, with_source=args.with_source)
        else:
            parser.print_help()
            return
        print(result)
        return
    parser.print_help()

if __name__ == '__main__':
    main()
