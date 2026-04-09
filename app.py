import token

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

def enviar_whatsapp_template_recordatorio(numero, nombre_cliente, nombre_barbero, hora, servicio):
    if not numero:
        return False

    numero = normalizar_numero_cr(numero)
    token = (os.getenv("WHATSAPP_TOKEN") or "").strip()
    phone_number_id = (os.getenv("PHONE_NUMBER_ID") or "").strip()

    if not token or not phone_number_id:
        print("Faltan WHATSAPP_TOKEN o PHONE_NUMBER_ID")
        return False

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "template",
        "template": {
            "name": "recordatorio_cita_30min_cr",
            "language": {
                "code": "es_CR"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(nombre_cliente)},
                        {"type": "text", "text": str(nombre_barbero)},
                        {"type": "text", "text": str(hora)},
                        {"type": "text", "text": str(servicio)}
                    ]
                }
            ]
        }
    }

    try:
        print("PAYLOAD RECORDATORIO:", data)
        r = requests.post(url, headers=headers, json=data, timeout=15)
        print("WHATSAPP RECORDATORIO STATUS:", r.status_code)
        print("WHATSAPP RECORDATORIO RESPUESTA:", r.text)
        return r.status_code < 400
    except Exception as e:
        print("Error enviando recordatorio:", e)
        return False

def enviar_template_whatsapp(numero, template_name, variables, language_code="es_CR"):
    if not numero:
        return False

    numero = normalizar_numero_cr(numero)
    token = (os.getenv("WHATSAPP_TOKEN") or "").strip()
    phone_number_id = (os.getenv("PHONE_NUMBER_ID") or "").strip()

    if not token or not phone_number_id:
        print("Faltan WHATSAPP_TOKEN o PHONE_NUMBER_ID")
        return False

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body_parameters = []
    for valor in variables:
        body_parameters.append({
            "type": "text",
            "text": str(valor)
        })

    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code
            },
            "components": [
                {
                    "type": "body",
                    "parameters": body_parameters
                }
            ]
        }
    }

    try:
        print("Payload enviado a WhatsApp:", data)
        r = requests.post(url, headers=headers, json=data, timeout=15)
        print("WhatsApp template status:", r.status_code, r.text)
        return r.status_code < 400
    except Exception as e:
        print("Error enviando template WhatsApp:", e)
        return False

def enviar_whatsapp_template_barbero(numero, cliente, whatsapp_cliente, servicio, fecha, hora):
    if not numero:
        return False

    numero = normalizar_numero_cr(numero)
    token = (os.getenv("WHATSAPP_TOKEN") or "").strip()
    phone_number_id = (os.getenv("PHONE_NUMBER_ID") or "").strip()

    if not token or not phone_number_id:
        print("Faltan WHATSAPP_TOKEN o PHONE_NUMBER_ID")
        return False

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "template",
        "template": {
            "name": "nueva_cita_barbero",
            "language": {
                "code": "es_CR"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(cliente)},
                        {"type": "text", "text": str(whatsapp_cliente)},
                        {"type": "text", "text": str(servicio)},
                        {"type": "text", "text": str(fecha)},
                        {"type": "text", "text": str(hora)}
                    ]
                }
            ]
        }
    }

    try:
        print("PAYLOAD BARBERO:", data)
        r = requests.post(url, headers=headers, json=data, timeout=15)
        print("WHATSAPP BARBERO STATUS:", r.status_code)
        print("WHATSAPP BARBERO RESPUESTA:", r.text)
        return r.status_code < 400
    except Exception as e:
        print("Error enviando template al barbero:", e)
        return False        

def normalizar_numero_cr(numero):
    numero = str(numero).replace("+", "").replace(" ", "").replace("-", "").strip()

    if numero.startswith("506") and len(numero) == 11:
        return numero

    if len(numero) == 8:
        return f"506{numero}"

    return numero

