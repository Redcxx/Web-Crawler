import sys
print(sys.stdout.encoding)
sys.stdout.reconfigure(encoding='utf-8')
print(sys.stdout.encoding)
