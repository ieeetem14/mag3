import streamlit as st 

# --- Konfiguracja Aplikacji ---
st.set_page_config(page_title="Prosty Magazyn", layout="wide")

## Nagłówek
st.title("📦 Prosty Magazyn Towarów")
st.markdown("Aplikacja przechowuje dane w pamięci sesji (bez zapisu do plików).")

# --- Inicjalizacja Stanu Magazynu ---

# Używamy st.session_state do przechowywania listy towarów.
# Jest to kluczowe dla utrzymania stanu aplikacji pomiędzy interakcjami.
if 'towary' not in st.session_state:
    st.session_state['towary'] = []
    # Przykładowe dane na start (opcjonalne)
    st.session_state['towary'].append({"nazwa": "Laptop Business X", "ilosc": 5, "cena": 4500.00})
    st.session_state['towary'].append({"nazwa": "Myszka Bezprzewodowa", "ilosc": 50, "cena": 89.99})


# --- Funkcje do Zarządzania Towarami ---

def dodaj_towar(nazwa, ilosc, cena):
    """Dodaje nowy towar do listy."""
    try:
        ilosc = int(ilosc)
        cena = float(cena)
        if ilosc <= 0:
            st.error("Ilość musi być liczbą całkowitą większą niż 0.")
            return
        if cena <= 0:
            st.error("Cena musi być liczbą większą niż 0.")
            return

        nowy_towar = {
            "nazwa": nazwa.strip(),
            "ilosc": ilosc,
            "cena": cena
        }
        st.session_state['towary'].append(nowy_towar)
        st.success(f"Dodano towar: **{nazwa}** (Ilość: {ilosc})")

    except ValueError:
        st.error("Wprowadzono niepoprawną wartość dla Ilości lub Ceny.")


def usun_towar(indeks):
    """Usuwa towar na podstawie jego indeksu na liście."""
    if 0 <= indeks < len(st.session_state['towary']):
        nazwa_usunietego = st.session_state['towary'][indeks]['nazwa']
        del st.session_state['towary'][indeks]
        st.info(f"Usunięto towar: **{nazwa_usunietego}**")


# --- Sekcja Dodawania Towaru ---

st.header("➕ Dodaj Nowy Towar")
with st.form("form_dodawania_towaru", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        nowa_nazwa = st.text_input("Nazwa Towaru", key="input_nazwa")
    with col2:
        nowa_ilosc = st.number_input("Ilość", min_value=1, value=1, step=1, key="input_ilosc")
    with col3:
        nowa_cena = st.number_input("Cena Jednostkowa (PLN)", min_value=0.01, value=1.00, step=0.01, format="%.2f", key="input_cena")

    przycisk_dodaj = st.form_submit_button("Zapisz Towar", type="primary")

    if przycisk_dodaj:
        if nowa_nazwa.strip():
            dodaj_towar(nowa_nazwa, nowa_ilosc, nowa_cena)
        else:
            st.error("Nazwa towaru nie może być pusta.")

st.divider()

# --- Sekcja Wyświetlania i Usuwania Towarów ---

st.header("📋 Lista Towarów w Magazynie")

if st.session_state['towary']:
    # Tworzenie danych do wyświetlenia w tabeli
    dane_do_tabeli = []
    for i, towar in enumerate(st.session_state['towary']):
        dane_do_tabeli.append({
            "Indeks": i + 1,
            "Nazwa Towaru": towar['nazwa'],
            "Ilość": towar['ilosc'],
            "Cena (PLN)": f"{towar['cena']:.2f}",
            "Wartość Całkowita (PLN)": f"{towar['ilosc'] * towar['cena']:.2f}",
            "Akcja": f"Usuń_{i}" # Unikalny klucz do przycisku
        })

    # Wyświetlanie danych za pomocą st.data_editor dla możliwości dodania przycisków
    tabela = st.data_editor(
        dane_do_tabeli,
        column_config={
            "Akcja": st.column_config.ButtonColumn(
                "Usuń",
                help="Kliknij, aby usunąć towar.",
                key="usun_przycisk",
                on_click=usun_towar,
                args=(st.session_state['usun_przycisk_clicked_index'],)
            )
        },
        hide_index=True,
        num_rows="fixed"
    )

    # Streamlit nie daje bezpośredniego dostępu do indeksu klikniętego przycisku w data_editor.
    # W praktyce w prostszych aplikacjach często używa się osobnej sekcji z comboboxem i przyciskiem do usuwania,
    # albo stosuje się workaround z kluczami. Powyższy kod z data_editor jest bardziej elegancki,
    # ale wymaga nieco "magii" z kluczami, aby Streamlit zareagował poprawnie
    # na kliknięcie w ButtonColumn.

    # Najprostsza, najpewniejsza i najmniej skomplikowana alternatywa:
    st.subheader("Usuwanie Towarów (Alternatywne)")
    towary_do_wyboru = [f"{i+1}. {t['nazwa']} (Ilość: {t['ilosc']})" for i, t in enumerate(st.session_state['towary'])]
    
    if towary_do_wyboru:
        indeks_do_usuniecia = st.selectbox(
            "Wybierz towar do usunięcia",
            options=range(len(st.session_state['towary'])),
            format_func=lambda x: towary_do_wyboru[x]
        )
        
        if st.button("Usuń Wybrany Towar", key="przycisk_usun_alternatywa"):
            usun_towar(indeks_do_usuniecia)
            # Wymuszenie ponownego załadowania interfejsu
            st.experimental_rerun()
            
else:
    st.info("Magazyn jest pusty. Dodaj pierwszy towar powyżej!")


# --- Podsumowanie ---
if st.session_state['towary']:
    suma_ilosci = sum(t['ilosc'] for t in st.session_state['towary'])
    suma_wartosci = sum(t['ilosc'] * t['cena'] for t in st.session_state['towary'])
    
    st.markdown("---")
    st.subheader("📊 Podsumowanie Magazynu")
    colA, colB, colC = st.columns(3)
    colA.metric("Liczba różnych towarów", len(st.session_state['towary']))
    colB.metric("Łączna ilość sztuk", suma_ilosci)
    colC.metric("Łączna wartość magazynu", f"{suma_wartosci:,.2f} PLN")
