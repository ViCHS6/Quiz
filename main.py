import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Modern Quiz — Premium Edition")
        self.geometry("900x700")
        
        # --- ЦВЕТОВАЯ ПАЛИТРА ---
        self.colors = {
            "bg": "#FFFDF0",          # Фон: нежный крем
            "accent": "#FFB347",      # Акцент: пастельный оранжевый
            "hover": "#FFD180",       # Наведение (светлее акцента)
            "card_hover": "#FFF2C2",  # Наведение на карточку
            "text": "#4A4A4A",        # Основной текст
            "card": "#FFF9E3",        # Фон карточки ответа
            "white": "#FFFFFF",
            "correct": "#E8F5E9",     # Мягкий зеленый
            "wrong": "#FFEBEE",       # Мягкий розовый
            "progress_bg": "#F0EAD6"  # Фон полоски прогресса
        }
        
        self.configure(bg=self.colors["bg"])
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.score = 0
        self.current_question = 0
        self.questions = [] 
        self.history = []
        self.selected_option = tk.StringVar(value="")
        self.option_canvases = [] # Список для хранения ссылок на карточки

        if self.load_questions():
            self.show_start()
        else:
            self.destroy()

    def load_questions(self):
        try:
            if not os.path.exists('questions.json'):
                # Создаем пример файла, если его нет
                sample_data = [
                    {"question": "Какой язык программирования вы сейчас изучаете?", 
                     "options": ["Python", "Java", "C++", "JavaScript"], "answer": "Python"}
                ]
                with open('questions.json', 'w', encoding='utf-8') as f:
                    json.dump(sample_data, f, ensure_ascii=False)
            
            with open('questions.json', 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке: {e}")
            return False

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.option_canvases = []

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    # --- УНИВЕРСАЛЬНАЯ КНОПКА С ЭФФЕКТАМИ ---
    def create_styled_button(self, parent, text, command, width=200, height=50):
        btn = tk.Canvas(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, cursor="hand2")
        
        def render(color):
            btn.delete("all")
            self.draw_rounded_rect(btn, 2, 2, width-2, height-2, 20, fill=color)
            btn.create_text(width/2, height/2, text=text, fill="white", font=("Segoe UI", 11, "bold"))

        btn.bind("<Enter>", lambda e: render(self.colors["hover"]))
        btn.bind("<Leave>", lambda e: render(self.colors["accent"]))
        btn.bind("<Button-1>", lambda e: command())
        render(self.colors["accent"])
        return btn

    def show_start(self):
        self.clear_screen()
        container = tk.Frame(self, bg=self.colors["bg"])
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(container, text="Викторина", font=("Segoe UI", 42, "bold"), 
                 bg=self.colors["bg"], fg=self.colors["text"]).pack(pady=10)
        
        tk.Label(container, text="Проверьте знания в уютной атмосфере", 
                 font=("Segoe UI", 14), bg=self.colors["bg"], fg="#8B8B8B").pack(pady=10)

        self.create_styled_button(container, "Начать викторину", self.start_quiz, width=250, height=60).pack(pady=30)

    def start_quiz(self):
        self.score = 0
        self.current_question = 0
        self.history = []
        self.show_question()

    def show_question(self):
        self.clear_screen()
        if self.current_question >= len(self.questions):
            self.show_result()
            return

        q = self.questions[self.current_question]
        self.selected_option.set("")

        # Прогресс-бар
        progress_frame = tk.Frame(self, bg=self.colors["progress_bg"], height=6)
        progress_frame.pack(side="top", fill="x")
        width_pct = (self.current_question / len(self.questions))
        tk.Frame(progress_frame, bg=self.colors["accent"], height=6).place(relx=0, rely=0, relwidth=width_pct)

        main_content = tk.Frame(self, bg=self.colors["bg"])
        main_content.pack(expand=True, fill="both", padx=80, pady=40)

        tk.Label(main_content, text=f"ВОПРОС {self.current_question + 1} ИЗ {len(self.questions)}", 
                 font=("Segoe UI", 10, "bold"), bg=self.colors["bg"], fg=self.colors["accent"]).pack(anchor="w")

        tk.Label(main_content, text=q["question"], font=("Segoe UI", 24, "bold"), 
                 bg=self.colors["bg"], fg=self.colors["text"], wraplength=700, justify="left").pack(anchor="w", pady=(10, 40))

        # Карточки вариантов
        for option in q["options"]:
            self.create_option_card(main_content, option)

        # Кнопка подтверждения
        self.btn_next = self.create_styled_button(main_content, "Подтвердить →", self.check_answer)
        self.btn_next.pack(side="bottom", pady=20)

    def create_option_card(self, parent, text):
        card = tk.Canvas(parent, height=60, bg=self.colors["bg"], highlightthickness=0, cursor="hand2")
        card.pack(fill="x", pady=8)
        self.option_canvases.append((card, text))
        
        def render_card(state):
            card.delete("all")
            # Определяем цвета на основе состояния
            if self.selected_option.get() == text:
                bg_color = self.colors["accent"]
                txt_color = "white"
            elif state == "hover":
                bg_color = self.colors["card_hover"]
                txt_color = self.colors["text"]
            else:
                bg_color = self.colors["card"]
                txt_color = self.colors["text"]
            
            self.draw_rounded_rect(card, 2, 2, 730, 58, 20, fill=bg_color)
            card.create_text(30, 30, text=text, anchor="w", font=("Segoe UI", 12), fill=txt_color)

        def on_click(event):
            self.selected_option.set(text)
            self.redraw_options()

        card.bind("<Enter>", lambda e: render_card("hover") if self.selected_option.get() != text else None)
        card.bind("<Leave>", lambda e: render_card("normal") if self.selected_option.get() != text else None)
        card.bind("<Button-1>", on_click)
        
        render_card("normal")

    def redraw_options(self):
        # Перерисовываем все карточки, чтобы обновить выделение
        for card, text in self.option_canvases:
            card.delete("all")
            is_selected = self.selected_option.get() == text
            bg_color = self.colors["accent"] if is_selected else self.colors["card"]
            txt_color = "white" if is_selected else self.colors["text"]
            
            self.draw_rounded_rect(card, 2, 2, 730, 58, 20, fill=bg_color)
            card.create_text(30, 30, text=text, anchor="w", font=("Segoe UI", 12), fill=txt_color)

    def check_answer(self):
        user_choice = self.selected_option.get()
        if not user_choice:
            messagebox.showwarning("Внимание", "Пожалуйста, выберите вариант ответа!")
            return
        
        correct_answer = self.questions[self.current_question]["answer"]
        is_correct = user_choice == correct_answer
        if is_correct: self.score += 1
            
        self.history.append({
            "question": self.questions[self.current_question]["question"],
            "user_answer": user_choice,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })
        
        self.current_question += 1
        self.show_question()

    def show_result(self):
        self.clear_screen()
        header = tk.Frame(self, bg=self.colors["bg"])
        header.pack(fill="x", pady=30)
        
        tk.Label(header, text="Викторина завершена!", font=("Segoe UI", 24, "bold"), 
                 bg=self.colors["bg"], fg=self.colors["text"]).pack()
        
        score_pct = int((self.score / len(self.questions)) * 100)
        tk.Label(header, text=f"Ваш результат: {score_pct}% ({self.score}/{len(self.questions)})", 
                 font=("Segoe UI", 14), bg=self.colors["bg"], fg=self.colors["accent"]).pack()

        container = tk.Frame(self, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=50)

        canvas = tk.Canvas(container, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg"])

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=780)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i, item in enumerate(self.history):
            card_bg = self.colors["correct"] if item["is_correct"] else self.colors["wrong"]
            row_canvas = tk.Canvas(scrollable_frame, height=100, bg=self.colors["bg"], highlightthickness=0)
            row_canvas.pack(fill="x", pady=10, padx=10)
            
            self.draw_rounded_rect(row_canvas, 2, 2, 760, 98, 15, fill=card_bg)
            
            status = "✓" if item["is_correct"] else "✗"
            row_canvas.create_text(20, 25, text=f"{i+1}. {item['question']}", anchor="w", 
                                   font=("Segoe UI", 11, "bold"), fill=self.colors["text"], width=700)
            row_canvas.create_text(20, 55, text=f"Ваш ответ: {item['user_answer']}  {status}", anchor="w", 
                                   font=("Segoe UI", 10), fill=self.colors["text"])
            
            if not item["is_correct"]:
                row_canvas.create_text(20, 75, text=f"Правильно: {item['correct_answer']}", anchor="w", 
                                       font=("Segoe UI", 10, "italic"), fill="#666666")

        self.create_styled_button(self, "Повторить", self.start_quiz).pack(pady=20)

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()