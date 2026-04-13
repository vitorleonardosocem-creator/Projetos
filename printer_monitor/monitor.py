#!/usr/bin/env python3
"""
Printer Toner Monitor - Kyocera SNMP
Consulta impressoras via SNMP e envia alertas de email quando toner está abaixo do threshold.
"""
import json
import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Optional

from pysnmp.hlapi import (
    CommunityData, ContextData, ObjectIdentity, ObjectType,
    SnmpEngine, UdpTransportTarget, getCmd, nextCmd,
)

# ── OIDs Printer MIB (RFC 3805) ───────────────────────────────────────────────
OID_SYS_NAME         = '1.3.6.1.2.1.1.5.0'
OID_SUPPLY_DESC      = '1.3.6.1.2.1.43.11.1.1.6.1'   # prtMarkerSuppliesDescription
OID_SUPPLY_MAX_CAP   = '1.3.6.1.2.1.43.11.1.1.8.1'   # prtMarkerSuppliesMaxCapacity
OID_SUPPLY_CUR_LEVEL = '1.3.6.1.2.1.43.11.1.1.9.1'   # prtMarkerSuppliesCurrentLevel

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
STATE_FILE  = os.path.join(BASE_DIR, 'alert_state.json')

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'monitor.log'), encoding='utf-8'),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ── Config / State helpers ─────────────────────────────────────────────────────
def load_json(path: str, default=None):
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    return default if default is not None else {}


def save_json(path: str, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── SNMP helpers ───────────────────────────────────────────────────────────────
def snmp_get(ip: str, oid: str, community: str, timeout: int = 3) -> Optional[str]:
    error_indication, error_status, _, var_binds = next(
        getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, 161), timeout=timeout, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )
    )
    if error_indication or error_status:
        return None
    return str(var_binds[0][1])


def snmp_walk(ip: str, oid_prefix: str, community: str, timeout: int = 3) -> Dict:
    results = {}
    for error_indication, error_status, _, var_binds in nextCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=0),
        UdpTransportTarget((ip, 161), timeout=timeout, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(oid_prefix)),
        lexicographicMode=False,
    ):
        if error_indication or error_status:
            break
        for var_bind in var_binds:
            oid_str, value = var_bind
            results[str(oid_str)] = value
    return results


# ── Toner query ────────────────────────────────────────────────────────────────
def get_toner_levels(ip: str, community: str) -> List[Dict]:
    """
    Retorna lista de suprimentos de toner com percentual de nível.
    [{'name': 'Black Toner', 'level_pct': 42.0}, ...]
    """
    desc_data  = snmp_walk(ip, OID_SUPPLY_DESC,      community)
    max_data   = snmp_walk(ip, OID_SUPPLY_MAX_CAP,   community)
    level_data = snmp_walk(ip, OID_SUPPLY_CUR_LEVEL, community)

    # Palavras que indicam suprimentos que NÃO são toner (drums, waste box, etc.)
    EXCLUDE_KEYWORDS = ('waste', 'drum', 'belt', 'fuser', 'roller', 'filter', 'staple', 'torque', 'limiter', 'tray')

    supplies = []
    for full_oid, desc in desc_data.items():
        desc_str = str(desc).strip()
        desc_lower = desc_str.lower()

        # Ignora suprimentos que claramente não são toner
        if any(kw in desc_lower for kw in EXCLUDE_KEYWORDS):
            continue

        # Usa os dois últimos segmentos do OID como chave (device_idx.supply_idx)
        # Ex: 1.3.6.1.2.1.43.11.1.1.6.1.3 → idx = "1.3"
        parts = full_oid.split('.')
        idx = '.'.join(parts[-2:])

        max_val   = next((int(v) for k, v in max_data.items()   if k.endswith(f'.{idx}')), None)
        level_val = next((int(v) for k, v in level_data.items() if k.endswith(f'.{idx}')), None)

        if max_val is None or level_val is None:
            continue
        if max_val <= 0:
            continue  # -2 = capacidade desconhecida
        if level_val < 0:
            continue  # -3 = sem restrição / não reportado

        pct = round((level_val / max_val) * 100, 1)
        supplies.append({'name': desc_str, 'level_pct': pct})

    return supplies


# ── Email ──────────────────────────────────────────────────────────────────────
def send_alert_email(email_cfg: Dict, threshold: int, alerts: List[Dict]):
    count = len(alerts)
    subject = f"[ALERTA TONER] {count} Toner(s) abaixo de {threshold}%"

    lines = [
        f"O(s) seguinte(s) Toner(s) estão com nível abaixo de {threshold}%:",
        "",
    ]
    for a in alerts:
        lines += [
            f"  Impressora : {a['printer_name']} ({a['ip']})",
            f"  Toner : {a['supply_name']}",
            f"  Nível      : {a['level_pct']}%",
            "",
        ]
    lines.append(f"Verificação realizada em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")

    body = "\n".join(lines)

    msg = MIMEMultipart()
    msg['From']    = email_cfg['from']
    msg['To']      = ', '.join(email_cfg['to'])
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    with smtplib.SMTP(email_cfg['smtp_server'], email_cfg['smtp_port']) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(email_cfg['username'], email_cfg['password'])
        server.sendmail(email_cfg['from'], email_cfg['to'], msg.as_string())


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    config    = load_json(CONFIG_FILE)
    state     = load_json(STATE_FILE, default={})
    threshold = config.get('threshold_pct', 15)
    community = config.get('snmp_community', 'public')

    new_state  = {}
    new_alerts = []

    log.info("=== Início da verificação de toner ===")

    for printer in config['printers']:
        ip   = printer['ip']
        name = printer.get('name', ip)

        try:
            sys_name = snmp_get(ip, OID_SYS_NAME, community) or name
            supplies = get_toner_levels(ip, community)

            if not supplies:
                log.warning(f"{name} ({ip}): sem dados de toner via SNMP")
                continue

            for supply in supplies:
                key       = f"{ip}|{supply['name']}"
                level_pct = supply['level_pct']
                log.info(f"{sys_name} ({ip}) — {supply['name']}: {level_pct}%")

                if level_pct < threshold:
                    # Mantém flag de alerta enviado
                    already_alerted = state.get(key, {}).get('alerted', False)
                    new_state[key]  = {'alerted': True, 'level_pct': level_pct}

                    if not already_alerted:
                        log.warning(f"  >> ALERTA: {supply['name']} = {level_pct}% (abaixo de {threshold}%)")
                        new_alerts.append({
                            'ip':           ip,
                            'printer_name': sys_name,
                            'supply_name':  supply['name'],
                            'level_pct':    level_pct,
                        })
                    else:
                        log.info(f"  >> Alerta já enviado anteriormente, aguardando reposição.")
                else:
                    # Nível normalizado — reseta flag para permitir novo alerta futuro
                    new_state[key] = {'alerted': False, 'level_pct': level_pct}

        except Exception as exc:
            log.error(f"{name} ({ip}): erro ao consultar — {exc}")

    # ── Envia email agrupado ──────────────────────────────────────────────────
    if new_alerts:
        log.info(f"Enviando email com {len(new_alerts)} novo(s) alerta(s)...")
        try:
            send_alert_email(config['email'], threshold, new_alerts)
            log.info("Email enviado com sucesso.")
        except Exception as exc:
            log.error(f"Falha ao enviar email: {exc}")
    else:
        log.info("Nenhum novo alerta para enviar.")

    save_json(STATE_FILE, new_state)
    log.info("=== Verificação concluída ===\n")


if __name__ == '__main__':
    main()
