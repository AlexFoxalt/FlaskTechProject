from datetime import datetime

from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

from constants import COORDINATES
from services import get_params_from_data, get_forecast_by_cords_in_json_format, sum_values_in_array_by_value_name, \
    get_dict_of_lists_of_moving_means

app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


class City(db.Model):
    __tablename__ = 'city'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    forecasts = db.relationship("Forecast", backref="city", lazy='dynamic')

    def __repr__(self):
        return self.name


class Forecast(db.Model):
    __tablename__ = 'forecast'
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    date = db.Column(db.DateTime)
    temp = db.Column(db.SmallInteger)
    pcp = db.Column(db.Float)
    clouds = db.Column(db.Float)
    pressure = db.Column(db.SmallInteger)
    humidity = db.Column(db.SmallInteger)
    wind_speed = db.Column(db.Float)

    def get_all_values_in_dict_format(self):
        return dict({
            "date": self.date,
            "temp": self.temp,
            "pcp": self.pcp,
            "clouds": self.clouds,
            "pressure": self.pressure,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
        })


def get_data_from_response_write_it_to_db_and_return_status(response, city):
    try:
        for data in response.get("daily"):
            params = get_params_from_data(data)
            item = Forecast(city=city, **params)
            db.session.add(item)
        db.session.commit()
    except Exception as e:
        print(f'[ERROR] : {e}')
        return False
    return True


def create_city_and_return_instance(city_name):
    city = City(name=city_name)
    db.session.add(city)
    db.session.commit()
    return city


def get_array_of_forecasts_by_city_name(city_name):
    return City.query.filter_by(name=city_name).first().forecasts.all()


def get_forecasts_for_city_between_dates(city, start_dt, end_dt):
    return Forecast.query.filter(Forecast.city == city,
                                 Forecast.date >= start_dt,
                                 Forecast.date <= end_dt).all()


def fill_db():
    if any((Forecast.query.all(), City.query.all())):
        print('* DB is already filled')
        return
    statuses = {}
    for city_name, cords in COORDINATES.items():
        response = get_forecast_by_cords_in_json_format(cords)
        if not response:
            continue

        city = create_city_and_return_instance(city_name)
        status = get_data_from_response_write_it_to_db_and_return_status(response, city)
        statuses.update({city_name: status})
    print(statuses)


class GetListOfCities(Resource):
    def get(self):
        response = {'List of cities': [str(city) for city in City.query.all()]}
        return jsonify(response)


class GetMeanOfValue(Resource):
    def get(self):
        value_type = request.args.get("value_type")
        city_name = request.args.get("city")
        if not all((value_type, city_name)):
            return jsonify({'Success': False,
                            'Message': f'Required params are not found!',
                            'Message_Help': 'Required params are: city, value_type'})
        try:
            array_of_forecasts = get_array_of_forecasts_by_city_name(city_name)
            result = sum_values_in_array_by_value_name(array_of_forecasts, value_type)
        except AttributeError:
            return jsonify({'Success': False,
                            'Message': f'Params are invalid!'})
        return jsonify({'Success': True,
                        'Result': result})


class GetRecordsOfCity(Resource):
    def get(self):
        city_name = request.args.get("city")
        raw_start_dt = request.args.get("start_dt")
        raw_end_dt = request.args.get("end_dt")

        if not all((city_name, raw_start_dt, raw_end_dt)):
            return jsonify({'Success': False,
                            'Message': f'Required params are not found!',
                            'Message_Help': 'Required params are: city_name, start_dt, end_dt'})

        try:
            start_dt = datetime.strptime(raw_start_dt, "%Y-%m-%d")
            end_dt = datetime.strptime(raw_end_dt, "%Y-%m-%d")
        except ValueError:
            return jsonify({'Success': False,
                            'Message': f'Datetime params are invalid!',
                            'Help': 'Format is: YEAR-MO-DY'})

        try:
            city = City.query.filter_by(name=city_name).first()
            forecasts = get_forecasts_for_city_between_dates(city, start_dt, end_dt)
        except AttributeError:
            return jsonify({'Success': False,
                            'Message': f'Params are invalid!'})

        result = {num: value.get_all_values_in_dict_format() for num, value in enumerate(forecasts, 1)}
        return jsonify({'Success': True,
                        'Result': result})


class GetMovingMeanOfValue(Resource):
    def get(self):
        value_type = request.args.get("value_type")
        city_name = request.args.get("city")
        if not all((value_type, city_name)):
            return jsonify({'Success': False,
                            'Message': f'Required params are not found!',
                            'Message_Help': 'Required params are: city, value_type'})
        try:
            array_of_forecasts = get_array_of_forecasts_by_city_name(city_name)
        except AttributeError:
            return jsonify({'Success': False,
                            'Message': f'Params are invalid!'})
        result = get_dict_of_lists_of_moving_means(array_of_forecasts, value_type)
        return jsonify({'Success': True,
                        'Result': result})


api.add_resource(GetListOfCities, '/cities')
api.add_resource(GetMeanOfValue, '/mean')
api.add_resource(GetRecordsOfCity, '/records')
api.add_resource(GetMovingMeanOfValue, '/moving_mean')

if __name__ == '__main__':
    fill_db()
    app.run(debug=True)
