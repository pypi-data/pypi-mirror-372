from fastapi.openapi.models import Contact
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict
from ..interfaces.dsp.metadb import IMetaDatabase
from ..models.dsp.v2025_1_rc2.low_level import Offer, Optional, Dataset
from ..models.slg.models import ExtendedOffer
import os
import uuid
from collections import defaultdict


def generate_uuid_urn(prefix: str = "urn:uuid:") -> str:
    return f"{prefix}{uuid.uuid4()}"

class MongoStorage(IMetaDatabase):
    def __init__(self):
        url = os.getenv('sconnector.meta.db_url')
        print(url)
        db_name = os.getenv('sconnector.meta.db_name')
        user = os.getenv('sconnector.meta.db_user')
        pwd = os.getenv('sconnector.meta.db_pwd')
        motor_url = f"mongodb://{user}:{pwd}@{url}/{db_name}?authSource={db_name}"
        self.client = AsyncIOMotorClient(motor_url)
        self.db = self.client[db_name]
        self.offers = self.db["offers"]
        self.exposed = self.db["exposed"]
        self.contacts = self.db["contacts"]

    async def create_offer(self, offer: ExtendedOffer) -> Offer:
        if offer.offer.id == "" or not offer.offer.id:
            offer.offer.id = generate_uuid_urn()
        offer_dict = offer.model_dump(by_alias=True)
        offer_dict["_id"] = offer_dict['offer']["@id"].split(':')[-1]
        await self.offers.insert_one(offer_dict)
        return offer.offer

    async def get_offer(self, offer_id: str) -> Optional[ExtendedOffer]:
        doc = await self.offers.find_one({"_id": offer_id})
        return ExtendedOffer(**doc) if doc else None

    async def list_offers(self) -> List[ExtendedOffer]:
        cursor = self.offers.find()
        docs = await cursor.to_list(length=1000)
        return [ExtendedOffer(**doc) for doc in docs]

    async def update_offer(self, offer: ExtendedOffer) -> bool:
        offer_dict = offer.model_dump(by_alias=True)
        result = await self.offers.replace_one({"_id": offer_dict["_id"]}, offer_dict)
        return result.modified_count == 1

    async def delete_offer(self, offer_id: str) -> bool:
        result = await self.offers.delete_one({"_id": offer_id})
        return result.deleted_count == 1

    # async def expose_dataset(self, dataset_id: str, offer_id: str) -> dict:
    #     body = {
    #         "_id": generate_uuid_urn(prefix=""),
    #         "offer_id": offer_id,
    #         "dataset_id": dataset_id
    #     }
    #     _ = await self.exposed.insert_one(body)
    #     return body

    async def get_offers_for_datasets(self, dataset_ids: List[str]) -> Dict[str, List[str]]:
        cursor = self.exposed.find({"dataset_id": {"$in": dataset_ids}})
        results = await cursor.to_list(length=None)

        mapping = defaultdict(list)
        for item in results:
            dataset_id = item.get("dataset_id")
            offer_id = item.get("offer_id")
            if dataset_id and offer_id:
                mapping[dataset_id].append(offer_id)
        return dict(mapping)

    async def create_contact(self, base_url: str, participant_id: str, version: str, prefix: str) -> bool:
        contact = {
            "_id": participant_id,
            "preferred_username": participant_id,
            "base_url": base_url,
            "version": version,
            "prefix": prefix
        }
        try:
            await self.contacts.insert_one(contact)
        except:
            return False
        return True

    async def list_contacts(self) -> List[Contact]:
        cursor = self.contacts.find()
        docs = await cursor.to_list(length=1000)
        return [Contact(**doc) for doc in docs]


# Singleton instance
mongo_storage: MongoStorage = MongoStorage()