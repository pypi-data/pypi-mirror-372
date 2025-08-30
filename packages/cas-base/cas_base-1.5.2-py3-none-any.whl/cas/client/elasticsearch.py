from elasticsearch import AsyncElasticsearch, NotFoundError
from ..base.logger import logger


class ElasticsearchClient:
    def __init__(self, host, username=None, password=None):
        # 初始化 Elasticsearch 客户端
        self.ins = AsyncElasticsearch(hosts=host, basic_auth=(username, password) if username and password else None)
        logger.debug("Elasticsearch 客户端已初始化")

    async def create_index(self, index_name, settings=None):
        # 创建索引
        if not await self.ins.indices.exists(index=index_name):
            await self.ins.indices.create(index=index_name, body=settings)
            logger.debug(f"索引 '{index_name}' 已创建")
        else:
            logger.error(f"索引 '{index_name}' 已存在")

    async def delete_index(self, index_name):
        # 删除索引
        try:
            await self.ins.indices.delete(index=index_name)
            logger.debug(f"索引 '{index_name}' 已删除")
        except NotFoundError:
            logger.warning(f"索引 '{index_name}' 未找到")

    async def index_document(self, index_name, doc_id, document):
        # 索引文档
        await self.ins.index(index=index_name, id=doc_id, document=document)
        logger.debug(f"文档 ID '{doc_id}' 已索引到 '{index_name}'")

    async def delete_document(self, index_name, doc_id):
        # 删除文档
        try:
            await self.ins.delete(index=index_name, id=doc_id)
            logger.debug(f"文档 ID '{doc_id}' 已从 '{index_name}' 删除")
        except NotFoundError:
            logger.debug(f"文档 ID '{doc_id}' 在索引 '{index_name}' 中未找到")

    async def get_document(self, index_name, doc_id):
        # 获取文档
        try:
            response = await self.ins.get(index=index_name, id=doc_id)
            logger.debug(f"文档 ID '{doc_id}' 从 '{index_name}' 获取成功")
            return response["_source"]
        except NotFoundError:
            logger.debug(f"文档 ID '{doc_id}' 未找到在 '{index_name}'")

    async def search(self, index_name, query, size=10):
        # 搜索文档
        response = await self.ins.search(index=index_name, body=query, size=size)
        logger.debug(f"在索引 '{index_name}' 中搜索成功")
        return response["hits"]["hits"]

    async def close(self):
        # 关闭客户端
        await self.ins.close()
        logger.debug("Elasticsearch 客户端已关闭")
