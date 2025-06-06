from .BaseDataModel import BaseDataModel
from .db_schemes.project import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def create_project(self, project: Project):
        
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id
        return project

    async def get_project_or_create_one(self, project_id: str) -> Project:
        project = await self.collection.find_one({"project_id": project_id})
        
        if not project:
            # If the project does not exist, create a new one
            new_project = Project(project_id=project_id)
            return await self.create_project(new_project)
        
        # Convert dict to Project model
        return Project(**project)
    
    # pagination is not implemented in this example 
    async def get_all_projects(self, page: int = 1, page_size: int = 10) -> list[Project]:
        
        total_documents = await self.collection.count_documents({})

        total_pages = total_documents // page_size 
        
        if total_documents % page_size > 0: 
            total_pages += 1
        
        # this solves the pagination issue returns cursor
        cursor = self.collection.skip((page - 1) * page_size).limit(page_size)

        projects = []

        async for project in cursor:
            projects.append(Project(**project))
        
        return projects, total_pages