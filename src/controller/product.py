from fastapi import APIRouter
from module import db
router = APIRouter(prefix="/product", tags=["Product"])

# GET ONE POST
@router.get("/{product_id}")
def get_product(product_id: int):
    data = db.execute_sql_command('SELECT * FROM products;')
    return {'test': product_id, 'data': data}