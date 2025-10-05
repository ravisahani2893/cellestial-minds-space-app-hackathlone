import streamlit as st
import streamlit.components.v1 as components

# Read your HTML file
with open("output/knowledge_graph.html", "r") as f:
    html_data = f.read()

# Render the HTML file
components.html(html_data, height=800, scrolling=True)