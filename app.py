from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os
import requests

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")
TZ = ZoneInfo(os.getenv("TZ", "America/Costa_Rica"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TIMEOUT = 10

servicios = {
    "Corte Difuminado": 5000,
    "Corte y Barba": 7000,
    "Corte Clasico": 4500,
    "Cejas": 1500,
    "Marcado y Barba": 3500,
    "Corte Niño": 4500,
}

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def supabase_request(method, path, params=None, json_body=None, extra_headers=None):
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{path}"
    headers = supabase_headers()
    if extra_headers:
        headers.update(extra_headers)

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_body,
            timeout=SUPABASE_TIMEOUT
        )
        response.raise_for_status()
        if response.text:
            return response.json()
        return None
    except Exception as e:
        print("Error Supabase:", e)
        return None

def obtener_barberos_activos():
    data = supabase_request(
        "GET",
        "barberos",
        params={
            "select": "id,nombre,slug,activo",
            "activo": "eq.true",
            "order": "id.asc"
        }
    )
    return data or []

def obtener_citas_por_fecha_y_barbero(fecha, barbero_id):
    data = supabase_request(
        "GET",
        "citas",
        params={
            "select": "id,fecha,hora,duracion,estado",
            "fecha": f"eq.{fecha}",
            "barbero_id": f"eq.{barbero_id}",
            "estado": "neq.cancelada",
            "order": "hora.asc"
        }
    )
    return data or []

def crear_cita(cliente, cliente_id, barbero_id, servicio, precio, fecha, hora, duracion):
    body = {
        "cliente": cliente,
        "cliente_id": cliente_id,
        "barbero_id": int(barbero_id),
        "servicio": servicio,
        "precio": int(precio),
        "fecha": fecha,
        "hora": hora,
        "duracion": int(duracion),
        "estado": "activa"
    }

    return supabase_request(
        "POST",
        "citas",
        json_body=body,
        extra_headers={"Prefer": "return=representation"}
    )

@app.route("/")
def index():
    barberos = obtener_barberos_activos()
    hoy_iso = datetime.now(TZ).strftime("%Y-%m-%d")
    return render_template(
        "index.html",
        barberos=barberos,
        servicios=servicios,
        hoy_iso=hoy_iso
    )

@app.route("/guardar", methods=["POST"])
def guardar():
    cliente = request.form.get("cliente", "").strip()
    telefono = request.form.get("telefono_cliente", "").strip()
    servicio = request.form.get("servicio", "").strip()
    fecha = request.form.get("fecha", "").strip()
    hora_12h = request.form.get("hora", "").strip()
    barbero_id = request.form.get("barbero_id", "").strip()

    if not cliente or not telefono or not servicio or not fecha or not hora_12h or not barbero_id:
        flash("Completa todos los campos.")
        return redirect(url_for("index"))

    precio = servicios.get(servicio, 0)
    duracion = 60 if "barba" in servicio.lower() else 30

    try:
        hora_db = datetime.strptime(hora_12h, "%I:%M %p").strftime("%H:%M:%S")
    except ValueError:
        flash("Hora inválida.")
        return redirect(url_for("index"))

    cita = crear_cita(
        cliente=cliente,
        cliente_id=telefono,
        barbero_id=barbero_id,
        servicio=servicio,
        precio=precio,
        fecha=fecha,
        hora=hora_db,
        duracion=duracion
    )

    if not cita:
        flash("No se pudo guardar la cita.")
        return redirect(url_for("index"))

    flash("Cita creada correctamente.")
    return redirect(url_for("index"))

@app.route("/horas")
def horas():
    fecha_str = request.args.get("fecha")
    barbero_id = request.args.get("barbero_id")

    if not fecha_str or not barbero_id:
        return jsonify([])

    try:
        f_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        ahora = datetime.now(TZ)
        hoy = ahora.date()

        if f_obj < hoy:
            return jsonify([])

        dia_semana = f_obj.weekday()
        if dia_semana == 6:
            h_i, h_f = 9, 16
        elif dia_semana in [4, 5]:
            h_i, h_f = 8, 20
        else:
            h_i, h_f = 9, 20

        horas_base = []
        temp = datetime.combine(f_obj, datetime.min.time()).replace(hour=h_i, minute=0, second=0)
        fin = datetime.combine(f_obj, datetime.min.time()).replace(hour=h_f, minute=0, second=0)

        while temp < fin:
            horas_base.append(temp.strftime("%H:%M:%S"))
            temp += timedelta(minutes=30)

        citas = obtener_citas_por_fecha_y_barbero(fecha_str, barbero_id)
        ocupadas = set()

        for c in citas:
            h = str(c.get("hora", ""))
            ocupadas.add(h)
            if int(c.get("duracion", 30)) > 30:
                dt_h = datetime.strptime(h, "%H:%M:%S")
                ocupadas.add((dt_h + timedelta(minutes=30)).strftime("%H:%M:%S"))

        disponibles = []
        for h in horas_base:
            h_dt = datetime.strptime(h, "%H:%M:%S")
            cita_dt = datetime.combine(f_obj, h_dt.time()).replace(tzinfo=TZ)

            if f_obj == hoy and cita_dt <= (ahora + timedelta(minutes=30)):
                continue

            if h not in ocupadas:
                disponibles.append(h_dt.strftime("%I:%M %p"))

        return jsonify(disponibles)

    except Exception as e:
        print("Error en /horas:", e)
        return jsonify([])

@app.route("/test_barberos")
def test_barberos():
    return jsonify(obtener_barberos_activos())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)