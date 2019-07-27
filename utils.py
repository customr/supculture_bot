import vk 
import json

with open('cfg.json') as cfg_read:
		_config = json.load(cfg_read)
		cfg_read.close()

def update_data(bot):
	sneakers = bot.market.get(owner_id=_config['group_id'], album_id=4, 
		extended=0, v=_config['api_v'])
	accessories = bot.market.get(owner_id=_config['group_id'], album_id=1, 
		extended=0, v=_config['api_v'])
	tshirts = bot.market.get(owner_id=_config['group_id'], album_id=5, 
		extended =0, v=_config['api_v'])
	jackets = bot.market.get(owner_id=_config['group_id'], album_id=6, 
		extended=0, v=_config['api_v'])

	with open('./data/Sneakers.txt', 'w') as sn:
		for sneaker in sneakers['items']:
			sn.write('{}\n'.format(sneaker['id']))
		print('sneakers update has been done')
		sn.close()


	with open('./data/Accessories.txt', 'w') as ac:
		for accessory in accessories['items']:
			ac.write('{}\n'.format(accessory['id']))
		for tshirt in tshirts['items']:
			ac.write('{}\n'.format(tshirt['id']))
		for jacket in jackets['items']:
			ac.write('{}\n'.format(jacket['id']))
		print('accessories update has been done')
		ac.close()
		