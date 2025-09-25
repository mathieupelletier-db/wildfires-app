from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
from services.spatial_service import spatial_service

# Load environment variables
load_dotenv()

app = FastAPI(title="Vibe Coding App", version="1.0.0")

# Mount static files from frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    """Serve the main index.html file"""
    return FileResponse("frontend/index.html")

@app.get("/api/spatial/tables")
async def get_spatial_tables():
    """Get list of tables with geometry columns"""
    try:
        tables = spatial_service.get_tables_with_geometry()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/spatial/geojson/{table_name}")
async def get_geojson_data(table_name: str, geometry_column: str = "geom", province_filter: str = "", province_column: str = "province", limit: int = 1000):
    """Get spatial data as GeoJSON from specified table"""
    try:
        geojson_data = spatial_service.get_spatial_data_as_geojson(
            table_name=table_name,
            geometry_column=geometry_column,
            province_filter=province_filter,
            province_column=province_column,
            limit=limit
        )
        return geojson_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/spatial/bounds/{table_name}")
async def get_table_bounds(table_name: str, geometry_column: str = "geom"):
    """Get bounding box for a spatial table"""
    try:
        bounds = spatial_service.get_bounds(table_name, geometry_column)
        return bounds
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/map")
async def read_map():
    """Serve the map page"""
    return FileResponse("frontend/map.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
