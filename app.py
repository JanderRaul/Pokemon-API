from flask import Flask, render_template, url_for
import requests
from sqlalchemy import false
import json

app = Flask(__name__)

favoritos = [1, 3, 5, 7]
time = [8, 14, 150]

@app.route('/')
def home():
    pokemons = []
    for i in range(1, 21):
        url = f'https://pokeapi.co/api/v2/pokemon/{i}/'
        pokemon = requests.get(url).json()
        pokemons.append(pokemon)        
        
    return render_template('index.html', pokemons=pokemons)

@app.route('/favorito')
def favorito():
    global favoritos
    pokemons = []
    for i in favoritos:
        url = f'https://pokeapi.co/api/v2/pokemon/{i}/'
        pokemon = requests.get(url).json()
        pokemons.append(pokemon)        
        
    return render_template('favoritos.html', pokemons=pokemons)

@app.route('/times')
def times():
    global time
    pokemons = []
    for i in time:
        url = f'https://pokeapi.co/api/v2/pokemon/{i}/'
        pokemon = requests.get(url).json()
        pokemons.append(pokemon)        
        
    return render_template('time.html', pokemons=pokemons)

# @app.route('/filtro/<typeA>')
# def filtro(typeA):
#     url = f'https://pokeapi.co/api/v2/type/{typeA}/'
#     resposta = requests.get(url).json()
#     pokemons = resposta['pokemon']
#     # urls = []
#     # for pokemon in pokemons:
#     #     urls.append(pokemon['url'])
#     # pokemons = []
#     # for url in urls:
#     #     resposta = requests.get(url).json()
#     #     pokemons.append(resposta)
            
#     return render_template('teste.html', pokemons=pokemons)
    

@app.route('/detalhes/<id>')
def detalhes(id):
    url = f'https://pokeapi.co/api/v2/pokemon/{id}/'
    pokemon = requests.get(url).json()
    return render_template('detalhes.html', pokemon=pokemon)

@app.route('/APIFavoritos')
def APIFavoritos():
    global favoritos
    pokemons = []
    for i in favoritos:
        url = f'https://pokeapi.co/api/v2/pokemon/{i}/'
        pokemon = requests.get(url).json()
        pokemons.append(pokemon)
    
    APIs = json.dumps(pokemons)       
        
    return render_template('APIFavoritos.html', pokemons=APIs)

if __name__ == '__main__':
    app.run(debug=True)