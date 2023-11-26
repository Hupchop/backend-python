from app import db

# collections
customer_collection = db.get_collection('customers')
transaction_summary_collection = db.get_collection('transaction_summary')
transaction_collection = db.get_collection('transactions')
earnings_collection = db.get_collection('earnings')
review_collection = db.get_collection('reviews')
image_collection = db.get_collection('hupchop_images')
inspiration_collection = db.get_collection('food_inspirations')
suggestion_collection = db.get_collection('suggestions')