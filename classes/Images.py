from database import image_collection
from bson import ObjectId

class Images():

    imageResponse : list = []
    _dataIds : list = []
     
    # constructor
    def __init__(self, dataIds : list) -> None:
        self._dataIds = dataIds

    
    async def loadImages(self):

        images = await image_collection.find(
            filter={"_id" : {"$in" : self._dataIds}}
        ).to_list(1000)

        if isinstance(images, list):
            self.imageResponse = images


    # load image
    async def loadImage(self, imageId):

        response = {
            "blur" : "",
            "path" : ""
        }

        if len(self.imageResponse) > 0:
            # read imageid
            imageId = str(imageId)

            for record in self.imageResponse:
                if str(record['_id']) == imageId:
                    response['blur'] = 'data:' + record['type'] + ';base64,' + record['blur']
                    response['path'] = record['path']


        return response
        