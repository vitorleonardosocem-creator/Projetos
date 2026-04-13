#!/usr/bin/env python3
"""
Script de diagnóstico SNMP — testa uma impressora e mostra o que está disponível.
Uso: python debug_snmp.py <IP> [community]
"""
import sys
from pysnmp.hlapi import (
    CommunityData, ContextData, ObjectIdentity, ObjectType,
    SnmpEngine, UdpTransportTarget, getCmd, nextCmd,
)

IP        = sys.argv[1] if len(sys.argv) > 1 else '192.168.14.212'
COMMUNITY = sys.argv[2] if len(sys.argv) > 2 else 'public'

def snmp_get(oid):
    err_ind, err_st, _, var_binds = next(
        getCmd(
            SnmpEngine(),
            CommunityData(COMMUNITY, mpModel=0),
            UdpTransportTarget((IP, 161), timeout=3, retries=1),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )
    )
    if err_ind:
        return f"ERRO: {err_ind}"
    if err_st:
        return f"ERRO SNMP: {err_st}"
    return str(var_binds[0][1])

def snmp_walk(oid_prefix, max_rows=30):
    results = {}
    count = 0
    for err_ind, err_st, _, var_binds in nextCmd(
        SnmpEngine(),
        CommunityData(COMMUNITY, mpModel=0),
        UdpTransportTarget((IP, 161), timeout=3, retries=1),
        ContextData(),
        ObjectType(ObjectIdentity(oid_prefix)),
        lexicographicMode=False,
    ):
        if err_ind or err_st:
            break
        for vb in var_binds:
            results[str(vb[0])] = str(vb[1])
            count += 1
            if count >= max_rows:
                return results
    return results

print(f"\n{'='*60}")
print(f"  DIAGNÓSTICO SNMP — {IP}  (community: '{COMMUNITY}')")
print(f"{'='*60}\n")

# ── 1. Conectividade básica ────────────────────────────────────────────────────
print("[ 1 ] Conectividade básica")
print(f"  sysDescr  : {snmp_get('1.3.6.1.2.1.1.1.0')}")
print(f"  sysName   : {snmp_get('1.3.6.1.2.1.1.5.0')}")
print(f"  sysContact: {snmp_get('1.3.6.1.2.1.1.4.0')}")

# ── 2. Tabela de suprimentos (Printer MIB) ────────────────────────────────────
print("\n[ 2 ] Tabela de suprimentos — prtMarkerSupplies (1.3.6.1.2.1.43.11)")
rows = snmp_walk('1.3.6.1.2.1.43.11', max_rows=50)
if rows:
    for oid, val in rows.items():
        print(f"  {oid} = {val}")
else:
    print("  !! Sem resposta para este OID")

# ── 3. Printer MIB geral ──────────────────────────────────────────────────────
print("\n[ 3 ] Printer MIB geral (1.3.6.1.2.1.43) — primeiras 20 entradas")
rows2 = snmp_walk('1.3.6.1.2.1.43', max_rows=20)
if rows2:
    for oid, val in rows2.items():
        print(f"  {oid} = {val}")
else:
    print("  !! Sem resposta para este OID")

# ── 4. OIDs Kyocera específicos ───────────────────────────────────────────────
print("\n[ 4 ] OIDs Kyocera (1.3.6.1.4.1.1347) — primeiras 20 entradas")
rows3 = snmp_walk('1.3.6.1.4.1.1347', max_rows=20)
if rows3:
    for oid, val in rows3.items():
        print(f"  {oid} = {val}")
else:
    print("  !! Sem resposta para este OID")

print(f"\n{'='*60}\n")
