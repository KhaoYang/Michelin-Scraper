from flask import Flask, jsonify, request
import json

app = Flask(__name__)

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
	with open('michelin_restaurants.json', 'r', encoding='utf-8') as f:
		data = json.load(f)
	cuisine = request.args.get('cuisine')
	city = request.args.get('city')
	name = request.args.get('name')
	filtered = data
	if cuisine:
		filtered = [r for r in filtered if 'cuisine' in r and cuisine.lower() in r['cuisine'].lower()]
	if city:
		filtered = [r for r in filtered if 'address' in r and city.lower() in r['address'].lower()]
	if name:
		filtered = [r for r in filtered if 'name' in r and name.lower() in r['name'].lower()]
	return jsonify(filtered)

if __name__ == '__main__':
	app.run(debug=True)
