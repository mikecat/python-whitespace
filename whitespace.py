# Copyright (c) 2014 MikeCAT
#
# This software is provided 'as-is', without any express or implied warranty.
# In no event will the authors be held liable for any damages arising from the
# use of this software.
#
# Permission is granted to anyone to use this software for any purpose, including
# commercial applications, and to alter it and redistribute it freely, subject to
# the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not claim
#    that you wrote the original software. If you use this software in a product,
#    an acknowledgment in the product documentation would be appreciated but is
#    not required.
#
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
# 3. This notice may not be removed or altered from any source distribution.

import sys

# check if the stack contains at least needed elements
def check_stack(stack,needed):
	if len(stack)<needed:
		print("stack underflow")
		quit()
	return True

# execute translated programs
def run_whitespace(program,input,realtime_io=False):
	i=0
	commands=program[0]
	labels=program[1]
	stack=[]
	heap={}
	subroutine_stack=[]
	input_reading_pos=0
	now_input=[]
	output=""
	while i<len(commands):
		if commands[i][0]==11:
			stack.append(commands[i][1])
		elif commands[i][0]==12:
			check_stack(stack,1)
			stack.append(stack[-1])
		elif commands[i][0]==13:
			check_stack(stack,commands[i][1]+1)
			stack.append(stack[-1-commands[i][1]])
		elif commands[i][0]==14:
			check_stack(stack,2)
			temp=stack[-2]
			stack[-2]=stack[-1]
			stack[-1]=temp
		elif commands[i][0]==15:
			check_stack(stack,1)
			stack.pop()
		elif commands[i][0]==16:
			check_stack(stack,commands[i][1]+1)
			stack[-1-commands[i][1]:-1]=[]
		elif commands[i][0]==21:
			check_stack(stack,2)
			stack[-2]+=stack[-1]
			stack.pop()
		elif commands[i][0]==22:
			check_stack(stack,2)
			stack[-2]-=stack[-1]
			stack.pop()
		elif commands[i][0]==23:
			check_stack(stack,2)
			stack[-2]*=stack[-1]
			stack.pop()
		elif commands[i][0]==24:
			check_stack(stack,2)
			stack[-2]//=stack[-1]
			stack.pop()
		elif commands[i][0]==25:
			check_stack(stack,2)
			stack[-2]%=stack[-1]
			stack.pop()
		elif commands[i][0]==31:
			check_stack(stack,2)
			heap[stack[-2]]=stack[-1]
			stack.pop()
			stack.pop()
		elif commands[i][0]==32:
			check_stack(stack,1)
			if stack[-1] in heap:
				stack[-1]=heap[stack[-1]]
			else:
				stack[-1]=0
		elif commands[i][0]==41:
			True # do nothing
		elif commands[i][0]==42:
			subroutine_stack.append(i)
			if commands[i][1] not in labels:
				print("unknown label")
				quit()
			i=labels[commands[i][1]]
		elif commands[i][0]==43:
			if commands[i][1] not in labels:
				print("unknown label")
				quit()
			i=labels[commands[i][1]]
		elif commands[i][0]==44:
			check_stack(stack,1)
			if stack[-1]==0:
				if commands[i][1] not in labels:
					print("unknown label")
					quit()
				i=labels[commands[i][1]]
			stack.pop()
		elif commands[i][0]==45:
			check_stack(stack,1)
			if stack[-1]<0:
				if commands[i][1] not in labels:
					print("unknown label")
					quit()
				i=labels[commands[i][1]]
			stack.pop()
		elif commands[i][0]==46:
			if len(subroutine_stack)==0:
				print("return without call")
				quit()
			i=subroutine_stack[-1]
			subroutine_stack.pop()
		elif commands[i][0]==47:
			break
		elif commands[i][0]==51:
			check_stack(stack,1)
			if realtime_io:
				sys.stdout.write(chr(stack[-1]))
				sys.stdout.flush()
			output=output+chr(stack[-1])
			stack.pop()
		elif commands[i][0]==52:
			check_stack(stack,1)
			if realtime_io:
				sys.stdout.write(str(stack[-1]))
				sys.stdout.flush()
			output=output+str(stack[-1])
			stack.pop()
		elif commands[i][0]==53:
			check_stack(stack,1)
			if realtime_io:
				if now_input==[]:
					heap[stack[-1]]=ord(sys.stdin.read(1))
				else:
					heap[stack[-1]]=ord(now_input)
					now_input=[]
			else:
				if input_reading_pos<len(input):
					heap[stack[-1]]=ord(input[input_reading_pos])
					input_reading_pos+=1
				else:
					heap[stack[-1]]=-1
			stack.pop()
		elif commands[i][0]==54:
			check_stack(stack,1)
			now_number=0
			sign=1
			if realtime_io:
				while now_input==[] or now_input.isspace():
					now_input=sys.stdin.read(1)
				if now_input=="-":
					sign=-1
					now_input=sys.stdin.read(1)
				while now_input.isdigit():
					now_number=now_number*10+int(now_input)
					now_input=sys.stdin.read(1)
			else:
				while input_reading_pos<len(input) and input[input_reading_pos].isspace():
					input_reading_pos+=1
				if input_reading_pos<len(input) and input[input_reading_pos]=="-":
					sign=-1
					input_reading_pos+=1
				while input_reading_pos<len(input) and input[input_reading_pos].isdigit():
					now_number=now_number*10+int(input[input_reading_pos])
					input_reading_pos+=1
			heap[stack[-1]]=sign*now_number
			stack.pop()
		i+=1
	return output

