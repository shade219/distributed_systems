#! python3

# Timed threads demo using a target function and anonymous Thread objects

def print_then_sleep(data, count, delay):
	time.sleep(delay)
	# loop -- print data count times
	for i in range(count):
		print( data )
		time.sleep(2)
		
if __name__ == "__main__":
	import threading, time
	threading.Thread( target= print_then_sleep, args= ('sleepy1',3,0) ).start()
	threading.Thread( target= print_then_sleep, args= ('sleepy2',3,0) ).start()

