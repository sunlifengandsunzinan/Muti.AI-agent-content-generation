lines = open('/root/moto/scripts/gpx_generator.py', 'r').readlines()
line = lines[599]
print('Before:', repr(line))
lines[599] = '        batch_process = globals().get("batch_process")\n'
open('/root/moto/scripts/gpx_generator.py', 'w').writelines(lines)
print('After:', repr(lines[599]))
print('Fixed')
