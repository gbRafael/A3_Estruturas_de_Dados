import networkx as nx
import folium
from geopy.distance import geodesic
from datetime import datetime, timedelta
import locale
import csv

class LogisticOptimizer:
    def __init__(self):
        self.graph = nx.Graph()
        self.locations = {}

    def add_cidade(self, nome, endereco, latitude, longitude):
        self.locations[nome] = (latitude, longitude)
        self.graph.add_node(nome, endereco=endereco, posicao=(latitude, longitude))

    def add_conecxoes(self, cidade1, cidade2):
        distancia = self.calcular_distancia(cidade1, cidade2)
        self.graph.add_edge(cidade1, cidade2, distancia=distancia)
        self.graph.add_edge(cidade2, cidade1, distancia=distancia)

    def calcular_distancia(self, cidade1, cidade2):
        posicao1 = self.locations[cidade1]
        posicao2 = self.locations[cidade2]
        return geodesic(posicao1, posicao2).km

    def rota_aprimorada(self, cidade_inicial, cidade_final):
        path = nx.shortest_path(self.graph, cidade_inicial,
                                cidade_final, weight='distancia')
        distancia = nx.shortest_path_length(
            self.graph, cidade_inicial, cidade_final, weight='distancia')
        custo = distancia * 20  # Custo por quilômetro rodado

        # Estimativa de tempo considerando 500 km por dia
        dias = distancia / 500
        hora = datetime.now()
        tempo_chegada = hora + timedelta(days=dias)

        return path, distancia, custo, tempo_chegada

    def display_mapa(self, path):
        mapa = self.locations[path[0]]
        m = folium.Map(location=mapa, zoom_start=6)

        for cidade in path:
            folium.Marker(location=self.locations[cidade], popup=cidade).add_to(m)

        folium.PolyLine(locations=[self.locations[cidade]
                        for cidade in path], color='blue').add_to(m)

        return m
    
    def exportar_csv(self, path, distancia, custo, tempo_chegada):
        with open('logistics_result.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['cidade'])

            for cidade in path:
                csv_writer.writerow([cidade])

            csv_writer.writerow([])  # Adicionar linha vazia
            csv_writer.writerow(['Distância Total (km)', 'Custo', 'Tempo de Chegada'])
            csv_writer.writerow([round(distancia, 2), round(custo, 2), tempo_chegada.strftime('%H:%M')])


if __name__ == "__main__":
    logistics = LogisticOptimizer()

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    # Cadastro das cidades
    logistics.add_cidade("Curitiba", "Curitiba/PR", -25.4284, -49.2733)
    logistics.add_cidade("Londrina", "Londrina/PR", -23.3105, -51.1628)
    logistics.add_cidade("Foz do Iguaçu", "Foz do Iguaçu/PR", -25.5478, -54.5882)
    logistics.add_cidade("União da Vitória",
                       "União da Vitória/PR", -26.2273, -51.0870)
    logistics.add_cidade("Joinville", "Joinville/SC", -26.3032, -48.8415)
    logistics.add_cidade("Chapecó", "Chapecó/SC", -27.1009, -52.6157)
    logistics.add_cidade("Porto Alegre", "Porto Alegre/RS", -30.0346, -51.2177)
    logistics.add_cidade("Uruguaiana", "Uruguaiana/RS", -29.7617, -57.0856)
    logistics.add_cidade("Pelotas", "Pelotas/RS", -31.7613, -52.3376)

    # Adiciona conexões(foi necessário adicionar mais conexões para o codigo solucionar o desafio)
    logistics.add_conecxoes("Curitiba", "Porto Alegre")
    logistics.add_conecxoes("Porto Alegre", "Pelotas")
    logistics.add_conecxoes("Foz do Iguaçu", "União da Vitória")
    logistics.add_conecxoes("Joinville", "Chapecó")

    # Solicitação de rota
    cidade_inicial = "Curitiba"
    cidade_final = "Pelotas"

    try:
        result = logistics.rota_aprimorada(cidade_inicial, cidade_final)

        # Exibe resultados
        path, distancia, custo, tempo_chegada = result
        print(f"Menor caminho de {cidade_inicial} para {cidade_final}: {path}")
        print(f"Distancia: {distancia:.2f} km")
        print(f"Custo estimado: {locale.format_string('%.2f', custo, grouping=True)}")
        print(f"Estimativa de tempo: {tempo_chegada.strftime('%H:%M')} Hrs")

        # Exibe mapa
        map_path = logistics.display_mapa(path)
        map_path.save("logistics_map.html")

        # Importa .CSV
        logistics.exportar_csv(path, distancia, custo, tempo_chegada)

    except nx.NetworkXNoPath:
        print(f"Não há caminho de {cidade_inicial} para {cidade_final} no grafo.")
    except Exception as e:
        print(f"Erro não esperado: {e}")
