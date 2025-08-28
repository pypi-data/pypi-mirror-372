#!/usr/bin/env python3
# aurora_console.py
import sys
sys.path.append(r'C:\Users\p_m_a\Aurora\Trinity-3')
import argparse, json
from allcode3new import Trigate, Transcender          # importa tu núcleo

def run_trigate(args):
    A = [int(x) if x != 'N' else None for x in args.A]
    B = [int(x) if x != 'N' else None for x in args.B]
    M = [int(x) if x != 'N' else None for x in args.M]
    tri = Trigate()
    if args.mode == 'infer':
        print(json.dumps(tri.infer(A, B, M)))
    elif args.mode == 'learn':
        print(json.dumps(tri.learn(A, B, M)))
    else:                       # synth = default
        print(json.dumps(tri.synthesize(A, B)))

def run_transcender(args):
    t = Transcender()
    A = [[int(c) for c in args.A[i:i+3]] for i in (0,3,6)]
    B = [[int(c) for c in args.B[i:i+3]] for i in (0,3,6)]
    C = [[int(c) for c in args.C[i:i+3]] for i in (0,3,6)]
    print(json.dumps(t.compute_vector_trio(A[0],B[0],C[0])))

p = argparse.ArgumentParser()
sub = p.add_subparsers(dest='cmd')

tri_p = sub.add_parser('trigate')
tri_p.add_argument('mode', choices=['infer','learn','synth'])
tri_p.add_argument('A'); tri_p.add_argument('B'); tri_p.add_argument('M')
tri_p.set_defaults(func=run_trigate)

tr_p = sub.add_parser('trio')
tr_p.add_argument('A'); tr_p.add_argument('B'); tr_p.add_argument('C')
tr_p.set_defaults(func=run_transcender)

args = p.parse_args()
if not hasattr(args, 'func'):
    p.print_help()
    exit(1)
args.func(args)
