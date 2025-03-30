
import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse
import asyncio
from datetime import time, datetime, timedelta
import database

import schemas
import crud


app = FastAPI()



async def daily_cleanup():
    while True:
        now = datetime.now()
        # Вычисляем время до следующего запуска (3:00 утра)
        next_run = datetime.combine(now.date(), time(3, 0))
        if now > next_run:
            next_run += timedelta(days=1)

        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        await crud.delete_expired_links(database.get_db)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(daily_cleanup())


@app.post("/links/shorten")
async def shorted_link(link: schemas.LinkCreate, db: AsyncSession = Depends(database.get_db)):
    return await crud.create_link(db, link)

@app.get("/links/{short_code}")
async def redirect_to_original(short_code: str, db: AsyncSession = Depends(database.get_db)):
    full_link = await crud.get_link_by_short_code(db, short_code)
    await crud.update_link_clicks(db, full_link )
    return RedirectResponse(url = full_link.original_url)


@app.delete("/links/{short_code}")
async def delete_short_score(short_code: str, db: AsyncSession = Depends(database.get_db)):
    await crud.get_link_deleted(db,short_code)
    return {"message" : f"Link has {short_code} has been deleted"}

@app.put("/links/{short_code}")
async def update_link_by_short(short_code: str, new_url: schemas.LinkCreate, db: AsyncSession = Depends(database.get_db)):
    await crud.update_link(db, short_code, new_url)
    return {"message":"Link has been changed"}

@app.get("/links/{short_code}/stats")
async def get_link_stat(short_code: str, db: AsyncSession = Depends(database.get_db)):
    link = await crud.get_link_by_short_code(db, short_code)
    return link

@app.get("/links/search")
async def search_links(original_url: str, db: AsyncSession = Depends(database.get_db)):
    results = await crud.get_link_by_origin(db,original_url)
    return results



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="info")