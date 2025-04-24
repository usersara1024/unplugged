import base64
import os
from google import genai
from google.genai import types

argomento="Informatica, Pythoon e variabili"
def generate():
    client = genai.Client(
        api_key="AIzaSyDaSlzqmRUZ2Bt2TTywhgccewlq1OAtGJc"
  )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Generami una domanda per uno studente sull'argomento {argomento} e 4 risposte e l'indice della risposta corretta"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=genai.types.Schema(
                        type = genai.types.Type.OBJECT,
                        required = ["Domanda", "Risposta", "Indice_Corretto"],
                        properties = {
                            "Domanda": genai.types.Schema(
                                type = genai.types.Type.STRING,
                            ),
                            "Risposta": genai.types.Schema(
                                type = genai.types.Type.ARRAY,
                                items = genai.types.Schema(
                                    type = genai.types.Type.STRING,
                                ),
                            ),
                            "Indice_Corretto": genai.types.Schema(
                                type = genai.types.Type.INTEGER,
                            ),
                        },
                    ),
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
