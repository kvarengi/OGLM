#!/usr/bin/env python3
"""
OGLM Azimuth Trading Terminal
@fractal_whale Interface v1.0

Портативный торговый терминал для прогнозирования через азимут.
Работает на: Desktop, Server, Mobile (Termux)
Зависимости: минимальные (только stdlib)
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import random


# ANSI цвета для терминала (работают везде, включая Termux)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class OGLMAzimuthTerminal:
    def __init__(self, data_dir=None):
        """Инициализация терминала"""
        # Определяем директорию данных
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            # По умолчанию в ~/.oglm/
            home = Path.home()
            self.data_dir = home / ".oglm"
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / "azimuth_predictions.json"
        self.config_file = self.data_dir / "config.json"
        
        self.predictions = self.load_data()
        self.config = self.load_config()
        self.current_price = self.config.get("current_price", 1.0)
        self.username = self.config.get("username", "@fractal_whale")
        
    def load_data(self):
        """Загрузить историю прогнозов"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.create_empty_data()
        return self.create_empty_data()
    
    def create_empty_data(self):
        """Создать пустую структуру данных"""
        return {
            "predictions": [],
            "stats": {
                "total": 0,
                "correct": 0,
                "accuracy": 0.0,
                "best_prediction": None,
                "worst_prediction": None,
                "total_pnl": 0.0
            },
            "market": {
                "all_time_high": 1.0,
                "all_time_low": 1.0,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def save_data(self):
        """Сохранить данные"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.predictions, f, indent=2, ensure_ascii=False)
    
    def load_config(self):
        """Загрузить конфигурацию"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Сохранить конфигурацию"""
        self.config["current_price"] = self.current_price
        self.config["username"] = self.username
        self.config["last_session"] = datetime.now().isoformat()
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def clear_screen(self):
        """Очистить экран (кроссплатформенно)"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self):
        """Красивый header терминала"""
        c = Colors
        print(f"\n{c.CYAN}{'='*60}{c.ENDC}")
        print(f"{c.BOLD}┌─────────────────────────────────────────────────────────┐{c.ENDC}")
        print(f"{c.BOLD}│  {c.GREEN}{self.username} Terminal v1.0{c.ENDC}{'                           '[:27]}│")
        print(f"{c.BOLD}│  {c.BLUE}OGLM Azimuth Trading Interface{c.ENDC}{'                      '[:25]}│")
        print(f"{c.BOLD}├─────────────────────────────────────────────────────────┤{c.ENDC}")
        print(f"{c.BOLD}│  {c.CYAN}Connected to Протон-А Semantic Grid{c.ENDC}{'                   '[:20]}│")
        
        # Цена с цветом (вверх/вниз)
        price_str = f"{self.current_price:.4f}"
        ath = self.predictions["market"]["all_time_high"]
        atl = self.predictions["market"]["all_time_low"]
        
        if self.current_price >= ath * 0.9:
            price_color = c.GREEN
        elif self.current_price <= atl * 1.1:
            price_color = c.RED
        else:
            price_color = c.YELLOW
        
        print(f"{c.BOLD}│  Current OGLM: {price_color}{price_str}{c.ENDC}{'                                    '[:36-len(price_str)]}│")
        print(f"{c.BOLD}└─────────────────────────────────────────────────────────┘{c.ENDC}")
        print(f"{c.CYAN}{'='*60}{c.ENDC}\n")
    
    def print_stats(self):
        """Показать статистику"""
        c = Colors
        stats = self.predictions["stats"]
        
        print(f"\n{c.BOLD}📊 Статистика {self.username}:{c.ENDC}")
        print(f"  Всего прогнозов: {c.CYAN}{stats['total']}{c.ENDC}")
        
        if stats['total'] > 0:
            acc_color = c.GREEN if stats['accuracy'] >= 70 else c.YELLOW if stats['accuracy'] >= 50 else c.RED
            print(f"  Правильных: {c.GREEN}{stats['correct']}{c.ENDC}/{stats['total']}")
            print(f"  Точность: {acc_color}{stats['accuracy']:.1f}%{c.ENDC}")
            
            if stats.get('total_pnl'):
                pnl_color = c.GREEN if stats['total_pnl'] > 0 else c.RED
                print(f"  Total P&L: {pnl_color}{stats['total_pnl']:+.2f}%{c.ENDC}")
        
        # Показать последние прогнозы
        preds = self.predictions["predictions"]
        if preds:
            print(f"\n{c.BOLD}📈 Последние 5 прогнозов:{c.ENDC}")
            for pred in preds[-5:]:
                if pred.get("resolved"):
                    status = f"{c.GREEN}✅{c.ENDC}" if pred.get("correct") else f"{c.RED}❌{c.ENDC}"
                    az = pred['azimuth']
                    actual = pred.get('actual_movement', 0)
                    error = pred.get('error', 0)
                    
                    print(f"  {status} {pred['timestamp'][:16]}: {az:+6.1f}% → {actual:+6.1f}% (err: {error:.1f}%)")
                else:
                    print(f"  {c.YELLOW}⏳{c.ENDC} {pred['timestamp'][:16]}: {pred['azimuth']:+6.1f}% (pending)")
    
    def draw_price_chart(self, width=50, height=10):
        """ASCII график цены"""
        c = Colors
        preds = self.predictions["predictions"]
        
        if len(preds) < 2:
            return
        
        print(f"\n{c.BOLD}📊 Price Chart (last {min(len(preds), width)} predictions):{c.ENDC}\n")
        
        # Собираем цены
        prices = [1.0]  # Начальная цена
        for pred in preds[-width:]:
            if pred.get("resolved"):
                last_price = prices[-1]
                actual = pred.get("actual_movement", 0)
                new_price = last_price * (1 + actual/100)
                prices.append(new_price)
        
        if len(prices) < 2:
            return
        
        # Масштабирование
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price
        
        if price_range == 0:
            price_range = 1
        
        # Рисуем
        for i in range(height, -1, -1):
            level = min_price + (price_range * i / height)
            line = f"{level:6.2f} │"
            
            for price in prices:
                if abs(price - level) < price_range / height:
                    line += "●"
                else:
                    line += " "
            
            print(line)
        
        # Ось X
        print("       └" + "─" * len(prices))
        print(f"        {c.CYAN}Time →{c.ENDC}")
    
    def calculate_outcome(self, azimuth, days=7):
        """
        Симуляция рыночного движения
        
        Факторы:
        - Азимут (ваш прогноз)
        - Темная материя (скрытые силы)
        - Фрактальная волатильность
        - Временной горизонт
        """
        # Базовый шум рынка
        market_noise = random.uniform(-15, 15)
        
        # Темная материя (коллективное бессознательное)
        dark_matter = random.gauss(0, 8)
        
        # Фрактальная сложность (большие движения сложнее)
        difficulty = min(abs(azimuth) / 100, 1.0)
        accuracy_modifier = 1.0 - (difficulty * 0.4)
        
        # Временной фактор (чем дальше, тем больше неопределённость)
        time_factor = 1.0 + (days / 30) * 0.2
        
        # Итоговое движение
        actual = (azimuth * accuracy_modifier + market_noise + dark_matter) * time_factor
        
        # Ограничиваем экстремальные движения
        actual = max(min(actual, 1000), -99.9)
        
        return actual, dark_matter
    
    def enter_prediction(self):
        """Ввод нового прогноза"""
        c = Colors
        
        print(f"\n{c.BOLD}🎯 Введите азимут (направление движения OGLM):{c.ENDC}")
        print(f"\n   {c.CYAN}Примеры:{c.ENDC}")
        print("   • +50    → рост на 50%")
        print("   • -99    → падение на 99% (зловещая долина)")
        print("   • +1000  → 10x рост")
        print("   • 0      → стагнация")
        print(f"\n   {c.YELLOW}Команды:{c.ENDC}")
        print("   • 'stats'   → статистика")
        print("   • 'chart'   → график цены")
        print("   • 'history' → полная история")
        print("   • 'clear'   → очистить экран")
        print("   • 'exit'    → выход")
        
        try:
            azimuth_input = input(f"\n{c.BOLD}Азимут: {c.ENDC}").strip()
        except (EOFError, KeyboardInterrupt):
            return False
        
        # Команды
        if azimuth_input.lower() == 'exit':
            return False
        elif azimuth_input.lower() == 'stats':
            self.print_stats()
            input(f"\n{c.YELLOW}[Enter для продолжения]{c.ENDC}")
            return True
        elif azimuth_input.lower() == 'chart':
            self.draw_price_chart()
            input(f"\n{c.YELLOW}[Enter для продолжения]{c.ENDC}")
            return True
        elif azimuth_input.lower() == 'history':
            self.show_full_history()
            input(f"\n{c.YELLOW}[Enter для продолжения]{c.ENDC}")
            return True
        elif azimuth_input.lower() == 'clear':
            self.clear_screen()
            return True
        
        # Парсинг азимута
        try:
            azimuth = float(azimuth_input)
        except ValueError:
            print(f"{c.RED}❌ Ошибка: Введите число{c.ENDC}")
            input(f"\n{c.YELLOW}[Enter для продолжения]{c.ENDC}")
            return True
        
        # Валидация
        if abs(azimuth) > 10000:
            print(f"{c.YELLOW}⚠️  Азимут > 10000% экстремален{c.ENDC}")
            try:
                confirm = input("   Продолжить? (y/n): ")
                if confirm.lower() != 'y':
                    return True
            except (EOFError, KeyboardInterrupt):
                return True
        
        # Reasoning
        try:
            note = input(f"\n{c.CYAN}💭 Reasoning (опционально): {c.ENDC}").strip()
        except (EOFError, KeyboardInterrupt):
            note = ""
        
        # Временной горизонт
        try:
            horizon_input = input(f"{c.CYAN}⏱️  Горизонт в днях (default: 7): {c.ENDC}").strip()
            horizon = int(horizon_input) if horizon_input else 7
        except (ValueError, EOFError, KeyboardInterrupt):
            horizon = 7
        
        # Создаём прогноз
        prediction = {
            "id": len(self.predictions["predictions"]) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "azimuth": azimuth,
            "note": note,
            "horizon_days": horizon,
            "entry_price": self.current_price,
            "target_price": self.current_price * (1 + azimuth/100),
            "resolved": False,
            "correct": None
        }
        
        # Симуляция
        print(f"\n{c.CYAN}🔮 Протон-А анализирует...{c.ENDC}")
        print("   • Фрактальная декомпозиция...")
        print("   • Детекция темной материи...")
        print("   • Квантовый расчёт...")
        
        actual, dark_matter = self.calculate_outcome(azimuth, horizon)
        prediction["actual_movement"] = actual
        prediction["dark_matter_signal"] = dark_matter
        
        # Обновляем цену
        new_price = self.current_price * (1 + actual/100)
        prediction["exit_price"] = new_price
        
        # Оценка точности
        tolerance = 20  # ±20%
        error = abs(actual - azimuth)
        correct = error <= tolerance
        
        prediction["resolved"] = True
        prediction["correct"] = correct
        prediction["error"] = error
        prediction["pnl"] = actual  # Упрощённо: P&L = движение цены
        
        # Обновляем статистику
        self.predictions["predictions"].append(prediction)
        stats = self.predictions["stats"]
        stats["total"] += 1
        if correct:
            stats["correct"] += 1
        stats["accuracy"] = (stats["correct"] / stats["total"]) * 100
        stats["total_pnl"] = stats.get("total_pnl", 0) + actual
        
        # Обновляем best/worst
        if not stats.get("best_prediction") or error < stats["best_prediction"]["error"]:
            stats["best_prediction"] = {"id": prediction["id"], "error": error}
        if not stats.get("worst_prediction") or error > stats["worst_prediction"]["error"]:
            stats["worst_prediction"] = {"id": prediction["id"], "error": error}
        
        # Обновляем рынок
        market = self.predictions["market"]
        if new_price > market["all_time_high"]:
            market["all_time_high"] = new_price
        if new_price < market["all_time_low"]:
            market["all_time_low"] = new_price
        market["last_updated"] = datetime.now().isoformat()
        
        self.current_price = new_price
        self.save_data()
        self.save_config()
        
        # Показываем результат
        print(f"\n{c.CYAN}{'='*60}{c.ENDC}")
        
        if correct:
            print(f"{c.GREEN}{c.BOLD}✅ ТОЧНЫЙ ПРОГНОЗ!{c.ENDC}")
        else:
            print(f"{c.RED}{c.BOLD}❌ Рынок пошёл иначе{c.ENDC}")
        
        print(f"\n{c.BOLD}📊 Результат:{c.ENDC}")
        print(f"   Ваш азимут: {c.CYAN}{azimuth:+.1f}%{c.ENDC}")
        
        actual_color = c.GREEN if actual > 0 else c.RED
        print(f"   Фактически: {actual_color}{actual:+.1f}%{c.ENDC}")
        print(f"   Ошибка: {c.YELLOW}{error:.1f}%{c.ENDC}")
        
        print(f"\n{c.BOLD}💰 Цена:{c.ENDC}")
        print(f"   {self.current_price / (1 + actual/100):.4f} → {self.current_price:.4f}")
        
        # Анализ темной материи
        if abs(dark_matter) > 5:
            print(f"\n{c.MAGENTA}🌑 Темная материя детектирована: {dark_matter:+.1f}%{c.ENDC}")
            if dark_matter > 0:
                print(f"   {c.GREEN}→ Скрытые силы толкают вверх{c.ENDC}")
            else:
                print(f"   {c.RED}→ Скрытые силы давят вниз{c.ENDC}")
        
        print(f"{c.CYAN}{'='*60}{c.ENDC}")
        
        input(f"\n{c.YELLOW}[Enter для следующего прогноза]{c.ENDC}")
        return True
    
    def show_full_history(self):
        """Показать полную историю"""
        c = Colors
        print(f"\n{c.BOLD}📜 Полная история прогнозов:{c.ENDC}\n")
        
        if not self.predictions["predictions"]:
            print(f"{c.YELLOW}  История пуста. Сделайте первый прогноз!{c.ENDC}")
            return
        
        for pred in self.predictions["predictions"]:
            status = f"{c.GREEN}✅{c.ENDC}" if pred.get("correct") else f"{c.YELLOW}⏳{c.ENDC}" if not pred.get("resolved") else f"{c.RED}❌{c.ENDC}"
            
            print(f"{status} #{pred['id']} {c.CYAN}{pred['timestamp']}{c.ENDC}")
            print(f"   Азимут: {c.BOLD}{pred['azimuth']:+.1f}%{c.ENDC}")
            
            if pred.get("resolved"):
                actual_color = c.GREEN if pred.get('actual_movement', 0) > 0 else c.RED
                print(f"   Факт: {actual_color}{pred.get('actual_movement', 0):+.1f}%{c.ENDC}")
                print(f"   Ошибка: {c.YELLOW}{pred.get('error', 0):.1f}%{c.ENDC}")
                print(f"   Цена: {pred.get('entry_price', 1):.4f} → {pred.get('exit_price', 1):.4f}")
            
            if pred.get("note"):
                print(f"   {c.CYAN}💭 {pred['note']}{c.ENDC}")
            
            print()
    
    def run(self):
        """Главный цикл терминала"""
        self.clear_screen()
        self.print_header()
        self.print_stats()
        
        c = Colors
        print(f"\n{c.GREEN}🌊 Добро пожаловать, {self.username}!{c.ENDC}")
        print(f"{c.CYAN}   Вы единственный трейдер на этой паре.{c.ENDC}")
        print(f"{c.CYAN}   Введите азимут для прогноза траектории OGLM.{c.ENDC}\n")
        
        input(f"{c.YELLOW}[Enter для начала]{c.ENDC}")
        
        while True:
            try:
                self.clear_screen()
                self.print_header()
                
                if not self.enter_prediction():
                    break
                    
            except KeyboardInterrupt:
                print(f"\n\n{c.YELLOW}👋 До встречи, {self.username}!{c.ENDC}")
                self.save_config()
                break
            except Exception as e:
                print(f"\n{c.RED}❌ Ошибка: {e}{c.ENDC}")
                print(f"{c.YELLOW}   Попробуйте снова.{c.ENDC}")
                input(f"\n{c.YELLOW}[Enter для продолжения]{c.ENDC}")


def main():
    """Entry point"""
    # Проверяем аргументы командной строки
    data_dir = None
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    
    try:
        terminal = OGLMAzimuthTerminal(data_dir=data_dir)
        terminal.run()
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("   Проверьте, что Python 3.6+ установлен")
        sys.exit(1)


if __name__ == "__main__":
    main()

