from Classes.classes import *
from math import radians, acos, sin, cos, degrees


def calcular_angulo_eixo_latitude(coord1, coord2):
    lat1, long1 = coord1
    lat2, long2 = coord2

    y = sin(long2 - long1) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(long2 - long1)
    angulo = atan2(y, x)

    return degrees(angulo)


def calcula_angulo_entre_tres_pontos(c1, c2, c3):
    # Converter coordenadas para radianos
    c1_lat_rad = radians(c1[0])
    c1_lon_rad = radians(c1[1])
    c2_lat_rad = radians(c2[0])
    c2_lon_rad = radians(c2[1])
    c3_lat_rad = radians(c3[0])
    c3_lon_rad = radians(c3[1])

    # Calcular ângulos entre as coordenadas
    a = acos(
        sin(c2_lat_rad) * sin(c3_lat_rad) + cos(c2_lat_rad) * cos(
            c3_lat_rad) * cos(
            c3_lon_rad - c2_lon_rad))
    b = acos(
        sin(c1_lat_rad) * sin(c2_lat_rad) + cos(c1_lat_rad) * cos(
            c2_lat_rad) * cos(
            c2_lon_rad - c1_lon_rad))
    c = acos(
        sin(c3_lat_rad) * sin(c1_lat_rad) + cos(c3_lat_rad) * cos(
            c1_lat_rad) * cos(
            c1_lon_rad - c3_lon_rad))
    # Calcular ângulo final
    try:
        angulo = degrees(
            acos((cos(a) - cos(b) * cos(c)) / (sin(b) * sin(c))))
    except ValueError:
        angulo = 180
    return angulo


class Poste(Ponto):
    def __init__(self):
        super().__init__()
        self._bap = False
        self._tracoes = []
        self._id = -1

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, valor):
        self._id = valor

    @property
    def bap(self):
        return self._bap

    @bap.setter
    def bap(self, valor):
        self._bap = valor

    @property
    def tracoes(self):
        return self._tracoes

    @tracoes.setter
    def tracoes(self, valor):
        self._tracoes = valor

    def add_tracao(self, string):
        self._tracoes.append(string)
        self.add_bap()

    def add_bap(self):
        self.bap = True


class Cto(Ponto):
    def __init__(self):
        super().__init__()


class Cabo(Caminho):
    def ancoragens(self, caixas, ang_aceitavel):
        ferragens = []
        for n, coordenada in enumerate(self.coordenadas):
            if coordenada != self.coordenadas[0] and coordenada != self.coordenadas[-1]:

                c2 = self.coordenadas[n - 1]
                c1 = self.coordenadas[n]
                c3 = self.coordenadas[n + 1]
                angulo = calcula_angulo_entre_tres_pontos(c1, c2, c3)

                nome = "passagem"
                if abs(angulo - 180) > ang_aceitavel:
                    nome = "ancoragem"
                ferragens.append(Ponto(nome=nome, coordenada=coordenada))
            else:
                ferragens.append(Ponto(nome="ancoragem", coordenada=coordenada))

        for n2, ferragem in enumerate(ferragens):
            for cto in caixas:
                if (ferragem - cto) <= DISTANCIA_ENTRE_POSTE_E_CABO:
                    ferragem.nome = "ancoragem"

        for n2, ferragem in enumerate(ferragens):
            if ferragem.nome == "passagem" and ferragens[n2 - 1] == "passagem":
                ferragem.nome = "ancoragem"

        ancoragens, passagens = 0, 0
        for ferragem in ferragens:
            if ferragem.nome == "passagem":
                passagens += 1
            elif ferragem.nome == "ancoragem":
                ancoragens += 1

        return ancoragens, passagens

    def osnap(self, postes):
        for n, coord in enumerate(self.coordenadas):
            mais_proximo = postes[0]
            dist_mais_proxima = distance(postes[0].coordenada, coord)
            for poste_ in postes:
                distancia = distance(poste_.coordenada, coord)
                if distancia < dist_mais_proxima:
                    dist_mais_proxima = distancia
                    mais_proximo = poste_
            self.coordenadas[n] = mais_proximo.coordenada
        self.eliminar_coordenadas_repetidas()

    def eliminar_coordenadas_repetidas(self):
        novas_coordenadas = []
        for cont, coordenada in enumerate(self.coordenadas):
            if cont > 0:
                if coordenada != novas_coordenadas[-1]:
                    novas_coordenadas.append(coordenada)
            else:
                novas_coordenadas.append(coordenada)

        self.coordenadas = novas_coordenadas


