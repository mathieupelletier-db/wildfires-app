# 2025 Vibe Coding App

A modern web application built with FastAPI featuring spatial data visualization capabilities. Integrates with PostGIS for geospatial data management and provides interactive mapping functionality.

## Technologies Used

-   **FastAPI**: High-performance web framework for building APIs
-   **Uvicorn**: ASGI server for running the FastAPI application
-   **Python-dotenv**: Environment variable management
-   **PostGIS**: Spatial database extension for PostgreSQL
-   **GeoAlchemy2**: SQLAlchemy extension for spatial data
-   **Leaflet**: Interactive mapping library
-   **psycopg2**: PostgreSQL database adapter
-   **HTML5/CSS3**: Modern, responsive frontend design

## Features

### 🗺️ Spatial Data Visualization

-   **Interactive Maps**: Leaflet-based mapping with OpenStreetMap tiles
-   **PostGIS Integration**: Direct connection to PostGIS spatial databases
-   **GeoJSON Support**: Native GeoJSON data format for web mapping
-   **Dynamic Table Discovery**: Automatically discover spatial tables in your database
-   **Feature Popups**: Click features to view their properties
-   **Responsive Design**: Works on desktop, tablet, and mobile devices

### 🎯 Core Functionality

-   **Spatial Data Loading**: Load and visualize spatial data from PostGIS tables
-   **Table Management**: Browse available spatial tables and geometry columns
-   **Data Filtering**: Limit number of features displayed for performance
-   **Auto-fit Bounds**: Automatically zoom to show all loaded data
-   **Real-time Updates**: Dynamic data loading without page refreshes

### 🎨 User Experience

-   **Beautiful Design**: Clean, modern interface with intuitive controls
-   **Loading States**: Visual feedback during data operations
-   **Error Handling**: User-friendly error messages and recovery
-   **Control Panel**: Easy-to-use interface for data selection and configuration

## Getting Started

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Set up environment variables:

    - Copy `example.env` to `.env`
    - Fill in your PostGIS database credentials:
        - `POSTGRES_HOST` (default: localhost)
        - `POSTGRES_PORT` (default: 5432)
        - `POSTGRES_DB` (your database name)
        - `POSTGRES_USER` (your username)
        - `POSTGRES_PASSWORD` (your password)

3. Run the application:

    ```bash
    python app.py
    ```

4. Open your browser to `http://localhost:8000`
5. Click "View Spatial Data Map" to access the mapping interface

## API Endpoints

### Spatial Data

-   `GET /api/spatial/tables` - Get list of tables with geometry columns
-   `GET /api/spatial/geojson/{table_name}` - Get spatial data as GeoJSON
-   `GET /api/spatial/bounds/{table_name}` - Get bounding box for a spatial table

### Web Pages

-   `GET /` - Main application page
-   `GET /map` - Interactive spatial data map

## Database Architecture

### PostGIS Integration

The app connects to PostGIS-enabled PostgreSQL databases to access spatial data:

-   **Spatial Tables**: Automatically discovers tables with geometry/geography columns
-   **GeoJSON Conversion**: Converts PostGIS spatial data to GeoJSON for web mapping
-   **Connection Management**: Singleton pattern with automatic connection refresh
-   **Performance**: Optimized queries with configurable feature limits

### Spatial Data Support

-   **Geometry Types**: Supports all PostGIS geometry types (Point, LineString, Polygon, etc.)
-   **Coordinate Systems**: Handles various coordinate reference systems
-   **Spatial Queries**: Leverages PostGIS spatial functions for data processing
-   **Bounds Calculation**: Automatic calculation of data extents for map fitting

### Security Considerations

⚠️ **SECURITY WARNING**: This demo uses f-string SQL queries for simplicity. In production, always use parameterized queries to prevent SQL injection attacks.

## Usage Examples

### Sample PostGIS Table

```sql
-- Example spatial table
CREATE TABLE sample_points (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom GEOMETRY(POINT, 4326)
);

-- Insert sample data
INSERT INTO sample_points (name, geom) VALUES 
('Point 1', ST_GeomFromText('POINT(-74.006 40.7128)', 4326)),
('Point 2', ST_GeomFromText('POINT(-73.9857 40.7484)', 4326));
```
