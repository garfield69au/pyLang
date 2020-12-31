import pandas as pd
import numpy as np
import plotly

from plotly.graph_objs import Scatter,Layout,Marker,Bar



# Read data

# Dataset: Life Expectancy and per capita income (Rosling) 
class BoxPlot(object):

    def plot(self, l:dict, chartTitle:str=""):
        """
        example structure of l: 
        l = [
                {'attribute' : 'mother_id', 'error_category':'Completeness'},
                {'attribute' : 'mother_id', 'error_category':'Completeness'},
                {'attribute' : 'frog', 'error_category':'Fishing'}
                
        ]
        """        

        if (l is None or len(l) == 0):
            print ("## nothing to plot ##")
            return
        
        df = pd.DataFrame.from_dict(l)
        df.replace(-1,0,inplace=True)
        
        df = df.sort_values(by=['attribute','error_dimension'])
        
        g = df.groupby(['error_dimension','attribute'])
        
        traces = list()
        
        for title, group in g:
            m=250
            
            traces.append(
                Scatter(
                    y= [group['error_dimension'].count()],
                    x= group['error_dimension'],
                    marker= plotly.graph_objs.scatter.Marker(
                                symbol="circle",
                                size=[group['error_dimension'].count()],
                                sizeref= 2.0*m / (100.0**2.0),
                                sizemode= 'area',
                                sizemin=20,
                                colorscale='Viridis',
                                showscale= False,
                                opacity=0.5,
                                line=dict (
                                    color= 'black',
                                    width= 2
                                ),
                    ),
                    mode= 'markers',
                    showlegend= True,
                    text= "Attribute: " + "<b>" + str(title[1]) + "</b>"
                )
            )
            
        # Create chart 

        # Output will be stored as a html file. 

        # Whenever we will open output html file, one popup option will ask us about if want to save it in jpeg format. #
        # If you want basic bubble chart with only one continent just include that particular trace while providing input. 
        
        if (chartTitle != ""):
            titleStr = chartTitle
        else:
            titleStr = "<b>Chart of Data Quality Errors by Count</b>"
            
        plotly.offline.plot(
        {
            "data": traces,
            "layout": Layout(

                                title=titleStr,
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
