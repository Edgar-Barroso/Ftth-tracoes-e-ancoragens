import xml.etree.ElementTree as Element
# from geopy.distance import distance
from math import sin, cos, sqrt, atan2, radians
import xmltodict
import zipfile


def distance(p1, p2):
    # Raio aproximado da terra
    r = 6371.0

    lat1 = radians(p1[0])
    lon1 = radians(p1[1])
    lat2 = radians(p2[0])
    lon2 = radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return r * c * 1000


class Ponto:
    def __init__(self, coordenada=None, nome='', descricao='', estilo='', estilokml=''):
        self._coordenada = coordenada
        self._nome = nome
        self._descricao = descricao
        self._estilo = estilo
        self._estilokml = estilokml

    @property
    def coordenada(self):
        return self._coordenada

    @coordenada.setter
    def coordenada(self, valor):
        if type(valor) is not list:
            raise ValueError('coordenada deve ser uma list')
        self._coordenada = valor

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        if type(valor) is not str:
            raise ValueError('nome deve ser uma string')
        self._nome = valor

    @property
    def descricao(self):
        return self._descricao

    @descricao.setter
    def descricao(self, valor):
        if type(valor) is not str:
            raise ValueError('descrição deve ser uma string')
        self._descricao = valor

    @property
    def estilo(self):
        return self._estilo

    @estilo.setter
    def estilo(self, valor):
        if type(valor) is not str:
            raise ValueError('estilo deve ser uma string')
        self._estilo = valor

    @property
    def estilokml(self):
        return self._estilo

    @estilokml.setter
    def estilokml(self, valor):
        if type(valor) is not str:
            raise ValueError('estilo deve ser uma string')
        self._estilokml = valor

    @classmethod
    def extrair_pontos(cls, arq_name):
        lista = []
        if '.kmz' in arq_name:
            with zipfile.ZipFile(arq_name, 'r') as f:
                f.extract('doc.kml', 'TEMP')
                arq_name = 'TEMP/doc.kml'
        doc = Element.parse(arq_name)
        root = doc.getroot()
        np = root.tag.split('}')[0] + '}'
        ids = {}
        ids_map = {}
        for c in root.iter(np + 'StyleMap'):
            for i in c:
                if i.tag == f'{np}Pair':
                    for h in i:
                        if h.tag == f'{np}styleUrl' and i[0].text == 'normal':
                            ids_map[c.attrib['id']] = h.text
        for c in root.iter(np + 'Style'):
            for i in c:
                if i.tag == f'{np}IconStyle':
                    for h in i:
                        if h.tag == f'{np}Icon':
                            ids[c.attrib['id']] = h[0].text
        for c in root.iter(np + 'Placemark'):
            ponto = False
            pt = cls()
            for j in c:
                if j.tag == f'{np}name':
                    pt.nome = j.text
                elif j.tag == f'{np}description':
                    pt.descricao = j.text
                elif j.tag == f'{np}Point':
                    ponto = True
                    for q in j:
                        if q.tag == f'{np}coordinates':
                            pt.coordenada = [float(q.text.strip().split(',')[1]), float(q.text.strip().split(',')[0])]
                elif j.tag == f'{np}styleUrl':
                    try:
                        pt.estilo = ids[ids_map[j.text.replace('#', '')].replace('#', '')]
                    except IndexError:
                        pt.estilo = j.text

            if ponto is True:
                lista.append(pt)
        return lista

    def __sub__(self, other):
        return distance(self.coordenada, other.coordenada)


class Caminho:
    def __init__(self, coordenadas=None, nome='', descricao='', estilo=''):
        self._coordenadas = coordenadas
        self._nome = nome
        self._descricao = descricao
        self._estilo = estilo

    @property
    def coordenadas(self):
        return self._coordenadas

    @coordenadas.setter
    def coordenadas(self, valor):
        if type(valor) is not list:
            raise ValueError('coordenadas deve ser uma list')
        self._coordenadas = valor

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        if type(valor) is not str:
            raise ValueError('nome deve ser uma string')
        self._nome = valor

    @property
    def descricao(self):
        return self._descricao

    @descricao.setter
    def descricao(self, valor):
        if type(valor) is not str:
            raise ValueError('descrição deve ser uma string')
        self._descricao = valor

    @property
    def estilo(self):
        return self._estilo

    @estilo.setter
    def estilo(self, valor):
        if type(valor) is not str:
            raise ValueError('estilo deve ser uma string')
        self._estilo = valor

    @property
    def metragem(self):
        total = 0.0
        for n, coord in enumerate(self.coordenadas):
            if n > 0:
                total += distance(coord, self.coordenadas[n - 1])
            else:
                continue
        return total

    @classmethod
    def extrair_caminhos(cls, arq_name):
        if '.kmz' in arq_name:
            with zipfile.ZipFile(arq_name, 'r') as f:
                f.extract('doc.kml', 'TEMP')
                arq_name = r'TEMP\doc.kml'
        with open(f'{arq_name}', 'r+') as f:
            arq = f.read()
        arq = arq.replace('<Folder>', '').replace('</Folder>', '')
        arq = arq.replace('<Document>', '').replace('</Document>', '')
        lista = []
        arq = xmltodict.parse(arq)
        dicionario = arq['kml']['Placemark']
        for place in dicionario:
            try:

                coordenadas_texto = place['LineString']['coordinates']
                coordenadas_float = []
                for coordenada in coordenadas_texto.split():
                    coordenada = [float(coordenada.split(',')[1]), float(coordenada.split(',')[0])]
                    coordenadas_float.append(coordenada)
                try:
                    nome = place['name']
                except KeyError:
                    nome = ''
                try:
                    descricao = place['description']
                except KeyError:
                    descricao = ''
                try:
                    estilo = place['styleUrl']
                except KeyError:
                    estilo = ''
                pt = cls()
                pt.coordenadas = coordenadas_float
                pt.nome = nome
                pt.descricao = descricao
                pt.estilo = estilo
                lista.append(pt)
            except KeyError:
                continue
        return lista
