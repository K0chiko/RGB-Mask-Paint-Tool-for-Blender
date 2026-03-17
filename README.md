# RGB Mask Paint Tool for Blender

[English](#english) | [Русский](#russian)

---

## English <a name="english"></a>

**RGB Mask Paint Tool** is a Blender add-on designed to streamline the setup of complex RGB-mask-based shaders. It automates the process of creating layered materials, configuring UV maps, and managing texture sets.

### Key Features
* **One-Click Setup:** Automatically creates required UV layers (`UV0_Base`, `UV1_Tiled`).
* **Shader Import:** Instantly appends the predefined "Layered_Mat" from the bundled `.blend` library.
* **Smart Texture Loading:** Supports linked texture pairs (Albedo `_a` and Normal `_n`). Selecting an Albedo map automatically loads the corresponding Normal map.
* **Normal Inversion:** Toggle the Green (G) channel for Normal maps (DirectX/OpenGL) directly from the UI.
* **Tiling Control:** Separate Scale controls for the Base layer and each of the four tiled layers.
* **Mask Generation:** Automatic creation of a 2048x2048 texture for mask painting, following the `Mask_ObjectName` naming convention.

### Installation
1. Download the latest `rgb_mask_tools.zip` from the **Releases** section.
2. In Blender, navigate to `Edit > Preferences > Add-ons`.
3. Click `Install...` and select the downloaded archive.
4. Enable the **"Material: RGB Mask Tools"** add-on.

### Usage
1. Open the **Properties** window and go to the **Material** tab.
2. Locate the **RGB Mask Tools** panel.
3. Click **"Подготовить модель к рисованию"** to initialize the UV layers and append the shader.
4. Click **"Создать RGB маску"** to generate the painting canvas.
5. Load texture sets into layers 0–3 and adjust the tiling parameters.

---

## Русский <a name="russian"></a>

**RGB Mask Paint Tool** — это аддон для Blender, предназначенный для оптимизации настройки шейдеров на основе RGB-масок. Инструмент автоматизирует создание слоистых материалов, настройку UV-координат и управление текстурными сетами.

### Основные функции
* **Быстрая настройка:** Автоматическое создание необходимых UV-слоев (`UV0_Base`, `UV1_Tiled`).
* **Импорт шейдера:** Добавление настроенного материала "Layered_Mat" из встроенной библиотеки `.blend`.
* **Умная загрузка текстур:** Поддержка связанных пар (Albedo `_a` и Normal `_n`). При выборе базового цвета аддон автоматически подгружает карту нормалей.
* **Инверсия нормалей:** Переключение зеленого канала (G) для корректного отображения нормалей (DirectX/OpenGL) через интерфейс панели.
* **Управление тайлингом:** Раздельный контроль масштаба для базового слоя и каждого из четырех дополнительных слоев.
* **Генерация маски:** Создание текстуры 2048x2048 для рисования масок с автоматическим именем `Mask_ИмяОбъекта`.

### Установка
1. Загрузите актуальную версию `rgb_mask_tools.zip` из раздела **Releases**.
2. В Blender перейдите в `Правка > Настройки > Аддоны`.
3. Нажмите `Установить...` и выберите скачанный архив.
4. Активируйте аддон **"Material: RGB Mask Tools"**.

### Использование
1. Перейдите во вкладку **Материал** в окне свойств.
2. Найдите панель **RGB Mask Tools**.
3. Нажмите **"Подготовить модель к рисованию"** для настройки UV и подготовки материала.
4. Нажмите **"Создать RGB маску"** для создания текстуры под рисование.
5. Загрузите текстурные сеты и настройте масштаб слоев.

---

### Requirements / Требования
* **Blender:** 4.2.0+
* **Author:** Aleksandr Panichevskii
* **Version:** 1.0