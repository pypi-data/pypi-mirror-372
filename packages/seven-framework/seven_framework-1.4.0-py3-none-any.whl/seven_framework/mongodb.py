from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult
from pymongo.cursor import Cursor
from bson import ObjectId

class MongoDBHelper():
    def __init__(self, mongodb_uri: str, db_name: str):
        """
        :description: 初始化MongoDBHelper
        :last_editors: ChenXiaolei
        """
        if not mongodb_uri or not db_name:
            raise ValueError("请设置mongodb_uri和db_name")

        self.client = MongoClient(mongodb_uri)
        self.db: Database = self.client[db_name]

    def generate_custom_id(self) -> str:
        """
        :description: 生成自定义的_id
        :return : 自定义的_id
        :last_editors: ChenXiaolei
        """        
        return str(ObjectId())

    def get_collection(self, collection_name) -> Collection:
        """
        :description: 获取集合
        :param collection_name: 集合名称
        :return : 集合对象
        :last_editors: ChenXiaolei
        """
        return self.db[collection_name]

    def insert_one(self, collection_name, document) -> str:
        """
        :description: 插入单个文档
        :param collection_name: 集合名称
        :param document: 要插入的文档
        :return: 插入文档的_id
        :last_editors: ChenXiaolei
        """
        collection = self.get_collection(collection_name)

        # 如果document中没有_id字段，则自动生成一个
        if "_id" not in document:
            document["_id"] = self.generate_custom_id()

        result:InsertOneResult = collection.insert_one(document)

        return str(result.inserted_id)

    def insert_many(self, collection_name: str, documents: list) -> list:
        """
        :description: 插入多个文档
        :param collection_name: 集合名称
        :param documents: 要插入的文档列表
        :return: 插入结果，包含插入文档的 _id 列表
        :last_editors: ChenXiaolei
        """
        if not collection_name or not documents:
            raise ValueError("无效的集合名称或文档列表")
        
        collection = self.get_collection(collection_name)

        # 如果document中没有_id字段，则自动生成一个
        for document in documents:
            if "_id" not in document:
                document["_id"] = self.generate_custom_id()

        result: InsertManyResult = collection.insert_many(documents)

        return [str(inserted_id) for inserted_id in result.inserted_ids]

    def delete_one(self, collection_name: str, filter: dict) -> int:
        """
        :description: 删除单个文档
        :param collection_name: 集合名称
        :param filter: 查询条件
        :return: 删除结果
        """
        if not collection_name or not filter:
            raise ValueError("集合名称或筛选器无效。筛选器不能为空")

        collection = self.get_collection(collection_name)
        return collection.delete_one(filter).deleted_count

    def delete_many(self, collection_name: str, filter: dict) -> int:
        """
        :description: 删除多个文档
        :param collection_name: 集合名称
        :param filter: 查询条件
        :return: 删除结果，包含删除的文档数量
        :last_editors: ChenXiaolei
        """
        if not collection_name or not filter:
            raise ValueError("集合名称或筛选器无效。筛选器不能为空")

        collection = self.get_collection(collection_name)
        return collection.delete_many(filter).deleted_count

    def find_many(self, collection_name: str, filter: dict = None, projection: dict = None, skip: int = 0, limit: int = 0, sort: list = None) -> list:
        """
        :description: 查询多个文档
        :param collection_name: 集合名称
        :param filter: 查询条件
        :param projection: 投影
        :param skip: 跳过数量
        :param limit: 限制数量
        :param sort: 排序
        :return: 查询结果，文档列表
        :last_editors: ChenXiaolei
        """
        collection = self.get_collection(collection_name)

        cursor = collection.find(filter, projection).skip(skip).limit(limit)

        if sort:
            cursor = cursor.sort(sort)

        return self.get_cursor_list(cursor)
    
    def find_page(self, collection_name: str, filter: dict = None, projection: dict = None, page_index: int = 0, page_size: int = 10, sort: list = None) -> list:
        """
        :description: 分页查询多个文档
        :param collection_name: 集合名称
        :param filter: 查询条件
        :param projection: 投影
        :param page_index: 页码，从 0 开始
        :param page_size: 每页显示的文档数量
        :param sort: 排序
        :return: 查询结果，文档列表
        :last_editors: ChenXiaolei
        """
        if not collection_name:
            raise ValueError("Invalid collection name")

        if page_index < 0 or page_size < 1:
            raise ValueError("page_index 必须大于或等于 0，page_size 必须大于 0")

        collection = self.get_collection(collection_name)
        skip = page_index * page_size
        limit = page_size
        cursor = collection.find(filter, projection).skip(skip).limit(limit)
        
        if sort:
            cursor = cursor.sort(sort)
        
        return self.get_cursor_list(cursor)

    def find_one(self, collection_name: str, filter: dict = None, projection: dict = None, sort: list = None, skip: int = 0) -> dict:
        """
        :description: 查询单个文档
        :param collection_name: 集合名称
        :param filter: 查询条件
        :param projection: 投影
        :param sort: 排序
        :param skip: 跳过数量
        :return: 查询结果，单个文档字典或 None
        :last_editors: ChenXiaolei
        """
        collection = self.get_collection(collection_name)
        return collection.find_one(filter, projection, skip=skip, sort=sort)

    def replace_one(self, collection_name: str, filter: dict, replacement: dict, upsert: bool = False, collation: dict = None, hint: str = None) -> UpdateResult:
        """
        :description: 替换集合中与指定条件匹配的第一个文档
        :param collection_name: 集合名称
        :param filter: 查询条件
        :param replacement: 替换后的文档内容
        :param upsert: 如果为 True，当没有文档匹配 filter 时，会插入 replacement 参数所指定的文档
        :param collation: 可选参数，用于指定排序规则
        :param hint: 可选参数，用于指定用于支持过滤的索引
        :return: 更新结果
        :last_editors: ChenXiaolei
        """
        collection = self.get_collection(collection_name)
        return collection.replace_one(filter, replacement, upsert=upsert, collation=collation, hint=hint)

    def update_one(self, collection_name: str, filter: dict, update: dict, upsert: bool = False):
        """
        更新单个文档
        :param collection_name: 集合名称
        :param filter: 查询条件
        :param update: 更新内容
        :return: 更新结果
        """
        collection = self.get_collection(collection_name)
        result: UpdateResult = collection.update_one(filter, update, upsert=upsert)

        if upsert:
            return str(result.upserted_id)
        
        return result.modified_count

    def update_many(self, collection_name: str, filter: dict, update: dict, upsert: bool = False):
        """
        :description: 更新多个文档
        :param collection_name: 集合名称
        :param filter: 查询条件
        :param update: 更新内容
        :return: 更新结果，包含修改的文档数量
        :last_editors: ChenXiaolei
        """
        collection = self.get_collection(collection_name)
        result: UpdateResult = collection.update_many(filter, update,upsert=upsert)

        if upsert:
            return str(result.upserted_id)
        
        return result.modified_count

    def count(self, collection_name: str, filter: dict = None) -> int:
        """
        :description: 统计文档数量
        :param collection_name: 集合名称
        :param filter: 查询条件
        :return: 文档数量
        :last_editors: ChenXiaolei
        """
        collection = self.get_collection(collection_name)
        return collection.count_documents(filter)

    def aggregate(self, collection_name: str, pipeline: list) -> Cursor:
        """
        :description: 执行聚合操作
        :param collection_name: 集合名称
        :param pipeline: 聚合管道
        :return: 聚合结果游标
        :last_editors: ChenXiaolei
        """
        collection = self.get_collection(collection_name)
        return collection.aggregate(pipeline)

    def data_context(self, collection_name, operate_type, object_content):
        """
        :description: 通用数据操作接口
        :param collection_name: 集合名称
        :param operate_type: 操作类型（insertOne/insertMany/find/count/updateMany/aggregate）
        :param object_content: 操作内容
        :return: 操作结果
        :last_editors: ChenXiaolei
        """
        collection = self.get_collection(collection_name)
        if operate_type in ["insertOne", "insertMany"]:
            if not object_content or len(object_content) < 1:
                raise ValueError(
                    "object_content must contain at least one document")
            method = getattr(collection, operate_type.replace(
                "One", "_one").replace("Many", "_many"))
            return method(object_content[0])
        elif operate_type in ["find", "count"]:
            method = getattr(collection, operate_type)
            if len(object_content) > 1:
                return method(object_content[0], **object_content[1])
            else:
                return method(object_content[0])
        elif operate_type == "updateMany":
            return collection.update_many(object_content[0], object_content[1])
        elif operate_type == "aggregate":
            return collection.aggregate(object_content[0])
        else:
            raise ValueError(f"Unsupported operation type: {operate_type}")

    def close(self):
        """
        关闭数据库连接
        """
        self.client.close()
