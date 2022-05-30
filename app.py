import json
import random
import requests
from flask import Flask, render_template, session, url_for, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'ot61vy32PjF%Rw6@$XdX'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)

class Favoritos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    id_pokemon = db.Column(db.Integer)

class Time(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer)
    id_pokemon = db.Column(db.Integer)

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Escreva seu nome"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Digite sua senha"})
    submit = SubmitField("Registrar")
    def validate_username(self, username):
        existing_user_name = User.query.filter_by(username=username.data).first()
        if existing_user_name:
            raise ValidationError("Este nome já está sendo utilizado. Escolha outro nome!!")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Escolha seu nick.."})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Crie sua senha.."})
    submit = SubmitField("Login")

listaImagens = [
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/4.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/7.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/15.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/39.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/54.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/61.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/74.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/80.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/94.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/104.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/105.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/122.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/130.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/143.png',
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/150.png',
]

@app.route('/')
def home():
    op = random.randint(0,16)
    imagem = listaImagens[op]
    
    return render_template('home.html', imagem=imagem, audio='audio.mp3')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('pokedex', pg=1))

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

def paginacao(pg):
    if pg == 1:
        inicio = 1
        fim = 25
    elif pg == 2:
        inicio = 25
        fim = 50
    elif pg == 3:
        inicio = 50
        fim = 75
    elif pg == 4:
        inicio = 75
        fim = 100
    elif pg == 5:
        inicio = 100
        fim = 125
    else:
        inicio = 125
        fim = 152
    return inicio, fim

@app.route('/pokedex/<int:pg>')
@login_required
def pokedex(pg):
    inicio, fim = paginacao(pg)
    user = User.query.get(current_user.id)
    pokemons = []
    for i in range(inicio, fim):
        url = f'https://pokeapi.co/api/v2/pokemon/{i}/'
        pokemon = requests.get(url).json()
        pokemons.append(pokemon)        

    return render_template('pokedex.html', nome=str(user.username), pokemons=pokemons)

@app.route('/detalhes/<id>', methods=['GET', 'POST'])
@login_required
def detalhes(id):
    user = User.query.get(current_user.id)
    url = f'https://pokeapi.co/api/v2/pokemon/{id}/'
    pokemon = requests.get(url).json()

    return render_template('detalhes.html', nome=str(user.username), pokemon=pokemon)

@app.route('/favoritar/<id>')
@login_required
def favoritar(id):
    existing_id = Favoritos.query.filter(Favoritos.id_usuario == current_user.id, Favoritos.id_pokemon == id).all()
    if existing_id:
        msg = 'Este pokemon já está na sua lista de favoritos'
    else:
        new_favorito = Favoritos(id_usuario=current_user.id, id_pokemon=id)
        db.session.add(new_favorito)
        db.session.commit()
        msg = 'Pokemon adicionado a sua lista de favoritos'

    url = f'https://pokeapi.co/api/v2/pokemon/{id}/'
    pokemon = requests.get(url).json()
    
    return render_template('msg.html', msg=msg, pokemon=pokemon)
    

@app.route('/time/<id>')
@login_required
def time(id):

    time = Time.query.filter(Time.id_usuario == current_user.id).all()
    if len(time) < 6:
        existing_id = Time.query.filter(Time.id_usuario == current_user.id, Time.id_pokemon == id).all()
        if existing_id:
            msg = 'Este pokemon já está no seu time'
        else:
            new_favorito = Time(id_usuario=current_user.id, id_pokemon=id)
            db.session.add(new_favorito)
            db.session.commit()
            msg = 'Pokemon adicionado ao seu time!!'
    else:
        msg = 'Seu time já tem 6 pokemons'

    url = f'https://pokeapi.co/api/v2/pokemon/{id}/'
    pokemon = requests.get(url).json()

    return render_template('msg.html', msg=msg, pokemon=pokemon)

