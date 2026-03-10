from fastapi import APIRouter,FastAPI, status, Request
import logging
from fastapi.responses import JSONResponse
from src.routes.schemas.nlp import PushRequest , SearchRequest
from src.models.Chunk_model import ChunkModel
from src.models.ProjectModel import ProjectModel
from src.controllers import NLPController
from src.models import ResponseSignals
from bson.objectid import ObjectId

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"],
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request : Request, project_id : str, PushRequest : PushRequest):
    project_model = await ProjectModel.create_instance(
        db_client= request.app.db_client
    )

    chunk_model= await ChunkModel.create_instance(db_client= request.app.db_client)


    project = await project_model.get_project_or_createone(
        project_id = project_id
    )
    
    if not project:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                            content= "project_not_found_error")
    
    nlp_controller = NLPController(vectordb_client = request.app.vectordb_client,
                                    generation_client= request.app.generation_client,
                                    embedding_client = request.app.embedding_client,
                                    )

    has_records = True
    page_no = 1 
    inserted_item_count = 0
    idx = 0 

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id= project_id, page_no =page_no)
        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len (page_chunks) == 0:
            has_records= False
            break

        chunks_ids = list (range(idx, idx +len(page_chunks)))
        idx +=len (page_chunks)

        is_inserted = nlp_controller.index_info_vectordb(
            project=project,
            chunks=page_chunks,
            do_reset = PushRequest.do_reset,
            chunk_ids= chunks_ids
        )
        if not is_inserted:
           return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                            content= {"insert into db error"})
        
        inserted_item_count+= len(page_chunks)
    return JSONResponse(
         content={"signal":"insert into db sucess","inserted item count":inserted_item_count}
        )

            
    #chunks = chunk_model.get_project_chunks(project_id= project_id)

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: str):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_createone(
        project_id=project_id
    )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
    )

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        content={
            "signal": "VECTORDB_COLLECTION_RETRIEVED",
            "collection_info": collection_info
        }
    )
@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: str, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_createone(
        project_id=project_id
    )
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": "ResponseSignals.VECTORDB_SEARCH_ERROR.value"},
        )

    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
    )

    results = nlp_controller.search_vector_db_collection(
        project=project, text=search_request.text, limit=search_request.limit
    )

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": "ResponseSignal.VECTORDB_SEARCH_ERROR.value"
                }
            )
    
    return JSONResponse(
        content={
            "signal": "ResponseSignal.VECTORDB_SEARCH_SUCCESS.value",
            "results": [ result.dict()  for result in results ]
        }
    )