# read the next number
def read_number_ws(str):
	ret=0
	i=1
	while i<len(str) and str[i]!="\n":
		ret*=2
		if str[i]=="\t":
			ret+=1
		i+=1
	if str[0]=="\t":
		ret=-ret
	return ret

# read the next label string
def read_label_ws(str):
	return str[:str.index("\n")]

# translate Whitespace program into a list of commands and labels
def compile_whitespace(pstr_raw):
	pstr=""
	for c in pstr_raw:
		if c==" " or c=="\t" or c=="\n":
			pstr=pstr+c
	i=0
	program=[]
	labels={}
	while i<len(pstr):
		pi=i
		if pstr[i]==" ":
			if pstr[i+1]==" ":
				program.append((11,read_number_ws(pstr[i+2:])))
				i+=2+len(read_label_ws(pstr[i+2:]))+1
			elif pstr[i+1]=="\n":
				if pstr[i+2]==" ":
					program.append((12,0))
					i+=3
				elif pstr[i+2]=="\t":
					program.append((14,0))
					i+=3
				elif pstr[i+2]=="\n":
					program.append((15,0))
					i+=3
			elif pstr[i+1]=="\t":
				if pstr[i+2]==" ":
					program.append((13,read_number_ws(pstr[i+3:])))
					i+=3+len(read_label_ws(pstr[i+3:]))+1
				elif pstr[i+2]=="\n":
					program.append((16,read_number_ws(pstr[i+3:])))
					i+=3+len(read_label_ws(pstr[i+3:]))+1
		elif pstr[i]=="\t" and pstr[i+1]==" ":
			if pstr[i+2]==" ":
				if pstr[i+3]==" ":
					program.append((21,0))
					i+=4
				elif pstr[i+3]=="\t":
					program.append((22,0))
					i+=4
				elif pstr[i+3]=="\n":
					program.append((23,0))
					i+=4
			elif pstr[i+2]=="\t":
				if pstr[i+3]==" ":
					program.append((24,0))
					i+=4
				elif pstr[i+3]=="\t":
					program.append((25,0))
					i+=4
		elif pstr[i]=="\t" and pstr[i+1]=="\t":
			if pstr[i+2]==" ":
				program.append((31,0))
				i+=3
			elif pstr[i+2]=="\t":
				program.append((32,0))
				i+=3
		elif pstr[i]=="\n":
			if pstr[i+1]==" ":
				if pstr[i+2]==" ":
					labels[read_label_ws(pstr[i+3:])]=len(program)
					program.append((41,read_label_ws(pstr[i+3:])))
					i+=3+len(read_label_ws(pstr[i+3:]))+1
				elif pstr[i+2]=="\t":
					program.append((42,read_label_ws(pstr[i+3:])))
					i+=3+len(read_label_ws(pstr[i+3:]))+1
				elif pstr[i+2]=="\n":
					program.append((43,read_label_ws(pstr[i+3:])))
					i+=3+len(read_label_ws(pstr[i+3:]))+1
			elif pstr[i+1]=="\t":
				if pstr[i+2]==" ":
					program.append((44,read_label_ws(pstr[i+3:])))
					i+=3+len(read_label_ws(pstr[i+3:]))+1
				elif pstr[i+2]=="\t":
					program.append((45,read_label_ws(pstr[i+3:])))
					i+=3+len(read_label_ws(pstr[i+3:]))+1
				elif pstr[i+2]=="\n":
					program.append((46,0))
					i+=3
			elif pstr[i+1]=="\n" and pstr[i+2]=="\n":
				program.append((47,0))
				i+=3
		elif pstr[i]=="\t" and pstr[i+1]=="\n":
			if pstr[i+2]==" ":
				if pstr[i+3]==" ":
					program.append((51,0))
					i+=4
				elif pstr[i+3]=="\t":
					program.append((52,0))
					i+=4
			elif pstr[i+2]=="\t":
				if pstr[i+3]==" ":
					program.append((53,0))
					i+=4
				elif pstr[i+3]=="\t":
					program.append((54,0))
					i+=4
		if pi==i:
			print("invalid program")
			quit()
	return (program,labels)

if len(sys.argv)==2:
	f=open(sys.argv[1],"r")
	program=""
	for line in f:
		program=program+line
	f.close()
	compiled_program=compile_whitespace(program)
	run_whitespace(compiled_program,"",True)
else:
	print("Usage: "+sys.argv[0]+" <program file>")
