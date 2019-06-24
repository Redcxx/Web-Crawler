



# take first and second file and write their different to the third file
import sys, os

if sys.argv[1] and sys.argv[2] and sys.argv[3]:
    with open(sys.argv[1], 'r', encoding='utf-8') as file1, open(sys.argv[2], 'r', encoding='utf-8') as file2, open(sys.argv[3], 'w', encoding='utf-8') as output:
        print(sys.argv[1])
        print(sys.argv[2])
        print(sys.argv[3])
        lines1 = set(file1.readlines())
        lines2 = set(file2.readlines())
        count = 0
        for line in lines1.symmetric_difference(lines2):
            output.write(line + os.linesep)
            count += 1
        print('done', count)
