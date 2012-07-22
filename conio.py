import sys, os
import termios

def gotoxy(y, x):
	sys.stdout.write('\x1b[%d;%dH' % (y, x))

def clear():
	sys.stdout.write('\x1b[2J')
	gotoxy(0, 0)

def getch():
	return sys.stdin.read(1)

def cbreak(enable = True):
	fd = sys.stdin.fileno()
	newattr = termios.tcgetattr(fd)
	if enable:
		newattr[3] = newattr[3] & ~termios.ICANON
	else:
		newattr[3] = newattr[3] | termios.ICANON
	termios.tcsetattr(fd, termios.TCSANOW, newattr)
	return

def echo(enable = True):
	fd = sys.stdin.fileno()
	newattr = termios.tcgetattr(fd)
	if enable:
		newattr[3] = newattr[3] | termios.ECHO
	else:
		newattr[3] = newattr[3] & ~termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, newattr)
	return


if __name__ == '__main__':
	cbreak()
	echo(False)
	print '> ',
	try:
		while 1:
			ch = getch()
			sys.stdout.write(ch)
	except:
		print 'exit'

	cbreak(False)
	echo()

