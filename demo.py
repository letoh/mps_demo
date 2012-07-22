#!/usr/bin/python
# coding: utf-8

class Word(object):
	def __init__(s, text):
		s.text = text

class Node(object):
	def __init__(s, level = 0):
		s.words = None
		s.next = None
		s.level = level

	def __addword(s, text, trace = []):
		if not s.level: return
		if s.words is None: s.words = []
		s.words.append(text)

	def insert(s, seq, text, trace = []):
		if not seq:
			s.__addword(text, trace)
			return

		if not s.next: s.next = {}

		cp = seq[0]
		if cp not in s.next:
			s.next[cp] = Node(s.level + 1)
		trace.append(cp)
		s.next[cp].insert(seq[1:], text, trace)
		trace.pop()

	def search(s, seq):
		if not seq:
			return s.words

		cp = seq[0]
		if cp not in s.next: return None
		return s.next[cp].search(seq[1:])

	def dump(s, trace = []):
		if s.words:
			print ''.join(trace), '[',
			for w in s.words: print w,
			print ']'
		if s.next is None: return

		for cp in s.next:
			n = s.next[cp]
			trace.append(cp)
			n.dump(trace)
			trace.pop()


def table_init(fn, limit = 0):
	tbl = Node()

	i = 0
	for line in open(fn):
		tok = line.strip().decode('utf-8').split(' ')
		tbl.insert(tok[0], tok[1])

		i += 1
		if limit and i > limit: break

	return tbl


def kblayout_init(fn):
	tbl = Node()

	for line in open(fn):
		tok = line.split(' ')
		tbl.insert(tok[1].strip(), tok[0])

	return tbl


class PreeditBuf(object):
	def __init__(s):
		s.buf = ['', '', '', '']

	def add(s, k):
		if k in " ˙ˊˇˋ":
			s.buf[3] = k
		elif k in "ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙ":
			s.buf[0] = k
		elif k in "ㄧㄨㄩ":
			s.buf[1] = k
		elif k in "ㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ":
			s.buf[2] = k
		else:
			return

	def pop(s):
		if s.buf[3] != '': s.buf[3] = ''; return True
		if s.buf[2] != '': s.buf[2] = ''; return True
		if s.buf[1] != '': s.buf[1] = ''; return True
		if s.buf[0] != '': s.buf[0] = ''; return True
		return False

	def flush(s):
		s.buf = ['', '', '', '']

	def __str__(s):
		return ''.join(s.buf)


class IMTableEngine(object):
	def __init__(s, fn, limit = 0):
		s.tbl = table_init(fn, limit)
		pass


class IMCtxt(object):
	def __init__(s):
		s.output = ""
		s.preedit = PreeditBuf()
		s.ime = None
		s.can = None
		s.commit = None
		pass


def keymap(fn):
	layout = kblayout_init(fn)
	def mapper(key):
		key1 = layout.search(key)
		if not key1: return key
		return key1[0]
	return mapper


def ime_key_press(ctxt, key):
	if ctxt.can:
		n = len(ctxt.can)
		if len(key) == 1 and key in '123456789'[:n]:
			ctxt.commit = ctxt.can[int(key) - 1]
			ctxt.can = None
			return True
		return False
	if len(key) > 1 or key == ' ':
		ctxt.preedit.add(key)
		# end key
		if key in " ˇˋˊ˙":
			seq = str(ctxt.preedit) \
					.replace('˙', '1').replace('ˊ', '2') \
					.replace('ˇ', '3') .replace('ˋ', '4').replace(' ', '')
			if not ctxt.ime or not ctxt.ime.tbl: return True
			# commit
			ctxt.can = ctxt.ime.tbl.search(seq.decode('utf-8'))
			if ctxt.can is None: return True
			if len(ctxt.can) == 1:
				ctxt.commit = ctxt.can[0]
				ctxt.can = None
		return True
	return False


def imf_key_press(ctxt, key):
	if len(key) == 1:
		if ord(key) == 0x7f:
			ctxt.can = None
			ret = ctxt.preedit.pop()
			if not ret and len(ctxt.output):
				ctxt.output = ctxt.output[:-1]
				ret = True
			return ret
		elif key == ' ':
			seq = str(ctxt.preedit)
			ctxt.can = ctxt.ime.tbl.search(seq.decode('utf-8'))
			if ctxt.can is None: return True
			if len(ctxt.can) == 1:
				ctxt.commit = ctxt.can[0]
				ctxt.can = None
			return True
	return False


if __name__ == '__main__':
	from conio import *

	keymapper = keymap('zo.kbmsrc')
	ctxt = IMCtxt()
	ctxt.ime = IMTableEngine('pho.tab2.src')

	def display(ctxt):
		clear()
		if ctxt.commit:
			ctxt.output = ctxt.output + ctxt.commit
			ctxt.commit = None
			ctxt.preedit.flush()
		if ctxt.output:
			print ctxt.output,
		if ctxt.can:
			print '<<', ', '.join(map(lambda x: str(x[0]) + ' ' + x[1],
				zip([i for i in xrange(1, len(ctxt.can) + 1)], ctxt.can))), '>>',
		else:
			print ctxt.preedit,

	cbreak(); echo(False)
	try:
		while 1:
			display(ctxt)
			key = getch()
			if not ctxt.can:
				key = keymapper(key)

			# ime_key_press
			if ime_key_press(ctxt, key): continue
			# imf_key_press
			if imf_key_press(ctxt, key): continue
	except Exception, e:
		print 'error:', e
	except:
		pass

	cbreak(False); echo()

	pass


