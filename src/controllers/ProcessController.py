from .BaseController import BaseController
from .ProjectController import ProjectController
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.text import TextLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter

from models import ProcessEnum


class ProcessController(BaseController):
    def __init__(self, project_id):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id:str):
        return os.path.splitext(file_id)[-1]
    
    def get_file_loader(self, file_id:str):

        file_ext = self.get_file_extension(file_id = file_id)

        file_path = os.path.join(
            self.project_path,
            file_id
        )

        if not os.path.exists(file_path) :
            return None


        if file_ext == ProcessEnum.TXT.value:
            return TextLoader(file_path, encoding='utf-8')
        
        if file_ext == ProcessEnum.PDF.value:
            return PyPDFLoader(file_path)
        
        return None
    
    def get_file_content(self, file_id):

        loader = self.get_file_loader(file_id= file_id)

        # if the extention doesn't exist it will return None 
        if loader is None :
            return None
        return loader.load()
    


    def process_file_content(self, file_content: list, file_id:str, 
                             chunk_size:int=100, overlap_size:int=20):
        

        file_content_texts = [rec.page_content for rec in file_content]
        file_content_metadatas = [rec.metadata for rec in file_content]

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
            is_separator_regex=False
        )


        chunks = text_splitter.create_documents(file_content_texts, metadatas=file_content_metadatas )

        #return  [{"content": chunk.page_content, "metadata": chunk.metadata} for chunk in chunks]
        return chunks





