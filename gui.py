import os
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk

from config import HEADERS, CSV_FILE, EXCEL_FILE
from tracker_core import run_tracker
from utils import generate_summary, send_email
from settings_manager import load_settings, save_settings
from translations import TRANSLATIONS


APP_TITLE = "Price Tracker Pro"


class PriceTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1180x820")
        self.root.minsize(1040, 720)

        icon_path = os.path.join("assets", "logo.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self.settings = load_settings()
        self.current_lang = self.settings.get("language", "tr")
        if self.current_lang not in TRANSLATIONS:
            self.current_lang = "tr"

        self.setup_theme()
        self.build_ui()
        self.load_settings_into_form()
        self.refresh_dashboard()
        self.apply_translations()

    def tr(self, key):
        return TRANSLATIONS[self.current_lang].get(key, key)

    def setup_theme(self):
        self.bg = "#0b1120"
        self.panel = "#111827"
        self.panel_2 = "#1f2937"
        self.panel_3 = "#0f172a"
        self.text = "#f8fafc"
        self.muted = "#94a3b8"
        self.accent = "#d4af37"
        self.accent_hover = "#e8c75a"
        self.green = "#22c55e"
        self.red = "#ef4444"
        self.yellow = "#f59e0b"
        self.blue = "#38bdf8"
        self.input_bg = "#08101f"
        self.log_bg = "#020617"
        self.border = "#243041"

        self.root.configure(bg=self.bg)

    def build_ui(self):
        self.main = tk.Frame(self.root, bg=self.bg, padx=18, pady=18)
        self.main.pack(fill="both", expand=True)

        self.build_header()
        self.build_stats_row()
        self.build_content_area()
        self.build_statusbar()

    def build_header(self):
        header = tk.Frame(self.main, bg=self.bg)
        header.pack(fill="x", pady=(0, 14))

        left_wrap = tk.Frame(header, bg=self.bg)
        left_wrap.pack(side="left", fill="x", expand=True)

        logo_path = os.path.join("assets", "logo.png")

        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img.thumbnail((380, 120))
                self.logo_img = ImageTk.PhotoImage(img)

                logo_label = tk.Label(
                    left_wrap,
                    image=self.logo_img,
                    bg=self.bg,
                    bd=0,
                    highlightthickness=0,
                )
                logo_label.pack(anchor="w")
            except Exception:
                self.build_fallback_title(left_wrap)
        else:
            self.build_fallback_title(left_wrap)

        self.subtitle_label = tk.Label(
            left_wrap,
            text="",
            bg=self.bg,
            fg=self.muted,
            font=("Segoe UI", 10),
        )
        self.subtitle_label.pack(anchor="w", pady=(4, 0))

        right_wrap = tk.Frame(header, bg=self.bg)
        right_wrap.pack(side="right", anchor="n")

        lang_wrap = tk.Frame(right_wrap, bg=self.bg)
        lang_wrap.pack(anchor="e", pady=(0, 8))

        self.language_label = tk.Label(
            lang_wrap,
            text="",
            bg=self.bg,
            fg=self.muted,
            font=("Segoe UI", 9),
        )
        self.language_label.pack(side="left", padx=(0, 8))

        self.language_var = tk.StringVar(value=self.current_lang.upper())
        self.language_menu = tk.OptionMenu(
            lang_wrap,
            self.language_var,
            "TR",
            "EN",
            command=self.change_language,
        )
        self.language_menu.config(
            bg=self.panel_2,
            fg=self.text,
            activebackground="#334155",
            activeforeground=self.text,
            relief="flat",
            highlightthickness=0,
            bd=0,
            font=("Segoe UI", 9),
            width=5,
        )
        self.language_menu["menu"].config(
            bg=self.panel_2,
            fg=self.text,
            activebackground="#334155",
            activeforeground=self.text,
            font=("Segoe UI", 9),
        )
        self.language_menu.pack(side="left")

        self.mail_status_var = tk.StringVar(value="")
        self.mail_status_label = tk.Label(
            right_wrap,
            textvariable=self.mail_status_var,
            bg=self.panel,
            fg=self.green,
            font=("Segoe UI", 10, "bold"),
            padx=14,
            pady=10,
        )
        self.mail_status_label.pack(anchor="e")

    def build_fallback_title(self, parent):
        self.title_label = tk.Label(
            parent,
            text=APP_TITLE,
            bg=self.bg,
            fg=self.text,
            font=("Segoe UI", 24, "bold"),
        )
        self.title_label.pack(anchor="w")

    def build_stats_row(self):
        stats_wrap = tk.Frame(self.main, bg=self.bg)
        stats_wrap.pack(fill="x", pady=(0, 14))

        self.total_products_var = tk.StringVar(value="0")
        self.total_records_var = tk.StringVar(value="0")
        self.last_status_var = tk.StringVar(value=self.tr("dashboard_default"))
        self.report_var = tk.StringVar(value=self.tr("no_report"))

        self.stat1 = self.create_stat_card(
            stats_wrap,
            color=self.blue,
            value_var=self.total_products_var,
        )
        self.stat1.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.stat2 = self.create_stat_card(
            stats_wrap,
            color=self.accent,
            value_var=self.total_records_var,
        )
        self.stat2.pack(side="left", fill="both", expand=True, padx=8)

        self.stat3 = self.create_stat_card(
            stats_wrap,
            color=self.green,
            value_var=self.last_status_var,
        )
        self.stat3.pack(side="left", fill="both", expand=True, padx=8)

        self.stat4 = self.create_stat_card(
            stats_wrap,
            color=self.yellow,
            value_var=self.report_var,
        )
        self.stat4.pack(side="left", fill="both", expand=True, padx=(8, 0))

    def create_stat_card(self, parent, color, value_var):
        card = tk.Frame(parent, bg=self.panel, bd=0, highlightthickness=1, highlightbackground=self.border)

        top_line = tk.Frame(card, bg=color, height=4)
        top_line.pack(fill="x")

        body = tk.Frame(card, bg=self.panel)
        body.pack(fill="both", expand=True, padx=14, pady=14)

        title_label = tk.Label(
            body,
            text="",
            bg=self.panel,
            fg=self.muted,
            font=("Segoe UI", 9),
        )
        title_label.pack(anchor="w")

        value_label = tk.Label(
            body,
            textvariable=value_var,
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 20, "bold"),
        )
        value_label.pack(anchor="w", pady=(6, 2))

        subtitle_label = tk.Label(
            body,
            text="",
            bg=self.panel,
            fg=self.muted,
            font=("Segoe UI", 9),
        )
        subtitle_label.pack(anchor="w")

        card.title_label = title_label
        card.subtitle_label = subtitle_label
        return card

    def build_content_area(self):
        content = tk.Frame(self.main, bg=self.bg)
        content.pack(fill="both", expand=True)

        left_col = tk.Frame(content, bg=self.bg)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_col = tk.Frame(content, bg=self.bg, width=320)
        right_col.pack(side="left", fill="y")
        right_col.pack_propagate(False)

        self.build_url_card(left_col)
        self.build_log_area(left_col)
        self.build_control_panel(right_col)

    def build_url_card(self, parent):
        card = tk.Frame(parent, bg=self.panel, bd=0, highlightthickness=1, highlightbackground=self.border)
        card.pack(fill="x", pady=(0, 12))

        self.url_title_label = tk.Label(
            card,
            text="",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 11, "bold"),
        )
        self.url_title_label.pack(anchor="w", padx=14, pady=(14, 4))

        self.url_desc_label = tk.Label(
            card,
            text="",
            bg=self.panel,
            fg=self.muted,
            font=("Segoe UI", 9),
        )
        self.url_desc_label.pack(anchor="w", padx=14, pady=(0, 10))

        self.url_text = scrolledtext.ScrolledText(
            card,
            height=9,
            font=("Consolas", 10),
            bg=self.input_bg,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            bd=0,
            padx=10,
            pady=10,
        )
        self.url_text.pack(fill="x", padx=14, pady=(0, 14))

        self.url_text.insert(
            "1.0",
            "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html\n"
            "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html\n"
            "https://books.toscrape.com/catalogue/soumission_998/index.html"
        )

    def build_log_area(self, parent):
        card = tk.Frame(parent, bg=self.panel, bd=0, highlightthickness=1, highlightbackground=self.border)
        card.pack(fill="both", expand=True)

        top_row = tk.Frame(card, bg=self.panel)
        top_row.pack(fill="x", padx=14, pady=(14, 8))

        self.log_title_label = tk.Label(
            top_row,
            text="",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 11, "bold"),
        )
        self.log_title_label.pack(side="left")

        self.log_subtitle_label = tk.Label(
            top_row,
            text="",
            bg=self.panel,
            fg=self.muted,
            font=("Segoe UI", 9),
        )
        self.log_subtitle_label.pack(side="right")

        self.log_box = scrolledtext.ScrolledText(
            card,
            height=20,
            font=("Consolas", 10),
            bg=self.log_bg,
            fg="#cbd5e1",
            insertbackground="#cbd5e1",
            relief="flat",
            bd=0,
            padx=12,
            pady=12,
        )
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

    def build_control_panel(self, parent):
        card = tk.Frame(parent, bg=self.panel, bd=0, highlightthickness=1, highlightbackground=self.border)
        card.pack(fill="both", expand=True)

        self.controls_title_label = tk.Label(
            card,
            text="",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 12, "bold"),
        )
        self.controls_title_label.pack(anchor="w", padx=14, pady=(14, 10))

        self.run_button = tk.Button(
            card,
            text="",
            command=self.start_tracker,
            bg=self.accent,
            fg="black",
            activebackground=self.accent_hover,
            activeforeground="black",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            bd=0,
            padx=18,
            pady=12,
            cursor="hand2",
        )
        self.run_button.pack(fill="x", padx=14, pady=(0, 10))

        self.csv_button = self.create_side_button(card, self.open_csv)
        self.csv_button.pack(fill="x", padx=14, pady=6)

        self.excel_button = self.create_side_button(card, self.open_excel)
        self.excel_button.pack(fill="x", padx=14, pady=6)

        self.refresh_button = self.create_side_button(card, self.refresh_dashboard)
        self.refresh_button.pack(fill="x", padx=14, pady=6)

        self.clear_button = self.create_side_button(card, self.clear_log)
        self.clear_button.pack(fill="x", padx=14, pady=6)

        self.build_email_settings(card)

        info_box = tk.Frame(card, bg=self.panel_3)
        info_box.pack(fill="x", padx=14, pady=(14, 14))

        self.help_title_label = tk.Label(
            info_box,
            text="",
            bg=self.panel_3,
            fg=self.text,
            font=("Segoe UI", 10, "bold"),
        )
        self.help_title_label.pack(anchor="w", padx=12, pady=(12, 6))

        self.help_short_label = tk.Label(
            info_box,
            text="",
            justify="left",
            bg=self.panel_3,
            fg=self.muted,
            font=("Segoe UI", 9),
        )
        self.help_short_label.pack(anchor="w", padx=12, pady=(0, 10))

        self.help_button = self.create_side_button(info_box, self.show_app_password_help)
        self.help_button.pack(fill="x", padx=12, pady=(0, 12))

    def build_email_settings(self, parent):
        section = tk.Frame(parent, bg=self.panel_3)
        section.pack(fill="x", padx=14, pady=(14, 8))

        self.email_settings_title_label = tk.Label(
            section,
            text="",
            bg=self.panel_3,
            fg=self.text,
            font=("Segoe UI", 10, "bold"),
        )
        self.email_settings_title_label.pack(anchor="w", padx=12, pady=(12, 4))

        self.email_settings_subtitle_label = tk.Label(
            section,
            text="",
            bg=self.panel_3,
            fg=self.muted,
            font=("Segoe UI", 9),
        )
        self.email_settings_subtitle_label.pack(anchor="w", padx=12, pady=(0, 8))

        self.email_address_var = tk.StringVar()
        self.email_password_var = tk.StringVar()
        self.to_email_var = tk.StringVar()
        self.smtp_server_var = tk.StringVar()
        self.smtp_port_var = tk.StringVar()

        self.sender_email_label, _ = self.create_labeled_entry(section, self.email_address_var)
        self.app_password_label, _ = self.create_labeled_entry(section, self.email_password_var, show="*")
        self.receiver_email_label, _ = self.create_labeled_entry(section, self.to_email_var)
        self.smtp_server_label, _ = self.create_labeled_entry(section, self.smtp_server_var)
        self.smtp_port_label, _ = self.create_labeled_entry(section, self.smtp_port_var)

        buttons_row = tk.Frame(section, bg=self.panel_3)
        buttons_row.pack(fill="x", padx=12, pady=(8, 12))

        self.save_settings_button = tk.Button(
            buttons_row,
            text="",
            command=self.save_email_settings,
            bg=self.blue,
            fg="black",
            activebackground="#67d3ff",
            activeforeground="black",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            bd=0,
            padx=12,
            pady=10,
            cursor="hand2",
        )
        self.save_settings_button.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.test_mail_button = tk.Button(
            buttons_row,
            text="",
            command=self.send_test_email,
            bg=self.green,
            fg="black",
            activebackground="#4ade80",
            activeforeground="black",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            bd=0,
            padx=12,
            pady=10,
            cursor="hand2",
        )
        self.test_mail_button.pack(side="left", fill="x", expand=True, padx=(6, 0))

    def create_labeled_entry(self, parent, variable, show=None):
        wrap = tk.Frame(parent, bg=self.panel_3)
        wrap.pack(fill="x", padx=12, pady=4)

        label = tk.Label(
            wrap,
            text="",
            bg=self.panel_3,
            fg=self.muted,
            font=("Segoe UI", 9),
        )
        label.pack(anchor="w", pady=(0, 4))

        entry = tk.Entry(
            wrap,
            textvariable=variable,
            show=show,
            bg=self.input_bg,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            bd=0,
            font=("Segoe UI", 10),
        )
        entry.pack(fill="x", ipady=8)
        return label, entry

    def create_side_button(self, parent, command):
        return tk.Button(
            parent,
            text="",
            command=command,
            bg=self.panel_2,
            fg=self.text,
            activebackground="#334155",
            activeforeground=self.text,
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            cursor="hand2",
        )

    def build_statusbar(self):
        self.status_var = tk.StringVar(value=self.tr("status_ready"))
        self.status_label = tk.Label(
            self.main,
            textvariable=self.status_var,
            bg=self.bg,
            fg=self.muted,
            anchor="w",
            font=("Segoe UI", 9),
        )
        self.status_label.pack(fill="x", pady=(12, 0))

    def load_settings_into_form(self):
        self.email_address_var.set(self.settings.get("email_address", ""))
        self.email_password_var.set(self.settings.get("email_password", ""))
        self.to_email_var.set(self.settings.get("to_email", ""))
        self.smtp_server_var.set(str(self.settings.get("smtp_server", "smtp.gmail.com")))
        self.smtp_port_var.set(str(self.settings.get("smtp_port", 587)))

    def get_email_config_from_form(self):
        return {
            "EMAIL_ADDRESS": self.email_address_var.get().strip(),
            "EMAIL_PASSWORD": self.email_password_var.get().strip(),
            "TO_EMAIL": self.to_email_var.get().strip(),
            "SMTP_SERVER": self.smtp_server_var.get().strip(),
            "SMTP_PORT": int(self.smtp_port_var.get().strip()),
        }

    def save_current_settings(self):
        settings = {
            "email_address": self.email_address_var.get().strip(),
            "email_password": self.email_password_var.get().strip(),
            "to_email": self.to_email_var.get().strip(),
            "smtp_server": self.smtp_server_var.get().strip(),
            "smtp_port": int(self.smtp_port_var.get().strip() or 587),
            "language": self.current_lang,
        }
        save_settings(settings)
        self.settings = settings

    def save_email_settings(self):
        try:
            config = self.get_email_config_from_form()
        except ValueError:
            messagebox.showerror(self.tr("error"), self.tr("smtp_must_be_number"))
            return

        settings = {
            "email_address": config["EMAIL_ADDRESS"],
            "email_password": config["EMAIL_PASSWORD"],
            "to_email": config["TO_EMAIL"],
            "smtp_server": config["SMTP_SERVER"],
            "smtp_port": config["SMTP_PORT"],
            "language": self.current_lang,
        }

        save_settings(settings)
        self.settings = settings
        self.refresh_dashboard()
        self.status_var.set(self.tr("status_settings_saved"))
        messagebox.showinfo(self.tr("success"), self.tr("settings_saved_popup"))

    def send_test_email(self):
        try:
            config = self.get_email_config_from_form()
        except ValueError:
            messagebox.showerror(self.tr("error"), self.tr("smtp_must_be_number"))
            return

        if not config["EMAIL_ADDRESS"] or not config["EMAIL_PASSWORD"] or not config["TO_EMAIL"]:
            messagebox.showwarning(self.tr("warning"), self.tr("required_mail_fields"))
            return

        try:
            send_email(
                subject=self.tr("test_mail_subject"),
                body=self.tr("test_mail_body"),
                config=config,
            )
            self.status_var.set(self.tr("status_test_sent"))
            messagebox.showinfo(self.tr("success"), self.tr("test_sent_popup"))
        except Exception as e:
            self.status_var.set(self.tr("status_test_failed"))
            messagebox.showerror(self.tr("mail_error"), f"{self.tr('mail_error')}\n\n{e}")

    def show_app_password_help(self):
        messagebox.showinfo(self.tr("help_title"), self.tr("detailed_help_text"))

    def log(self, message: str):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        self.log_box.delete("1.0", tk.END)
        self.status_var.set(self.tr("status_log_cleared"))

    def open_csv(self):
        if os.path.exists(CSV_FILE):
            os.startfile(CSV_FILE)
            self.status_var.set(self.tr("status_csv_opened"))
        else:
            messagebox.showwarning(self.tr("warning"), self.tr("no_csv_yet"))

    def open_excel(self):
        if os.path.exists(EXCEL_FILE):
            os.startfile(EXCEL_FILE)
            self.status_var.set(self.tr("status_excel_opened"))
        else:
            messagebox.showwarning(self.tr("warning"), self.tr("no_excel_yet"))

    def set_running_state(self, running: bool):
        state = "disabled" if running else "normal"
        self.run_button.config(state=state)
        self.csv_button.config(state=state)
        self.excel_button.config(state=state)
        self.refresh_button.config(state=state)
        self.clear_button.config(state="normal")
        self.save_settings_button.config(state=state)
        self.test_mail_button.config(state=state)

    def refresh_dashboard(self):
        summary = generate_summary(CSV_FILE)

        self.total_products_var.set(str(len(summary)))

        total_records = 0
        for item in summary:
            total_records += int(item.get("record_count", 0))
        self.total_records_var.set(str(total_records))

        if summary:
            statuses = [item.get("status", "") for item in summary]
            if "Düştü" in statuses or "Dropped" in statuses:
                self.last_status_var.set(self.tr("status_dropped"))
            elif "Arttı" in statuses or "Increased" in statuses:
                self.last_status_var.set(self.tr("status_increased"))
            elif "Aynı" in statuses or "Same" in statuses:
                self.last_status_var.set(self.tr("status_same"))
            else:
                self.last_status_var.set(self.tr("dashboard_default"))
        else:
            self.last_status_var.set(self.tr("dashboard_default"))

        self.report_var.set(self.tr("has_report") if os.path.exists(EXCEL_FILE) else self.tr("no_report"))

        email_ready = (
            bool(self.email_address_var.get().strip())
            and bool(self.email_password_var.get().strip())
            and bool(self.to_email_var.get().strip())
        )

        if email_ready:
            self.mail_status_var.set(self.tr("mail_ready"))
            self.mail_status_label.config(fg=self.green)
        else:
            self.mail_status_var.set(self.tr("mail_missing"))
            self.mail_status_label.config(fg=self.yellow)

    def start_tracker(self):
        urls = [
            line.strip()
            for line in self.url_text.get("1.0", tk.END).splitlines()
            if line.strip()
        ]

        if not urls:
            messagebox.showwarning(self.tr("warning"), self.tr("enter_url"))
            return

        try:
            email_config = self.get_email_config_from_form()
        except ValueError:
            messagebox.showerror(self.tr("error"), self.tr("smtp_must_be_number"))
            return

        self.set_running_state(True)
        self.status_var.set(self.tr("status_tracking_started"))
        self.log(self.tr("tracking_started_log"))

        thread = threading.Thread(
            target=self.run_tracker_thread,
            args=(urls, email_config),
            daemon=True,
        )
        thread.start()

    def run_tracker_thread(self, urls, email_config):
        try:
            run_tracker(
                target_urls=urls,
                headers=HEADERS,
                csv_file=CSV_FILE,
                excel_file=EXCEL_FILE,
                email_config=email_config,
                logger=self.log,
            )

            self.status_var.set(self.tr("status_tracking_done"))
            self.log(self.tr("tracking_finished_log"))
        except Exception as e:
            self.status_var.set(self.tr("status_unexpected_error"))
            self.log(f"\n{self.tr('status_unexpected_error')}: {e}")
        finally:
            self.refresh_dashboard()
            self.set_running_state(False)

    def change_language(self, selected):
        self.current_lang = selected.lower()
        self.language_var.set(selected.upper())
        self.save_current_settings()
        self.apply_translations()
        self.refresh_dashboard()

    def apply_translations(self):
        self.root.title(self.tr("app_title"))
        if hasattr(self, "title_label"):
            self.title_label.config(text=self.tr("app_title"))

        self.subtitle_label.config(text=self.tr("subtitle"))
        self.language_label.config(text=self.tr("language"))

        self.stat1.title_label.config(text=self.tr("tracked_products"))
        self.stat1.subtitle_label.config(text=self.tr("tracked_products_sub"))

        self.stat2.title_label.config(text=self.tr("total_records"))
        self.stat2.subtitle_label.config(text=self.tr("total_records_sub"))

        self.stat3.title_label.config(text=self.tr("last_status"))
        self.stat3.subtitle_label.config(text=self.tr("last_status_sub"))

        self.stat4.title_label.config(text=self.tr("excel_report"))
        self.stat4.subtitle_label.config(text=self.tr("excel_report_sub"))

        self.url_title_label.config(text=self.tr("url_title"))
        self.url_desc_label.config(text=self.tr("url_desc"))

        self.log_title_label.config(text=self.tr("log_title"))
        self.log_subtitle_label.config(text=self.tr("log_subtitle"))

        self.controls_title_label.config(text=self.tr("controls"))
        self.run_button.config(text=self.tr("start_tracking"))
        self.csv_button.config(text=self.tr("open_csv"))
        self.excel_button.config(text=self.tr("open_excel"))
        self.refresh_button.config(text=self.tr("refresh_dashboard"))
        self.clear_button.config(text=self.tr("clear_log"))

        self.email_settings_title_label.config(text=self.tr("email_settings"))
        self.email_settings_subtitle_label.config(text=self.tr("settings_section_sub"))
        self.sender_email_label.config(text=self.tr("sender_email"))
        self.app_password_label.config(text=self.tr("app_password"))
        self.receiver_email_label.config(text=self.tr("receiver_email"))
        self.smtp_server_label.config(text=self.tr("smtp_server"))
        self.smtp_port_label.config(text=self.tr("smtp_port"))
        self.save_settings_button.config(text=self.tr("save_settings"))
        self.test_mail_button.config(text=self.tr("send_test_email"))

        self.help_title_label.config(text=self.tr("help_title"))
        self.help_short_label.config(text=self.tr("help_short"))
        self.help_button.config(text=self.tr("detailed_help"))

        self.status_var.set(self.tr("status_ready"))
        self.refresh_dashboard()


if __name__ == "__main__":
    root = tk.Tk()
    app = PriceTrackerGUI(root)
    root.mainloop()