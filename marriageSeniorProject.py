import random, math, copy, sys
from multiprocessing import Pool

class client:
	def __init__(self, client_str):
		str_del = client_str.split(', ')
		self.name = str_del[2]
		self.choice_num = int(str_del[0])
		self.team = []
		
		# this can be modified per team and such
		self.max_size = int(str_del[1])
		
		if len(str_del) > 2:
			self.team = str_del[3:]
	
	def assign_rankings(self, prefs_matrix, preferred_students, other_students):
		# client basically inputs its preferences into the big preference matrix
		for i, stu in enumerate(self.team):
			prefs_matrix[self.choice_num-1][stu][0] = i
		
		# shuffle all the other students who you have not yet chosen
		random.shuffle(preferred_students)
		shift_index = len(self.team)
		
		for i, stu in enumerate(preferred_students):
			if stu not in self.team:
				prefs_matrix[self.choice_num-1][stu][0] = i + shift_index
			else:
				shift_index -= 1
		
		shift_index += len(preferred_students)
		random.shuffle(other_students)
		
		for i, stu in enumerate(other_students):
			if stu not in self.team:
				prefs_matrix[self.choice_num-1][stu][0] = i + shift_index
			else:
				shift_index -= 1
	
	# returns the student who is kicked out, None if no one is kicked out
	def ask_to_marry(self, stu, prefs_matrix):
		# team not full, let's put this person in
		
		if len(self.team) < self.max_size:
			self.team.append(stu)
			stu.client = self
			return None	
		else:
			# team is full, gotta kick someone out
			max_rank = (self.team[0], prefs_matrix[self.choice_num-1][self.team[0].netid][0])
			for cur_stu in self.team[1:]:
				rank = prefs_matrix[self.choice_num-1][cur_stu.netid][0]
				if rank > max_rank[1]:
					max_rank = (cur_stu, rank)
			
			if prefs_matrix[self.choice_num-1][stu.netid][0] < max_rank[1]:
				self.team.remove(max_rank[0])
				self.team.append(stu)
				stu.client = self
				
				return max_rank[0]
			return stu
	
	def __repr__(self):
		return self.name + ' ' + str(self.team)
		
class student:
	def __init__(self, student_str):
		if len(student_str) == 0:
			self.work_with = []
			self.not_work_with = []
		else:	
			str_del = student_str.split(',')
			self.name = str_del[0]
			self.netid = str_del[1]
			if '@' in self.netid:
				self.netid = self.netid.split('@')[0]
			self.email = str_del[2]
			self.prefs = []
			self.client = None
			
			sponsored_prefs = str_del[3].split(' ')
			normal_prefs = str_del[4].split(' ')
			
			for pref in sponsored_prefs + normal_prefs:
				if pref != '':
					self.prefs.append(int(pref))
			
			self.work_with = str_del[5].split(' ')
			self.not_work_with = str_del[6].split(' ')
		
	# Not really used, but here for consistency
	def assign_rankings(self, prefs_matrix, clients):
		randomize_other_clients = list(set(clients) - set(self.prefs))
		#print self.prefs
		random.shuffle(randomize_other_clients)
		self.prefs += randomize_other_clients
		
		for i, pref in enumerate(self.prefs):
			#print i, pref
			prefs_matrix[pref-1][self.netid][1] = i
	
	def get_matched_pref(self):
		return self.prefs.index(self.client.choice_num)
		
	
	def __repr__(self):
		return self.netid

def score_sorting(students):
	# go through each student
	total_score = 0
	stu_score = 0
	
	worst_pref = 0
	prefs = [0 for i in range(len(clients))]
	working = []
	
	for stu in students.values():
		# if they got their top preference -> lower score
		stu_pref = stu.get_matched_pref()
		prefs[stu_pref] += 1
		
		stu_work = [0.0, 0.0]
		
		if stu_pref > worst_pref:
			worst_pref = stu_pref
		
		stu_score += 2**(stu_pref)
		
		# if someone they don't want to work with is on the same team, incur huge penalty
		nw_count = 0
		for not_work in stu.not_work_with:
			if not_work in stu.client.team:
				nw_count += 1
				stu_score = stu_score ** 2
		
		# if someone they do want to work with is on the same team, subtract from score
		w_count = 0
		for work in stu.work_with:
			if work in stu.client.team:
				w_count += 1
				stu_score *= .66
		
		list_sizes = [len(stu.work_with), len(stu.not_work_with)]
		
		if list_sizes[0] > 0 or list_sizes[1] > 0:
			list_sizes[0] = 1 if list_sizes[0] == 0 else list_sizes[0]
			list_sizes[1] = 1 if list_sizes[1] == 0 else list_sizes[1]
				
			stu_work = {'work with': [w_count,list_sizes[0]], 'not work with': [nw_count,list_sizes[1]]}
			
			working.append(stu_work)
		
		total_score += math.ceil(stu_score)
	
	return int(total_score), worst_pref, prefs[:worst_pref+1], working

