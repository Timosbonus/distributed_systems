from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from app.dependencies import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.schemas.price_history import PriceHistoryResponse
from app.services.product_service import ProductService


router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse)
async def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    new_product = service.add_product(
        name=product.name,
        idealo_link=product.idealo_link,
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        image_data=product.image_data,
        description=product.description,
        minimum_margin=product.minimum_margin,
        manual_sell_price=product.manual_sell_price
    )

    await service.scrape_and_update_price(new_product.id)
    new_product = service.get_product(new_product.id)

    image_data_list = []
    if new_product.image_data:
        try:
            image_data_list = json.loads(new_product.image_data)
        except:
            image_data_list = []

    return ProductResponse(
        id=new_product.id,
        name=new_product.name,
        idealo_link=new_product.idealo_link,
        lowest_price=new_product.lowest_price,
        lowest_seller=new_product.lowest_seller,
        quantity=new_product.quantity,
        cost_per_unit=new_product.cost_per_unit,
        sell_price=new_product.sell_price,
        manual_sell_price=new_product.manual_sell_price,
        last_price_update=new_product.last_price_update.isoformat() if new_product.last_price_update else None,
        image_data=image_data_list,
        description=new_product.description,
        minimum_margin=new_product.minimum_margin
    )


@router.get("", response_model=List[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    service = ProductService(db)
    products = service.get_all_products()

    result = []
    for p in products:
        image_data_list = []
        if p.image_data:
            try:
                image_data_list = json.loads(p.image_data)
            except:
                pass

        result.append(ProductResponse(
            id=p.id,
            name=p.name,
            idealo_link=p.idealo_link,
            lowest_price=p.lowest_price,
            lowest_seller=p.lowest_seller,
            quantity=p.quantity,
            cost_per_unit=p.cost_per_unit,
            sell_price=p.sell_price,
            manual_sell_price=p.manual_sell_price,
            last_price_update=p.last_price_update.isoformat() if p.last_price_update else None,
            image_data=image_data_list,
            description=p.description,
            minimum_margin=p.minimum_margin
        ))

    return result


@router.post("/{product_id}/update-price", response_model=ProductResponse)
async def update_price(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    result = await service.scrape_and_update_price(product_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product = service.get_product(product_id)

    image_data_list = []
    if product.image_data:
        try:
            image_data_list = json.loads(product.image_data)
        except:
            pass

    return ProductResponse(
        id=product.id,
        name=product.name,
        idealo_link=product.idealo_link,
        lowest_price=product.lowest_price,
        lowest_seller=product.lowest_seller,
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        sell_price=product.sell_price,
        manual_sell_price=product.manual_sell_price,
        last_price_update=product.last_price_update.isoformat() if product.last_price_update else None,
        image_data=image_data_list,
        description=product.description,
        minimum_margin=product.minimum_margin
    )


@router.get("/{product_id}/history", response_model=List[PriceHistoryResponse])
def price_history(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    history = service.get_price_history(product_id)

    return [
        PriceHistoryResponse(
            id=h.id,
            price=h.price,
            seller=h.seller,
            timestamp=h.timestamp.isoformat()
        )
        for h in history
    ]


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    deleted = service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    updated = service.update_product(
        product_id=product_id,
        name=product.name,
        idealo_link=product.idealo_link,
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        description=product.description,
        minimum_margin=product.minimum_margin,
        image_data=product.image_data,
        manual_sell_price=product.manual_sell_price
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")

    image_data_list = []
    if updated.image_data:
        try:
            image_data_list = json.loads(updated.image_data)
        except:
            pass

    return ProductResponse(
        id=updated.id,
        name=updated.name,
        idealo_link=updated.idealo_link,
        lowest_price=updated.lowest_price,
        lowest_seller=updated.lowest_seller,
        quantity=updated.quantity,
        cost_per_unit=updated.cost_per_unit,
        sell_price=updated.sell_price,
        manual_sell_price=updated.manual_sell_price,
        last_price_update=updated.last_price_update.isoformat() if updated.last_price_update else None,
        image_data=image_data_list,
        description=updated.description,
        minimum_margin=updated.minimum_margin
    )
