import matplotlib.pyplot as plt

with open("./n4test.txt", "r") as f: #change file as needed
	raws = f.readlines()

time = []
voltage = []

for i in raws:
	tmp = i.split(", ")
	time.append(float(tmp[0]))
	voltage.append(float(tmp[1]))

plt.plot(time, voltage)
plt.show()