def unparsed_student(netid, client):
	stu = student('')
	
	stu.netid = netid
	stu.client = client
	stu.prefs = [client.choice_num]
	
	return stu

clients = []	
students = {}
preferred_students = []
#other_students = []

	
f = open('identifyingFiles/clients.csv', 'r')
data = f.read().split('\n')
f.close()

for dat in data[1:]:
	clients.append(client(dat))		

f = open('identifyingFiles/parsedStudents.csv', 'r')
data = f.read().split('\n')
f.close()

for dat in data[1:-1]:
	stu = student(dat)
	students[stu.netid] = stu
		
f = open('identifyingFiles/preferredStudents.csv', 'r')
data = f.read().split('\n')
f.close()

for dat in data[1:]:
	dat_del = dat.split(',')
	stu_netid = dat_del[3]
	
	if stu_netid in students.keys():
		preferred_students.append(stu_netid)

def iteration((students, clients, preferred_students)):
	other_students = list(set(students.keys()) - set(preferred_students))
	
	# at prefs_matrix[client index][student netid] first number is client's rank for student, second is student's rank for client
	# the student's rank for client isn't used yet...I use the internal param for preference...sooo
	prefs_matrix = [{} for y in range(len(clients))]
	
	for cli in clients:
		for stu in cli.team:
			if stu not in students.keys():
				students[stu] = unparsed_student(stu, cli)
	
	for cli_pref in prefs_matrix:
		for stu in students.keys():
			cli_pref[stu] = [0,0]
	
	client_indexes = [cli.choice_num for cli in clients]
	unassigned_students = [stu for stu in students.values()]
	
	for stu in students.values():
		stu.assign_rankings(prefs_matrix, client_indexes)
		new_work_with = []
		for i, work in enumerate(stu.work_with):
			if work != '' and work in students.keys():
				new_work_with.append(students[work])
		stu.work_with = new_work_with
		
		new_not_work_with = []		
		for i, work in enumerate(stu.not_work_with):
			if work != '' and work in students.keys():
				new_not_work_with.append(students[work])
				
		stu.not_work_with = new_not_work_with
	
	for cli in clients:
		cli.assign_rankings(prefs_matrix, preferred_students, other_students)
		for i, stu in enumerate(cli.team):
			cli.team[i] = students[stu]
			cli.team[i].client = cli
			unassigned_students.remove(students[stu])
	
	# Take all students, put them into a queue, process, pop
	while len(unassigned_students) > 0:
		stu = random.choice(unassigned_students)
		
		unassigned_students.remove(stu)
		married = False
		
		for pref in stu.prefs:
			kicked_out = clients[pref-1].ask_to_marry(stu, prefs_matrix)
			
			# if no one is kicked out, everything is ok, if you're kicked out, try the next preference, if someone else is kicked out, put them back in the queue
			if kicked_out == None:
				married = True
				break
			elif kicked_out != stu:
				married = True
				kicked_out.client = None
				unassigned_students.append(kicked_out)
				break
		
		if not married:
			kicked_out.client = None
			unassigned_students.append(stu)
	
	return score_sorting(students), clients

def write_to_file(clients, score, worst_pref):
	w = open('identifyingFiles/assignments/assignments_' + str(score) + '_' + str(worst_pref) + '.csv', 'w')
	w.write('client id, client name, students\n')
	
	for cli in clients:
		w.write(str(cli.choice_num) + ', ' + cli.name + ', ')
		for stu in cli.team:
			w.write(stu.netid + ', ')
		for i in range(6-len(cli.team)):
			w.write(',')
		w.write('\n')
	
	w.close()
	
def see_distribution(clients, students):
	for stu in students.values():
		clients[stu.prefs[0]-1].team.append(stu)
		
	for cli in clients:
		print cli.name, len(cli.team), cli.team
	

iterations = 10000
lowest_score = sys.maxint

students_copy = copy.deepcopy(students)
clients_copy = copy.deepcopy(clients)

#see_distribution(clients_copy, students_copy)

pool = Pool(processes=8)

# mutlithreading for the win
poolParams = []
for x in range(8):
	poolParams.append((copy.deepcopy(students), copy.deepcopy(clients)))
	
for i in range(iterations):
	if i % 1000 == 0:
		print '---',i,'---'

	for x in range(8):
		poolParams[x] = (copy.deepcopy(students), copy.deepcopy(clients), preferred_students)
	
	for (score, worst_pref, pref_count, working), clients_copy in pool.map(iteration, poolParams):
		
		if score < lowest_score:
			write_to_file(clients_copy, score, worst_pref)
			lowest_score = score
			print pref_count, score

	
# # unassigned_students, students, clients
# students_copy = copy.deepcopy(students)
# clients_copy = copy.deepcopy(clients)
# iteration(students_copy, clients_copy, preferred_students)

# print score_sorting(students_copy)

# students_copy = copy.deepcopy(students)
# clients_copy = copy.deepcopy(clients)
# iteration(students_copy, clients_copy, preferred_students)

# print score_sorting(students_copy)				