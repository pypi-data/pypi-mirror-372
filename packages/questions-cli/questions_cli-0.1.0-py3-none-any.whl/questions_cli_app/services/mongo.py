import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pymongo import MongoClient, UpdateOne
from bson import ObjectId
from questions_cli_app import config


class MongoRepo:
    def __init__(self):
        uri = os.getenv("MONGO_URI") or config.MONGO_URI
        dbname = os.getenv("MONGO_DB") or config.MONGO_DB
        topics_coll = os.getenv("MONGO_TOPICS_COLLECTION") or config.MONGO_TOPICS_COLLECTION
        questions_coll = os.getenv("MONGO_QUESTIONS_COLLECTION") or config.MONGO_QUESTIONS_COLLECTION
        allow_local = os.getenv("ALLOW_LOCAL_MONGO", "0") == "1"

        if not uri and not allow_local:
            raise RuntimeError("MONGO_URI is required. Set ALLOW_LOCAL_MONGO=1 to use local default client.")

        self.client = MongoClient(uri, appname="questions-cli") if uri else MongoClient(appname="questions-cli")
        self.db = self.client[dbname]
        self.topics = self.db[topics_coll]
        self.questions = self.db[questions_coll]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        try:
            self.client.close()
        except Exception:
            pass

    def insert_topic(self, topic: Dict[str, Any]) -> ObjectId:
        now = datetime.utcnow()
        topic.setdefault("createdAt", now)
        topic["updatedAt"] = now
        result = self.topics.insert_one(topic)
        inserted_id = result.inserted_id
        return inserted_id

    def upsert_topic(self, topic: Dict[str, Any]):
        topic["updatedAt"] = datetime.utcnow()
        self.topics.update_one({"_id": topic["_id"]}, {"$set": topic}, upsert=True)

    def insert_question(self, question: Dict[str, Any]) -> ObjectId:
        now = datetime.utcnow()
        question.setdefault("createdAt", now)
        question["updatedAt"] = now
        result = self.questions.insert_one(question)
        inserted_id = result.inserted_id
        return inserted_id

    def bulk_upsert_questions(self, questions: List[Dict[str, Any]]):
        now = datetime.utcnow()
        ops = []
        for q in questions:
            q["updatedAt"] = now
            ops.append(UpdateOne({"_id": q["_id"]}, {"$set": q}, upsert=True))
        if ops:
            self.questions.bulk_write(ops, ordered=False) 