import folium

# Создаем карту с начальной точкой
m = folium.Map(location=[55.751244, 37.618423], zoom_start=10)  # Москва

# Список точек с координатами и названиями
locations = [
    (55.751244, 37.618423, "Красная площадь"),
    (55.758611, 37.620556, "Большой театр"),
    (55.765835, 37.605636, "Парк Зарядье"),
]

# Добавляем маркеры на карту
for lat, lon, name in locations:
    folium.Marker([lat, lon], popup=name).add_to(m)

# Сохраняем карту в HTML-файл
m.save("map.html")

print("Карта сохранена в файл map.html")