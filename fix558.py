import sys

path = '/root/moto/scripts/gpx_generator.py'
lines = open(path, 'r').readlines()

idx = 557
line = lines[idx]
print('Before:', repr(line))

lines[idx] = '        batch_process = globals().get("batch_process")\n'
print('After:', repr(lines[idx]))

open(path, 'w').writelines(lines)
print('Done')
