import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.route('/')
def sitemap():
    return generate_sitemap(app)


# ── PEOPLE ──────────────────────────────────────────

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([p.serialize() for p in people]), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        raise APIException("Person not found", status_code=404)
    return jsonify(person.serialize()), 200


@app.route('/people', methods=['POST'])
def create_person():
    body = request.get_json()
    if body is None:
        raise APIException("Body is empty", status_code=400)

    name = body.get("name")
    if not name:
        raise APIException("Name is required", status_code=400)

    new_person = People(
        name=name,
        birth_year=body.get("birth_year"),
        gender=body.get("gender"),
        height=body.get("height"),
        skin_color=body.get("skin_color"),
        eye_color=body.get("eye_color")
    )
    db.session.add(new_person)
    db.session.commit()
    return jsonify(new_person.serialize()), 201


@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        raise APIException("Person not found", status_code=404)

    body = request.get_json()
    if body is None:
        raise APIException("Body is empty", status_code=400)

    person.name = body.get("name", person.name)
    person.birth_year = body.get("birth_year", person.birth_year)
    person.gender = body.get("gender", person.gender)
    person.height = body.get("height", person.height)
    person.skin_color = body.get("skin_color", person.skin_color)
    person.eye_color = body.get("eye_color", person.eye_color)

    db.session.commit()
    return jsonify(person.serialize()), 200


@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        raise APIException("Person not found", status_code=404)

    db.session.delete(person)
    db.session.commit()
    return jsonify({"msg": "Person deleted"}), 200

# ── PLANETS ─────────────────────────────────────────


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException("Planet not found", status_code=404)
    return jsonify(planet.serialize()), 200


@app.route('/planets', methods=['POST'])
def create_planet():
    body = request.get_json()
    if body is None:
        raise APIException("Body is empty", status_code=400)

    name = body.get("name")
    if not name:
        raise APIException("Name is required", status_code=400)

    new_planet = Planet(
        name=name,
        climate=body.get("climate"),
        population=body.get("population"),
        terrain=body.get("terrain"),
        diameter=body.get("diameter"),
        rotation_period=body.get("rotation_period")
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify(new_planet.serialize()), 201


@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException("Planet not found", status_code=404)

    body = request.get_json()
    if body is None:
        raise APIException("Body is empty", status_code=400)

    planet.name = body.get("name", planet.name)
    planet.climate = body.get("climate", planet.climate)
    planet.population = body.get("population", planet.population)
    planet.terrain = body.get("terrain", planet.terrain)
    planet.diameter = body.get("diameter", planet.diameter)
    planet.rotation_period = body.get(
        "rotation_period", planet.rotation_period)

    db.session.commit()
    return jsonify(planet.serialize()), 200


@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException("Planet not found", status_code=404)

    db.session.delete(planet)
    db.session.commit()
    return jsonify({"msg": "Planet deleted"}), 200


# ── USERS ────────────────────────────────────────────

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200


# ── FAVORITES ────────────────────────────────────────
CURRENT_USER_ID = 1


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user = User.query.get(CURRENT_USER_ID)
    if user is None:
        raise APIException("User not found", status_code=404)
    favorites = Favorite.query.filter_by(user_id=CURRENT_USER_ID).all()
    return jsonify([f.serialize() for f in favorites]), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['GET'])
def get_favorite_planet(planet_id):
    fav = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID, planet_id=planet_id
    ).first()
    if fav is None:
        raise APIException("Favorite planet not found", status_code=404)
    return jsonify(fav.serialize()), 200


@app.route('/favorite/people/<int:people_id>', methods=['GET'])
def get_favorite_people(people_id):
    fav = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID, people_id=people_id
    ).first()
    if fav is None:
        raise APIException("Favorite person not found", status_code=404)
    return jsonify(fav.serialize()), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException("Planet not found", status_code=404)
    existing = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID, planet_id=planet_id).first()
    if existing:
        raise APIException("Planet already in favorites", status_code=400)
    new_fav = Favorite(user_id=CURRENT_USER_ID, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.serialize()), 201


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    person = People.query.get(people_id)
    if person is None:
        raise APIException("Person not found", status_code=404)
    existing = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID, people_id=people_id).first()
    if existing:
        raise APIException("Person already in favorites", status_code=400)
    new_fav = Favorite(user_id=CURRENT_USER_ID, people_id=people_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify(new_fav.serialize()), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    fav = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID, planet_id=planet_id).first()
    if fav is None:
        raise APIException("Favorite not found", status_code=404)
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite planet deleted"}), 200


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    fav = Favorite.query.filter_by(
        user_id=CURRENT_USER_ID, people_id=people_id).first()
    if fav is None:
        raise APIException("Favorite not found", status_code=404)
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite person deleted"}), 200


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
