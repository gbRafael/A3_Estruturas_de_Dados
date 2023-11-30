import networkx as nx
import folium
from geopy.distance import geodesic
from datetime import datetime, timedelta
import locale


class LogisticOptimizer:
    def __init__(self):
        self.graph = nx.Graph()
        self.locations = {}

    def add_city(self, name, address, latitude, longitude):
        self.locations[name] = (latitude, longitude)
        self.graph.add_node(name, address=address, pos=(latitude, longitude))

    def add_connection(self, city1, city2):
        distance = self.calculate_distance(city1, city2)
        self.graph.add_edge(city1, city2, distance=distance)
        self.graph.add_edge(city2, city1, distance=distance)

    def calculate_distance(self, city1, city2):
        pos1 = self.locations[city1]
        pos2 = self.locations[city2]
        return geodesic(pos1, pos2).km

    def find_optimal_route(self, start_city, end_city):
        path = nx.shortest_path(self.graph, start_city,
                                end_city, weight='distance')
        distance = nx.shortest_path_length(
            self.graph, start_city, end_city, weight='distance')
        cost = distance * 20  # Custo por quilômetro rodado

        # Estimativa de tempo considerando 500 km por dia
        days_required = distance / 500
        current_time = datetime.now()
        arrival_time = current_time + timedelta(days=days_required)

        return path, distance, cost, arrival_time

    def display_map(self, path):
        map_center = self.locations[path[0]]
        m = folium.Map(location=map_center, zoom_start=6)

        for city in path:
            folium.Marker(location=self.locations[city], popup=city).add_to(m)

        folium.PolyLine(locations=[self.locations[city]
                        for city in path], color='blue').add_to(m)

        return m


if __name__ == "__main__":
    logistics = LogisticOptimizer()

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    # Cadastro das cidades
    logistics.add_city("Curitiba", "Curitiba/PR", -25.4284, -49.2733)
    logistics.add_city("Londrina", "Londrina/PR", -23.3105, -51.1628)
    logistics.add_city("Foz do Iguaçu", "Foz do Iguaçu/PR", -25.5478, -54.5882)
    logistics.add_city("União da Vitória",
                       "União da Vitória/PR", -26.2273, -51.0870)
    logistics.add_city("Joinville", "Joinville/SC", -26.3032, -48.8415)
    logistics.add_city("Chapecó", "Chapecó/SC", -27.1009, -52.6157)
    logistics.add_city("Porto Alegre", "Porto Alegre/RS", -30.0346, -51.2177)
    logistics.add_city("Uruguaiana", "Uruguaiana/RS", -29.7617, -57.0856)
    logistics.add_city("Pelotas", "Pelotas/RS", -31.7613, -52.3376)

    # Adiciona conexões(foi necessário adicionar mais conexões para o codigo solucionar o desafio)
    logistics.add_connection("Curitiba", "Porto Alegre")
    logistics.add_connection("Porto Alegre", "Pelotas")
    logistics.add_connection("Foz do Iguaçu", "União da Vitória")
    logistics.add_connection("Joinville", "Chapecó")

    # Solicitação de rota
    start_city = "Curitiba"
    end_city = "Pelotas"

    try:
        result = logistics.find_optimal_route(start_city, end_city)

        # Exibe resultados
        path, distance, cost, arrival_time = result
        print(f"Menor caminho de {start_city} para {end_city}: {path}")
        print(f"Distancia: {distance:.2f} km")
        print(f"Custo estimado: {locale.format_string('%.2f', cost, grouping=True)}")
        print(f"Estimativa de tempo: {arrival_time.strftime('%H:%M')} Hrs")

        # Exibe mapa
        map_path = logistics.display_map(path)
        map_path.save("logistics_map.html")

    except nx.NetworkXNoPath:
        print(f"Não há caminho de {start_city} para {end_city} no grafo.")
    except Exception as e:
        print(f"Erro não esperado: {e}")
