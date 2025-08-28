from typing import List
from pydantic import BaseModel

from .common import Id


class Folder(BaseModel):
    id: Id
    key: str
    title: str
    children: List["Folder"] = []


class CreateFolderRequest(BaseModel):
    name: str
    parentId: Id
    spaceId: Id


class MoveFolderRequest(BaseModel):
    folderId: Id
    newParentId: Id


class RenameFolderRequest(BaseModel):
    folderId: Id
    newName: str


# Это необходимо для рекурсивных ссылок в моделях
Folder.model_rebuild()
