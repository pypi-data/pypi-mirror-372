
from .metadata_adapter import MetadataAdapter
from .local import FileMetadataAdapter


def create_meta_adapter() -> MetadataAdapter:
    # todo 切换为数据库的元数据管理
    return FileMetadataAdapter()


__all__ = ['create_meta_adapter']