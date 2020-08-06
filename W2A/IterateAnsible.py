import os
import subprocess
import json
import logging

class IterateAnsible(object):

	def __init__(self, assistantv1, workspaceID, playbks_dir, vaultpss):
		self.assistantv1 = assistantv1
		self.workspaceID = workspaceID
		self.playbooks_dirs = playbks_dir
		self.vaultpss = vaultpss
		self.tryAgain = {}


	def __getPlaybooksPresents(self):
		entities = []

		for dir in self.playbooks_dirs:
			playbooks = os.listdir(dir)
			for playbook in playbooks:
				entities.append({'value': playbook.split('.')[0]})   # <- Get the playbooks of the playbooks dirs

		return entities


	def __executePlaybooks(self, playbooks, userID, act):
		playbookStr = ' '
		for Dirs in self.playbooks_dirs:
			for Playbook in playbooks:
				playbookStr = "%s %s/%s.yml" % (playbookStr, Dirs, Playbook)

		self.tryAgain[userID] = [playbooks, userID, act]

		try:
			if act == 1:
				logging.info('(i) Validating syntax of ' + playbookStr)
				res = subprocess.check_output("ansible-playbook --syntax-check " + playbookStr, shell=True, stderr=subprocess.STDOUT)
			elif act == 2:
				logging.info('(i) Simulate execution of ' + playbookStr)
				res = subprocess.check_output("ansible-playbook -C" + playbookStr, shell=True, stderr=subprocess.STDOUT)
			elif act == 3:
				logging.info('(i) Executing ' + playbookStr)
				res = subprocess.check_output("ansible-playbook" + playbookStr, shell=True, stderr=subprocess.STDOUT)

			logging.info('(i) Result: ' + str(res))
			return {'res': res}
		except subprocess.CalledProcessError as e:
			mainE = None
			try:
				if e.returncode == 1:
					if act == 1:
						logging.info('(i) Validating syntax of ' + playbookStr + 'with vault')
						return {'res': subprocess.check_output("ansible-playbook --vault-password-file=%s --syntax-check %s" % (self.vaultpss, playbookStr), shell=True, stderr=subprocess.STDOUT)}
					elif act == 2:
						logging.info('(i) Simulate execution of ' + playbookStr + 'with vault')
						return {'res': subprocess.check_output("ansible-playbook --vault-password-file=%s -C %s" % (self.vaultpss, playbookStr), shell=True, stderr=subprocess.STDOUT)}
					elif act == 3:
						logging.info('(i) Executing ' + playbookStr + 'with vault')
						return {'res': subprocess.check_output("ansible-playbook --vault-password-file=%s %s" % (self.vaultpss, playbookStr), shell=True, stderr=subprocess.STDOUT)}
				else:
					mainE = RuntimeError("Command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
					logging.error('(X) Error: ' + str(mainE))
					return {'error': True, 'res': str(mainE)}
			except subprocess.CalledProcessError as e:
					mainE = RuntimeError("Command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
					logging.error('(X) Error: ' + str(mainE))
					return {'error': True, 'res': str(mainE)}
			except Exception as e:
				logging.error('(X) Error: ' + str(e))
				return {'error': True, 'res': str(e)}
		except Exception as e:
			logging.error('(X) Error: ' + type(e).__name__)
			return {'error': True, 'res': "Error:\n %s" % (type(e).__name__)}


	def updatePlaybooksInEntities(self):
		Entities = self.__getPlaybooksPresents()

		response = self.assistantv1.update_entity(
		    workspace_id=self.workspaceID,  	# <- You do get it of API Details Skill (Skill ID)
		    entity='playbook',
		    new_values=Entities
		).get_result()
		

	# Execute in Ansible
	def execute(self, WatsonRes, userID):
		playbooksEx = []
		intents = WatsonRes["output"]["intents"]
		entities = WatsonRes["output"]["entities"]
		res = None

		for Entity in entities:
			if Entity["entity"] == "playbook":
				playbooksEx.append(Entity["value"])  # <- Get playbooks to iterate

		if entities and playbooksEx:
			entity = entities[0]["entity"]
			if entity == "syntax-check": # <- The first entity in the object indicates the activity to be executed
				res = self.__executePlaybooks(playbooksEx, userID, 1)
			elif entity == "simulate":
				res = self.__executePlaybooks(playbooksEx, userID, 2)
			elif entity == "execute":
				res = self.__executePlaybooks(playbooksEx, userID, 3)

			if res == None:
				return { 'msg': 'doubts', 'Ansible_result': ''}


		if intents:
			if intents[0]["intent"] == "Try_Again":
				if userID in self.tryAgain:
					usr = self.tryAgain[userID]
					res = self.__executePlaybooks(usr[0], usr[1], usr[2])

		if res != None:
			ret = { 'msg': 'done', 'Ansible_result': res['res'] }
			if "error" in res:
				ret["error"] = True
				ret["msg"] = 'error'
			return ret			

		return False
