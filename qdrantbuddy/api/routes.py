from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
from pathlib import Path
from pydantic import BaseModel
from qdrantbuddy.config import load_config
from qdrantbuddy.crud import QdrantCRUD

# Load the configuration
config = load_config()

# Initialize the Indexer instance (assuming config is set)
qdrant_crud = QdrantCRUD()

router = APIRouter()

@router.post("/add-files/")
async def add_files(files: List[UploadFile] = File(...)):
    try:
        # Create a temporary directory to store files
        temp_dir = Path("tmp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the uploaded files to the temporary directory
        file_paths = []
        for file in files:
            file_path = temp_dir / Path(file.filename).name
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            file_paths.append(file_path)
        
        # Now pass the directory path to the Indexer
        await qdrant_crud.add_files(path=temp_dir)

        # Optionally, clean up the temporary directory after processing
        for file_path in file_paths:
            os.remove(file_path)
        
        return JSONResponse(content={"message": "Files processed and added to the vector database."}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Define Pydantic model for request body
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5  # default to 5 if not provided

@router.post("/search/")
async def search(query_params: SearchRequest):
    try:
        # Extract query and top_k from request
        query = query_params.query
        top_k = query_params.top_k
        
        # Perform the search using the Indexer
        results = await qdrant_crud.search(query, top_k)
        
        # Transforming the results (assuming they are LangChain documents)
        documents = [{"page_content": doc.page_content, "metadata": doc.metadata} for doc in results]
        
        # Return results
        return JSONResponse(content={"results": documents}, status_code=200)

    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-files/")
async def delete_files(file_names: List[str]):
    """
    Delete points in Qdrant associated with the given file names.

    Args:
        file_names (List[str]): A list of file names whose points are to be deleted.

    Returns:
        JSONResponse: A confirmation message including details of files processed.
    """

    try:
        deleted_files, not_found_files = qdrant_crud.delete_files(file_names)
        return {
            "message": "File processing completed.",
            "files_deleted": deleted_files,
            "files_not_found": not_found_files,
        }

    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=500, detail=str(e))