def posicionar_cabos_nos_pontos(cabos, postes):
    for cabo in cabos:
        cabo.osnap(postes)


def relatorio_ancoragens(cabos, caixas):
    for cabo in cabos:
        print(cabo.nome)
        ancoragens, passagens = cabo.ancoragens(caixas, ANGULO_PARA_ANCORAGEM)
        print(f"Ancoragens = {ancoragens} | Passagens = {passagens}")


def calcular_tracao_postes(postes, cabos):
    for poste_ in postes:
        for cabo in cabos:
            for n, coordenada in enumerate(cabo.coordenadas):
                if distance(poste_.coordenada, coordenada) < DISTANCIA_ENTRE_POSTE_E_CABO:
                    c1 = cabo.coordenadas[n]
                    if 0 < n < (len(cabo.coordenadas) - 1):
                        c2 = cabo.coordenadas[n - 1]
                        c3 = cabo.coordenadas[n + 1]
                        distancia_1 = distance(c1, c2)
                        distancia_2 = distance(c1, c3)
                        angulo_entre_cabos = calcula_angulo_entre_tres_pontos(c1, c2, c3)
                        angulo_eixo_latitude = calcular_angulo_eixo_latitude(c1, c3)
                        poste_.add_tracao(
                            f"{cabo.nome} : {distancia_1:.2f}m | {int(angulo_entre_cabos)}º | {distancia_2:.2f}m |"
                            f" {int(angulo_eixo_latitude)}ºNorte")
                    elif n == 0:
                        c3 = cabo.coordenadas[n + 1]
                        distancia_2 = distance(c1, c3)
                        angulo_eixo_latitude = calcular_angulo_eixo_latitude(c1, c3)
                        poste_.add_tracao(f"{cabo.nome} : 0m | 0º | {distancia_2:.2f}m | {int(angulo_eixo_latitude)}ºNorte")
                    elif n == (len(cabo.coordenadas) - 1):
                        c2 = cabo.coordenadas[n - 1]
                        distancia_1 = distance(c1, c2)
                        angulo_eixo_latitude = calcular_angulo_eixo_latitude(c1, c2)
                        poste_.add_tracao(f"{cabo.nome} : {distancia_1:.2f}m | 0º - 0m | {int(angulo_eixo_latitude)}ºNorte")


DISTANCIA_ENTRE_POSTE_E_CABO = 3  # metros
ANGULO_PARA_ANCORAGEM = 15  # graus


def relatorio_tracoes(postes):
    for poste in postes:
        if poste.bap:
            print(f"Poste ID:{poste.id}")
            print(poste.tracoes)


def gerar_id_postes(postes):
    for n, poste in enumerate(postes):
        poste.id = n + 1


if __name__ == '__main__':
    # extraindo
    postes_projeto = Poste.extrair_pontos("postes.kmz")
    ctos_projeto = Cto.extrair_pontos("ctos.kmz")
    cabos_projeto = Cabo.extrair_caminhos("cabos.kmz")

    # regulando posicionamento dos cabos e calculando tracoa do postes
    gerar_id_postes(postes_projeto)
    posicionar_cabos_nos_pontos(cabos_projeto, postes_projeto)
    calcular_tracao_postes(postes_projeto, cabos_projeto)

    # gerando relatorio
    relatorio_ancoragens(cabos_projeto, ctos_projeto)
    relatorio_tracoes(postes_projeto)
