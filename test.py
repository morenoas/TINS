import time
import os

# print('hello world!')

# for i in range(1, 12, 3):
#     print(i)

# now1 = time.time()
# time.sleep(2)
# now2 = time.time()
# sum = now2 - now1
# print(sum)
# print(type(sum))

# f = open("demofile.txt", "r")

# print(f.read())
# print(f.readline())
# print(f.readline())


# os.remove("demofile.txt")

filename = "Client.py"
os.chmod(filename, 0o777)
executable = os.access(filename, os.X_OK)
print(executable)