def enviar_whatsapp_template_confirmacion(numero, nombre_cliente, nombre_barbero, servicio, fecha, hora):
    if not numero:
        return False

    numero = normalizar_numero_cr(numero)
    token = (os.getenv("WHATSAPP_TOKEN") or "").strip()
    phone_number_id = (os.getenv("PHONE_NUMBER_ID") or "").strip()

    if not token or not phone_number_id:
        print("Faltan WHATSAPP_TOKEN o PHONE_NUMBER_ID")
        return False

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "template",
        "template": {
            "name": "confirmacion_cita",
            "language": {
                "code": "es_CR"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(nombre_cliente)},
                        {"type": "text", "text": str(servicio)},
                        {"type": "text", "text": str(fecha)},
                        {"type": "text", "text": str(hora)},
                        {"type": "text", "text": str(nombre_barbero)}
                    ]
                }
            ]
        }
    }

    try:
        print("Payload confirmacion:", data)
        r = requests.post(url, headers=headers, json=data, timeout=15)
        print("WhatsApp confirmacion status:", r.status_code, r.text)
        return r.status_code < 400
    except Exception as e:
        print("Error enviando template confirmacion:", e)
        return False

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def cambiar_estado_cita(cita_id, nuevo_estado):
    return supabase_request(
        "PATCH",
        "citas",
        params={"id": f"eq.{cita_id}"},
        json_body={"estado": nuevo_estado},
        extra_headers={"Prefer": "return=minimal"}
    )

def formatear_hora_12h(hora_str):
    try:
        return datetime.strptime(str(hora_str), "%H:%M:%S").strftime("%I:%M %p")
    except:
        return str(hora_str)
    
def formatear_fecha_es(fecha_str):
    try:
        dt = datetime.strptime(fecha_str, "%Y-%m-%d")

        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

        return f"{dias[dt.weekday()]} {dt.day} de {meses[dt.month - 1]} del {dt.year}"
    except Exception:
        return fecha_str    
    

def enviar_whatsapp_template_barbero(numero, cliente, whatsapp_cliente, servicio, fecha, hora):
    if not numero:
        return False

    numero = normalizar_numero_cr(numero)
    token = (os.getenv("WHATSAPP_TOKEN") or "").strip()
    phone_number_id = (os.getenv("PHONE_NUMBER_ID") or "").strip()

    if not token or not phone_number_id:
        print("Faltan WHATSAPP_TOKEN o PHONE_NUMBER_ID")
        return False

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "template",
        "template": {
            "name": "nueva_cita_barbero",
            "language": {
                "code": "es_CR"
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": str(cliente)},
                        {"type": "text", "text": str(whatsapp_cliente)},
                        {"type": "text", "text": str(servicio)},
                        {"type": "text", "text": str(fecha)},
                        {"type": "text", "text": str(hora)}
                    ]
                }
            ]
        }
    }

    try:
        print("PAYLOAD BARBERO:", data)
        r = requests.post(url, headers=headers, json=data, timeout=15)
        print("WHATSAPP BARBERO STATUS:", r.status_code)
        print("WHATSAPP BARBERO RESPUESTA:", r.text)
        return r.status_code < 400
    except Exception as e:
        print("Error enviando template al barbero:", e)
        return False    

def enviar_whatsapp(numero, mensaje):
    if not numero:
        return False

    numero = normalizar_numero_cr(numero)
    token = (os.getenv("WHATSAPP_TOKEN") or "").strip()
    phone_number_id = (os.getenv("PHONE_NUMBER_ID") or "").strip()

    if not token or not phone_number_id:
        print("Faltan WHATSAPP_TOKEN o PHONE_NUMBER_ID")
        return False

    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": mensaje}
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        print("WhatsApp status:", r.status_code, r.text)
        return r.status_code < 400
    except Exception as e:
        print("Error enviando WhatsApp:", e)
        return False


def obtener_barbero_por_id(barbero_id):
    data = supabase_request(
        "GET",
        "barberos",
        params={
            "select": "id,nombre,slug,telefono,activo",
            "id": f"eq.{barbero_id}",
            "limit": "1"
        }
    )
    if data and len(data) > 0:
        return data[0]
    return None


def obtener_nombre_barbero_desde_relacion(cita):
    rel = cita.get("barberos")
    if isinstance(rel, list) and rel:
        return rel[0].get("nombre", "")
    if isinstance(rel, dict):
        return rel.get("nombre", "")
    return ""    