@app.route('/MeusFavoritos')
@login_required
def MeusFavoritos():
    pokemons = []
    favoritos = Favoritos.query.filter(Favoritos.id_usuario == current_user.id).all()
    if favoritos:
        msg = ''
        for id in favoritos:
            url = f'https://pokeapi.co/api/v2/pokemon/{id.id_pokemon}/'
            pokemon = requests.get(url).json()
            pokemons.append(pokemon)
    else:
        msg = 'Sua lista de favoritos está vazia :('
        
    return render_template('MeusFavoritos.html', msg=msg, pokemons=pokemons)

@app.route('/MeuTime')
@login_required
def MeuTime():
    pokemons = []
    vazios = []
    time = Time.query.filter(Time.id_usuario == current_user.id).all()
    if time:
        msg = ''
        for id in time:
            url = f'https://pokeapi.co/api/v2/pokemon/{id.id_pokemon}/'
            pokemon = requests.get(url).json()
            pokemons.append(pokemon)
    else:
        msg = ''
    if len(time) < 7:
        diferenca = 6 - len(time)
        for i in range(1, diferenca+1):
            vazios.append('https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png')

    return render_template('MeuTime.html', msg=msg, pokemons=pokemons, vazios=vazios)

@app.route('/desfavoritar/<id>')
@login_required
def desfavoritar(id):
    
    url = f'https://pokeapi.co/api/v2/pokemon/{id}/'
    pokemon = requests.get(url).json()

    Favoritos.query.filter(Favoritos.id_usuario == current_user.id, Favoritos.id_pokemon == id).delete()
    db.session.commit()
    msg ='Pokemon retirado da sua lista de favoritos'

    return render_template('msg.html', msg=msg, pokemon=pokemon)

@app.route('/tirartime/<id>')
@login_required
def tirartime(id):
    
    url = f'https://pokeapi.co/api/v2/pokemon/{id}/'
    pokemon = requests.get(url).json()

    Time.query.filter(Time.id_usuario == current_user.id, Time.id_pokemon == id).delete()
    db.session.commit()
    msg ='Pokemon foi retirado do seu time'

    return render_template('msg.html', msg=msg, pokemon=pokemon)

@app.route('/sobre')
def sobre():
    imagem_jander = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png'
    imagem_marcelo = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/6.png'
    
    return render_template('sobre.html', imagem_jander=imagem_jander, imagem_marcelo=imagem_marcelo)

@app.route('/MinhaAPI')
def MinhaAPI():
    user = User.query.get(current_user.id)
    time = Time.query.filter(Time.id_usuario == current_user.id).all()
    favoritos = Favoritos.query.filter(Favoritos.id_usuario == current_user.id).all()

    vetorTime = []
    for inf in time:
        vetorTime.append(f'id_pokemon : {inf.id_pokemon}')
    
    vetorFavoritos = []
    for inf in favoritos:
        vetorFavoritos.append(f'id_pokemon : {inf.id_pokemon}')

    dados = {
        'id' : f'{user.id}',
        'nome' : f'{user.username}',
        'time' : vetorTime,
        'favoritos' : vetorFavoritos,
    }

    return jsonify(dados)

@app.route('/importar')
@login_required
def importar():
    user = User.query.get(current_user.id)
    time = Time.query.filter(Time.id_usuario == current_user.id).all()
    favoritos = Favoritos.query.filter(Favoritos.id_usuario == current_user.id).all()

    vetorTime = []
    for inf in time:
        vetorTime.append(f'id_pokemon : {inf.id_pokemon}')
    
    vetorFavoritos = []
    for inf in favoritos:
        vetorFavoritos.append(f'id_pokemon : {inf.id_pokemon}')

    dados = {
        'id' : f'{user.id}',
        'nome' : f'{user.username}',
        'time' : vetorTime,
        'favoritos' : vetorFavoritos,
    }

    json_object = json.dumps(dados, indent=4)
    with open("arquivoJson.json", "w") as outfile: 
        outfile.write(json_object)

    imagem = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/132.png'

    return render_template('importar.html', arquivo='arquivoJson.json', imagem=imagem)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)