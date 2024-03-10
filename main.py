from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.numeric import FloatField
from wtforms.validators import DataRequired
import requests
from dotenv import load_dotenv
import os

# .env file contains api keys in the format of API_KEY="xxxxxx", get it using os.environ['API_KEY']; before that pip install python-dotenv
load_dotenv()  # take environment variables from .env.

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Yuvalco11'
bootstrap = Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)


# Optional: this will allow each book object to be identified by its title when printed.
def __repr__(self):
    return f'<Movie {self.title}>'


with app.app_context():
    db.create_all()
    print('test')


class UpdateForm(FlaskForm):
    new_rating = StringField("Your Rating Out of 10 e.g. 7.5")
    new_review = StringField('New Review')
    submit = SubmitField('Done')


@app.route("/edit/<int:id>/", methods=['GET', 'POST'])
def update(id):
    movie_to_update = db.get_or_404(Movie, id)
    form = UpdateForm()
    if form.validate_on_submit():
        movie_to_update.rating = float(form.new_rating.data)
        movie_to_update.review = form.new_review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie_to_update, form=form)


class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        new_movie = form.title.data
        print(new_movie)
        TMDB_READ_TOKEN = os.environ['TMDB_READ_TOKEN']
        TMDB_AUTH = "Bearer " + TMDB_READ_TOKEN
        TMDB_URL = "https://api.themoviedb.org/3/search/movie?"
        TMDB_HEADERS = {"accept": "application/json", "Authorization": TMDB_AUTH}
        tmdb_parameters = {"query": new_movie, "language": "en-US"}
        response = requests.get(url=TMDB_URL, params=tmdb_parameters, headers=TMDB_HEADERS)
        results = response.json()["results"]
        print(results)
        return render_template('select.html', results=results)

    return render_template('add.html', form=form)


@app.route("/addid/<int:id>/", methods=['GET', 'POST'])
def addid(id):
    TMDB_READ_TOKEN = os.environ['TMDB_READ_TOKEN']
    TMDB_AUTH = "Bearer " + TMDB_READ_TOKEN
    TMDB_URL = "https://api.themoviedb.org/3/movie/" + str(id)
    TMDB_HEADERS = {"accept": "application/json", "Authorization": TMDB_AUTH}
    tmdb_parameters = {"language": "en-US"}
    response = requests.get(url=TMDB_URL, params=tmdb_parameters, headers=TMDB_HEADERS)
    result = response.json()
    base_img_url = "https://image.tmdb.org/t/p/w500"
    title = result["title"]
    year = result["release_date"].split("-")[0]
    description = result["overview"]
    rating = result["vote_average"]
    ranking = round(result["popularity"])
    review = ""
    img_url = base_img_url + result["poster_path"]
    new_movie = Movie(title=title, year=year, description=description, rating=rating, ranking=ranking, review=review, img_url=img_url)
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete")
def delete():
    movie_id = request.args.get('id')
    # DELETE A RECORD BY ID
    movie_to_delete = db.get_or_404(Movie, movie_id)
    # Alternative way to select the book to delete.
    # book_to_delete = db.session.execute(db.select(Book).where(Book.id == book_id)).scalar()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/")
def home():
    result = db.session.execute(db.select(Movie).order_by(Movie.id))
    all_movies = result.scalars()
    return render_template("index.html", movies=all_movies)


if __name__ == '__main__':
    app.run(debug=True)
