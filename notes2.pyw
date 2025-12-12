import tkinter as tk
from tkinter import filedialog, messagebox, font, colorchooser, simpledialog
import os
import json

class PersistentNotepad:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Reminder")
        self.root.geometry("300x300")
        self.root.minsize(300, 300)
        
        # Configurações
        self.current_file = None
        self.settings_file = "notepad_settings.json"
        self.auto_save = True
        
        # Modo escuro/claro
        self.dark_mode = False
        self.dark_bg = "#2b2b2b"
        self.dark_fg = "#ffffff"
        self.light_bg = "#FFFFFF"
        self.light_fg = "#000000"
        
        # Carregar configurações salvas
        self.load_settings()
        
        # Configurar menu
        self.setup_menu()
        
        # Área de texto
        self.setup_text_area()
        
        # Bind para salvar automático
        self.text.bind("<KeyRelease>", self.auto_save_content)
        
        # Carregar conteúdo salvo
        self.load_content()
        
        # Bind para fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Aplicar tema inicial
        self.apply_theme()
        
    def setup_text_area(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de rolagem
        scrollbar = tk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Área de texto
        self.text = tk.Text(
            main_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            undo=True,
            font=self.current_font,
            fg=self.text_color,
            bg=self.bg_color,
            insertbackground=self.text_color  # Cor do cursor
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.text.yview)
        
        # Adicionar atalhos de teclado
        self.setup_keyboard_shortcuts()
        
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Salvar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Salvar Como...", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sempre no Topo", command=self.toggle_always_on_top)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Menu Editar
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Desfazer", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Refazer", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Recortar", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copiar", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Colar", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Selecionar Tudo", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Buscar...", command=self.find_text, accelerator="Ctrl+F")
        
        # Menu Formatação
        format_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Formatação", menu=format_menu)
        format_menu.add_command(label="Fonte...", command=self.change_font)
        format_menu.add_command(label="Cor do Texto...", command=self.change_text_color)
        format_menu.add_command(label="Cor do Fundo...", command=self.change_bg_color)
        
        # Menu Exibir
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Exibir", menu=view_menu)
        view_menu.add_checkbutton(label="Quebra de Linha", command=self.toggle_wrap)
        view_menu.add_separator()
        view_menu.add_command(label="Modo Escuro", command=self.toggle_dark_mode, accelerator="Ctrl+D")
        view_menu.add_separator()
        view_menu.add_command(label="Zoom +", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom -", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Zoom Padrão", command=self.zoom_reset, accelerator="Ctrl+0")
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.show_about)
        
    def setup_keyboard_shortcuts(self):
        # Atalhos de teclado
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<Control-f>', lambda e: self.find_text())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.zoom_reset())
        # Atalho para "Sempre no Topo" - Alt+T
        self.root.bind('<Alt-t>', lambda e: self.toggle_always_on_top())
        # Atalho para Modo Escuro - Ctrl+D
        self.root.bind('<Control-d>', lambda e: self.toggle_dark_mode())
        
    def load_settings(self):
        """Carrega configurações salvas"""
        default_font = ("Arial", 10)
        default_settings = {
            "font": default_font,
            "text_color": "#000000",
            "bg_color": "#FFFFFF",
            "wrap": True,
            "font_size": 10,
            "content": "",
            "window_geometry": "300x300",
            "always_on_top": False,
            "dark_mode": False,  # Nova configuração: modo escuro
            "saved_light_bg": "#FFFFFF",  # Salvar cor de fundo claro personalizada
            "saved_light_fg": "#000000",  # Salvar cor de texto claro personalizada
            "saved_dark_bg": "#2b2b2b",   # Salvar cor de fundo escuro personalizada
            "saved_dark_fg": "#ffffff"    # Salvar cor de texto escuro personalizada
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Mesclar com padrões para garantir todas as chaves existem
                    for key in default_settings:
                        if key not in settings:
                            settings[key] = default_settings[key]
            else:
                settings = default_settings
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
            settings = default_settings
            
        self.current_font = tuple(settings["font"])
        self.text_color = settings["text_color"]
        self.bg_color = settings["bg_color"]
        self.wrap_text = settings["wrap"]
        self.font_size = settings["font_size"]
        self.saved_content = settings.get("content", "")
        self.root.geometry(settings.get("window_geometry", "300x300"))
        self.always_on_top = settings.get("always_on_top", False)
        self.dark_mode = settings.get("dark_mode", False)
        
        # Carregar cores salvas para os temas
        self.saved_light_bg = settings.get("saved_light_bg", "#FFFFFF")
        self.saved_light_fg = settings.get("saved_light_fg", "#000000")
        self.saved_dark_bg = settings.get("saved_dark_bg", "#2b2b2b")
        self.saved_dark_fg = settings.get("saved_dark_fg", "#ffffff")
        
        # Se estiver em modo escuro, usar cores escuras salvas
        if self.dark_mode:
            self.text_color = self.saved_dark_fg
            self.bg_color = self.saved_dark_bg
        else:
            self.text_color = self.saved_light_fg
            self.bg_color = self.saved_light_bg
        
        # Aplicar configuração "sempre no topo" se salva anteriormente
        if self.always_on_top:
            self.root.attributes('-topmost', True)
        
    def save_settings(self):
        """Salva configurações atuais"""
        # Atualizar cores salvas baseadas no tema atual
        if self.dark_mode:
            self.saved_dark_bg = self.bg_color
            self.saved_dark_fg = self.text_color
        else:
            self.saved_light_bg = self.bg_color
            self.saved_light_fg = self.text_color
        
        settings = {
            "font": self.current_font,
            "text_color": self.text_color,
            "bg_color": self.bg_color,
            "wrap": self.wrap_text,
            "font_size": self.font_size,
            "content": self.text.get("1.0", tk.END),
            "window_geometry": self.root.geometry(),
            "always_on_top": self.always_on_top,
            "dark_mode": self.dark_mode,
            "saved_light_bg": self.saved_light_bg,
            "saved_light_fg": self.saved_light_fg,
            "saved_dark_bg": self.saved_dark_bg,
            "saved_dark_fg": self.saved_dark_fg
        }
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def load_content(self):
        """Carrega conteúdo salvo"""
        if self.saved_content:
            self.text.insert("1.0", self.saved_content)
    
    def auto_save_content(self, event=None):
        """Salva automaticamente o conteúdo"""
        if self.auto_save:
            self.save_settings()
    
    def toggle_always_on_top(self):
        """Alterna entre manter a janela sempre visível ou não"""
        self.always_on_top = not self.always_on_top
        self.root.attributes('-topmost', self.always_on_top)
        self.save_settings()
        status = "ativado" if self.always_on_top else "desativado"
        self.show_status_message(f"Sempre no Topo {status}")
    
    def toggle_dark_mode(self):
        """Alterna entre modo escuro e claro"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Salvar cores claras atuais
            self.saved_light_bg = self.bg_color
            self.saved_light_fg = self.text_color
            # Usar cores escuras
            self.bg_color = self.saved_dark_bg
            self.text_color = self.saved_dark_fg
        else:
            # Salvar cores escuras atuais
            self.saved_dark_bg = self.bg_color
            self.saved_dark_fg = self.text_color
            # Usar cores claras
            self.bg_color = self.saved_light_bg
            self.text_color = self.saved_light_fg
        
        self.apply_theme()
        self.save_settings()
        
        status = "ativado" if self.dark_mode else "desativado"
        self.show_status_message(f"Modo Escuro {status}")
    
    def apply_theme(self):
        """Aplica o tema atual (escuro ou claro)"""
        # Atualizar cores da área de texto
        self.text.config(
            fg=self.text_color,
            bg=self.bg_color,
            insertbackground=self.text_color  # Cor do cursor
        )
        
        # Atualizar cor de fundo da janela principal
        self.root.config(bg=self.bg_color)
        
        # Atualizar todos os widgets filhos (menus, etc.)
        self.update_widget_colors(self.root)
    
    def update_widget_colors(self, widget):
        """Atualiza recursivamente as cores de todos os widgets"""
        try:
            # Para widgets que suportam bg/fg
            if hasattr(widget, 'config'):
                # Atualizar background se não for um botão ou entrada
                widget_type = str(widget.winfo_class())
                if widget_type not in ['Button', 'Entry', 'Spinbox', 'Listbox']:
                    widget.config(bg=self.bg_color)
                    widget.config(fg=self.text_color)
                
                # Para menus especificamente
                if widget_type == 'Menu':
                    widget.config(bg=self.bg_color, fg=self.text_color)
        except:
            pass
        
        # Atualizar widgets filhos
        for child in widget.winfo_children():
            self.update_widget_colors(child)
    
    def show_status_message(self, message):
        """Mostra uma mensagem temporária na barra de status"""
        # Criar uma barra de status temporária
        if hasattr(self, 'status_label'):
            self.status_label.destroy()
        
        self.status_label = tk.Label(
            self.root, 
            text=message, 
            bg="lightyellow" if not self.dark_mode else "#444444",
            fg="black" if not self.dark_mode else "white",
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Remover após 2 segundos
        self.root.after(2000, self.status_label.destroy)
    
    # Funcionalidades do Menu Arquivo
    def new_file(self):
        if self.text.get("1.0", "end-1c"):
            if messagebox.askyesno("Novo Arquivo", "Deseja salvar as alterações?"):
                self.save_file()
        self.text.delete("1.0", tk.END)
        self.current_file = None
        self.root.title("Bloco de Notas - Sem título")
        
    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), 
                      ("Todos os arquivos", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", content)
                self.current_file = file_path
                self.root.title(f"Bloco de Notas - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o arquivo:\n{str(e)}")
    
    def save_file(self):
        if self.current_file:
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.text.get("1.0", tk.END))
                self.save_settings()
                messagebox.showinfo("Salvo", "Arquivo salvo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar o arquivo:\n{str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), 
                      ("Todos os arquivos", "*.*")]
        )
        if file_path:
            self.current_file = file_path
            self.save_file()
            self.root.title(f"Bloco de Notas - {os.path.basename(file_path)}")
    
    # Funcionalidades do Menu Editar
    def undo(self):
        try:
            self.text.edit_undo()
        except:
            pass
    
    def redo(self):
        try:
            self.text.edit_redo()
        except:
            pass
    
    def cut(self):
        self.text.event_generate("<<Cut>>")
    
    def copy(self):
        self.text.event_generate("<<Copy>>")
    
    def paste(self):
        self.text.event_generate("<<Paste>>")
    
    def select_all(self):
        self.text.tag_add('sel', '1.0', 'end')
    
    def find_text(self):
        find_window = tk.Toplevel(self.root)
        find_window.title("Buscar")
        find_window.geometry("300x150")
        find_window.transient(self.root)
        
        # Aplicar tema à janela de busca
        find_window.config(bg=self.bg_color)
        
        tk.Label(find_window, text="Buscar:", bg=self.bg_color, fg=self.text_color).pack(pady=5)
        find_entry = tk.Entry(find_window, width=30, bg=self.bg_color, fg=self.text_color)
        find_entry.pack(pady=5)
        
        def find():
            search_term = find_entry.get()
            if search_term:
                content = self.text.get("1.0", tk.END)
                if search_term in content:
                    self.text.tag_remove("found", "1.0", tk.END)
                    start_pos = "1.0"
                    while True:
                        start_pos = self.text.search(search_term, start_pos, stopindex=tk.END)
                        if not start_pos:
                            break
                        end_pos = f"{start_pos}+{len(search_term)}c"
                        self.text.tag_add("found", start_pos, end_pos)
                        start_pos = end_pos
                    highlight_color = "#FFFF00" if not self.dark_mode else "#FF9900"
                    self.text.tag_config("found", background=highlight_color)
                else:
                    messagebox.showinfo("Buscar", "Texto não encontrado.")
        
        tk.Button(find_window, text="Buscar", command=find).pack(pady=5)
        find_entry.focus()
    
    # Funcionalidades do Menu Formatação
    def change_font(self):
        font_window = tk.Toplevel(self.root)
        font_window.title("Fonte")
        font_window.geometry("300x200")
        
        # Aplicar tema à janela de fonte
        font_window.config(bg=self.bg_color)
        
        tk.Label(font_window, text="Família da Fonte:", bg=self.bg_color, fg=self.text_color).pack(pady=5)
        
        font_families = list(font.families())
        font_families.sort()
        
        font_var = tk.StringVar(value=self.current_font[0])
        font_listbox = tk.Listbox(font_window, height=5, bg=self.bg_color, fg=self.text_color)
        scrollbar = tk.Scrollbar(font_window, orient=tk.VERTICAL)
        
        for family in font_families[:50]:  # Mostra as primeiras 50
            font_listbox.insert(tk.END, family)
        
        font_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=font_listbox.yview)
        
        font_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(font_window, text="Tamanho:", bg=self.bg_color, fg=self.text_color).pack(pady=5)
        size_var = tk.StringVar(value=str(self.font_size))
        size_spinbox = tk.Spinbox(font_window, from_=8, to=72, textvariable=size_var, bg=self.bg_color, fg=self.text_color)
        size_spinbox.pack(pady=5)
        
        def apply_font():
            try:
                selected_font = font_listbox.get(font_listbox.curselection())
            except:
                selected_font = self.current_font[0]
            selected_size = int(size_var.get())
            self.current_font = (selected_font, selected_size)
            self.font_size = selected_size
            self.text.config(font=self.current_font)
            font_window.destroy()
            self.save_settings()
        
        tk.Button(font_window, text="Aplicar", command=apply_font).pack(pady=10)
    
    def change_text_color(self):
        color = colorchooser.askcolor(title="Escolha a cor do texto", initialcolor=self.text_color)
        if color[1]:
            self.text_color = color[1]
            self.text.config(fg=self.text_color, insertbackground=self.text_color)
            # Atualizar cores salvas baseadas no tema
            if self.dark_mode:
                self.saved_dark_fg = self.text_color
            else:
                self.saved_light_fg = self.text_color
            self.save_settings()
    
    def change_bg_color(self):
        color = colorchooser.askcolor(title="Escolha a cor do fundo", initialcolor=self.bg_color)
        if color[1]:
            self.bg_color = color[1]
            self.text.config(bg=self.bg_color)
            self.root.config(bg=self.bg_color)
            # Atualizar cores salvas baseadas no tema
            if self.dark_mode:
                self.saved_dark_bg = self.bg_color
            else:
                self.saved_light_bg = self.bg_color
            self.save_settings()
    
    # Funcionalidades do Menu Exibir
    def toggle_wrap(self):
        self.wrap_text = not self.wrap_text
        if self.wrap_text:
            self.text.config(wrap=tk.WORD)
        else:
            self.text.config(wrap=tk.NONE)
        self.save_settings()
    
    def zoom_in(self):
        self.font_size += 1
        self.current_font = (self.current_font[0], self.font_size)
        self.text.config(font=self.current_font)
        self.save_settings()
    
    def zoom_out(self):
        if self.font_size > 8:
            self.font_size -= 1
            self.current_font = (self.current_font[0], self.font_size)
            self.text.config(font=self.current_font)
            self.save_settings()
    
    def zoom_reset(self):
        self.font_size = 10
        self.current_font = (self.current_font[0], self.font_size)
        self.text.config(font=self.current_font)
        self.save_settings()
    
    # Ajuda
    def show_about(self):
        about_text = """Bloco de Notas Persistente

Versão 2.0

• Mantém conteúdo entre sessões
• Modo Escuro/Claro (Ctrl+D)
• Opção 'Sempre no Topo' (Alt+T)
• Todas as funcionalidades básicas de um bloco de notas
• Configurações totalmente persistentes
• Desenvolvido by Rug"""
        
        messagebox.showinfo("Sobre", about_text)
    
    def on_closing(self):
        """Salva tudo ao fechar"""
        self.save_settings()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PersistentNotepad()
    app.run()