import warnings
warnings.filterwarnings('ignore') # somente para ignorar os warnings
import pandas as pd # ferramenta para ciencia de dados
from tqdm import tqdm
import psycopg2
import json
import folium # Para usar o mapa
import folium.plugins as plugins # Para usar o cluster
import branca
import os

class make_map():
    def __init__(self):
        self.con = psycopg2.connect(host='ec2-3-213-228-206.compute-1.amazonaws.com', 
                         database='dbola8cfs4iili',
                         user='mljmaxtzayxmfi',
                         password = 'f06107039bb077725d49b11b67a04e5bc3a70a4761fbbc3b859111f6a267a174',
                         port = 5432)
        
        self.df = pd.read_sql('select nome,bairro,uf,area_total,nome_empresa,situacao,ST_AsGeoJSON(geom_novo) from public.prototipo_construcoes', self.con)
        self.m = folium.Map(location = [-15.763048872811966, -47.870631102672284],zoom_start = 10)
        
        self.monta_mapa()
        
        self.m.save('map.html')
        
        print('acesse o endereço http://localhost:8000/map.html')
        
        os.system("killport 8000")
        os.system("python -m http.server 8000")
        
        
        
    def trata_dados(self):
        self.df['st_asgeojson'] = self.df['st_asgeojson'].apply(lambda x: json.loads(x)['coordinates'])
        
    def adiciona_cluster(self):
        self.marker_cluster_ativo = plugins.MarkerCluster(name = 'Obras Ativas').add_to(self.m)
        self.marker_cluster_suspensas = plugins.MarkerCluster(name = 'Obras Suspensas',show = False).add_to(self.m)
        self.marker_cluster_paralizadas = plugins.MarkerCluster(name = 'Obras Paralizadas',show = False).add_to(self.m)
        
    def fancy_html(self,row):
        i = row

        Nome = self.df['nome'].iloc[i]                             
        Bairro = self.df['bairro'].iloc[i]                           
        Estado = self.df['uf'].iloc[i]
        Area_total = self.df['area_total'].iloc[i]                                           
        Nome_Empresarial = self.df['nome_empresa'].iloc[i]                               

        left_col_colour = "#2A799C"
        right_col_colour = "#C5DCE7"

        html = """<!DOCTYPE html>
    <html>

        <head>
        <h4 style="margin-bottom:0"; width="300px">{}</h4>""".format(Estado) + """

        </head>
            <table style="height: 126px; width: 300px;">
        <tbody>
        <tr>
        <td style="background-color: """+ left_col_colour +""";"><span style="color: #ffffff;">Nome da Obra</span></td>
        <td style="width: 200px;background-color: """+ right_col_colour +""";">{}</td>""".format(Nome) + """
        </tr>
        <tr>
        <td style="background-color: """+ left_col_colour +""";"><span style="color: #ffffff;">Bairro</span></td>
        <td style="width: 200px;background-color: """+ right_col_colour +""";">{}</td>""".format(Bairro) + """
        </tr>
        <tr>
        <td style="background-color: """+ left_col_colour +""";"><span style="color: #ffffff;">Área total</span></td>
        <td style="width: 200px;background-color: """+ right_col_colour +""";">{}m²</td>""".format(Area_total) + """
        </tr>
        <tr>
        <td style="background-color: """+ left_col_colour +""";"><span style="color: #ffffff;">Nome da Empresa</span></td>
        <td style="width: 200px;background-color: """+ right_col_colour +""";">{}</td>""".format(Nome_Empresarial) + """
        </tr>
        </tbody>
        </table>
    </html>
    """
        return html

    def insere_dados_mapa(self,situacao):
        if situacao == '2':
            cluster = self.marker_cluster_ativo
            color = 'green'
            desc = 'ativas'
        
        elif situacao == '3':
            cluster = self.marker_cluster_suspensas
            color = 'orange'
            desc = 'suspensas'
            
        elif situacao == '14':
            cluster = self.marker_cluster_paralizadas
            color = 'red'
            desc = 'paralizadas'
        
        df_tmp = self.df[self.df['situacao'] == situacao]
        df_tmp = df_tmp.reset_index(drop = True)

        for i in tqdm(range(0,len(df_tmp)),desc='Inserindo obras {}'.format(desc)):
            html = self.fancy_html(i)
 
            iframe = branca.element.IFrame(html=html,width=400,height = 300)
            popup = folium.Popup(iframe,parse_html=True)
    
            folium.Marker([df_tmp['st_asgeojson'][i][1], df_tmp['st_asgeojson'][i][0]],
                  popup=popup,icon=folium.Icon(color=color, icon='info-sign')).add_to(cluster)
        
    def monta_mapa(self):
        self.trata_dados()
        self.adiciona_cluster()
        
        self.insere_dados_mapa('2')
        self.insere_dados_mapa('3')
        self.insere_dados_mapa('14')
        
        folium.LayerControl().add_to(self.m)
        


make_map()