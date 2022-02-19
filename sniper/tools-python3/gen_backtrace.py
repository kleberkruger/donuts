#!/usr/bin/env python3

import sys, os, env_setup, addr2line

if len(sys.argv) > 1:
  if sys.argv[1] == '-':
    data = sys.stdin.readlines()
  else:
    data = file(sys.argv[1])
else:
  data = file('debug_backtrace.out')

objname = data.next().strip()
marker = int(next(data))
backtrace = data.next().split()
message = next(data)

if objname == 'sniper':
  bin = os.path.join(env_setup.sim_root(), 'lib', 'sniper')
elif objname == 'pin_sim.so':
  bin = os.path.join(env_setup.sim_root(), 'lib', 'pin_sim.so')
elif objname == 'sift_recorder':
  bin = os.path.join(env_setup.sim_root(), 'sift', 'recorder', 'sift_recorder')
else:
  print('Unknown object name', objname, file=sys.stderr)

a2l = addr2line.Addr2Line(bin, marker)

print('-'*60)
print(message)
print('Backtrace:')
for addr in backtrace:
  (file, function, line) = a2l.addr2line(addr)
  print('   ', ':'.join((file, function, line)).strip())
print('-'*60)
