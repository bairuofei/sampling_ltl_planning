import time

time_start = time.time()
for i in range(10):
    time.sleep(1)
time_end = time.time()
print(time_end-time_start)
