#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
Mapa de Suscetibilidade à Erosão com Dados Topográficos e Qualidade de Pastagem
Autor: [João Marcos Gonçalves]
Contato [joaogs.geo@gmail.com]
Descrição: Gera um mapa de suscetibilidade ponderado com base em múltiplos fatores geomorfológicos e pastagem.
Licença: MIT
"""


import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import matplotlib.pyplot as plt

#PARTE1-RECORTANDO OS RASTERS COM O POLÍGONO DA ÁREA DE INTERESSE 

def recortar_raster(caminho_raster, geometria, pasta_saida):
    with rasterio.open(caminho_raster) as src:
        out_image, out_transform = mask(src, geometria, crop=True)
        out_meta = src.meta
        
        out_meta.update({
            "driver": "GTiff",
            "count": 1,
            "crs": src.crs,
            "transform": out_transform
        })

    nome_raster = os.path.basename(caminho_raster).replace('.tif', '_recortado.tif')
    caminho_saida_raster = os.path.join(pasta_saida, nome_raster)

    with rasterio.open(caminho_saida_raster, "w", **out_meta) as dest:
        dest.write(out_image)

    print(f"Raster recortado salvo em: {caminho_saida_raster}")

    # Exibir o raster recortado
    plt.figure(figsize=(8, 6))
    plt.imshow(out_image[0], cmap='viridis')
    plt.title(f"Raster Recortado: {nome_raster}")
    plt.colorbar()
    plt.show()

    return caminho_saida_raster


def recortar_rasters_para_municipio(shapefile_path, pasta_rasters, pasta_saida):
    municipios_rj = gpd.read_file(shapefile_path)
    
    # Verificar se o CRS do shapefile é o mesmo dos rasters
    with rasterio.open(list(pasta_rasters.values())[0]) as src:
        raster_crs = src.crs

    if municipios_rj.crs != raster_crs:
        print(f"CRS do shapefile ({municipios_rj.crs}) não é o mesmo que o CRS do raster ({raster_crs}). Reprojetando...")
        municipios_rj = municipios_rj.to_crs(raster_crs)

    pinheiral = municipios_rj[municipios_rj["NM_MUN"] == "Pinheiral"]

    os.makedirs(pasta_saida, exist_ok=True)

    for nome, caminho_raster in pasta_rasters.items():
        recortar_raster(caminho_raster, pinheiral.geometry, pasta_saida)


# Caminhos dos arquivos
shapefile_path = r"C:\Users\Desktop\PROJETOSGIS\poligono.shp"
pasta_rasters = {
    "declividade": r"C:\Users\Desktop\PROJETOSGIS\declividade.tif",
    "altitude": r"C:\Users\Desktop\PROJETOSGIS\altitude.tif",
    "curv_vert": r"C:\Users\Desktop\PROJETOSGIS\curvatura_vertical.tif",
    "curv_horiz": r"C:\Users\Desktop\PROJETOSGIS\curvatura_horizontal.tif",
    "forma_terreno": r"C:\Users\Desktop\PROJETOSGIS\formato_terreno.tif",
}
pasta_saida = r"C:\Users\Desktop\PROJETOSGIS\Rasters_Recortados"

# Recortar os rasters para o município de Pinheiral
recortar_rasters_para_municipio(shapefile_path, pasta_rasters, pasta_saida)


# In[ ]:


#PARTE2-GERANDO O MAPA A PARTIR DOS RASTERS RECORTADOS 

import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.enums import Resampling

def normalizar(array):
    array = array.astype('float32')
    array[array == -9999] = np.nan
    return (array - np.nanmin(array)) / (np.nanmax(array) - np.nanmin(array))

def main():
    # Pasta base com os rasters
    base = os.path.join("data", "rasters_recortados")

    # Arquivos de entrada
    rasters = {
        'declividade': os.path.join(base, "declividade_recortado.tif"),
        'altitude': os.path.join(base, "altitude_recortado.tif"),
        'curv_horiz': os.path.join(base, "curv_horiz_recortado.tif"),
        'curv_vert': os.path.join(base, "curv_vert_recortado.tif"),
        'forma_terreno': os.path.join(base, "forma_terreno_recortado.tif")
    }

    pesos = {
        'declividade': 0.4,
        'altitude': 0.2,
        'curv_horiz': 0.15,
        'curv_vert': 0.15,
        'forma_terreno': 0.1
    }

    qualidade_path = os.path.join(base, "qualidade_pastagem.tif")
    peso_pastagem = 0.1

    dados = {}

    for nome, path in rasters.items():
        with rasterio.open(path) as src:
            array = src.read(1)
            perfil = src.profile
            dados[nome] = normalizar(array)

    with rasterio.open(qualidade_path) as src:
        qualidade = src.read(1).astype('float32')
        qualidade[qualidade == src.nodata] = np.nan

        with rasterio.open(rasters['declividade']) as ref:
            qualidade_resized = src.read(
                out_shape=(ref.count, ref.height, ref.width),
                resampling=Resampling.bilinear
            )[0]
            qualidade_resized = normalizar(qualidade_resized)

    # Criar máscara para áreas nulas
    nan_mask = np.isnan(qualidade_resized)
    for v in dados.values():
        nan_mask |= np.isnan(v)

    suscetibilidade = sum(dados[k] * pesos[k] for k in dados) + qualidade_resized * peso_pastagem
    suscetibilidade[nan_mask] = np.nan

    # Visualização
    plt.figure(figsize=(10, 6))
    plt.imshow(suscetibilidade, cmap='YlOrBr')
    plt.title('Mapa de Suscetibilidade à Erosão')
    plt.colorbar(label='Índice de Suscetibilidade (0 a 1)')
    plt.axis('off')

    output_img = os.path.join(base, "mapa_suscetibilidade.png")
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    plt.show()

    # Salvar como GeoTIFF
    output_raster = os.path.join(base, "suscetibilidade.tif")
    suscetibilidade[np.isnan(suscetibilidade)] = -9999

    perfil.update({
        'dtype': 'float32',
        'count': 1,
        'nodata': -9999,
        'compress': 'lzw'
    })

    with rasterio.open(output_raster, 'w', **perfil) as dst:
        dst.write(suscetibilidade, 1)

if __name__ == "__main__":
    main()

