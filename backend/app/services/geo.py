# Бизнес-логика: проверка попадания в радиус геопозиции (HTML5 Geolocation API / navigator.geolocation).
import math

def check_proximity(lat1: float, lon1: float, lat2: float, lon2: float, radius_meters: int) -> bool:
    """
    Проверяет, находится ли игрок в пределах заданного радиуса от целевой точки.
    Использует формулу Гаверсинусов для вычисления расстояния на сфере.
    
    lat1, lon1 — текущие GPS-координаты игрока (со смартфона)
    lat2, lon2 — координаты цели (из базы данных, заданные автором квеста)
    radius_meters — радиус круга в метрах (например, 30 метров)
    """
    # Средний радиус Земли в метрах
    EARTH_RADIUS = 6371000.0

    # Переводим градусы координат в радианы, так как тригонометрические функции Python работают только с ними
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    # Вычисляем квадрат половины длины хорды между точками
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    
    # Вычисляем угловое расстояние в радианах
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    # Финальное расстояние между игроком и точкой в метрах
    distance = EARTH_RADIUS * c

    # Выводим расстояние в консоль бэкенда для удобной отладки в VS Code
    print(f"[GEO INFO] Дистанция до точки: {distance:.2f} метров. Требуемый радиус: {radius_meters}м.")

    # Если фактически вычисленное расстояние меньше или равно радиусу — возвращаем True
    return distance <= radius_meters
