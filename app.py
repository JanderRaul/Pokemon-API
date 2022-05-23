from flask import Flask, render_template, url_for
import requests

app = Flask(__name__)

@app.route('/')
def home():
    pokemons = []
    for i in range(1, 21):
        url = f'https://pokeapi.co/api/v2/pokemon/{i}/'
        pokemon = requests.get(url).json()
        pokemons.append(pokemon)
    return render_template('index.html', pokemons=pokemons)

@app.route('/detalhes/<id>')
def detalhes(id):
    url = f'https://pokeapi.co/api/v2/pokemon/{id}/'
    pokemon = requests.get(url).json()
    return render_template('detalhes.html', pokemon=pokemon)

if __name__ == '__main__':
    app.run(debug=True)