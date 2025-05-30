import pandas as pd
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

def _weather_to_dataframe(city, weather):
    df = pd.DataFrame(weather)
    df.insert(0, "city", city)
    return df

def generate_excel(city, weather):
    df = _weather_to_dataframe(city, weather)
    path = f"{city}_weather.xlsx"
    df.to_excel(path, index=False, engine='xlsxwriter')
    return path

def generate_csv(city, weather):
    df = _weather_to_dataframe(city, weather)
    path = f"{city}_weather.csv"
    df.to_csv(path, index=False)
    return path

def generate_pdf(city, weather):
    df = _weather_to_dataframe(city, weather)
    template_env = Environment(loader=FileSystemLoader('.'))
    template = template_env.get_template("template.html")

    html_content = template.render(city=city, table=df.to_html(index=False))
    pdf_path = f"{city}_weather.pdf"
    with open(pdf_path, "wb") as pdf_file:
        pisa.CreatePDF(html_content, dest=pdf_file)
    return pdf_path
