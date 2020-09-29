import sys
import os

def isChar(string, index):
	if (string[index].isdigit() or string[index].isalpha()):
		return True
	return False

def isSpecial(string, index):
	if (string[index].isdigit() or string[index].isalpha()):
		return False
	elif (string[index] == '<' or string[index] == '>' or string[index] == '(' or string[index] == ')' or string[index] == '['
		or string[index] == ']' or string[index] == '\\' or string[index] == '.' or string[index] == ',' or string[index] == ';'
		or string[index] == ':' or string[index] == '@' or string[index] == '"' or string[index] == ' ' or string[index] == '\t' or string[index] == '\n'):
		return True
	return False

def nullspace(string, index):
	while index < len(string):
		if (string[index] == '\t' or string[index] == ' '):
			index+=1
		else:
			return index
	return 0

def whitespace(string, index):
	if (string[index] != ' ' and string[index] != '\t'):
		return 0
	return nullspace(string, index + 1)

def element(string, index):
	if (not string[index].isalpha()):
		return 0
	while index < len(string):
		if not isChar(string, index):
			return index
		index += 1
	return 0

def domain(string, index):
	while index < len(string):
		index = element(string, index)
		if (index == 0):
			return 0
		elif (string[index] == '.'):
			index += 1
		elif not isChar(string, index) and string[index] != '>':
			return 0
		else:
			return index
	return 0

def localpart(string, index):
	if string[index] == '@':
		return 0
	while index < len(string):
		if (isSpecial(string, index)):
			return index
		else:
			index += 1
	return 0

def mailbox(string, index):
	index = localpart(string, index)
	if (index == 0):
		print("501 Syntax error in parameters or arguments")
		return 0
	if (string[index] != '@'):
		print("501 Syntax error in parameters or arguments")
		return 0
	index = domain(string, index + 1)
	if (index == 0):
		print("501 Syntax error in parameters or arguments")
		return 0
	return index

def path(string, index):
	if (string[index] != '<'):
		print("501 Syntax error in parameters or arguments")
		return 0
	index = mailbox(string, index + 1)
	if (index == 0):
		return 0
	if (string[index] != '>'):
		print("501 Syntax error in parameters or arguments")
		return 0
	out = index
	index = nullspace(string, index + 1)
	if (string[index] != '\n'):
		print("501 Syntax error in parameters or arguments")
		return 0
	return out

def mailfrom(string):
	if (string[0:8] == "RCPT TO:" or string[0:4] == "DATA"):
		print("503 Bad sequence of commands")
		return 0
	if string[0:4] != "MAIL":
		print("500 Syntax error: command unrecognized")
		return 0
	index = whitespace(string, 4)
	if (index == 0):
		print("500 Syntax error: command unrecognized")
		return 0
	if string[index:index+5] != "FROM:":
		print("500 Syntax error: command unrecognized")
		return 0
	index = nullspace(string, index + 5)
	out = path(string, index)
	if (out == 0):
		return 0
	else:
		print("250 OK")
		return string[index+1:out]

def rcptTo(string, first):
	if first and string[0:4] == "DATA":
		print("503 Bad sequence of commands")
		return 0
	if string[0:4] != "RCPT":
		if string[0:10] == "MAIL FROM:":
			print("503 Bad sequence of commands")
			return 0
		print("500 Syntax error: command unrecognized")
		return 0
	index = whitespace(string, 4)
	if string[index:index+3] != "TO:":
		print("500 Syntax error: command unrecognized")
		return 0
	index = nullspace(string, index + 3)
	out = path(string, index)
	if (out == 0):
		return 0
	else:
		print("250 OK")
		return string[index+1:out]

def data(string):
	if string[0:4] != "DATA":
		if (string[0:4] == "MAIL"):
			print("503 Bad sequence of commands")
			return 0
		print("500 Syntax error: command unrecognized")
		return 0
	index = nullspace(string, 4)
	if string[index] != "\n":
		errorMessage("DATA")
		return 0
	print("354 Start mail input; end with <CRLF>.<CRLF>")
	return

def message(string):
	if string[0] == "." and string[1] == "\n":
		print("250 OK")
		return 0

while True:
	sender = ""
	receivers = []
	messages = []
	if not os.path.exists('forward'):
		os.system("mkdir forward")
	mail_from = sys.stdin.readline()
	if mail_from:
		sys.stdout.write(mail_from)
		sender = mailfrom(mail_from)
		if (sender == 0):
			continue
		first = True
		while True:
			rcpt_to = sys.stdin.readline()
			if (first):
				sys.stdout.write(rcpt_to)
				recipient = rcptTo(rcpt_to, first)
				if (recipient != 0):
					receivers.append(recipient)
					first = False
			elif rcpt_to[0:4] == "RCPT":
				sys.stdout.write(rcpt_to)
				recipient = rcptTo(rcpt_to, first)
				if (recipient != 0):
					receivers.append(recipient)
			else:
				data_tag = rcpt_to
				sys.stdout.write(data_tag)
				ex = data(data_tag)
				if ex == 0:
					continue
				while True:
					msg = sys.stdin.readline()
					sys.stdout.write(msg)
					ex = message(msg)
					if ex == 0:
						break
					messages.append(msg)
				break
		i = 0
		while i < len(receivers):
			j = 0
			file = open('forward/' + receivers[i], 'a')
			file.write('From: <' + sender + '>\n')
			r = 0
			while r < len(receivers):
				file.write('To: <' + receivers[r] + '>\n')
				r += 1
			while j < len(messages):
				file.write(messages[j])
				j += 1
			i += 1
	else:
		sys.exit(0)
