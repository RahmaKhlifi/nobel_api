from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_cors import CORS
import config

# Initialize Flask App
app = Flask(__name__)
app.config["MONGO_URI"] = config.MONGO_URI
mongo = PyMongo(app)

CORS(app)  # Enable Cross-Origin Resource Sharing

# Collection reference
laureates_collection = mongo.db.laureates

# Routes

@app.route('/laureates', methods=['GET'])
def get_all_laureates():
    """Retrieve all laureates"""
    laureates = laureates_collection.find()
    result = [{key: laureate[key] for key in laureate if key != '_id'} for laureate in laureates]
    return jsonify(result), 200

@app.route('/laureates/<string:laureate_id>', methods=['GET'])
def get_laureate_by_id(laureate_id):
    """Retrieve a single laureate by ID"""
    laureate = laureates_collection.find_one({"id": laureate_id})
    if laureate:
        laureate.pop('_id')  # Remove ObjectId
        return jsonify(laureate), 200
    return jsonify({"error": "Laureate not found"}), 404

@app.route('/laureates', methods=['POST'])
def add_laureate():
    """Add a new laureate"""
    data = request.json
    if 'id' not in data:
        return jsonify({"error": "ID is required"}), 400
    laureates_collection.insert_one(data)
    return jsonify({"message": "Laureate added successfully"}), 201

@app.route('/laureates/<string:laureate_id>', methods=['PUT'])
def update_laureate(laureate_id):
    """Update a laureate"""
    data = request.json
    result = laureates_collection.update_one({"id": laureate_id}, {"$set": data})
    if result.matched_count > 0:
        return jsonify({"message": "Laureate updated successfully"}), 200
    return jsonify({"error": "Laureate not found"}), 404

@app.route('/laureates/<string:laureate_id>', methods=['DELETE'])
def delete_laureate(laureate_id):
    """Delete a laureate"""
    result = laureates_collection.delete_one({"id": laureate_id})
    if result.deleted_count > 0:
        return jsonify({"message": "Laureate deleted successfully"}), 200
    return jsonify({"error": "Laureate not found"}), 404

@app.route('/laureates/country/<string:laureate_country>',methods=['GET'])
def get_laureates_by_country(laureate_country):
    """Retrieve laureates by country"""
    laureates = laureates_collection.find({"bornCountry": laureate_country})
    result = [{key: laureate[key] for key in laureate if key != '_id'} for laureate in laureates]
    return jsonify(result), 200

@app.route('/laureates/prizes/<string:category>', methods=['GET'])
def get_laureates_by_prize(category):
    """Retrieve laureates by prize category and year"""
    query = {"prizes.category": category}
    laureates = laureates_collection.find(query)
    result = [{key: laureate[key] for key in laureate if key != '_id'} for laureate in laureates]
    return jsonify(result), 200

@app.route('/laureates/prizes/year/<string:year>', methods=['GET'])
def get_laureates_by_prize_year(year):
    """Retrieve laureates who won prizes in a specific year"""
    query = {"prizes.year": year}
    laureates = laureates_collection.find(query)
    result = [{key: laureate[key] for key in laureate if key != '_id'} for laureate in laureates]
    return jsonify(result), 200

@app.route('/laureates/prizes/multiple/<string:categories>', methods=['GET'])
def get_laureates_by_multiple_prizes(categories):
    """Retrieve laureates by multiple prize categories"""
    categories_list = categories.split(',')
    print(categories_list)
    query = {"prizes.category": {"$in": categories_list}}
    laureates = laureates_collection.find(query)
    result = [{key: laureate[key] for key in laureate if key != '_id'} for laureate in laureates]
    return jsonify(result), 200

@app.route('/laureates/prizes/<string:category>/year/<string:year>', methods=['GET'])
def get_laureates_by_prize_category_and_year(category, year):
    """Retrieve laureates by prize category and year"""
    query = {
        "prizes.category": category,
        "prizes.year": year
    }
    laureates = laureates_collection.find(query)

    # Prepare the result by excluding the '_id' and keeping prize information
    result = []
    for laureate in laureates:
        laureate_info = {key: laureate[key] for key in laureate if key != '_id'}  # Exclude '_id'
        
        # Filter prizes for matching category and year
        laureate_prizes = []
        for prize in laureate.get('prizes', []):
            if prize.get('category') == category and prize.get('year') == year:
                laureate_prizes.append({
                    'category': prize.get('category'),
                    'year': prize.get('year')
                })

        # Add laureate prize details to the result
        laureate_info['prizes'] = laureate_prizes
        result.append(laureate_info)

    return jsonify(result), 200

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
