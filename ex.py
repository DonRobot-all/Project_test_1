import webbrowser

# HTML-код с Яндекс.Картами
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Яндекс.Карта с метками</title>
    <script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU" type="text/javascript"></script>
    <script type="text/javascript">
        function init() {
            var myMap = new ymaps.Map("map", {
                center: [55.751244, 37.618423],
                zoom: 10
            });

            var locations = [
                [55.751244, 37.618423, "Красная площадь"],
                [55.758611, 37.620556, "Большой театр"],
                [55.765835, 37.605636, "Парк Зарядье"]
            ];

            locations.forEach(function (loc) {
                var placemark = new ymaps.Placemark([loc[0], loc[1]], {
                    balloonContent: loc[2]
                });
                myMap.geoObjects.add(placemark);
            });
        }

        ymaps.ready(init);
    </script>
</head>
<body>
    <div id="map" style="width: 100%; height: 500px;"></div>
</body>
</html>
"""

# Сохраняем в файл
file_path = "map_yandex.html"
with open(file_path, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"Карта сохранена в файл {file_path}")

# Открываем в браузере
webbrowser.open(file_path)
