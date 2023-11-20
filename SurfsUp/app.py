# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text
import datetime as dt
from dateutil.relativedelta import relativedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the homepage!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0//api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)

    most_recent = session.query(measurement.date).order_by(text("date DESC")).first()

    # Calculate the date one year from the last date in data set.
    latest_date = pd.to_datetime(most_recent[0]).date()
    one_year_ago = latest_date - relativedelta(years=1)
    one_year_ago = str(one_year_ago)
    one_year_ago 

    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).order_by(measurement.date).all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    session.close()
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    station_list = [result[0] for result in results]
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent = session.query(measurement.date).order_by(text("date DESC")).first()

    # Calculate the date one year from the last date in data set.
    latest_date = pd.to_datetime(most_recent[0]).date()
    one_year_ago = latest_date - relativedelta(years=1)
    one_year_ago = str(one_year_ago)
    one_year_ago    

    most_active_station = "USC00519281"
    results = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station).\
              filter(measurement.date >= one_year_ago).order_by(measurement.date).all()

    # Convert the query results to a list of dictionaries
    tobs_data = [{"date": date, "observations": tobs} for date, tobs in results]

    session.close()
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
# use 'YYYY-MM-DD' for start
def start(start):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
              filter(measurement.date >= start).all()

    # Convert the query results to a dictionary
    temperature_stats = {
        "Minimun Temp": results[0][0],
        "Average Temp": results[0][1],
        "Maximum Temp": results[0][2]
    }    
    session.close()
    return jsonify(temperature_stats)

@app.route("/api/v1.0/<start>/<end>")
# use 'YYYY-MM-DD/YYYY-MM-DD' for start/end
def start_end(start, end):
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
              filter(measurement.date >= start).\
              filter(measurement.date <= end).all()

    # Convert the query results to a dictionary
    temperature_stats = {
        "Minimun Temp": results[0][0],
        "Average Temp": results[0][1],
        "Maximum Temp": results[0][2]
    }

    session.close()
    return jsonify(temperature_stats)

if __name__ == "__main__":
    app.run(debug=True)