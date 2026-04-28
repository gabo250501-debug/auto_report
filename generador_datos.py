import csv
import random
from datetime import datetime, timedelta

equipos = {
    'Motor_Principal': {'consumo_base': 450, 'horas_base': 22, 'prob_falla': 0.05},
    'Compresor_A': {'consumo_base': 320, 'horas_base': 18, 'prob_falla': 0.15},
    'Bomba_Agua': {'consumo_base': 150, 'horas_base': 24, 'prob_falla': 0.02},
    'Ventilador_Norte': {'consumo_base': 110, 'horas_base': 24, 'prob_falla': 0.01},
    'Generador_Respaldo': {'consumo_base': 85, 'horas_base': 4, 'prob_falla': 0.10},
    'Banda_Transportadora': {'consumo_base': 210, 'horas_base': 16, 'prob_falla': 0.08}
}

fecha_inicio = datetime(2026, 4, 1)
dias = 730 # Mes y medio de datos

with open('datos_proyecto.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Fecha', 'Equipo', 'Consumo_kWh', 'Horas_Operativas', 'Fallas_Detectadas'])
    
    for dia in range(dias):
        fecha_actual = fecha_inicio + timedelta(days=dia)
        fecha_str = fecha_actual.strftime('%Y-%m-%d')
        
        for equipo, params in equipos.items():
            # Variaciones aleatorias
            consumo = max(0, int(random.normalvariate(params['consumo_base'], params['consumo_base'] * 0.1)))
            horas = min(24, max(0, int(random.normalvariate(params['horas_base'], 2))))
            
            # Generar fallas basadas en la probabilidad
            fallas = 0
            if random.random() < params['prob_falla']:
                fallas = random.randint(1, 3)
                
            writer.writerow([fecha_str, equipo, consumo, horas, fallas])

print("Datos generados exitosamente.")
