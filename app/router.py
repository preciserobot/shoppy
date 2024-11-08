import os
from typing import Union, Optional, Annotated
from fastapi import APIRouter, HTTPException, Form, Request, status
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.models import Item
from app.config import ITEM_PREFIX
from app.redis import DB

router = APIRouter(
    prefix="",
    responses={
        200: {"description": "Item found and returned"},
        201: {"description": "Item created (empty)"},
        204: {"description": "Item updated"},
        303: {"description": "Redirect to curation interface"},
        400: {"description": "Bad Request (content-type)"},
        404: {"description": "Item not found"},
        500: {"description": "Internal Server Error, please check the logs"},
    }
)

# Load templates
app_dir = os.path.dirname(__file__)
template_dir = os.path.join(app_dir, "templates")
templates = Jinja2Templates(directory=template_dir)

# manually create a new item
@router.post("/items", description="Create item by EAN", response_class=RedirectResponse)
async def create_item(
    request: Request,
    ean: Annotated[Optional[str], Form(description="EAN code", required=True)],
    name: Annotated[str, Form(description="Item name", required=True)],
    detail: Annotated[str, Form(description="Item detail")],
    quantity: Annotated[str, Form(description="Item quantity")],
    unit: Annotated[str, Form(description="Item unit")],
) -> RedirectResponse:
    # Check if already exists
    if Item.from_redis(ean):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item already exists")
    # Check if JSON body is provided (API)
    if request.headers.get("content-type") == "application/x-www-form-urlencoded":
        item = Item(ean=ean, name=name, detail=detail, quantity=quantity, unit=unit)
        item.write()
        return RedirectResponse(url="/items", status_code=status.HTTP_303_SEE_OTHER)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid content-type")

# read single item JSON
@router.get("/items/{ean}", description="Read item by EAN", response_model=Item)
async def read_item(request: Request, ean: str, create: bool = True) -> Item:
    # check if item exists
    item = Item.from_redis(ean)
    # get from API
    if not item:
        item = Item.from_api(ean)
        if item:
            item.write()
    # return item
    if item:
        return JSONResponse(content=item.model_dump(), status_code=status.HTTP_200_OK)
    if create:
        item = Item(ean=ean, name="Unknown Item")
        item.write()
        return JSONResponse(content=item.model_dump(), status_code=status.HTTP_201_CREATED)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

# Curation interface for all items
@router.get("/items", description="Curation interface", response_model=list[Item])
async def read_items(request: Request) -> HTMLResponse:
    db = DB()
    keys = db.keys(f"{ITEM_PREFIX}*")
    items = []
    for key in keys:
        item = Item.from_redis(key.replace(ITEM_PREFIX, ""))
        if item:
            items.append(item.model_dump())
    if request.headers.get("content-type") == "application/json":
        return JSONResponse(content=items, status_code=status.HTTP_200_OK)
    return templates.TemplateResponse(request=request, name="items.html", context={ 'items': items })

# Update Item (JSON)
@router.put("/items", description="Update item by EAN (JSON)", response_model=Item)
async def update_item(
    request: Request,
    json_body: Item,
) -> Union[Item, RedirectResponse]:
    # Get item from Redis
    item = Item.from_redis(json_body.ean)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if request.headers.get("content-type") == "application/json":
        item.update(json_body).write()
        return JSONResponse(content=item.model_dump(), status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")

# Update Item (FORM)
@router.post("/items/{ean}/update", description="Update item by EAN (FORM)", response_class=RedirectResponse)
async def update_item(
    request: Request,
    ean: str,
    name: Annotated[str, Form(description="Item name", required=True)],
    detail: Annotated[Union[str, None], Form(description="Item detail")] = None,
    quantity: Annotated[Union[str, None], Form(description="Item quantity")] = None,
    unit: Annotated[str, Form(description="Item unit")] = None,
) -> RedirectResponse:
    # Get item from Redis
    item = Item.from_redis(ean)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    # Check if form data is provided (Curation interface)
    if request.headers.get("content-type") == "application/x-www-form-urlencoded":
        new_item = Item(ean=item.ean, name=name, detail=detail, quantity=quantity, unit=unit)
        item.update(new_item)
        item.write()
        return RedirectResponse(url="/items", status_code=status.HTTP_303_SEE_OTHER)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")
    
# Delete Item (FORM)
@router.post("/items/{ean}/delete", description="Delete item by EAN", response_class=RedirectResponse)
async def delete_item(request: Request, ean: str) -> RedirectResponse:
    item = Item.from_redis(ean)
    if not item: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    item.delete()
    return RedirectResponse(url="/items", status_code=status.HTTP_303_SEE_OTHER)
