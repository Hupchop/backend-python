from database import customer_collection, transaction_collection, review_collection
from entities import GeneralEntities
from app import db

class Review:

    customer : dict

    EXCELLENT : str = 'Excellent';
    GOOD : str = 'Good';
    FAIR : str = 'Fair';
    POOR : str = 'Poor';
    VERY_BAD : str = 'Very Bad';

    # verify customer purchase
    async def verifiedFoodPurchase(self, customer_phone : str, foodid : str) -> bool:

        verified = False

        self.customer = await customer_collection.find_one(
            filter={"phone" : customer_phone}
        )

        # is customer
        if self.customer != None:

            # get transaction
            transaction = await transaction_collection.find_one(
                filter={
                    "customer" : self.customer['_id'],
                    "itemid" : foodid
                }
            )

            verified = True if transaction != None else False

        
        # all good
        return verified


    # verify resturant purchase
    async def verifiedRestaurantPurchase(self, customer_phone : str, sellerid : str) -> bool:
        
        verified = False

        self.customer = await customer_collection.find_one(
            filter={"phone" : customer_phone}
        )

        # is customer
        if self.customer != None:

            # get transaction
            transaction = await transaction_collection.find_one(
                filter={
                    "customer" : self.customer['_id'],
                    "seller" : sellerid
                }
            )

            verified = True if transaction != None else False

        # all good
        return verified
    

    # get review experience
    def getExperience(rating : int):
        
        reviewOptions = (Review.VERY_BAD, Review.POOR, Review.FAIR, Review.GOOD, Review.EXCELLENT)
        return reviewOptions[(rating-1)]
    

    # update review count
    async def updateReviewCount(self, data : GeneralEntities.SubmitReviewEntity):

        collection = db.get_collection(data.review_type)

        filters = {
            "food"          : {'foodid' : data.id}, 
            "restaurant"    : {'sellerid' : data.id},
            "hupchop"       : {"operation" : data.id, "identity" : "hupchop"}
        }

        filter_var : dict = filters[data.review_type]

        # get single record
        record = await collection.find_one(filter=filter_var)

        # update val
        update = {
            "reviews" : 1,
            "rating" : int(data.rating)
        }

        # has record
        if record != None:

            update["reviews"] = 1 if record['reviews'] == None else (record['reviews'] + 1)
            update["rating"] = update["rating"] if record['rating'] == None else (int(record['rating']) + int(data.rating))

        # update
        update.update(filter_var)

        # update or create record
        await collection.update_one(
            filter=filter_var,
            update={
                "$set" : update
            },
            upsert=True
        )

    # this unpacks a customer review
    def unpackCustomerReview(self, review : dict):
        return {
            "id" : str(review['_id']),
            "customer_name" : str(review['customer']['name']).capitalize(),
            "rating" : int(review['rating']),
            "title" : str(review['review_title']).capitalize(),
            "review" : str(review['review']),
            "verified" : review['verified_purchase'],
            "helpful" : review['helpful'],
            "date" : review['date_created']
        }
    
    # get all reviews by id
    async def getReviewsByID(self, typeid : str):

        reviews = await review_collection.find(
            filter={"typeid" : typeid}
        ).to_list(100000000)

        total_reviews = len(reviews)
        rating = 0
        customer_reviews = []
        stars = {"5" : 0, "4" : 0, "3" : 0, "2" : 0, "1" : 0}

        if total_reviews > 0:

            for review in reviews:
                customer_reviews.append(self.unpackCustomerReview(review))
                rating += review['rating']
                stars[str(review['rating'])] += 1

            # adjust rating
            rating = round(rating / total_reviews)

        # read stars
        for starIndex in stars:
            star = stars[str(starIndex)]
            percentage = '0%'

            if total_reviews > 0:
                percentage = '0%' if star == 0 else (str(round((star*100)/total_reviews)) + '%')

            # update stars
            stars[str(starIndex)] = percentage

        # all good
        return {
            "total_reviews" : total_reviews,
            "rating" : rating,
            "reviews" : customer_reviews,
            "stars" : stars
        }

    ...
