#!/usr/bin/env python3
"""
OGLM Azimuth Trading Terminal
@fractal_whale Interface v0.1

Простой интерфейс для прогнозирования траектории OGLM через азимут (цифру).
"""

import json
import os
from datetime import datetime
from pathlib import Path


class AzimuthTrader:
    def __init__(self, data_file="azimuth_predictions.json"):
        self.data_file = Path(__file__).parent / data_file
        self.predictions = self.load_predictions()
        self.current_price = 1.0  # Базовая цена OGLM
        
    def load_predictions(self):
        """Загрузить историю прогнозов"""
        if self.data_file.exists():
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "predictions": [],
            "stats": {
                "total": 0,
                "correct": 0,
                "accuracy": 0.0
            }
        }
    
    def save_predictions(self):
        """Сохранить историю"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.predictions, f, indent=2, ensure_ascii=False)
    
    def print_header(self):
        """Красивый header"""
        print("\n" + "="*60)
        print("┌─────────────────────────────────────────────────────────┐")
        print("│  @fractal_whale Terminal v0.1                           │")
        print("│  OGLM Azimuth Trading Interface                         │")
        print("├─────────────────────────────────────────────────────────┤")
        print("│  Connected to Протон-А Semantic Grid                    │")
        print(f"│  Current OGLM: {self.current_price:.2f}                                      │")
        print("└─────────────────────────────────────────────────────────┘")
        print("="*60 + "\n")
    
    def print_stats(self):
        """Показать статистику"""
        stats = self.predictions["stats"]
        preds = self.predictions["predictions"]
        
        print("\n📊 Статистика @fractal_whale:")
        print(f"  Всего прогнозов: {stats['total']}")
        print(f"  Правильных: {stats['correct']}")
        print(f"  Точность: {stats['accuracy']:.1f}%")
        
        if preds:
            print("\n📈 Последние 5 прогнозов:")
            for pred in preds[-5:]:
                status = "✅" if pred.get("correct") else "⏳" if not pred.get("resolved") else "❌"
                print(f"  {status} {pred['timestamp']}: {pred['azimuth']:+.1f}% | {pred.get('note', '')}")
    
    def calculate_outcome(self, azimuth, days=7):
        """
        Симуляция результата на основе азимута
        В реальности это будет подключено к рынку
        """
        import random
        
        # Темная материя - добавляем случайность, но с корреляцией к азимуту
        market_noise = random.uniform(-10, 10)
        dark_matter = random.uniform(-5, 5)
        
        # Фрактальная корреляция: большие движения сложнее предсказать
        difficulty = abs(azimuth) / 100
        accuracy_modifier = 1.0 - (difficulty * 0.3)
        
        # Базовое движение с шумом
        actual = azimuth * accuracy_modifier + market_noise + dark_matter
        
        return actual
    
    def enter_prediction(self):
        """Основной цикл ввода прогноза"""
        print("\n🎯 Введите азимут (направление и величину движения OGLM)")
        print("   Примеры:")
        print("   • +50  → ожидается рост на 50%")
        print("   • -99  → зловещая долина, падение на 99%")
        print("   • +1000 → экспоненциальный рост 10x")
        print("   • 0    → стагнация")
        print("\n   Или команды:")
        print("   • 'stats' → показать статистику")
        print("   • 'history' → полная история")
        print("   • 'exit' → выход\n")
        
        azimuth_input = input("Азимут: ").strip()
        
        # Команды
        if azimuth_input.lower() == 'exit':
            return False
        elif azimuth_input.lower() == 'stats':
            self.print_stats()
            return True
        elif azimuth_input.lower() == 'history':
            self.show_full_history()
            return True
        
        # Парсинг азимута
        try:
            azimuth = float(azimuth_input)
        except ValueError:
            print("❌ Ошибка: Введите число (например: -99 или +50)")
            return True
        
        # Валидация
        if abs(azimuth) > 10000:
            print("⚠️  Предупреждение: Азимут > 10000% выглядит экстремально")
            confirm = input("   Продолжить? (y/n): ")
            if confirm.lower() != 'y':
                return True
        
        # Заметка (опционально)
        note = input("\n💭 Reasoning (опционально): ").strip()
        
        # Временной горизонт
        try:
            horizon_input = input("⏱️  Горизонт прогноза в днях (default: 7): ").strip()
            horizon = int(horizon_input) if horizon_input else 7
        except ValueError:
            horizon = 7
        
        # Создаём прогноз
        prediction = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "azimuth": azimuth,
            "note": note,
            "horizon_days": horizon,
            "entry_price": self.current_price,
            "target_price": self.current_price * (1 + azimuth/100),
            "resolved": False,
            "correct": None
        }
        
        # Симуляция (в реальности ждём horizon дней)
        print("\n🔮 Протон-А анализирует...")
        print("   • Фрактальная декомпозиция...")
        print("   • Детекция темной материи...")
        print("   • Квантовый расчёт вероятности...")
        
        actual = self.calculate_outcome(azimuth, horizon)
        prediction["actual_movement"] = actual
        
        # Оценка точности (±20% tolerance)
        tolerance = 20
        error = abs(actual - azimuth)
        correct = error <= tolerance
        
        prediction["resolved"] = True
        prediction["correct"] = correct
        prediction["error"] = error
        
        # Сохраняем
        self.predictions["predictions"].append(prediction)
        self.predictions["stats"]["total"] += 1
        if correct:
            self.predictions["stats"]["correct"] += 1
        self.predictions["stats"]["accuracy"] = (
            self.predictions["stats"]["correct"] / 
            self.predictions["stats"]["total"] * 100
        )
        
        self.save_predictions()
        
        # Результат
        print("\n" + "="*60)
        if correct:
            print("✅ ТОЧНЫЙ ПРОГНОЗ!")
        else:
            print("❌ Рынок пошёл иначе")
        
        print(f"\n📊 Результат:")
        print(f"   Ваш азимут: {azimuth:+.1f}%")
        print(f"   Фактически: {actual:+.1f}%")
        print(f"   Ошибка: {error:.1f}%")
        print(f"   Цена: {self.current_price:.2f} → {self.current_price * (1 + actual/100):.2f}")
        
        # Обновляем текущую цену
        self.current_price *= (1 + actual/100)
        
        # Анализ темной материи
        dark_matter_signal = actual - azimuth
        if abs(dark_matter_signal) > 10:
            print(f"\n🌑 Темная материя детектирована: {dark_matter_signal:+.1f}%")
            if dark_matter_signal > 0:
                print("   → Скрытые силы толкают вверх (накопление китов?)")
            else:
                print("   → Скрытые силы давят вниз (атака? FUD?)")
        
        print("="*60)
        
        return True
    
    def show_full_history(self):
        """Показать полную историю"""
        print("\n📜 Полная история прогнозов:\n")
        for i, pred in enumerate(self.predictions["predictions"], 1):
            status = "✅" if pred.get("correct") else "⏳" if not pred.get("resolved") else "❌"
            print(f"{i}. {status} {pred['timestamp']}")
            print(f"   Азимут: {pred['azimuth']:+.1f}%")
            if pred.get("resolved"):
                print(f"   Факт: {pred.get('actual_movement', 0):+.1f}%")
                print(f"   Ошибка: {pred.get('error', 0):.1f}%")
            if pred.get("note"):
                print(f"   💭 {pred['note']}")
            print()
    
    def run(self):
        """Главный цикл"""
        self.print_header()
        self.print_stats()
        
        print("\n🌊 Добро пожаловать, @fractal_whale!")
        print("    Вы единственный трейдер на этой паре.")
        print("    Введите азимут для прогноза траектории OGLM.\n")
        
        while True:
            try:
                if not self.enter_prediction():
                    break
            except KeyboardInterrupt:
                print("\n\n👋 До встречи, @fractal_whale!")
                break
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
                print("   Попробуйте снова.")


def main():
    trader = AzimuthTrader()
    trader.run()


if __name__ == "__main__":
    main()

