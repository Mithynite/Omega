## Nastavení projektu na vlastním zařízení

- Poznámka: *Pokud není řečeno jinak, tak pracujeme stále ve stejné složce.*

1) **Stáhnout či naklonovat** projekt z tohoto GitHubu:
   příkaz: `git clone https://github.com/Mithynite/Omega.git`
3) Použít **terminál** (např. CMD) a dostat se do **složky s projektem**:
	příkaz: `cd cesta/k/projektu/WristWatcher`
4) Tvorba **virtuálního prostředí** `.venv`:
	příkaz: `python -m venv .venv`
5) Dále virtuální prostředí aktivujeme (pozor, je důležité zadat zpětná lomítka `\`):
	příkaz: `.venv\Scripts\activate`
6) Nyní naistalujeme potřebné knihovny z `requirements.txt`
	příkaz: `pip install -r requirements.txt` (může to chvíli trvat, v případě jakékoliv chyby neváhejte kontaktovat autora)
7) Následně přejdeme do složky `/app`
	příkaz: `cd app`
8) Zde spustíme aplikaci:
	příkaz: `python app.py`
9) Hotovo! Nyní by aplikace měla běžet na vašem zařízení (lokálně)
	Můžeme si otevřít libovolný Internetový prohlížeč a jít na adresu: http://127.0.0.1:5000
