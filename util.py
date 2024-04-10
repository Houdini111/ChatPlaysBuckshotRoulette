from time import sleep

def waitForFalse(checker):
	print("Waiting for method to return false")
	i = 0
	while checker():
		i += 1
		#print(f"Waiting for method to return false. Attempts: {i}", end='\r')
		print(f"Waiting for method to return false. Attempts: {i}")
		sleep(0.1)

def waitForTrue(checker):
	print("Waiting for method to return true")
	i = 0
	while not checker():
		i += 1
		#print(f"Waiting for method to return true. Attempts: {i}", end='\r')
		print(f"Waiting for method to return true. Attempts: {i}")
		sleep(0.1)