# Inserisce foto e immagini profilo (base64) nel template e produce chat_animata.html
import base64, pathlib
d = pathlib.Path(__file__).parent
uri = lambda f: "data:image/jpeg;base64," + base64.b64encode((d / f).read_bytes()).decode()
s = (d / "template.html").read_text()
for key, f in {"__IMG__": "foto_sposa.jpg", "__AV_GROUP__": "profili/gruppo.jpg", "__AV_Martina__": "profili/martina.jpg",
               "__AV_Chiara__": "profili/chiara.jpg", "__AV_Federica__": "profili/federica.jpg"}.items():
    s = s.replace(key, uri(f))
(d / "chat_animata.html").write_text(s)
