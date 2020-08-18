import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of all_passengerst
    all_dates = []
    for date, prcp in prcp_data:
        date_dict = {}
        date_dict["date"] = date
        date_dict["prcp"] = prcp
        all_dates.append(date_dict)

    return jsonify(all_dates)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB'''
    session = Session(engine)

    results = session.query(Measurement.station).distinct().all()

    station = list(np.ravel(results))
    return jsonify(station)


# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # What are the most active stations? (i.e. what stations have the most rows)?
    # List the stations and the counts in descending order.'''
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    most_active = active_stations[0][0]

    results = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date.desc()).all()

    session.close()

    tobs = list(np.ravel(results))
    return jsonify(tobs)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature
# for a given start date
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
@app.route("/api/v1.0/<start>")
def tobStartDate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    return jsonify(results)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature
# for a given start-end range.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start
# and end date inclusive.
@app.route("/ api/v1.0/<start>/<end>")
def tobsRangeDate(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
