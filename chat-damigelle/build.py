# Inserisce la foto (base64) nel template e produce chat_animata.html
import base64, pathlib
d = pathlib.Path(__file__).parent
img = "data:image/jpeg;base64," + base64.b64encode((d / "foto_sposa.jpg").read_bytes()).decode()
(d / "chat_animata.html").write_text((d / "template.html").read_text().replace("__IMG__", img))
