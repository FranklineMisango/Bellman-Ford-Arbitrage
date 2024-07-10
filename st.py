import streamlit as st
import os
from arbitrage_algos import ArbitrageAlgorithms
from visualization import GraphVisualization
from forex_scraper import ForexScraper

# Function to format paths
def format_paths(paths):
    """
    This is a helper method that formats the inputted paths into a displayable
    string with currency emojis.
    """
    path_string = ""
    percentage_string = ""
    for path, percentage in paths:
        percentage_string += "+ " + str(percentage) + "% profit\n"
        for currency in path[:-1]:
            path_string += ForexScraper.currency_flags[currency] + " " + currency + " ⟶ "
        path_string += ForexScraper.currency_flags[path[-1]] + " " + path[-1]
        path_string += "\n"
    return (path_string, percentage_string)

# Ensure the Graphs directory exists
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Ensure the directory exists
ensure_directory_exists("static/Graphs")

# Streamlit app starts here
st.title("Forex Arbitrage Opportunities")

# User inputs for date and base currency
date = st.text_input("Enter date (YYYY-MM-DD or 'now'/'today')", "latest")
base_currency = st.text_input("Enter base currency (e.g., USD)", "USD").upper()

# Button to run the arbitrage program
if st.button("Calculate"):
    # RUN THE FOREX SCRAPER AND CREATE ADJACENCY MATRIX & EXCHANGE TABLE WITH CURRENCIES
    scraper = ForexScraper(date, base_currency)
    adjacency_matrix = scraper.get_adjacency_matrix()
    exchange_table = scraper.get_exchange_table_html()

    # CREATE GRAPH VISUALIZATION OF ALL RETRIEVED CURRENCIES/EXCHANGE RATES
    visualization = GraphVisualization()
    digraph = visualization.create_graph_from_dataframe(adjacency_matrix)
    all_vertices_path = "Graphs/all_vertices_digraph.png"
    try:
        visualization.draw_graph(digraph, output_file=all_vertices_path,
                                 size="small", edge_weights=False)
        if os.path.exists(all_vertices_path):
            st.image(all_vertices_path, caption="All Currencies/Exchange Rates Graph")
        else:
            st.error(f"Error: {all_vertices_path} not found.")
    except Exception as e:
        st.error(f"Error generating graph: {e}")

    # FIND ARBITRAGE OPPORTUNITIES ON THE GRAPH
    arbitrage = ArbitrageAlgorithms(digraph)
    paths = arbitrage.run_arbitrage()
    path_string, percentage_string = format_paths(paths)

    # CREATE NEW ADJACENCY MATRIX USING ONLY CURRENCIES INVOLVED IN ARBITRAGE OPPORTUNITIES
    arbitrage_currencies = arbitrage.get_arbitrage_currencies()
    currency_set = set(scraper.get_currency_list())
    no_arbitrage_currencies = currency_set.difference(arbitrage_currencies)
    filtered_adj_matrix = adjacency_matrix.copy()
    filtered_adj_matrix = filtered_adj_matrix.drop(index=no_arbitrage_currencies,
                                                   columns=no_arbitrage_currencies)

    # CREATE GRAPH VISUALIZATION OF CURRENCIES/EXCHANGE RATES INVOLVED IN ARBITRAGE OPPORTUNITIES
    filtered_digraph = visualization.create_graph_from_dataframe(filtered_adj_matrix)
    filtered_vertices_path = "Graphs/filtered_digraph.png"
    try:
        visualization.draw_graph(filtered_digraph, output_file=filtered_vertices_path,
                                 size="large", edge_weights=True)
        if os.path.exists(filtered_vertices_path):
            st.image(filtered_vertices_path, caption="Currencies/Exchange Rates Involved in Arbitrage")
        else:
            st.error(f"Error: {filtered_vertices_path} not found.")
    except Exception as e:
        st.error(f"Error generating graph: {e}")

    st.markdown(f"### Arbitrage Paths:\n{path_string}")
    st.markdown(f"### Potential Profit:\n{percentage_string}")
    st.markdown(f"### Exchange Rates Table ({date}):\n{exchange_table}", unsafe_allow_html=True)
