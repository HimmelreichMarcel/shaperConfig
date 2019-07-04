import os

with open("values.txt", "r") as file:
    data = file.read().replace(' ', '\n').replace("\"","")

f = open("metric.txt", "w+")
for line in data:
    f.write(line)

f.close()
