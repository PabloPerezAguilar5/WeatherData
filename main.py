import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests
from collections import deque
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializa la aplicación Dash
app = dash.Dash(__name__)

# Inicializa listas para almacenar los datos del clima en tiempo real
max_len = 20
times = deque(maxlen=max_len)
temps = deque(maxlen=max_len)
humidities = deque(maxlen=max_len)
pressures = deque(maxlen=max_len)

# Layout de la aplicación
app.layout = html.Div([
    html.H1('Weather Dashboard', style={'textAlign': 'center'}),
    
    html.Div([
        html.Label('Enter a City:'),
        dcc.Input(id='city-input', value='Buenos Aires', type='text'),
        html.Button(id='submit-button', n_clicks=0, children='Submit')
    ], style={'textAlign': 'center', 'padding': 10}),
    
    html.H2(id='live-temperature', style={'textAlign': 'center', 'fontSize': 40}),
    
    dcc.Graph(id='live-weather-graph'),
    
    dcc.Interval(
        id='interval-component',
        interval=10*60*1000,  # Actualiza cada 10 minutos
        n_intervals=0
    )
])

def get_weather_data(city):
    api_key = os.getenv('OPENWEATHER_API_KEY')
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

@app.callback(
    [Output('live-weather-graph', 'figure'),
     Output('live-temperature', 'children')],
    [Input('submit-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State('city-input', 'value')]
)
def update_weather(n_clicks, n, city):
    data = get_weather_data(city)
    
    if data and data.get('main'):
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        
        # Agrega los datos actuales a las listas
        current_time = datetime.now().strftime('%H:%M:%S')
        times.append(current_time)
        temps.append(temp)
        humidities.append(humidity)
        pressures.append(pressure)
        
        figure = {
            'data': [
                go.Scatter(x=list(times), y=list(temps), mode='lines+markers', name='Temperature (°C)', line=dict(color='firebrick')),
                go.Scatter(x=list(times), y=list(humidities), mode='lines+markers', name='Humidity (%)', line=dict(color='blue')),
                go.Scatter(x=list(times), y=list(pressures), mode='lines+markers', name='Pressure (hPa)', line=dict(color='green')),
            ],
            'layout': go.Layout(
                title=f'Weather Data for {city}',
                xaxis=dict(title='Time (HH:MM:SS)'),
                yaxis=dict(title='Values'),
                showlegend=True
            )
        }

        current_temp_text = f"Current Temperature in {city}: {temp:.1f}°C"
    else:
        figure = {}
        current_temp_text = f"City '{city}' not found or error fetching data. Please try again."
    
    return figure, current_temp_text

# Ejecuta la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)