def obtener_citas_con_barbero():
    data = supabase_request(
        "GET",
        "citas",
        params={
            "select": "id,cliente,cliente_id,servicio,precio,fecha,hora,duracion,estado,barbero_id,barberos(nombre)",
            "order": "fecha.asc,hora.asc"
        }
    )
    return data or []

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
            "select": "id,nombre,slug,telefono,activo",
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
        "estado": "activa",
        "recordatorio_30_enviado": False,
        "fecha_recordatorio_30": None
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


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    verify_token = os.getenv("VERIFY_TOKEN")

    if mode == "subscribe" and token == verify_token:
        return challenge, 200
    return "Token inválido", 403


@app.route("/webhook", methods=["POST"])
def recibir_webhook():
    data = request.get_json(silent=True)
    print("WEBHOOK RECIBIDO:", data)
    return "EVENT_RECEIVED", 200

@app.route("/guardar", methods=["POST"])
def guardar():
    cliente = request.form.get("cliente", "").strip()
    telefono = normalizar_numero_cr(request.form.get("telefono_cliente", ""))
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

    barbero = obtener_barbero_por_id(barbero_id)
    nombre_barbero = barbero["nombre"] if barbero else "tu barbero"
    telefono_barbero = barbero["telefono"] if barbero else None
    fecha_bonita = formatear_fecha_es(fecha)

    # Cliente -> template aprobado en Meta
    
    enviar_whatsapp_template_confirmacion(
    numero=telefono,
    nombre_cliente=cliente,
    nombre_barbero=nombre_barbero,
    servicio=servicio,
    fecha=fecha_bonita,
    hora=hora_12h
)

    # Barbero -> template aprobado en Meta
    if telefono_barbero:
        enviar_whatsapp_template_barbero(
            numero=telefono_barbero,
            cliente=cliente,
            whatsapp_cliente=telefono[-8:] if len(telefono) >= 8 else telefono,
            servicio=servicio,
            fecha=fecha_bonita,
            hora=hora_12h
        )

    print("Telefono cliente:", telefono)
    print("Telefono barbero:", telefono_barbero)
    print("Nombre barbero:", nombre_barbero)

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

@app.route("/panel")
def panel():
    citas_raw = obtener_citas_con_barbero()
    barberos = obtener_barberos_activos()

    citas = []
    total_citas = 0
    total_activas = 0
    total_canceladas = 0
    total_atendidas = 0
    total_cobrado = 0

    for c in citas_raw:
        nombre_barbero = obtener_nombre_barbero_desde_relacion(c)
        estado = (c.get("estado") or "activa").lower()
        precio = int(c.get("precio") or 0)

        cita = {
            "id": c.get("id"),
            "cliente": c.get("cliente"),
            "cliente_id": c.get("cliente_id"),
            "servicio": c.get("servicio"),
            "precio": precio,
            "fecha": c.get("fecha"),
            "hora": formatear_hora_12h(c.get("hora")),
            "duracion": c.get("duracion"),
            "estado": estado,
            "barbero_id": c.get("barbero_id"),
            "barbero_nombre": nombre_barbero
        }
        citas.append(cita)

        total_citas += 1
        if estado == "activa":
            total_activas += 1
        elif estado == "cancelada":
            total_canceladas += 1
        elif estado == "atendida":
            total_atendidas += 1
            total_cobrado += precio

    stats = {
        "total_citas": total_citas,
        "total_activas": total_activas,
        "total_canceladas": total_canceladas,
        "total_atendidas": total_atendidas,
        "total_cobrado": total_cobrado
    }

    return render_template("panel.html", citas=citas, barberos=barberos, stats=stats)

