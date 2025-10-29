#!/usr/bin/env python3
"""
Script para corregir automáticamente errores comunes de linting
"""
import os
import re

def fix_python_files():
    """Corregir errores comunes en archivos Python"""
    print("🔧 Corrigiendo errores de linting...")
    
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                fix_file(filepath)
    
    print("✅ Correcciones aplicadas")

def fix_file(filepath):
    """Corregir un archivo específico"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Reemplazar comillas simples por dobles (excepto en docstrings)
        content = re.sub(r'(?<!\\)\"(.*?)(?<!\\)\"', r"'\1'", content)  # Temporal
        content = re.sub(r"(?<!\\)'(.*?)(?<!\\)'", r'"\1"', content)
        
        # 2. Eliminar espacios en blanco al final de línea
        content = "\n".join(line.rstrip() for line in content.split("\n"))
        
        # 3. Asegurar 2 líneas en blanco al final del archivo
        content = content.rstrip() + "\n\n"
        
        # 4. Dividir líneas muy largas (simplificado)
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if len(line) > 88 and "(" in line and ")" in line:
                # Intentar dividir llamadas largas
                line = re.sub(r'\.(\w+)\(', r'.\n    \1(', line)
            new_lines.append(line)
        content = "\n".join(new_lines)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ Corregido: {filepath}")
        
    except Exception as e:
        print(f"❌ Error en {filepath}: {e}")

if __name__ == "__main__":
    fix_python_files()