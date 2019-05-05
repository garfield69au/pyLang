import pandas as pd
import numpy as np
import plotly

from plotly.graph_objs import Scatter,Layout,Marker,Bar
from piLang.piLang.Measurement import Measurement, MeasurementCategory



# Read data

# Dataset: Life Expectancy and per capita income (Rosling) 
class BoxPlot(object):

    def plot(self, l:list):
        """
        example structure of l: 
            l = [
                {'attribute' : 'mother_id', 'errorCategory':'Completeness', 'errorCount': 5000, 'attributeCount': 20000, 'Mean': -1.0, 'Percent': 50},
                {'attribute' : 'mother_id', 'errorCategory':'Completeness', 'errorCount': 15000, 'attributeCount': 20000, 'Mean': -1.0, 'Percent': 75},
                {'attribute' : 'mother_id', 'errorCategory':'Completeness', 'errorCount': 700, 'attributeCount': 20000, 'Mean': -1.0, 'Percent': 12},
                {'attribute' : 'mother_id', 'errorCategory':'Completeness', 'errorCount': 1000, 'attributeCount': 20000, 'Mean': -1.0, 'Percent': 35},
                {'attribute' : 'mother_id', 'errorCategory':'Accuracy', 'errorCount': 1000, 'attributeCount': 20000, 'Mean': -1.0, 'Percent': 10},
                {'attribute' : 'mother_id', 'errorCategory':'Accuracy', 'errorCount': 10, 'attributeCount': 20000, 'Mean': -1.0, 'Percent': 2},
                {'attribute' : 'mother_id', 'errorCategory':'Accuracy', 'errorCount': 70, 'attributeCount': 20000, 'Mean': -1.0, 'Percent': 8},
                {'attribute' : 'mother_id', 'errorCategory':'Consistency', 'errorCount': 8000, 'attributeCount': 20000, 'Mean': -1.0, 'Percent': 10},
                {'attribute' : 'mother_id', 'errorCategory':'Consistency', 'errorCount': 20000, 'attributeCount': 20000, 'Mean': -1.0, 'Percent': 100},
                {'attribute' : 'mother_id', 'errorCategory':'Consistency', 'errorCount': 5, 'attributeCount': 20000, 'Mean': -1.0, 'Percent': .5}
               ]
        """        
        df = pd.DataFrame.from_records(l)
        df.replace(-1,0,inplace=True)

        df = df.sort_values(['errorCategory', 'attribute', 'errorCount'])
        
        m = max(df["errorCount"])
        
        trace1 = Scatter(
            y= df["errorCount"],
            x= df["errorCategory"],
            marker= plotly.graph_objs.scatter.Marker(
                        symbol="circle",
                        size=df["errorCount"],                        
                        sizeref= 2.0*m / (100.0**2.0),
                        sizemode= 'area',
                        sizemin=10,
                        colorscale='Viridis',
                        color=df["errorCount"],
                        showscale= True,
                        opacity=0.4,
                        line=dict (
                            color= 'black',
                            width= 2
                        ),
            ),
            mode= 'markers',
            showlegend= True,
            text= "Attribute: " + "<b>" + df["attribute"] + "</b>"
        )

        # Create chart 

        # Output will be stored as a html file. 

        # Whenever we will open output html file, one popup option will ask us about if want to save it in jpeg format. #
        # If you want basic bubble chart with only one continent just include that particular trace while providing input. 
        
        
        plotly.offline.plot(
        {
                        "data": [trace1],
                        "layout": Layout(

                                            title="<b>Mater HEALTH<br>PDC Data Quality Analysis using LANG</b>",
                                            autosize=True,
                                            hovermode='closest',                                            
                                            xaxis= dict(
                                                title= '<b>Data Quality Dimensions</b>',
                                                zeroline= False,
                                                gridcolor='rgb(183,183,183)',
                                                showline=True,
                                                ticklen=5,
                                                gridwidth= 2
                                            ),
                                            yaxis=dict(
                                                title= '<b>Count of Data Quality Errors</b>',
                                                gridcolor='rgb(183,183,183)',
                                                zeroline=False,
                                                showline=True,
                                                ticklen=5,
                                                gridwidth= 2
                                            )
                                        )

                            },
                            filename='bubble_chart.html',
                            image='jpeg'
        ) 
