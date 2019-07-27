import argparse
import json
import vk
from time import sleep, time, mktime, strftime
from datetime import datetime
import random
import utils

"""
TODO: 
	-add month error exception in the time set function
	-make more flexible and user-friendly code
	-add logging
"""

class Base(object):
	def __init__(self):
		with open('cfg.json', 'r+') as cfg_read:
			_config = json.load(cfg_read)

			parser = argparse.ArgumentParser()
			parser.add_argument('--api_v', type=int, default=_config['api_v'], 
				help="VK api version.")
			parser.add_argument('--app_id', type=int, default=_config['app_id'], 
				help="Your VK app id.")
			parser.add_argument('--user_id', type=int, default=_config['user_id'], 
				help="Your user id.")
			parser.add_argument('--group_id', type=int, default=_config['group_id'], 
				help="Your group id (with minuse at the start).")
			parser.add_argument('--scope', type=str, default=_config['scope'], 
				help="Scope of api.")
			parser.add_argument('-l', type=str, default=_config['l'], 
				help="VK login.")
			parser.add_argument('-p', type=str, default=_config['p'],
				help="VK password")
			parser.add_argument('--classes', type=list, default=_config['classes'],
				help="Names of shop categories.")
			parser.add_argument('--hours', type=list, default=_config['hours'],
				help="Hours to place.")
			parser.add_argument('--minute', type=int, default=_config['minute'],
				help="Minute(s) to place.")
			parser.add_argument('--range', type=int, default=_config['range'],
				help="Count of posts to publish.")
			parser.add_argument('--date', type=int, default=0,
				help="Start publish from that date.")
			parser.add_argument('--last_ids', type=list, default=_config['last_ids'],
				help="Indexes to save.")
			parser.add_argument('-u', type=bool, default=0,
				help="Update data or not.")
			parser.add_argument('--add_group', type=int, default=None,
				help="Update data or not.")
			parser.add_argument('--mode', type=str, default='post', 
				help="Post or advert.")
			self._args = vars(parser.parse_args())
			
			for name in _config.keys():
				_config[name] = self._args[name]

			cfg_read.close()

		with open('cfg.json', 'w+') as cfg_rewrite:
			cfg_rewrite.write(json.dumps(_config))
			cfg_rewrite.truncate()
			cfg_rewrite.close()

		session = vk.AuthSession(self._args["app_id"], self._args["l"], 
								 self._args["p"], scope=self._args["scope"])

		self.api = vk.API(session)

		if len(self._args['l']) == 0:
			raise ValueError('Login is required.')

		if len(self._args['p']) == 0:
			raise ValueError('Password is required.')

		if self._args['add_group'] is not None:
			if self._args['add_group'] not in self._args['group_urls']:
				self._args['group_urls'].append(self._args['add_group'])
			else:
				print(self._args['add_group']+' already in data.')

		if self._args['u'] == 1: 
			utils.update_data(self.api)
	

class Post(Base):
	def __init__(self):
		Base.__init__(self)
		self.update()

	def update(self):
		self.data = {name:[] for name in self._args["classes"]}
		self.data_posted = []

		for n, name in enumerate(self._args["classes"]):
			try:
				c1 = open('./data/{}.txt'.format(name), 'r')
			except Exception: 
				c1 = open('./data/{}.txt'.format(name), 'w+')
			finally:
				for x in c1:
					self.data['{}'.format(name)].append(int(x))
				c1.close()

			try:
				c2 = open('./posted/posted_{}.txt'.format(name), 'r')
			except Exception: 
				c2 = open('./posted/posted_{}.txt'.format(name), 'w+')
			finally:
				temp = []
				for y in c2: 
					temp.append(y)

				rewrite = open('./posted/posted_{}.txt'.format(name), 'w')
				for k in temp[-self._args['last_ids'][n]:-1]:
					rewrite.write(k)
					self.data_posted.append(k)

				rewrite.close()	
				c2.close()

	def times(self, year, month, day, dshift, dy=0):
		return {str(hour): mktime(datetime(
							year=year, month=month, 
							day=day+dshift*(int(dy==0))+dy, 
							hour=hour, minute=self._args["minute"]).timetuple()) 
				for hour in self._args["hours"]}


	def post(self):
		def upd():
			can_be_post = {name:[] for name in self._args["classes"]}
			for name in self._args['classes']:
				name_can_post = list(set(self.data[name])\
									-set(self.data_posted))
				can_be_post[name] = name_can_post
			return can_be_post

		y = int(strftime('%Y'))
		m =	int(strftime('%m'))
		d = int(strftime('%d'))
		if self._args["date"]==0: dnum = datetime(y, m, d).weekday()
		else:
			d = self._args["date"]
			dnum = datetime(y, m, self._args["date"]).weekday()

		for n in range(self._args["range"]):
			day_times = self.times(y,m,d,n)
			can_post = upd()

			p_ids  = [None, None]
			p_time = [None, None]

			flag = (d+n)%2
			daynum = (dnum+n)%6
			
			if daynum!=6 and daynum!=0: 
				if flag:
					p_time[0] = day_times['14']
					p_time[1] = day_times['20']
					p_ids[0]  = random.choice(can_post['Sneakers'])
					p_ids[1]  = random.choice(can_post['Accessories'])
				else:
					p_time[0] = day_times['10']
					p_time[1] = day_times['18']
					p_ids[0]  = random.choice(can_post['Sneakers'])
					p_ids[1]  = random.choice(can_post['Accessories'])
			else: 
				if flag:
					p_time[0] = day_times['12']
					p_time[1] = day_times['18']
					p_ids[0]  = random.choice(can_post['Sneakers'])
					p_ids[1]  = random.choice(can_post['Accessories'])
				else:
					p_time[0] = day_times['12']
					p_time[1] = day_times['20']
					p_ids[0]  = random.choice(can_post['Sneakers'])
					p_ids[1]  = random.choice(can_post['Accessories'])


			for ind, tim in zip(p_ids, p_time):
				try:
					self.api.wall.post(
						owner_id = self._args["group_id"], from_group = 1, 
						message = self.api.market.getById(
										item_ids = '{}_{}'.format(self._args["group_id"], ind), 
										v=self._args["api_v"])['items'][0]['description'], 
						attachments = 'market{}_{}'.format(self._args["group_id"], ind),
						publish_date = tim,
						v=self._args["api_v"])
				except Exception:
					continue
			

			for n, name in zip(range(len(p_ids)), self._args["classes"]):
				ps = open('./posted/posted_{}.txt'.format(name), 'a')
				ps.write(str(p_ids[n])+'\n')
				self.data_posted.append(p_ids[n])
				ps.close()

			sleep(3)


if __name__=='__main__':
	bot = Post()
	bot.post()
