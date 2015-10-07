import random, copy, string, sys
from multiprocessing import Pool

"""

top three methods are helpers to generate data before I had any good info

"""

# Generate a fake netid
def makeNetid():
	netidString = ''.join((random.choice(string.ascii_lowercase) for x in range(5)))
	netidString += ''.join((random.choice(string.digits) for x in range(2)))
	return netidString

# Generate a list of discussions
def makeChoiceBucket():
	days = ['TH', 'FR']
	times = [x for x in range(8, 22, 2)]
	timesodd = [x for x in range(9, 23, 2)]
	bestTimes = [13, 14, 15, 16]
	#sections = ['S1','S2']

	bucket = []

	for x in days:
		for y in times:
				if y in bestTimes:
					bucket.append(x + ' ' + str(y))
				bucket.append(x + ' ' + str(y))

	for y in timesodd:
		if y in bestTimes:
			bucket.append('TH' + ' ' + str(y))
		bucket.append('TH' + ' ' + str(y))

	return bucket

# Generating arbitrary choices for fake students
def generateDataset(choices):
	f = open('sampleDataset', 'w')

	bucket = makeChoiceBucket()
	for x in range(205):
		netid = makeNetid()
		sections = []
		while len(sections) < choices:
			sec = random.choice(bucket)
			if sec not in sections:
				sections.append(sec)

		f.write(netid + ',' +' ' + ', '.join(sections) +  '\n')

# Calculating the score for this discussion section assignment
def prefsScore(disc):
	prefs = [0 for x in range(20)]
	highestChoice = 0
	for key, dis in disc.items():
		for i, disSec in enumerate(dis):
			for stu in disSec.students:
				prefs[stu.discussion] += 1
				if stu.discussion > highestChoice:
					highestChoice = stu.discussion

	score = 0
	prefs = prefs[:highestChoice+1]
	for i, pref in enumerate(prefs):
		score += pref * 2**(i*2)
	return prefs, score

# Student class
class student:
	def __init__(self, line):
		self.choices = []
		self.cannot = []
		# If they didn't follow the rules, I flag them
		self.redFlag = False

		data = line.split('"')
		nopes = []
		if len(data) > 1:
			nopes = data[-2].split(', ')
		data = data[0].split(',')
		
		self.netid = data[1].split('@')[0]
		yeps = data[2:]
		
		# Yeps are sections they want to do, nopes are the ones they cant
		for yep in yeps:
			if len(yep) > 1:
				yepLabels = yep.split(' ')
				day = 'TH' if yepLabels[0] == 'Thursday' else 'FR'
				timeString = yepLabels[2]
				time = int(timeString.split(':')[0])
				if time != 12 and 'pm' in timeString:
					time += 12
				
				self.choices.append(day + ' ' + str(time))

		for nope in nopes:
			if len(nope) > 1:
				nopeLabels = nope.split(' ')
				day = 'TH' if nopeLabels[0] == 'Thursday' else 'FR'
				timeString = nopeLabels[2]
				time = int(timeString.split(':')[0])
				if time != 12 and 'pm' in timeString:
					time += 12
				
				self.cannot.append(day + ' ' + str(time))

		if len(self.choices)!=len(set(self.choices)):
			self.redFlag = True
		self.ranking = 0
		self.discussion = 0

	def assignDiscussion(self, disc):
		self.discussion = self.choices.index(disc.time)

	def addRestOfChoices(self, discussions):
		# take list of discussions - choices - nope, scramble add to choices
		leftOver = list(set(discussions) - set(self.choices) - set(self.cannot))
		if len(leftOver) == 0:
			self.redFlag = True
		#	print self.netid
		for dis in scrambled(leftOver):
			self.choices.append(dis)

	def __repr__(self):
		return self.netid

# discussion class
class discussion:
	def __init__(self, line):
		self.name = line
		self.time = ' '.join(line.split(' ')[:2])
		self.students = []
		self.potentialStudents = []

	def isFull(self):
		return True if len(self.students) == 6 else False

	def addStudent(self, student):
		self.students.append(student)
		student.assignDiscussion(self)

	# crux of the marriage algorithm
	def askToGetIn(self, stu):
		maxStu = self.students[0]
		for disStu in self.students:
			if disStu.ranking > maxStu.ranking:
				maxStu = disStu
		if stu.ranking < maxStu.ranking:
			self.students.remove(maxStu)
			self.students.append(stu)
			stu.assignDiscussion(self)
			return (True, maxStu)
		else:
			return (False, None)


	def __repr__(self):
		return str(self.students) 

# get a random arrangement of the array
def scrambled(orig):
    dest = orig[:]
    random.shuffle(dest)
    return dest

# randomize algorithm to see if it would behave better
def randomizedAlgo(students, discussions):
	studentsAssigned = []
	studentsNotAssigned = []

	while len(students) > 0:
		stu = random.choice(students)
		assigned = False
		for dis in stu.choices:
			for disSec in discussions[dis]:
				if not disSec.isFull():
					disSec.addStudent(stu)
					assigned = True
					break;
			if assigned:
				studentsAssigned.append(stu)
				break;
		if not assigned:
			studentsNotAssigned.append(stu)
		students.remove(stu)

	return studentsAssigned, studentsNotAssigned


