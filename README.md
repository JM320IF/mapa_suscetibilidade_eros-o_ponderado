# Mapa de Suscetibilidade à Erosão com Dados Topográficos e Qualidade de Pastagem

## Autor
João Marcos Gonçalves

## Contato
[joaogs.geo@gmail.com](mailto:joaogs.geo@gmail.com)

## Descrição
Este projeto tem como objetivo gerar um mapa de suscetibilidade à erosão utilizando dados topográficos e informações sobre a qualidade de pastagem. Ele realiza o recorte de rasters para um município específico (Pinheiral) e calcula o índice de suscetibilidade baseado em múltiplos fatores geomorfológicos e de pastagem.

## Funcionalidades

- **Recorte de Rasters:** Recorta múltiplos rasters (declividade, altitude, curvatura, etc.) para o município de Pinheiral usando um shapefile com a geometria do município.
- **Cálculo da Suscetibilidade à Erosão:** Utiliza dados de declividade, altitude, curvatura e qualidade de pastagem para calcular o índice de suscetibilidade à erosão ponderado.
- **Visualização e Salvamento:** Gera uma visualização do mapa de suscetibilidade à erosão e salva o resultado como uma imagem e um arquivo GeoTIFF.

## Dependências

- `geopandas`
- `rasterio`
- `numpy`
- `matplotlib`

## Como Usar

1. **Prepare os Dados:**
   - Tenha os rasters (declividade, altitude, curvatura, formato do terreno e qualidade de pastagem) prontos e salvos no formato `.tif`. Obs: você pode obter os dados de altimetria na plataforma TOPODATA do INPE e os dados de Uso e Cobertura do Solo (como qualidade de pastagem) na plataforma MAPBIOMAS.
   - Tenha um shapefile contendo a geometria da área de interesse.

2. **Alterar os Caminhos dos Arquivos:**
   - No código, altere os caminhos dos arquivos de entrada (shapefile e rasters) para os locais corretos no seu sistema.

3. **Executar o Código:**
   - Execute os scripts para recortar os rasters e gerar o mapa de suscetibilidade à erosão.
