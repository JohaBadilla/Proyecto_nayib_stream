import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.set_page_config(page_title="Análisis de datos Chinook", page_icon="📊")
    
    st.title("Proyecto de Análisis de Ventas Chinook")
    st.subheader("Johanna UB")
    
    st.markdown("""
    ## Introducción

    El siguiente dashboard presenta un análisis detallado de la base de datos Chinook, 
    la cual contiene información sobre ventas de música digital, artistas, géneros y canciones. 
    Este proyecto forma parte del curso de Taller de Programación impartido por el Profesor Nayib Vargas.

    ### Objetivo del Proyecto
    Realizar un análisis detallado de las tendencias de ventas y reproducciones musicales 
    de la base de datos Chinook, utilizando técnicas de visualización de datos y análisis 
    estadístico para identificar patrones relevantes y oportunidades de mejora en la gestión de la colección musical.

    
    """
                )
    
    # Aquí puedes agregar más secciones o visualizaciones según tu proyecto
    st.sidebar.header("Johanna Umaña Badilla")
    st.sidebar.info("2024")

if __name__ == "__main__":
    main()