

import os

import psycopg2
import psycopg2.extras


import os


class Processor:

    conn = None
    cursor = None
    
    conn_string = ''
    osm2pgsql_string = ''
    
    def __init__(self,conn_string = None,osm2pgsql_string = None):
        #Подключение к базе, адреса передаются в аргументах этого конструктора
       
        # get a connection, if a connect cannot be made an exception will be raised here
        self.conn = psycopg2.connect(conn_string)
        self.conn.autocommit = True #для vaccuum 
        # conn.cursor will return a cursor object, you can use this cursor to perform queries
        self.cursor = self.conn.cursor()
        self.conn_string = conn_string
        self.osm2pgsql_string = osm2pgsql_string
        

    def drop_osm(self):
        
        sql='''
DROP TABLE IF EXISTS planet_osm_point CASCADE;
DROP TABLE IF EXISTS planet_osm_polygon CASCADE;
DROP TABLE IF EXISTS planet_osm_roads CASCADE
        '''
        self.cursor.execute(sql)
        self.conn.commit()


        
    def import_osm(self, filename='RU-SPE.osm.pbf', boundary_filename = 'city_boundary.geojson'):
        print 'Import OSM to PostGIS'

        print 'clip osm'
        
        #сmd = 'python ogr2poly.py '+'geodata/city_boundary.geojson ' + 'bounds.poly'
        cmd = 'python ogr2poly.py '+boundary_filename
        os.system(cmd) #todo addr
        poly_filename = os.path.basename(boundary_filename)
        poly_filename = os.path.splitext(poly_filename)[0] + '_0.poly'
        cmd = 'osmconvert {src} -B={poly_filename} -o=clipped.pbf'.format(src=filename, poly_filename=poly_filename)
        print cmd        
        os.system(cmd)


        print 'pbf to postgis'
        cmd='osm2pgsql {osm2pgsql_string} -s --create --multi-geometry --latlon  -C 1200 --number-processes 3 --hstore   --style special.style {filename}'.format(filename='clipped.pbf',osm2pgsql_string=self.osm2pgsql_string)
        print cmd        
        os.system(cmd)
        os.unlink('clipped.pbf')

    def import_local_geodata(self):
        #Запуск утилиты ogr2ogr которая грузит файл geojson в PostGIS
        cmd='ogr2ogr -f PostgreSQL PG:"{conn_string}" -t_srs EPSG:4326 blacklist.geojson -nln blacklist -nlt MultiPolygon -overwrite'.format(conn_string=self.conn_string)
        os.system(cmd)
        cmd='ogr2ogr -f PostgreSQL PG:"{conn_string}" -t_srs EPSG:4326 whitelist.geojson -nln whitelist -nlt MultiPolygon -overwrite'.format(conn_string=self.conn_string)
        os.system(cmd)
        cmd='ogr2ogr -f PostgreSQL PG:"{conn_string}" -t_srs EPSG:4326 city_boundary.geojson -nln cities -nlt MultiPolygon -overwrite'.format(conn_string=self.conn_string)
        os.system(cmd)



    def import_tags(self):
        print 'import tags table a2'


        sql='''
        DROP TABLE IF EXISTS tags CASCADE;
        CREATE TABLE tags (id serial primary key, sql varchar, dist varchar, city varchar, note varchar);
        '''
        self.cursor.execute(sql)
        self.conn.commit()

        import csv
        with open('OVD - Перечень.csv', 'rb') as f:
            reader = csv.reader(f)
            tags_list = list(reader)


        header=[]
        linecnt=0
        okaycounter=0
        for line in tags_list:
            linecnt+=1

            if (linecnt == 1):
                cellcnt=0
                for cell in line:
                    cellcnt = cellcnt + 1
                    s = str(cell)
                    header.append(s)
            elif (linecnt>2):
                linecnt += 1
                if ((line[0] != '' )):
                    query=line[0]
                    desc=line[1]
                    use=line[2]
                    maxval = line[4]
                    colcnt = 5
                    if str(use) != '0':
                        while colcnt<len(header):
                            #получение ширины буфера
                            if str(line[colcnt]).rstrip() == 'нпт':
                                #если нпт, то берётся из столбца 4
                                dist = str(maxval).rstrip()
                            elif ((len(str(line[colcnt]).rstrip())  > 4) and ((str(line[colcnt]).rstrip()[:4])=='нпт,' )):
                                #если запись вида "нпт,50" то берётся из этого столбца и прибавляется к столбцу 4
                                dist = str( int(maxval)[-4:] + int( str(line[colcnt]).rstrip() ))
                            else:
                                #если цифра, то берётся из этого столбца
                                dist=str(line[colcnt]).rstrip()


                            sql="INSERT INTO tags (sql, dist, use, city, note) VALUES ('{sql}','{dist}','{use}','{city}','{desc}')".format(
                                sql=query.replace("'","''").rstrip(),desc=desc,dist=dist,city=str(header[colcnt]), use=str(use) )
                            colcnt+=1
                            
                            self.cursor.execute(sql)
                            self.conn.commit()
                    else:
                        print 'no use'

                        



    def generate_areas(self,city='Москва'):


        #----------------------- polygons
        sql='''SELECT tags.sql, 
        CASE WHEN CAST((COALESCE(NULLIF(REGEXP_REPLACE(dist, '[^0-9]+', '', 'g'), ''), '0')) AS INTEGER) = 0 THEN 10 
        ELSE CAST((COALESCE(NULLIF(REGEXP_REPLACE(dist, '[^0-9]+', '', 'g'), ''), '0')) AS INTEGER) END AS dist,
        '' AS sql,
        note AS note 
        FROM tags 
        WHERE city ='{city}' AND dist IS NOT NULL AND length(sql) > 0 AND length(dist) > 0'''.format(city=city)
        self.cursor.execute(sql)
        self.conn.commit()
        rows = self.cursor.fetchall()
        classes=[]            
        for row in rows:
            classes.append(row)


        for featureclass in classes:
            sql1='''SELECT ST_Buffer(planet_osm_polygon.way::geography,{dist}) AS the_geog, name, '{sql}' AS sql, '{note}' AS note FROM planet_osm_polygon WHERE {where}'''.format(
                where=self.sql_natural_escape(featureclass[0]),dist=featureclass[1],
                sql=featureclass[2],note=featureclass[3]
                )

            sql = 'INSERT INTO areas (the_geog,name, sql, note) ({sql})'.format(sql=sql1)
            
            self.cursor.execute(sql)
            self.conn.commit()
