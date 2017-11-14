import cpu_usage

for i in range(-1, 9):
	if i == 8:
		n = None
	else:
		n = i
	x = cpu_usage.deltaTime(1, n)
	if i == -1:
		print(i)
		for y in x:
			print(y)
	else:
		print('{} {}'.format(n if not n is None else 'all', x))

print("All cpu usage:")
print(cpu_usage.getCpuLoad(-1))
