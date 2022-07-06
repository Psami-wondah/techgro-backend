from pymongo import MongoClient
import os
from utils.config import MONGO_URI

conn = MongoClient(MONGO_URI)

db = conn.techgro
