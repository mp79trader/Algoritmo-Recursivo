"""
Script para sincronizar data_source_config.json entre raíz y frontend
Se ejecuta automáticamente cuando se modifica el archivo
"""
import os
import shutil
import json
from pathlib import Path

def sync_config():
    """Sincroniza el archivo de configuración entre raíz y frontend"""
    root_config = Path(__file__).parent / 'data_source_config.json'
    frontend_config = Path(__file__).parent / 'frontend' / 'data_source_config.json'
    
    # Verificar que el archivo raíz existe
    if not root_config.exists():
        print(f"❌ Error: {root_config} no existe")
        return False
    
    # Validar que es un JSON válido
    try:
        with open(root_config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        print(f"✅ Configuración válida en {root_config}")
    except json.JSONDecodeError as e:
        print(f"❌ Error: JSON inválido en {root_config}: {e}")
        return False
    
    # Copiar al frontend
    try:
        shutil.copy2(root_config, frontend_config)
        print(f"✅ Configuración sincronizada: {root_config} → {frontend_config}")
        
        # Mostrar configuración actual
        print(f"\n📋 Configuración actual:")
        print(f"   Fuente en tiempo real: {config_data.get('realtime_source', 'N/A')}")
        print(f"   Fuente histórica: {config_data.get('historical_source', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ Error al copiar: {e}")
        return False

if __name__ == '__main__':
    print("🔄 Sincronizando configuración de fuentes de datos...\n")
    success = sync_config()
    
    if success:
        print("\n✅ Sincronización completada exitosamente")
    else:
        print("\n❌ Sincronización fallida")
        exit(1)
