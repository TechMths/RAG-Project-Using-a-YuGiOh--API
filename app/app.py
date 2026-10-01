import streamlit as st
import sys
import json
from pathlib import Path

from retrieval.pipeline import RetrievalPipeline
from base.processing.processor import load_cards

st.set_page_config(page_title="Yu-Gi-Oh! RAG Search", layout="wide")

@st.cache_resource
def load_pipeline():
    return RetrievalPipeline()

@st.cache_data
def load_cards_by_name():
    cards = load_cards()  
    return {card["name"]: card for card in cards}

pipeline = load_pipeline()
cards_by_name = load_cards_by_name()

st.title("Busca de Cartas Yu-Gi-Oh!")
query = st.text_input("O que você está procurando?", placeholder="ex: High ATK Dark Monsters")

if query:
    img = load_cards()
    results = pipeline.search(query, top_k=10)
    cols = st.columns(5)
    for i, result in enumerate(results):
        metadata = result["metadata"]
        card = cards_by_name.get(metadata["name"])

        with cols[i % 5]:
            if card and card.get("card_images"):
                st.image(card["card_images"][0]["image_url"])
            st.caption(f"**{metadata['name']}**\nATK{metadata.get('atk')} / DEF {metadata.get('def')}")