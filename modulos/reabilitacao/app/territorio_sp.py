"""Classificação territorial aproximada de São Paulo a partir dos bairros cadastrados no CNES.

ATENÇÃO:
- Zonas (Norte/Sul/Leste/Oeste/Centro) podem ser definidas oficialmente por
  limites de distritos, mas o CNES fornece um texto de *bairro* que não equivale
  necessariamente ao distrito administrativo.
- Esta versão usa APENAS correspondências literais de bairros com localização
  amplamente identificável, de maneira conservadora; casos não mapeados são
  marcados 'nao_identificada'.
- Não usar esse campo como comprovante de endereço ou delimitação oficial.
- Para maior precisão, cruzar coordenadas do CNES com polígonos distritais GeoSampa.
"""
from .service import normalize

ZONAS = {
    'centro': 'Centro', 'norte': 'Zona Norte', 'sul': 'Zona Sul',
    'leste': 'Zona Leste', 'oeste': 'Zona Oeste',
    'nao_identificada': 'Zona não identificada',
}
# Correspondências explícitas para evitar inferência automática de endereços.
BAIRROS_POR_ZONA = {
    'centro': [
        'ACLIMACAO', 'BELA VISTA', 'BOM RETIRO', 'CAMPOS ELISEOS', 'CENTRO', 'SE',
    ],
    'norte': [
        'BRASILANDIA','CARANDIRU','CASA VERDE','FREGUESIA DO O','JACANA',
        'JARAGUA','JARDIM DA FELICIDADE','JARDIM PERI','JD SAO PAULO',
        'PARQUE SAO DOMINGOS','PERUS','PIRITUBA','SANTANA','VILA CAIUBA PERUS',
        'VILA CONSTANCA','VILA MARIA ALTA','VILA MAZZEI','VILA NOVA CACHOEIRIN',
    ],
    'leste': [
        'ARICANDUVA','BELENZINHO','CIDADE SAO MATEUS','CIDADE TIRADENTES',
        'COHAB JUSCELINO','ERMELINO MATARAZZO','GUAIANASES','ITAIM PAULISTA',
        'ITAQUERA','J NELIA','JARDIM CAMARGO NOVO','JARDIM IV CENTENARIO',
        'JD SAPOPEMBA','MAE DO CEU','MOOCA','PARQUE BOTURUSSU','PENHA',
        'SAO MATEUS','SAO MIGUEL PAULISTA','SAO MIGUEL PTA','VILA CARDOSO FRANCO',
        'VILA ESPERANCA','VILA FORMOSA','VILA JACUI','VILA PARANAGUA','VILA PRUDENTE',
    ],
    'oeste': [
        'BARRA FUNDA','CAXINGUI','CERQUEIRA CESAR','FAZENDA MORUMBI',
        'ITAIM BIBI','JARDIM HUMAITA','JARDIM PANORAMA','LAPA','PERDIZES',
        'PINHEIROS','PQ DA LAPA','SUMARE','VILA BUTANTA','VILA HAMBURGUESA',
        'VILA PROGREDIOR','VILA ROMANA',
    ],
    'sul': [
        'BALNEARIO MAR PAULIS','BALNEARIO SAO JOSE','BOM REFUGIO','CAMPO LIMPO',
        'CHACARA STO ANTONIO','CID VARGAS','CIDADE DUTRA','CIDADE NOVA HELIOPOL',
        'GRAJAU','IPIRANGA','JARDIM BOM REFUGIO','JARDIM CASABLANCA',
        'JARDIM LIDIA','JARDIM NOVO PARELHEI','JARDIM PEDREIRA','JARDIM REPRESA',
        'JARDIM ROSCHEL','JARDIM UMARIZAL','MOEMA','PLANALTO PAULISTA',
        'RIVIERA','RIVIERA PAULISTA','SANTO AMARO','SHANGRILA','SOCORRO',
        'STO AMARO','USINA PIRATININGA','V MONUMENTO','VILA ANDRADE',
        'VILA DAS BELEZAS','VILA GUARANI','VILA MARIANA','VILA CLEMENTINO',
    ],
}
INDICE = {}
for zona, bairros in BAIRROS_POR_ZONA.items():
    for bairro in bairros:
        chave = normalize(bairro)
        assert chave not in INDICE, f'Bairro com zona duplicada: {bairro}'
        INDICE[chave] = zona

def zona_do_bairro(bairro: str) -> str:
    return INDICE.get(normalize(bairro), 'nao_identificada')
