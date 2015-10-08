import re, sys

class student:
	def __init__(self, delString):
		self.name = delString[1]
		self.netId = delString[18]
		
		self.email = delString[2]
		self.sponsoredPicks = self.parse_choices(delString[3])
		self.normalPicks = self.parse_choices(delString[21])
		
		self.work_with = self.parse_people(delString[17].strip())
		self.not_work_with = self.parse_people(delString[19].strip())
		
		#print self.work_with, self.not_work_with
	
	def parse_choices(self, strToParse):
		p = re.compile(ur'([\d+.]*\d+)')
		numExtract = re.findall(p, strToParse)
		
		if len(numExtract) > 0:
			return numExtract
			
		first_word = strToParse.split(' ')[0].lower()
		if 'no' in first_word or 'n\a' in first_word or 'n/a' in first_word:
			return []
			
		return [strToParse]
	
	def parse_people(self, strToParse):
		p = re.compile(ur'[a-z]{3,8}[0-9]{1,3}')
		netid_extract = re.findall(p, strToParse)
		
		if len(netid_extract) > 0:
			return netid_extract
			
		first_word = strToParse.split(' ')[0].lower()
		
		# For now if I don't see any netids, nuke errythings
		#if 'no' in first_word or 'n\a' in first_word or 'n/a' in first_word:
		return []
			
		#return [strToParse]
		
	def __str__(self):
		return stu.name + ',' + stu.netId + ',' + stu.email + ',' + ' '.join(stu.sponsoredPicks) + ',' + ' '.join(stu.normalPicks) + ',' + ' '.join(stu.work_with) + ',' + ' '.join(stu.not_work_with)

f = open(sys.argv[1], 'r')
data = f.read().split('\n')
f.close()

w = open('identifyingFiles/parsedStudents.csv', 'w')
w.write('name, netid, email, sponsored picks (space delimited), non-sponsored picks (space delimited), wants to work with (space delimited), doesn\'t want to work with (space delimited)\n')
for dat in data[1:]:
	stu = student(dat.split('\t'))
	w.write(str(stu) + '\n')
w.close()