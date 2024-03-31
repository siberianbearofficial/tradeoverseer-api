from fastapi import APIRouter

from utils.exceptions import exception_handler
from utils.dependency import OrdersServiceDep

from orders.schemas import Order

router = APIRouter(prefix='/orders', tags=['Orders'])


@router.post('')
@exception_handler
async def post_order_handler(order: Order,
                             orders_service: OrdersServiceDep):
    await orders_service.add_order(order)
    return {
        'data': None,
        'detail': 'Order was added.'
    }
