import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

def load_data():
    """Cargar datos de la base de datos SQLite Chinook"""
    conn = sqlite3.connect("data/Chinook_Sqlite.sqlite")
    
    album = pd.read_sql_query("SELECT * FROM Album", conn)
    artist = pd.read_sql_query("SELECT * FROM Artist", conn)
    genre = pd.read_sql_query("SELECT * FROM Genre", conn)
    track = pd.read_sql_query("SELECT * FROM Track", conn)
    invoice = pd.read_sql_query("SELECT * FROM Invoice", conn)
    invoice_line = pd.read_sql_query("SELECT * FROM InvoiceLine", conn)

    conn.close()
    
    return album, artist, genre, track, invoice, invoice_line

def prepare_data(album, artist, genre, track, invoice, invoice_line):
    """Preparar los datos para análisis"""
    # Canciones por género
    track_counts = track.groupby('GenreId').size().reset_index(name='TrackCount')
    genre_track_counts = pd.merge(track_counts, genre, on='GenreId')
    total_tracks = genre_track_counts['TrackCount'].sum()
    genre_track_counts['Percentage'] = (genre_track_counts['TrackCount'] / total_tracks) * 100
    genre_track_counts.loc[genre_track_counts['Percentage'] < 5, 'Name'] = 'Otros géneros'
    genre_summary = genre_track_counts.groupby('Name', as_index=False).agg({'TrackCount': 'sum'})
    genre_summary['Percentage'] = (genre_summary['TrackCount'] / total_tracks) * 100

    # Artistas más escuchados
    query = """
        SELECT Artist.Name AS ArtistName, COUNT(InvoiceLine.TrackId) AS PlayCount
        FROM InvoiceLine
        JOIN Track ON InvoiceLine.TrackId = Track.TrackId
        JOIN Album ON Track.AlbumId = Album.AlbumId
        JOIN Artist ON Album.ArtistId = Artist.ArtistId
        GROUP BY Artist.Name
        ORDER BY PlayCount DESC
    """
    conn = sqlite3.connect("data/Chinook_Sqlite.sqlite")
    top_artists = pd.read_sql_query(query, conn).head(10)
    conn.close()

    # Ventas por año
    invoice['InvoiceDate'] = pd.to_datetime(invoice['InvoiceDate'])
    invoice['Year'] = invoice['InvoiceDate'].dt.year
    sales_by_year = invoice.groupby('Year')['Total'].sum().reset_index()

    return genre_summary, top_artists, sales_by_year

def main():
    st.set_page_config(page_title="Análisis de Chinook", layout="wide")
    st.title("🎵 Dashboard de Análisis de Chinook")

    # Cargar y preparar datos
    try:
        album, artist, genre, track, invoice, invoice_line = load_data()
        genre_summary, top_artists, sales_by_year = prepare_data(album, artist, genre, track, invoice, invoice_line)
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return

    # Sidebar para filtros
    st.sidebar.header("Filtros de Análisis")
    years = sales_by_year['Year'].unique()
    selected_years = st.sidebar.multiselect("Seleccionar Años", options=years.tolist(), default=years.tolist())
    
    genres = genre['Name'].unique()
    selected_genres = st.sidebar.multiselect("Seleccionar Géneros", options=genres.tolist(), default=genres.tolist())

    # Filtrar datos por años seleccionados
    filtered_sales_by_year = sales_by_year[sales_by_year['Year'].isin(selected_years)]

    # Filtrar datos por géneros seleccionados
    filtered_genre_summary = genre_summary[genre_summary['Name'].isin(selected_genres)]

    # Métricas principales
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Géneros", value=len(genre))
    col2.metric("Total de Artistas", value=len(artist))
    col3.metric("Total de Canciones", value=len(track))

    # Visualizaciones
    col1, col2 = st.columns(2)

    # Gráfico de Canciones por Género
    with col1:
        st.subheader("Distribución de Canciones por Género")
        fig_genre = go.Figure(
            data=[
                go.Pie(
                    labels=filtered_genre_summary['Name'],
                    values=filtered_genre_summary['TrackCount'],
                    hole=0.4,
                    marker=dict(colors=px.colors.qualitative.Pastel)
                )
            ]
        )
        fig_genre.update_layout(title_text="Canciones por Género")
        st.plotly_chart(fig_genre, use_container_width=True)

    # Gráfico de Artistas más escuchados
    with col2:
        st.subheader("Top 10 Artistas Más Escuchados")
        fig_artists = px.bar(
            top_artists,
            x='PlayCount',
            y='ArtistName',
            orientation='h',
            title='Artistas Más Escuchados',
            labels={'PlayCount': 'Reproducciones', 'ArtistName': 'Artista'},
            text='PlayCount'
        )
        fig_artists.update_traces(marker_color='skyblue', textposition='outside')
        fig_artists.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_artists, use_container_width=True)

    # Gráfico de Ventas por Año
    st.subheader("Evolución de Ventas Anuales")
    fig_sales = px.line(
        filtered_sales_by_year,
        x='Year',
        y='Total',
        title='Ventas Totales por Año',
        labels={'Year': 'Año', 'Total': 'Ventas Totales'},
        markers=True
    )
    st.plotly_chart(fig_sales, use_container_width=True)

    # Recomendaciones
    st.header("🚀 Recomendaciones")
    st.markdown(
        """
        - **Ampliar Géneros con Baja Representación**: Agregar más canciones en "Otros géneros".
        - **Promover Artistas Populares**: Impulsar promociones para los artistas más escuchados.
        - **Optimizar Estrategias de Ventas**: Analizar factores que impulsan ventas en años específicos.
        """
    )

if __name__ == "__main__":
    main()

