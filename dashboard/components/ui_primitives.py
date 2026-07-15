import streamlit as st
import os

def load_css(file_name="assets/academia_style.css"):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def ui_ornate_divider():
    """Renders a classical ornate divider with a glyph"""
    html = '''
    <div class="ornate-divider-container">
        <div class="ornate-divider"></div>
        <div class="ornate-glyph">✶</div>
    </div>
    '''
    st.markdown(html, unsafe_allow_html=True)

def ui_volume_header(volume_num: str, title: str):
    """Renders a section header in Volume style"""
    html = f'''
    <span class="volume-overline">Volume {volume_num}</span>
    <h2 class="volume-title">{title}</h2>
    '''
    st.markdown(html, unsafe_allow_html=True)

def ui_drop_cap_paragraph(text: str):
    """Renders a paragraph with an illuminated drop cap"""
    html = f'''
    <p class="drop-cap">{text}</p>
    '''
    st.markdown(html, unsafe_allow_html=True)

def ui_arch_image(image_path: str, caption: str = ""):
    """Renders an image with the cathedral arch-top styling"""
    # Streamlit base64 images or public URLs. We can use st.image but wrap it in an arch-top container.
    # To style st.image from python, we wrap it in a div that we target via CSS.
    st.markdown('<div class="arch-top">', unsafe_allow_html=True)
    st.image(image_path, caption=caption, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)