def marriage(students, discussions):
	# each discussion needs a "priority" list for the students it wants in its section. For the sake of consistency, every discussion has the same student ranking
	randoRanking = scrambled(students)

	for i, stu in enumerate(students):
		stu.ranking = randoRanking.index(stu)

	married = []
	notMarried = students
	unwantedStudents = []
	
	# whilst there are students to be married, try to add it into a discussion
	while len(notMarried) > 0:
		stu = random.choice(notMarried)
		unwanted = True
		for dis in stu.choices:
			noFreeSpots = True
			
			# add to first discussion based on student's preferences
			for disSec in discussions[dis]:
				if not disSec.isFull():
					disSec.addStudent(stu)
					
					married.append(stu)
					notMarried.remove(stu)
					noFreeSpots = False
					unwanted = False
					break;

			# we can ask to get into a discussion, if discussion has someone that's ranked lower, it will kick them out in favor of this student with a higher rank
			if noFreeSpots:
				for disSec in discussions[dis]:
					askResult = disSec.askToGetIn(stu)
					# result is (bool, student kicked out)
					if askResult[0]:
						married.append(stu)
						notMarried.remove(stu)

						notMarried.append(askResult[1])
						married.remove(askResult[1])
						unwanted = False
						break;

			if not unwanted:
				break;

		if unwanted:
			unwantedStudents.append(stu)
			notMarried.remove(stu)

	return married, unwantedStudents

# randomized iteration, if all students are put into sections, we break and return, otherwise, try again
def iteration((students, discussions)):

	for stu in students:
		stu.addRestOfChoices(discussions.keys())

	count = 0
	while True:
		count += 1
		stuInst = copy.deepcopy(students)
		discInst = copy.deepcopy(discussions)
		marResult = marriage(stuInst, discInst)
		if len(marResult[1]) == 0:
			break;


	#print count, 

	return discInst

# gets all students with redflags
def getRedFlags(fileName):
	exceptions = []
	
	f = open(fileName, 'r')
	data = f.read().split('\n')[1:]
	f.close()

	students = []
	for dat in data:
		students.append(student(dat))

	checkWhoRegistered(students)

	f = open('discussions', 'r')
	data = f.read().split('\n')
	f.close()

	w = open('redFlags', 'w')

	redFlagCount = 0
	discussions = {}
	for dat in data:
		time = dat.split(' ')
		if ' '.join(time[:-1]) not in discussions.keys(): 
			discussions[' '.join(time[:-1])] = []
		discussions[' '.join(time[:-1])].append(discussion(dat))

	for stu in students:
		stu.addRestOfChoices(discussions.keys())
		if stu.redFlag and stu.netid not in exceptions:
			redFlagCount += 1
			w.write(stu.netid + ' ' + str(stu.choices) + '\n')
	w.close()

	print 'Red flags:', redFlagCount

# cross referencing who has registered and who has not
def checkWhoRegistered(registered):
	f = open('students', 'r')
	roster = f.read().split('\n')
	f.close()

	notInOfficialRoster = []
	notRegistered = []
	for stu in registered:
		if stu.netid in roster:
			roster.remove(stu.netid)
		else:
			notInOfficialRoster.append(stu.netid)
	
	for stu in roster:
		notRegistered.append(stu)

	print 'Not registered:', len(notRegistered)

	w = open('notRegistered', 'w')
	w.write('Not Registered' + '\n')
	w.write(str(notRegistered) + '\n')
	w.write("Not in Official Roster" + '\n')
	w.write(str(notInOfficialRoster))
	w.close();


# write a file with the sorting score
def writeToFile(discInst, score):

	f = open('assignments/sectionAssignments' + str(score), 'w')
	sortedKeys = sorted(discInst.keys())
	for key in sortedKeys:
		dis = discInst[key]
		for i, disSec in enumerate(dis):
			f.write(key + ' S' + str(i) + ', ' + ', '.join(str(x) for x in disSec.students) + '\n')
	f.close()


minScore = 10000000
iterations = int(sys.argv[1])
fileName = sys.argv[2]

getRedFlags(fileName)
jobs = []

f = open(fileName, 'r')
data = f.read().split('\n')[1:]
f.close()

students = []
for dat in data:
	students.append(student(dat))

f = open('discussions', 'r')
data = f.read().split('\n')
f.close()

discussions = {}
for dat in data:
	time = dat.split(' ')
	if ' '.join(time[:-1]) not in discussions.keys(): 
		discussions[' '.join(time[:-1])] = []
	discussions[' '.join(time[:-1])].append(discussion(dat))

pool = Pool(processes=8)

# mutlithreading for the win
poolParams = []
for x in range(8):
	poolParams.append((copy.deepcopy(students), copy.deepcopy(discussions)))

for i in range(iterations):
	if i % 100 == 0:
		print '---',i,'---'

	for x in range(8):
		poolParams[x] = (copy.deepcopy(students), copy.deepcopy(discussions))
	
	for resultDisc in pool.map(iteration, poolParams):
		prefScore = prefsScore(resultDisc)
		#print prefScore[1],
		if prefScore[1] < minScore:
			writeToFile(resultDisc, prefScore[1])
			minScore = prefScore[1]
			print 'written', prefScore[1], prefScore[0]

	
#resultDisc = iteration(fileName)
#print prefsScore(resultDisc, 10)
#writeToFile(resultDisc)