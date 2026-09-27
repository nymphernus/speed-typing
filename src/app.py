"""
Main application module.
Tkinter GUI for the speed typing test.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import time
from typing import Optional

from .document_parser import extract_text, split_into_words
from .typing_engine import TypingEngine, TimedTypingEngine
from .timer import Timer, CountdownTimer


# Color palette
BG_COLOR = "#FAFAFA"
CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#1A1A2E"
TEXT_SECONDARY = "#6B7280"
ACCENT = "#3B82F6"
ACCENT_HOVER = "#2563EB"
SUCCESS = "#10B981"
ERROR = "#EF4444"
BORDER = "#E5E7EB"
INPUT_BG = "#F9FAFB"


class SpeedTypingApp:
    """Main application class."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Speed Typing Test")
        self.root.geometry("900x650")
        self.root.minsize(600, 400)
        self.root.configure(bg=BG_COLOR)
        
        # Configure grid weights for scalability
        self.root.grid_rowconfigure(2, weight=1)  # Main text area
        self.root.grid_columnconfigure(0, weight=1)
        
        # State
        self.text = ""
        self.words = []
        self.engine: Optional[TypingEngine] = None
        self.timed_engine: Optional[TimedTypingEngine] = None
        self.timer = Timer()
        self.countdown_timer: Optional[CountdownTimer] = None
        self.mode = "normal"
        self.time_limit = 60
        self._update_job = None
        
        # Build UI
        self._create_menu()
        self._create_toolbar()
        self._create_main_area()
        self._create_input_area()
        self._create_status_bar()
        
        # Set default text
        self._set_default_text()
    
    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root, bg=CARD_BG, fg=TEXT_PRIMARY,
                         activebackground=ACCENT, activeforeground="white",
                         borderwidth=0, font=("Segoe UI", 10))
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=CARD_BG, fg=TEXT_PRIMARY,
                           activebackground=ACCENT, activeforeground="white",
                           borderwidth=0, font=("Segoe UI", 10))
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть документ...", command=self._open_file,
                            accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Mode menu
        mode_menu = tk.Menu(menubar, tearoff=0, bg=CARD_BG, fg=TEXT_PRIMARY,
                           activebackground=ACCENT, activeforeground="white",
                           borderwidth=0, font=("Segoe UI", 10))
        menubar.add_cascade(label="Режим", menu=mode_menu)
        mode_menu.add_command(label="Обычный", command=lambda: self._set_mode("normal"))
        mode_menu.add_command(label="С таймером", command=lambda: self._set_mode("timed"))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=CARD_BG, fg=TEXT_PRIMARY,
                           activebackground=ACCENT, activeforeground="white",
                           borderwidth=0, font=("Segoe UI", 10))
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self._show_about)
        
        self.root.bind('<Control-o>', lambda e: self._open_file())
    
    def _create_toolbar(self):
        """Create toolbar."""
        toolbar = tk.Frame(self.root, bg=BG_COLOR, padx=20, pady=8)
        toolbar.grid(row=0, column=0, sticky="ew")
        
        # Left side: Mode and time
        left_frame = tk.Frame(toolbar, bg=BG_COLOR)
        left_frame.pack(side=tk.LEFT)
        
        # Mode
        mode_frame = tk.Frame(left_frame, bg=BG_COLOR)
        mode_frame.pack(side=tk.LEFT, padx=(0, 16))
        
        tk.Label(mode_frame, text="Режим", font=("Segoe UI", 9),
                bg=BG_COLOR, fg=TEXT_SECONDARY).pack(anchor=tk.W)
        
        self.mode_var = tk.StringVar(value="normal")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.mode_var,
                                   values=["normal", "timed"],
                                   state="readonly", width=12,
                                   font=("Segoe UI", 10))
        mode_combo.pack(anchor=tk.W, pady=(2, 0))
        mode_combo.bind('<<ComboboxSelected>>', self._on_mode_change)
        
        # Time limit (for timed mode)
        time_frame = tk.Frame(left_frame, bg=BG_COLOR)
        time_frame.pack(side=tk.LEFT)
        
        tk.Label(time_frame, text="Время (сек)", font=("Segoe UI", 9),
                bg=BG_COLOR, fg=TEXT_SECONDARY).pack(anchor=tk.W)
        
        self.time_limit_var = tk.StringVar(value="60")
        self.time_limit_entry = tk.Entry(time_frame, textvariable=self.time_limit_var,
                                        width=6, font=("Segoe UI", 10),
                                        bg=INPUT_BG, fg=TEXT_PRIMARY,
                                        relief=tk.FLAT, highlightthickness=1,
                                        highlightcolor=BORDER, highlightbackground=BORDER)
        self.time_limit_entry.pack(anchor=tk.W, pady=(2, 0), ipady=4)
        
        # Right side: Timer and buttons
        right_frame = tk.Frame(toolbar, bg=BG_COLOR)
        right_frame.pack(side=tk.RIGHT)
        
        # Timer
        self.timer_label = tk.Label(right_frame, text="00:00",
                                   font=("Segoe UI", 20, "bold"),
                                   bg=BG_COLOR, fg=TEXT_PRIMARY)
        self.timer_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Buttons
        self.start_btn = tk.Button(right_frame, text="Старт",
                                  bg=ACCENT, fg="white",
                                  activebackground=ACCENT_HOVER,
                                  activeforeground="white",
                                  relief=tk.FLAT, padx=20, pady=8,
                                  font=("Segoe UI", 10, "bold"),
                                  cursor="hand2", borderwidth=0,
                                  command=self._start_session)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.reset_btn = tk.Button(right_frame, text="Сброс",
                                  bg=CARD_BG, fg=TEXT_PRIMARY,
                                  activebackground=INPUT_BG,
                                  activeforeground=TEXT_PRIMARY,
                                  relief=tk.FLAT, padx=20, pady=8,
                                  font=("Segoe UI", 10),
                                  cursor="hand2", borderwidth=1,
                                  highlightthickness=1,
                                  highlightbackground=BORDER,
                                  highlightcolor=BORDER,
                                  command=self._reset_session)
        self.reset_btn.pack(side=tk.LEFT)
    
    def _create_main_area(self):
        """Create main text display area."""
        # Container with padding
        container = tk.Frame(self.root, bg=BG_COLOR, padx=20)
        container.grid(row=2, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Card frame
        card = tk.Frame(container, bg=CARD_BG, padx=24, pady=20,
                       highlightthickness=1, highlightbackground=BORDER)
        card.grid(row=0, column=0, sticky="nsew")
        card.grid_rowconfigure(0, weight=1)
        card.grid_columnconfigure(0, weight=1)
        
        # Text widget
        self.text_widget = tk.Text(card, wrap=tk.WORD,
                                   font=("Consolas", 15),
                                   padx=4, pady=4,
                                   bg=CARD_BG, fg=TEXT_PRIMARY,
                                   relief=tk.FLAT, state=tk.DISABLED,
                                   spacing1=4, spacing2=2, spacing3=4)
        
        scrollbar = ttk.Scrollbar(card, orient=tk.VERTICAL,
                                   command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Tags
        self.text_widget.tag_configure("current",
                                       foreground=ACCENT,
                                       underline=True,
                                       underlinefg=ACCENT)
        self.text_widget.tag_configure("completed", foreground=SUCCESS)
    
    def _create_input_area(self):
        """Create input area."""
        container = tk.Frame(self.root, bg=BG_COLOR, padx=20, pady=8)
        container.grid(row=3, column=0, sticky="ew")
        
        # Input card
        input_card = tk.Frame(container, bg=CARD_BG, padx=20, pady=16,
                             highlightthickness=1, highlightbackground=BORDER)
        input_card.pack(fill=tk.X)
        
        tk.Label(input_card, text="Начните вводить текст",
                font=("Segoe UI", 9),
                bg=CARD_BG, fg=TEXT_SECONDARY).pack(anchor=tk.W, pady=(0, 8))
        
        # Large input field
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(input_card, textvariable=self.input_var,
                                   font=("Consolas", 18),
                                   bg=INPUT_BG, fg=TEXT_PRIMARY,
                                   relief=tk.FLAT, highlightthickness=1,
                                   highlightcolor=BORDER, highlightbackground=BORDER,
                                   insertbackground=TEXT_PRIMARY,
                                   insertwidth=2)
        self.input_entry.pack(fill=tk.X, ipady=12)
        self.input_entry.bind('<KeyRelease>', self._on_key_release)
    
    def _create_status_bar(self):
        """Create status bar."""
        container = tk.Frame(self.root, bg=BG_COLOR, padx=20, pady=8)
        container.grid(row=4, column=0, sticky="ew")
        
        # Stats in a row
        stats_frame = tk.Frame(container, bg=BG_COLOR)
        stats_frame.pack(fill=tk.X)
        
        # WPM
        stat_wpm = tk.Frame(stats_frame, bg=CARD_BG, padx=16, pady=10,
                           highlightthickness=1, highlightbackground=BORDER)
        stat_wpm.pack(side=tk.LEFT, padx=(0, 8))
        self.wpm_label = tk.Label(stat_wpm, text="0",
                                 font=("Segoe UI", 16, "bold"),
                                 bg=CARD_BG, fg=ACCENT)
        self.wpm_label.pack()
        tk.Label(stat_wpm, text="WPM", font=("Segoe UI", 8),
                bg=CARD_BG, fg=TEXT_SECONDARY).pack()
        
        # Accuracy
        stat_acc = tk.Frame(stats_frame, bg=CARD_BG, padx=16, pady=10,
                           highlightthickness=1, highlightbackground=BORDER)
        stat_acc.pack(side=tk.LEFT, padx=(0, 8))
        self.accuracy_label = tk.Label(stat_acc, text="100%",
                                      font=("Segoe UI", 16, "bold"),
                                      bg=CARD_BG, fg=SUCCESS)
        self.accuracy_label.pack()
        tk.Label(stat_acc, text="Точность", font=("Segoe UI", 8),
                bg=CARD_BG, fg=TEXT_SECONDARY).pack()
        
        # Word time
        stat_time = tk.Frame(stats_frame, bg=CARD_BG, padx=16, pady=10,
                            highlightthickness=1, highlightbackground=BORDER)
        stat_time.pack(side=tk.LEFT, padx=(0, 8))
        self.word_time_label = tk.Label(stat_time, text="0.0с",
                                       font=("Segoe UI", 16, "bold"),
                                       bg=CARD_BG, fg=TEXT_PRIMARY)
        self.word_time_label.pack()
        tk.Label(stat_time, text="Время слова", font=("Segoe UI", 8),
                bg=CARD_BG, fg=TEXT_SECONDARY).pack()
        
        # Progress
        stat_prog = tk.Frame(stats_frame, bg=CARD_BG, padx=16, pady=10,
                            highlightthickness=1, highlightbackground=BORDER)
        stat_prog.pack(side=tk.RIGHT)
        self.progress_label = tk.Label(stat_prog, text=f"0/{len(self.words)}",
                                      font=("Segoe UI", 16, "bold"),
                                      bg=CARD_BG, fg=TEXT_PRIMARY)
        self.progress_label.pack()
        tk.Label(stat_prog, text="Прогресс", font=("Segoe UI", 8),
                bg=CARD_BG, fg=TEXT_SECONDARY).pack()
    
    def _set_default_text(self):
        """Set default text for typing practice."""
        default_text = ("The quick brown fox jumps over the lazy dog. "
                       "Pack my box with five dozen liquor jugs. "
                       "How vexingly quick daft zebras jump! "
                       "Съешь же ещё этих мягких французских булок, да выпей чаю. "
                       "В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!")
        self.text = default_text
        self.words = split_into_words(default_text)
        self._update_text_display()
    
    def _open_file(self):
        """Open a document file."""
        filepath = filedialog.askopenfilename(
            title="Открыть документ",
            filetypes=[
                ("Документы", "*.docx *.doc"),
                ("Текстовые файлы", "*.txt"),
                ("Все файлы", "*.*")
            ]
        )
        
        if not filepath:
            return
        
        try:
            self.text = extract_text(filepath)
            self.words = split_into_words(self.text)
            self._update_text_display()
            self._reset_session()
            messagebox.showinfo("Успех", f"Текст загружен: {len(self.words)} слов")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
    
    def _set_mode(self, mode: str):
        """Set typing mode."""
        self.mode = mode
        self.mode_var.set(mode)
        self._reset_session()
    
    def _on_mode_change(self, event=None):
        """Handle mode change."""
        self.mode = self.mode_var.get()
        self._reset_session()
    
    def _start_session(self):
        """Start typing session."""
        if not self.words:
            messagebox.showwarning("Предупреждение", "Нет текста для набора")
            return
        
        self._reset_session()
        
        if self.mode == "normal":
            self.engine = TypingEngine(self.text)
            self.engine.start()
            self.timer.start()
        else:
            try:
                self.time_limit = int(self.time_limit_var.get())
                if self.time_limit <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Некорректное значение времени")
                return
            
            self.timed_engine = TimedTypingEngine(self.text, self.time_limit)
            self.timed_engine.start()
            self.countdown_timer = CountdownTimer(self.time_limit, self._on_time_up)
            self.countdown_timer.start()
        
        self.input_entry.focus_set()
        self._update_display()
        self._schedule_update()
    
    def _reset_session(self):
        """Reset typing session."""
        self.engine = None
        self.timed_engine = None
        self.timer.reset()
        if self.countdown_timer:
            self.countdown_timer.stop()
            self.countdown_timer = None
        
        if self._update_job:
            self.root.after_cancel(self._update_job)
            self._update_job = None
        
        self.input_var.set("")
        self.timer_label.config(text="00:00")
        self.wpm_label.config(text="0")
        self.accuracy_label.config(text="100%")
        self.word_time_label.config(text="0.0с")
        self.progress_label.config(text=f"0/{len(self.words)}")
        
        self._update_text_display()
    
    def _on_key_release(self, event=None):
        """Auto-submit when typed text length matches current word length."""
        if self.mode == "normal" and self.engine:
            if not self.engine.is_running():
                return
            
            typed = self.input_var.get()
            expected_length = self.engine.get_current_word_length()
            
            if expected_length > 0 and len(typed) >= expected_length:
                self.engine.submit_word(typed)
                self.input_var.set("")
                self._update_display()
                self._update_text_display()
                
                if self.engine.is_complete():
                    self._on_session_complete()
        
        elif self.mode == "timed" and self.timed_engine:
            if not self.timed_engine.is_running():
                return
            
            typed = self.input_var.get()
            expected_length = self.timed_engine.get_current_word_length()
            
            if expected_length > 0 and len(typed) >= expected_length:
                self.timed_engine.submit_word(typed)
                self.input_var.set("")
                self._update_display()
                self._update_text_display()
                
                if self.timed_engine.is_finished():
                    self._on_session_complete()
    
    def _on_time_up(self):
        """Handle time up event."""
        self._on_session_complete()
    
    def _on_session_complete(self):
        """Handle session completion."""
        if self._update_job:
            self.root.after_cancel(self._update_job)
            self._update_job = None
        
        if self.mode == "normal" and self.engine:
            total_time = self.engine.get_total_time()
            wpm = self.engine.get_wpm()
            accuracy = self.engine.get_accuracy()
            
            messagebox.showinfo("Результаты",
                f"Время: {total_time:.1f} сек\n"
                f"WPM: {wpm:.1f}\n"
                f"Точность: {accuracy:.1f}%\n"
                f"Слов: {self.engine.get_current_index()}")
        
        elif self.mode == "timed" and self.timed_engine:
            words_typed = self.timed_engine.get_words_typed()
            errors = self.timed_engine.get_errors()
            
            messagebox.showinfo("Результаты",
                f"Слов введено: {words_typed}\n"
                f"Ошибок: {errors}\n"
                f"Время: {self.time_limit} сек")
    
    def _update_display(self):
        """Update display with current statistics."""
        if self.mode == "normal" and self.engine:
            self.timer_label.config(text=self.timer.get_formatted_time())
            self.wpm_label.config(text=f"{self.engine.get_wpm():.0f}")
            self.accuracy_label.config(text=f"{self.engine.get_accuracy():.0f}%")
            
            current_idx = self.engine.get_current_index()
            if current_idx > 0:
                word_time = self.engine.get_word_time(current_idx - 1)
                if word_time:
                    self.word_time_label.config(text=f"{word_time:.1f}с")
            
            self.progress_label.config(
                text=f"{self.engine.get_current_index()}/{len(self.words)}"
            )
        
        elif self.mode == "timed" and self.timed_engine:
            if self.countdown_timer:
                self.timer_label.config(text=self.countdown_timer.get_formatted_remaining())
            
            self.wpm_label.config(text=f"{self.timed_engine.get_words_typed()}")
            self.accuracy_label.config(text=f"{self.timed_engine.get_errors()}")
            self.progress_label.config(
                text=f"{self.timed_engine.get_words_typed()}/{len(self.words)}"
            )
    
    def _update_text_display(self):
        """Update text display with highlighting."""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete('1.0', tk.END)
        
        if not self.text:
            self.text_widget.config(state=tk.DISABLED)
            return
        
        self.text_widget.insert('1.0', self.text)
        
        if self.mode == "normal" and self.engine:
            current_idx = self.engine.get_current_index()
            if current_idx < len(self.words):
                self._highlight_word(current_idx, "current")
                for i in range(current_idx):
                    self._mark_word_completed(i)
        
        elif self.mode == "timed" and self.timed_engine:
            current_idx = self.timed_engine.current_index
            if current_idx < len(self.words):
                self._highlight_word(current_idx, "current")
                for i in range(current_idx):
                    self._mark_word_completed(i)
        
        self.text_widget.config(state=tk.DISABLED)
    
    def _highlight_word(self, word_index: int, tag: str):
        """Highlight a specific word in the text using regex."""
        word = self.words[word_index]
        escaped_word = re.escape(word)
        pattern = r'\b' + escaped_word + r'\b'
        
        for match in re.finditer(pattern, self.text):
            if match.start() == self._get_word_position(word_index):
                start_idx = f"1.0 + {match.start()} chars"
                end_idx = f"1.0 + {match.end()} chars"
                self.text_widget.tag_add(tag, start_idx, end_idx)
                return
    
    def _mark_word_completed(self, word_index: int):
        """Mark a word as completed."""
        word = self.words[word_index]
        escaped_word = re.escape(word)
        pattern = r'\b' + escaped_word + r'\b'
        
        for match in re.finditer(pattern, self.text):
            if match.start() == self._get_word_position(word_index):
                start_idx = f"1.0 + {match.start()} chars"
                end_idx = f"1.0 + {match.end()} chars"
                self.text_widget.tag_add("completed", start_idx, end_idx)
                return
    
    def _get_word_position(self, word_index: int) -> int:
        """Get the character position of a word in the text."""
        pos = 0
        for i in range(word_index):
            word = self.words[i]
            escaped_word = re.escape(word)
            pattern = r'\b' + escaped_word + r'\b'
            match = re.search(pattern, self.text[pos:])
            if match:
                pos += match.end()
        word = self.words[word_index]
        escaped_word = re.escape(word)
        pattern = r'\b' + escaped_word + r'\b'
        match = re.search(pattern, self.text[pos:])
        if match:
            return pos + match.start()
        return 0
    
    def _schedule_update(self):
        """Schedule periodic UI updates."""
        if self.mode == "normal" and self.engine and self.engine.is_running():
            self._update_display()
            self._update_job = self.root.after(100, self._schedule_update)
        elif self.mode == "timed" and self.timed_engine and self.timed_engine.is_running():
            self._update_display()
            if self.countdown_timer:
                self.countdown_timer.check_time_up()
            self._update_job = self.root.after(100, self._schedule_update)
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo("О программе",
            "Speed Typing Test\n\n"
            "Приложение для проверки скорости печати.\n"
            "Поддерживает форматы: .docx, .doc, .txt\n"
            "Режимы: обычный и с ограничением времени.")
