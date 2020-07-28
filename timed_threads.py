#! python

# Timed threads demo using identified Thread objects

import sleepy
sleepy1= sleepy.Sleepy( 'sleepy1', 3, 0 )
sleepy2= sleepy.Sleepy( 'sleepy2', 3, 1 )
sleepy1.start()
sleepy2.start()
