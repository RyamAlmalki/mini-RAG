from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy.future import select
from sqlalchemy import func


# .commit() is used to save changes to the database
# .execute() is used to execute to retrieve data from the database
# .scalars() is used to retrieve a single column from the result set
# .scalar_one_or_none() is used to retrieve a single row from the result set or None if no rows are found
# .refresh() is used to refresh the state of an object from the database
# .add() is used to add an object to the session
# .begin() is used to begin a transaction
# .offset() is used to skip a number of rows in the result set
# .limit() is used to limit the number of rows returned in the result set
# .all() is used to retrieve all rows from the result set


class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

   
    @classmethod 
    async def create_instance(cls, db_client: object):
        instance = cls(db_client=db_client) # this will call the __init__ method
        return instance

    
    async def create_project(self, project: Project):
        
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        
        return project



    async def get_project_or_create_one(self, project_id: str) -> Project:
        async with self.db_client() as session:
            async with session.begin():
                
                query = select(Project).where(Project.project_id == project_id)
                project = query.scaler_one_or_none()
                
                if project is None:
                    project_rec = Project(project_id=project_id)
                    project = self.create_project(project_rec)

                    return project
                
                else:
                    return project



    async def get_all_projects(self, page: int = 1, page_size: int = 10) -> list[Project]:
        
        async with self.db_client() as session:
            async with session.begin():
                
                # this just made the query to get all projects
                total_documents = await session.execute(
                    select(func.count(Project.project_id))
                )
                
                # here we excute the query to get the total number of documents
                total_documents = total_documents.scalar_one()

                total_pages = total_documents // page_size
                
                if total_documents % page_size > 0:
                    total_pages += 1

                query = select(Project).offset((page - 1) * page_size).limit(page_size)

                project = await session.execute(query).scalars().all()


                return project, total_pages