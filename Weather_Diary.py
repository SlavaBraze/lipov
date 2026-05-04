import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("950x600")

        # Файл для хранения данных
        self.data_file = "weather_data.json"
        self.records = []

        # Загрузка данных
        self.load_data()

        # Создание интерфейса
        self.create_widgets()

        # Обновление таблицы
        self.refresh_table()

        # Обновление статистики
        self.update_statistics()

    def create_widgets(self):
        # === Фрейм для ввода данных ===
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись о погоде", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)

        # Осадки
        ttk.Label(input_frame, text="Осадки:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.precipitation_var = tk.StringVar(value="нет")
        self.precipitation_combo = ttk.Combobox(input_frame, textvariable=self.precipitation_var, width=10)
        self.precipitation_combo['values'] = ('да', 'нет')
        self.precipitation_combo.grid(row=0, column=5, padx=5, pady=5)

        # Описание погоды
        ttk.Label(input_frame, text="Описание погоды:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.description_entry = ttk.Entry(input_frame, width=50)
        self.description_entry.grid(row=1, column=1, columnspan=5, padx=5, pady=5, sticky="ew")

        # Кнопка добавления
        ttk.Button(input_frame, text="Добавить запись", command=self.add_record).grid(row=1, column=6, padx=10, pady=5)

        # === Фрейм для фильтрации ===
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация записей", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.filter_date_entry.bind('<KeyRelease>', self.on_filter_change)

        ttk.Label(filter_frame, text="Температура выше:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)
        self.filter_temp_entry.bind('<KeyRelease>', self.on_filter_change)

        ttk.Label(filter_frame, text="°C").grid(row=0, column=4, padx=0, pady=5, sticky="w")

        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters).grid(row=0, column=5, padx=10,
                                                                                           pady=5)

        # === Таблица с записями ===
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Скроллбары
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")

        self.tree = ttk.Treeview(table_frame, columns=("id", "date", "temperature", "precipitation", "description"),
                                 show="headings", yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Настройка заголовков
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("precipitation", text="Осадки")
        self.tree.heading("description", text="Описание погоды")

        # Настройка ширины колонок
        self.tree.column("id", width=50)
        self.tree.column("date", width=120)
        self.tree.column("temperature", width=100)
        self.tree.column("precipitation", width=80)
        self.tree.column("description", width=450)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        # === Статистика ===
        stats_frame = ttk.LabelFrame(self.root, text="Статистика", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=5)

        self.stats_labels = {}
        stats = ["total_records", "avg_temperature", "max_temperature", "min_temperature", "rainy_days"]
        stat_names = ["Всего записей", "Средняя температура", "Макс. температура", "Мин. температура",
                      "Дней с осадками"]

        for i, (stat, name) in enumerate(zip(stats, stat_names)):
            ttk.Label(stats_frame, text=f"{name}:").grid(row=i // 3, column=(i % 3) * 2, padx=5, pady=2, sticky="e")
            self.stats_labels[stat] = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
            self.stats_labels[stat].grid(row=i // 3, column=(i % 3) * 2 + 1, padx=5, pady=2, sticky="w")

        # === Кнопки управления ===
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(button_frame, text="Удалить выбранное", command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Сохранить в JSON", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Загрузить из JSON", command=self.load_data_dialog).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Обновить статистику", command=self.update_statistics).pack(side="left", padx=5)

    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_temperature(self, temp_str):
        """Проверка температуры"""
        try:
            temp = float(temp_str)
            return True
        except ValueError:
            return False

    def validate_description(self, description):
        """Проверка описания"""
        return description.strip() != ""

    def add_record(self):
        """Добавление новой записи"""
        date = self.date_entry.get().strip()
        temperature = self.temp_entry.get().strip()
        precipitation = self.precipitation_var.get()
        description = self.description_entry.get().strip()

        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты!\nИспользуйте формат: ГГГГ-ММ-ДД\nПример: 2026-05-15")
            return

        if not self.validate_temperature(temperature):
            messagebox.showerror("Ошибка", "Температура должна быть числом!\nПримеры: 25, -10, 15.5")
            return

        if not self.validate_description(description):
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым!\nОпишите погодные условия.")
            return

        temp_num = float(temperature)

        # Генерация ID
        new_id = max([r.get("id", 0) for r in self.records] + [0]) + 1

        new_record = {
            "id": new_id,
            "date": date,
            "temperature": temp_num,
            "precipitation": precipitation,
            "description": description
        }

        self.records.append(new_record)

        # Обновление интерфейса
        self.refresh_table()
        self.update_statistics()
        self.save_data()  # Автосохранение

        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.precipitation_var.set("нет")

        messagebox.showinfo("Успех", "Запись о погоде добавлена!")

    def get_filtered_records(self):
        """Получение отфильтрованных записей"""
        filtered = self.records.copy()

        # Фильтр по дате
        filter_date = self.filter_date_entry.get().strip()
        if filter_date:
            if self.validate_date(filter_date):
                filtered = [r for r in filtered if r["date"] == filter_date]

        # Фильтр по температуре (выше указанного значения)
        filter_temp = self.filter_temp_entry.get().strip()
        if filter_temp:
            try:
                temp_threshold = float(filter_temp)
                filtered = [r for r in filtered if r["temperature"] > temp_threshold]
            except ValueError:
                pass  # Игнорируем некорректный ввод

        return filtered

    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Добавление отфильтрованных записей
        for record in self.get_filtered_records():
            # Добавляем смайлик для температуры
            temp_display = f"{record['temperature']}°C"
            if record['temperature'] > 25:
                temp_display += " ☀️"
            elif record['temperature'] < 0:
                temp_display += " ❄️"

            # Отображаем осадки со смайликом
            precip_display = "Да 🌧️" if record['precipitation'] == 'да' else "Нет ☀️"

            self.tree.insert("", "end", values=(
                record.get("id", ""),
                record["date"],
                temp_display,
                precip_display,
                record["description"]
            ))

    def update_statistics(self):
        """Обновление статистики"""
        if not self.records:
            for key in self.stats_labels:
                self.stats_labels[key].config(text="0")
            return

        total_records = len(self.records)
        temperatures = [r["temperature"] for r in self.records]
        avg_temp = sum(temperatures) / len(temperatures) if temperatures else 0
        max_temp = max(temperatures) if temperatures else 0
        min_temp = min(temperatures) if temperatures else 0
        rainy_days = len([r for r in self.records if r["precipitation"] == "да"])

        stats_data = {
            "total_records": total_records,
            "avg_temperature": round(avg_temp, 1),
            "max_temperature": max_temp,
            "min_temperature": min_temp,
            "rainy_days": rainy_days
        }

        for key, value in stats_data.items():
            if key in self.stats_labels:
                # Добавляем °C для температур
                if key in ["avg_temperature", "max_temperature", "min_temperature"]:
                    self.stats_labels[key].config(text=f"{value}°C")
                else:
                    self.stats_labels[key].config(text=str(value))

    def on_filter_change(self, event=None):
        """Обработчик изменения фильтров"""
        self.refresh_table()

    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.refresh_table()

    def delete_selected(self):
        """Удаление выбранных записей"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return

        if messagebox.askyesno("Подтверждение", f"Удалить выбранные записи ({len(selected)} шт.)?"):
            # Получаем текущие отфильтрованные данные
            filtered = self.get_filtered_records()

            # Создаем список ID для удаления
            indices_to_delete = [self.tree.index(item) for item in selected]
            ids_to_delete = [filtered[i].get("id") for i in indices_to_delete]

            # Удаляем из оригинального списка
            self.records = [r for r in self.records if r.get("id") not in ids_to_delete]

            self.refresh_table()
            self.update_statistics()
            self.save_data()

            messagebox.showinfo("Успех", "Записи удалены")

    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            # Обновляем статистику
            self.update_statistics()

            # Подготавливаем данные для сохранения
            data_to_save = {
                "records": self.records,
                "metadata": {
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_records": len(self.records)
                }
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Успех", f"Данные сохранены в файл {self.data_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = data.get("records", [])
                    print(f"Загружено {len(self.records)} записей")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.records = []
        else:
            self.records = []

    def load_data_dialog(self):
        """Диалог загрузки данных"""
        self.load_data()
        self.refresh_table()
        self.update_statistics()
        messagebox.showinfo("Успех", f"Загружено {len(self.records)} записей")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
