from fastapi import APIRouter, HTTPException
from typing import List
from bson import ObjectId
from backend.app.db.crud.product import add_product, get_all_products, get_product_by_id, update_product, delete_product
from backend.app.db.models.product import AddProduct, GetProduct
from backend.app.services.validation import check_product_details
from backend.app.services.moderation import check_product_moderation

router = APIRouter(prefix="/api", tags=["Product"])


@router.post("/products", response_model=str, summary="Add a new product")
async def create_product(product: AddProduct):
    """
    Create a new product in the database.
    - **product**: Product details as per AddProduct schema.
    """
    # Validate product details using the external API
    validation_result = check_product_details(product.dict())
    if not validation_result.get("validated"):
        raise HTTPException(
            status_code=400,
            detail=f"Product validation failed. Reason: {validation_result.get('error', 'Invalid product details.')}",
        )
    
    # Check the moderation status of the product details
    moderation_result = check_product_moderation(product.dict())
    if moderation_result.get("inappropriate_content"):
        raise HTTPException(
            status_code=400,
            detail=f"Product validation failed. Reason: {moderation_result.get('error', 'Inappropriate Content')}",
        )
    
    # Add product to the database
    product_id = add_product(product)
    if not product_id:
        raise HTTPException(status_code=500, detail="Failed to add product.")
    return product_id

@router.get(
    "/products", response_model=List[GetProduct], summary="Retrieve all products"
)
async def list_products():
    """
    Retrieve all products from the database.
    """
    products = get_all_products()
    if not products:
        raise HTTPException(status_code=404, detail="No products found.")
    return products


@router.put(
    "/products/{product_id}",
    response_model=GetProduct,
    summary="Update a product by ID",
)
async def update_product(product_id: str, product: AddProduct):
    """
    Update a product by its ID.
    - **product_id**: The ID of the product to update.
    - **product**: Product details as per AddProduct schema.
    """
    try:
        if not ObjectId.is_valid(product_id):
            raise HTTPException(status_code=400, detail="Invalid product ID format.")
        updated = update_product(product_id, product)
        if not updated:
            raise HTTPException(status_code=404, detail="Product not found.")
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating product: {str(e)}"
        )
    
@router.delete(
    "/products/{product_id}", response_model=List[GetProduct], summary="Delete a product"
)
async def remove_product(product_id: str):
    """
    Delete a product by its ID.
    - **product_id**: The ID of the product to delete.
    """
    try:
        if not ObjectId.is_valid(product_id):
            raise HTTPException(status_code=400, detail="Invalid product ID format.")
        deleted = delete_product(product_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Product not found.")
        return deleted
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting product: {str(e)}"
        )


@router.get(
    "/products/{product_id}",
    response_model=GetProduct,
    summary="Retrieve a product by ID",
)
async def retrieve_product(product_id: str):
    """
    Retrieve a product by its ID.
    - **product_id**: The ID of the product to retrieve.
    """
    try:
        if not ObjectId.is_valid(product_id):
            raise HTTPException(status_code=400, detail="Invalid product ID format.")
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found.")
        return product
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving product: {str(e)}"
        )
