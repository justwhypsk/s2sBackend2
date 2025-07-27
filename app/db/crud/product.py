from bson import ObjectId
from ..models.product import AddProduct, GetProduct
from ..mongo import get_collection
from app.services.cloudinary import upload_to_cloudinary

# Get the products collection
collection = get_collection("products")


def get_all_products():
    """
    Retrieve all products from the database.
    Returns a list of products as GetProduct instances.
    """
    try:
        productscur = collection.find()
        products = []
        for obj in productscur:
            obj["id"] = str(
                obj.pop("_id")
            )  # Convert ObjectId to string and rename to 'id'
            products.append(GetProduct(**obj))  # Initialize Pydantic model
        return products
    except Exception as e:
        print(f"An error occurred while retrieving products: {e}")
        return []


def add_product(product: AddProduct):
    """
    Add a new product to the database.
    Returns the inserted product's ID as a string.
    """
    try:
        # Check if image is base64 if it is then upload to cloudinary and replace with image link
        if product.image.startswith("data:image"):
            image_link = upload_to_cloudinary(product.image)
            product.image = image_link
        result = collection.insert_one(product.dict())
        product_id = str(result.inserted_id)
        return product_id
    except Exception as e:
        print(f"An error occurred while adding a product: {e}")
        return None


def get_product_by_id(productid: str):
    """
    Retrieve a product by its ID.
    Returns the product as a GetProduct instance.
    """
    try:
        product = collection.find_one({"_id": ObjectId(productid)})
        if product:
            product["id"] = str(
                product.pop("_id")
            )  # Convert ObjectId to string and rename to 'id'
            return GetProduct(**product)  # Convert to Pydantic model
    except Exception as e:
        print(f"An error occurred while retrieving a product: {e}")
    return None


def update_product(productid: str, product: AddProduct):
    """
    Update a product by its ID.
    Returns True if the update was successful, False otherwise.
    """
    try:
        result = collection.update_one(
            {"_id": ObjectId(productid)}, {"$set": product.dict()}
        )
        return result.upserted_id
    except Exception as e:
        print(f"An error occurred while updating a product: {e}")
        return False

def delete_product(productid: str):
    """
    Delete a product by its ID.
    Returns True if the deletion was successful, False otherwise.
    """
    try:
        result = collection.delete_one({"_id": ObjectId(productid)})
        all_products = get_all_products()
        return all_products
    except Exception as e:
        print(f"An error occurred while deleting a product: {e}")
        return False