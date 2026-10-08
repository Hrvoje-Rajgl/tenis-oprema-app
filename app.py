import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("Sustav za upravljanje teniskom opremom")
st.write("Aplikacija za vođenje i analizu inventara teniske opreme.")

conn = st.connection("gsheets", type=GSheetsConnection)
MOJ_SHEET_URL = "https://docs.google.com/spreadsheets/d/1lRvGJAYXRRt7merBh94LPFkxLgCN0wan101aoySDbOg/edit?usp=sharing"
prikaz_df = conn.read(spreadsheet=MOJ_SHEET_URL, ttl=0)
podaci = prikaz_df.to_dict(orient="records")

st.sidebar.header("Izbornik")
opcija = st.sidebar.radio(
    "Odaberite opciju:",
    ["Pregled i Filtriranje", "Dodaj novu opremu", "Obriši opremu", "Analiza i Rangiranje"]
)

if opcija == "Pregled i Filtriranje":
    st.header("Pregled teniske opreme u bazi")

    pretraga = st.text_input("Pretraži po nazivu ili modelu:").lower()

    sve_kategorije = ["Sve"]
    for red in podaci:
        kat = str(red.get("Kategorija", "")).strip()
        if kat and kat not in sve_kategorije:
            sve_kategorije.append(kat)

    odabrana_kategorija = st.selectbox("Filtriraj po kategoriji:", sve_kategorije)

    filtrirani_podaci = []
    for red in podaci:
        naziv = str(red.get("Naziv/Model", "")).lower()
        kategorija = str(red.get("Kategorija", "")).strip()

        uvjet_kategorija = (odabrana_kategorija == "Sve") or (kategorija == odabrana_kategorija)
        uvjet_pretraga = (pretraga == "") or (pretraga in naziv)

        if uvjet_kategorija and uvjet_pretraga:
            filtrirani_podaci.append(red)

    st.table(filtrirani_podaci)

elif opcija == "Dodaj novu opremu":
    st.header("Dodavanje nove opreme u bazu")

    with st.form("forma_za_unos"):
        novi_id = f"EQ-{101 + len(podaci)}"
        st.write(f"Automatski generiran ID: **{novi_id}**")

        naziv = st.text_input("Naziv / Model opreme:")
        brand = st.selectbox("Brand:", ["Wilson", "Babolat", "Head", "Yonex", "Ostalo"])
        kategorija = st.selectbox("Kategorija:", ["Reket", "Reket za djecu", "Stroj za špananje", "Loptice", "Dodatno"])
        cijena = st.number_input("Cijena (€):", min_value=0, value=50)
        stanje = st.number_input("Količina na stanju (kom.):", min_value=1, value=1)

        gumb_spremi = st.form_submit_button("Spremi novu opremu")

    if gumb_spremi:
        if naziv == "":
            st.error("Molimo unesite naziv opreme!")
        else:
            novi_zapis = {
                "ID": novi_id,
                "Naziv/Model": naziv,
                "Brand": brand,
                "Kategorija": kategorija,
                "Cijena(€)": cijena,
                "Na stanju kom.": stanje
            }

            podaci.append(novi_zapis)
            conn.update(spreadsheet=MOJ_SHEET_URL, data=podaci)
            st.success(f"Uspješno ste dodali opremu: **{naziv}**!")

elif opcija == "Obriši opremu":
    st.header("Brisanje opreme iz baze")

    lista_za_izbornik = []
    for red in podaci:
        lista_za_izbornik.append(f"{red.get('ID')} - {red.get('Naziv/Model')}")

    if len(lista_za_izbornik) == 0:
        st.info("Baza podataka je prazna.")
    else:
        odabrana_oprema = st.selectbox("Odaberite opremu za brisanje:", lista_za_izbornik)

        if st.button("Obriši odabranu opremu"):
            id_za_brisanje = odabrana_oprema.split(" - ")[0]
            novi_podaci = []
            for red in podaci:
                if str(red.get("ID")) != id_za_brisanje:
                    novi_podaci.append(red)
            
            conn.update(spreadsheet=MOJ_SHEET_URL, data=novi_podaci)
            st.success(f"Oprema s ID-om **{id_za_brisanje}** je uspješno obrisana!")

elif opcija == "Analiza i Rangiranje":
    st.header("Rangiranje opreme po cijeni")
    def uzmi_cijenu(zapis):
        try:
            return float(zapis.get("Cijena(€)", 0))
        except:
            return 0.0

    sortirani_podaci = sorted(podaci, key=uzmi_cijenu, reverse=True)

    st.subheader("Top 3 najskuplja artikla")
    st.table(sortirani_podaci[:3])
    st.subheader("Top 3 najjeftinija artikla")
    najjeftiniji = sorted(podaci, key=uzmi_cijenu, reverse=False)
    st.table(najjeftiniji[:3])