@app.route("/panel/<slug_barbero>")
def panel_barbero(slug_barbero):
    citas_raw = obtener_citas_con_barbero()
    barberos = obtener_barberos_activos()

    barbero_obj = None
    for b in barberos:
        if b.get("slug") == slug_barbero:
            barbero_obj = b
            break

    if not barbero_obj:
        return "Barbero no encontrado", 404

    citas = []
    total_citas = 0
    total_activas = 0
    total_canceladas = 0
    total_atendidas = 0
    total_cobrado = 0

    for c in citas_raw:
        if int(c.get("barbero_id")) != int(barbero_obj["id"]):
            continue

        estado = (c.get("estado") or "activa").lower()
        precio = int(c.get("precio") or 0)

        cita = {
            "id": c.get("id"),
            "cliente": c.get("cliente"),
            "cliente_id": c.get("cliente_id"),
            "servicio": c.get("servicio"),
            "precio": precio,
            "fecha": c.get("fecha"),
            "hora": formatear_hora_12h(c.get("hora")),
            "duracion": c.get("duracion"),
            "estado": estado,
            "barbero_id": c.get("barbero_id"),
            "barbero_nombre": barbero_obj["nombre"]
        }
        citas.append(cita)

        total_citas += 1
        if estado == "activa":
            total_activas += 1
        elif estado == "cancelada":
            total_canceladas += 1
        elif estado == "atendida":
            total_atendidas += 1
            total_cobrado += precio

    stats = {
        "total_citas": total_citas,
        "total_activas": total_activas,
        "total_canceladas": total_canceladas,
        "total_atendidas": total_atendidas,
        "total_cobrado": total_cobrado,
        "nombre_barbero": barbero_obj["nombre"]
    }

    return render_template("panel_barbero.html", citas=citas, stats=stats, barbero=barbero_obj)

@app.route("/panel/cancelar", methods=["POST"])
def panel_cancelar():
    cita_id = request.form.get("id")
    if cita_id:
        cambiar_estado_cita(cita_id, "cancelada")
        flash("Cita cancelada correctamente.")
    return redirect(request.referrer or url_for("panel"))

@app.route("/panel/atendida", methods=["POST"])
def panel_atendida():
    cita_id = request.form.get("id")
    if cita_id:
        cambiar_estado_cita(cita_id, "atendida")
        flash("Cita marcada como atendida.")
    return redirect(request.referrer or url_for("panel"))

@app.route("/api/recordatorios", methods=["POST"])
def procesar_recordatorios():
    auth = request.headers.get("X-CRON-TOKEN")
    if auth != os.getenv("CRON_SECRET"):
        return jsonify({"error": "No autorizado"}), 401

    try:
        ahora = datetime.now(TZ)
        ventana_inicio = ahora + timedelta(minutes=25)
        ventana_fin = ahora + timedelta(minutes=35)

        hoy = ahora.strftime("%Y-%m-%d")

        data = supabase_request(
            "GET",
            "citas",
            params={
                "select": "id,cliente,cliente_id,hora,barbero_id,servicio,recordatorio_30_enviado,estado",
                "fecha": f"eq.{hoy}",
                "estado": "eq.activa",
                "recordatorio_30_enviado": "eq.false"
            }
        ) or []

        recordatorios_enviados = 0

        for cita in data:
            hora_str = cita.get("hora", "")
            try:
                hora_cita = datetime.strptime(hora_str, "%H:%M:%S").time()
                hora_cita_dt = datetime.combine(ahora.date(), hora_cita).replace(tzinfo=TZ)
            except Exception:
                continue

            if ventana_inicio <= hora_cita_dt <= ventana_fin:
                cliente_telefono = cita.get("cliente_id", "")
                if cliente_telefono:
                    barbero = obtener_barbero_por_id(cita.get("barbero_id"))
                    nombre_barbero = barbero["nombre"] if barbero else "tu barbero"
                    nombre_cliente = cita.get("cliente", "")
                    servicio = cita.get("servicio", "")
                    hora_formateada = formatear_hora_12h(hora_str)

                    enviado = enviar_whatsapp_template_recordatorio(
                        numero=cliente_telefono,
                        nombre_cliente=nombre_cliente,
                        nombre_barbero=nombre_barbero,
                        hora=hora_formateada,
                        servicio=servicio
                    )

                    if enviado:
                        cambiar_recordatorio = supabase_request(
                            "PATCH",
                            "citas",
                            params={"id": f"eq.{cita.get('id')}"},
                            json_body={
                                "recordatorio_30_enviado": True,
                                "fecha_recordatorio_30": datetime.now(TZ).isoformat()
                            },
                            extra_headers={"Prefer": "return=minimal"}
                        )
                        recordatorios_enviados += 1

        return jsonify({"success": True, "recordatorios_enviados": recordatorios_enviados})

    except Exception as e:
        print("Error procesando recordatorios:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)