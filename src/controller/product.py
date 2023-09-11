from fastapi import APIRouter
from module import db, format
router = APIRouter(prefix="/product", tags=["Product"])

# GET ONE POST
@router.get("/{product_id}")
def get_product(product_id: int):
    data = db.execute_sql_command("""select p.*, (select c.category_name from categories c where c.category_id=p.category_id) as category_name from products p where p.product_id='%s' limit 1;""" % (product_id))
    return format.successResponse(data)