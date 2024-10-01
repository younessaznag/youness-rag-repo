from .enums.DataBaseEnum import DataBaseEnum
from .BaseDataModel import BaseDataModel
from .db_schemas.data_chunk import DataChunk
from bson.objectid import ObjectId
from pymongo import InsertOne


class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes :
                await self.collection.create_index(
                    index["key"],
                    name = index["name"],
                    unique = index["unique"]
                )
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    

    async def create_chunk(self, chunk :DataChunk ):

        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk.id = result.inserted_id

        return chunk
    
    
    async def get_chunk(self, chunk_id:str ):

        result = self.collection.find(
            {'_id':ObjectId(chunk_id) }
        )

        if result is None :
            return None 
        
        return DataChunk(**result)
    

    async def insert_many_chunks(self, chunks: list, batch_size: int=100):

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+100]

            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in batch
            ]

            await self.collection.bulk_write(operations)

        return len(chunks)
    
    async def delete_chunks_by_chunk_project_id(self, chunk_project_id: ObjectId):
        result = await self.collection.delete_many(
            {
                "chunk_project_id": chunk_project_id
            }
        )
 
        return result.deleted_count
    


        