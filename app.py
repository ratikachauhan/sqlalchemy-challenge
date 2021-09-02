import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#last date
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

#last 12 months
query_date = dt.date(2017,8,23) - dt.timedelta(days=365)

session.close()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawaii Climate<br/> "
        f"<br/>"  
        f"<br/>"  
        f"Available Routes:<br/>"
        f"<br/>"  
        f"Precipitation Details:<br/>"
        f"/api/v1.0/precipitation<br/>"   
        f"<br/>"      
        f"List of stations:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"  
        f"Temperature observations (TOBS) for the previous year:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"  
        f"Temperature summary from the start date(yyyy-mm-dd): <br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"<br/>"  
        f"Temperature summary from start to end dates(yyyy-mm-dd):<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )

#Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    precipitation = []
    for date, prcp in results:
        prcp_df = {}
        prcp_df["Date"] = date
        prcp_df["Precipitation"] = prcp
        precipitation.append(prcp_df)

    return jsonify(precipitation)


#Stations Route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()
    stations = []   
    for station,name,lat,lon,el in results:
        station_df = {}
        station_df["Station"] = station
        station_df["Name"] = name
        station_df["Lat"] = lat
        station_df["Lon"] = lon
        station_df["Elevation"] = el
        stations.append(station_df)

    return jsonify(stations)
#tobs
@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(latest, '%Y-%m-%d')
    last_twelve_months = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    sel = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*sel).filter(Measurement.date >= last_twelve_months).all()
    session.close()

    tobs_list = []
    for date, tobs in queryresult:
        tob_df = {}
        tob_df["Date"] = date
        tob_df["Tobs"] = tobs
        tobs_list.append(tob_df)

    return jsonify(tobs_list)

#Start Date - Temperature stat from the start date(yyyy-mm-dd)
@app.route('/api/v1.0/<start>')
def getstartdate(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    temp_start = []
    for min,avg,max in results:
        temp = {}
        temp["Min"] = min
        temp["Average"] = avg
        temp["Max"] = max
        temp_start.append(temp)

    return jsonify(temp_start)

#Start to End Date `/api/v1.0/<start>/<end>`
@app.route('/api/v1.0/<start>/<end>')
def get_t_start_stop(start,end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temp_start_end = []
    for min,avg,max in results:
        temp = {}
        temp["Min"] = min
        temp["Average"] = avg
        temp["Max"] = max
        temp_start_end.append(temp)

    return jsonify(temp_start_end)



#run the app
if __name__ == "__main__":
    app.run(debug=True)