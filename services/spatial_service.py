import os
import psycopg2
from psycopg2.extras import RealDictCursor
import geojson
from shapely import wkt
from shapely.geometry import mapping
from typing import List, Dict, Any, Optional
import logging

import services.lakebase as lakebase
from databricks.sdk import WorkspaceClient

# Configuration
local_service_principal_name = 'local-service-principal'
group_name = '2025_vibe_coding'
instance_name = 'mpelletier-demo'
LAKEBASE_DB_NAME = 'databricks_postgres'
user_email = 'mathieu.pelletier@databricks.com'

# Create workspace client
w = WorkspaceClient(profile="adb-984752964297111")

# Get the database instance
instance = w.database.get_database_instance(instance_name)

logger = logging.getLogger(__name__)

class SpatialService:
    """Service for handling spatial data queries with PostGIS"""
    
    def __init__(self):
        self._connection = None
        self._connection_time = None
    
    def _get_connection(self):
        """Get or create database connection with singleton pattern"""
        import time
        
        # Check if connection exists and is not expired (59 minutes)
        if (self._connection is None or 
            self._connection.closed != 0 or 
            (self._connection_time and time.time() - self._connection_time > 3540)):  # 59 minutes
            
            try:
                
                # Create connection
                self._connection = lakebase.create_lakebase_connection(wc=w, instance=instance, db_name=LAKEBASE_DB_NAME, user=user_email)
                self._connection.set_isolation_level(0)

                self._connection_time = time.time()
                logger.info("New PostGIS connection established")
            except Exception as e:
                logger.error(f"Failed to connect to PostGIS: {e}")
                raise e
        
        return self._connection
    
    def query(self, sql: str) -> List[Dict[str, Any]]:
        """Execute spatial query and return results as list of dicts"""
        try:
            connection = self._get_connection()
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                connection.commit()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Spatial query failed: {e}")
            raise e
    
    def get_spatial_data_as_geojson(self, table_name: str, geometry_column: str = 'geom', 
                                  where_clause: str = '', province_filter: str = '', province_column: str = 'province', limit: int = 1000) -> Dict[str, Any]:
        """Get spatial data from PostGIS table and return as GeoJSON"""
        try:
            # Build where conditions
            where_conditions = []
            if where_clause:
                where_conditions.append(where_clause)
            if province_filter:
                where_conditions.append(f"{province_column} = '{province_filter}'")
            
            where_sql = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # Build the query to get spatial data as GeoJSON
            sql = f"""
            SELECT jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_agg(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry', ST_AsGeoJSON({geometry_column})::jsonb,
                        'properties', to_jsonb(t.*) - '{geometry_column}'
                    )
                )
            ) as geojson
            FROM (
                SELECT * FROM {table_name}
                {where_sql}
                LIMIT {limit}
            ) t;
            """
            
            result = self.query(sql)
            if result and result[0]['geojson']:
                return result[0]['geojson']
            else:
                return {
                    "type": "FeatureCollection",
                    "features": []
                }
        except Exception as e:
            logger.error(f"Failed to get spatial data as GeoJSON: {e}")
            raise e
    
    def get_tables_with_geometry(self) -> List[Dict[str, Any]]:
        """Get list of tables that contain geometry columns"""
        sql = """
            SELECT 
                schemaname,
                viewname AS tablename,
                attname AS geometry_column,
                typname AS geometry_type
            FROM pg_views t
            JOIN pg_attribute a ON a.attrelid = (
                SELECT oid FROM pg_class WHERE relname = t.viewname
            )
            JOIN pg_type ty ON ty.oid = a.atttypid
            WHERE schemaname = 'public' 
            AND typname IN ('geometry', 'geography')
            ORDER BY tablename;
        """
        return self.query(sql)
    
    def get_bounds(self, table_name: str, geometry_column: str = 'geom') -> Dict[str, float]:
        """Get bounding box for a spatial table"""
        sql = f"""
        SELECT 
            ST_XMin(ST_Extent({geometry_column})) as minx,
            ST_YMin(ST_Extent({geometry_column})) as miny,
            ST_XMax(ST_Extent({geometry_column})) as maxx,
            ST_YMax(ST_Extent({geometry_column})) as maxy
        FROM {table_name};
        """
        result = self.query(sql)
        if result:
            return {
                'minx': float(result[0]['minx']) if result[0]['minx'] else 0,
                'miny': float(result[0]['miny']) if result[0]['miny'] else 0,
                'maxx': float(result[0]['maxx']) if result[0]['maxx'] else 0,
                'maxy': float(result[0]['maxy']) if result[0]['maxy'] else 0
            }
        return {'minx': -180, 'miny': -90, 'maxx': 180, 'maxy': 90}
    
    def get_wildfires_count(self, province_filter: str = '') -> int:
        """Get count of wildfires with optional province filtering"""
        where_clause = ""
        if province_filter:
            where_clause = f"WHERE properties->>'Province' = '{province_filter}'"
        
        sql = f"""
        SELECT COUNT(*) as count
        FROM wildfires
        {where_clause};
        """
        result = self.query(sql)
        if result and result[0]:
            return int(result[0]['count'])
        return 0
    
    def get_active_wildfires_count(self, province_filter: str = '') -> int:
        """Get count of active wildfires (wildfires near tracks) with optional province filtering"""
        where_clause = ""
        if province_filter:
            where_clause = f"WHERE w.properties->>'Province' = '{province_filter}'"
        
        sql = f"""
        SELECT COUNT(*) as count
        FROM fire_near_track ft
        JOIN wildfires w ON w.id = ft.wid
        {where_clause};
        """
        result = self.query(sql)
        if result and result[0]:
            return int(result[0]['count'])
        return 0

# Singleton instance
spatial_service = SpatialService()
