 # pyinstaller --onefile -w seu_script.py
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import serial
import threading
import serial.tools.list_ports
import time
from datetime import datetime

# Configurando o tema da janela
ctk.set_appearance_mode("dark")  # Pode ser "light", "dark", ou "system" (baseado no SO)
ctk.set_default_color_theme("blue")  # Pode ajustar o tema de cor também, blue, dark-blue, green


# Variável global para controle diversos
ser = None
is_connected = False
new_fonte = ("Courier New", 12)
save_debugger = [""] * 50


# Função para listar portas COM ativas
def listar_portas():
    return [port.device for port in serial.tools.list_ports.comports()]


# Função para atualizar a combobox com as portas disponíveis
def atualizar_com_port_combo():
    com_port_combo.set('')  # Limpa o texto selecionado da combobox
    portas = listar_portas()
    com_port_combo.configure(values=portas)  # Atualiza os valores da combobox
    if portas:
        com_port_combo.set(portas[0])  # Seleciona a primeira porta, se houver

                    
# Função para leitura da porta serial
def read_serial():
    global is_connected
    while ser and ser.is_open:
        try:
            data = ser.readline().decode('utf-8').strip()
            if data:
                process_protocol_data(data)
                #show_received_message() # Sinaliza recepção de dados
                
        except Exception as e:
            if e.args[0] == f"GetOverlappedResult failed (PermissionError(13, 'Acesso negado.', None, 5))":
                ser.close()
                is_connected = False
                connect_button.configure(text="Conectar")  # Muda o botão de volta para "Conectar"
                scan_button.configure(state='normal')  # Habilita o botão
                com_port_combo.configure(state='normal')  # Habilita o combo
                baudrate_combo.configure(state='normal')  # Habilita o combo
                conectar_serial() # Somente para atualizar debugger
                atualizar_com_port_combo() # Atualizar portas ativas
                print(f"Porta desconectada...")
            print(f"Erro ao ler da porta serial: {e}")


# Função para enviar dados
def send_data(data):
    try:
        if ser and ser.is_open:
            ser.write(data.encode('utf-8'))
            print(f"Dado enviado: {data}")
    except Exception as e:
        print(f"Erro ao enviar dados: {e}")

        
# Função para conectar/desconectar à porta serial
def conectar_serial():
    global ser, is_connected

    if not is_connected:
        try:
            com_port = com_port_combo.get()
            baudrate = baudrate_combo.get()
            ser = serial.Serial(com_port, baudrate=int(baudrate), timeout=1)
            is_connected = True
            connect_button.configure(text="Desconectar")
            scan_button.configure(state='disabled')
            com_port_combo.configure(state='disabled')
            baudrate_combo.configure(state='disabled')
            style.configure("TLabel", background="blue")
            frame_conexao.configure(style="TLabel")
            read_debugger_list() # busca nomes na lista de debugger
            
            # Iniciar a leitura da porta serial em uma thread separada
            thread = threading.Thread(target=read_serial)
            thread.daemon = True
            thread.start()

        except serial.SerialException as e:
            print(f"Erro ao conectar à porta serial: {e}")
    else:
        try:
            if ser:
                ser.close()
                is_connected = False
                connect_button.configure(text="Conectar")
                scan_button.configure(state='normal')
                com_port_combo.configure(state='normal')
                baudrate_combo.configure(state='normal')
                style.configure("TLabel", background="red")
                frame_conexao.configure(style="TLabel")
                break_button.configure(text="", fg_color="green")
                clear_listview()
        except Exception as e:
            print(f"Erro ao desconectar: {e}")


# Função para adicionar o nome do debugger ao listview
def add_debugger_name():
    debugger_name = debugger_entry.get()
    if debugger_name:  # Verifica se o campo não está vazio
        index = len(tree.get_children()) + 1  # Índice começa em 1
        tree.insert("", "end", values=(index, debugger_name, 0))  # Valor padrão 0
        debugger_entry.delete(0, tk.END)  # Limpa o campo de entrada
        

# Função para adiciona ou atualizar o valor no ListView no índice especificado.
def add_debugger_value(index, value):
    children = tree.get_children()
    found = False
    current_time = datetime.now().strftime('%H:%M:%S') # Obtenha a hora atual
    for child in children:
        item_index, _, _, _ = tree.item(child)['values']
        if int(item_index) == index:
            tree.item(child, values=(index, tree.item(child)['values'][1], value, current_time)) # Atualiza o valor e a hora
            found = True
            break
    if not found:
        tree.insert("", "end", values=(index, "Debugger", value, current_time)) # Adiciona se não encontrar


# Função para controle de protocolo recebido
def process_protocol_data(data):
    """Processa dados de protocolo no formato '#indexvalor'."""
    try:
        if data.startswith('#'):
            index_str = data[1]  # Extrai o primeiro dígito após '#'
            value_str = data[2:]  # Extrai o restante da string

            if value_str == "BREAK":
                break_button.configure(text="BREAK(" + index_str + ")", fg_color="Yellow")
            else:
                if index_str.isdigit() and value_str: # verifica se index é um dígito e value não está vazio.
                    index = int(index_str)
                    value = value_str
                    add_debugger_value(index, value)
                    return index, value
                else:
                    print("Formato de dados inválido: Índice deve ser um dígito e o valor não pode estar vazio.")
                    return None, None # retorna None, None caso haja erro no formato
        else:
            print("Formato de dados inválido: Deve começar com '#'.")
            return None, None # retorna None, None caso haja erro no formato
    except (IndexError, ValueError) as e:
        print(f"Erro ao processar dados: {e}")
        return None, None # retorna None, None em caso de exceção

    
# Função para clear do break point e enviando comando para próximo
def clear_break_point():
    data = '#'
    send_data(data)
    break_button.configure(text="", fg_color="green")

    
# Função para editar o nome do debugger selecionada no listview
def edit_debugger_name():
    global save_debugger
    try:
        selected_item = tree.selection()[0]  # Obtém o ID do item selecionado
        if selected_item:
            new_name = debugger_entry.get()
            if new_name:  # Verifica se um novo nome foi inserido
                current_values = tree.item(selected_item)['values']
                new_values = (current_values[0], new_name, current_values[2], current_values[3])  # Mantém índice e valor
                tree.item(selected_item, values=new_values)
                save_debugger[current_values[0]] = new_name # salva nome na lista de debugger
                debugger_entry.delete(0, tk.END)  # Limpa o campo de entrada
            else:
                print("Por favor, insira um novo nome para a variável.")
        else:
            print("Por favor, selecione uma variável para editar.")
    except IndexError:
        print("Nenhuma variável selecionada.")
        

# Função para reescrever nome dos debugger
def read_debugger_list():
    global save_debugger
    for index in range(len(save_debugger)):
        if save_debugger[index] != "":
            tree.insert("", "end", values=(index, save_debugger[index], "", ""))  # Valor, Time = Empty
            
            
# Função para limpar todo o listview
def clear_listview():
    """Limpa todos os itens do ListView."""
    for item in tree.get_children():
        tree.delete(item)


# Função para sinalizar dados recebidos pela serial
def show_received_message():
    style.configure("TLabel", background="yellow")
    frame_conexao.configure(style="TLabel")
    root.after(500, clear_received_message) # Mostra por 500ms (0.5 segundos)


def clear_received_message():
    style.configure("TLabel", background="blue")
    frame_conexao.configure(style="TLabel")


# Interface CustomTkinter
root = ctk.CTk()
root.title("Debugger v2.0.0 by DALÇÓQUIO AUTOMAÇÃO")
root.geometry("500x400")   

# Frame para configurações
frame_config = ctk.CTkFrame(root)
frame_config.grid(row=0, column=0, sticky="ew", padx=10, pady=10) # Usando grid aqui também
frame_config.grid_propagate(False)

# ComboBox para portas COM
com_port_combo = ctk.CTkComboBox(frame_config, font=new_fonte, values=listar_portas(), width=100, state="readonly")
com_port_combo.pack(side=tk.LEFT)

# Atualiza as portas COM no combo após criar a combobox
atualizar_com_port_combo()

# ComboBox para baudrate
baudrate_combo = ctk.CTkComboBox(frame_config, font=new_fonte, values=["1200", "2400", "4800", "9600",  "19200", "38400", "57600", "115200"], width=100, state="readonly")
baudrate_combo.pack(side=tk.LEFT, padx=10)
baudrate_combo.set("9600")  # Seleciona 9600 por padrão

# Botão para scanear portas
scan_button = ctk.CTkButton(frame_config, font=new_fonte, text="Scanear", command=atualizar_com_port_combo, width=120)
scan_button.pack(side=tk.LEFT, padx=10)

# Botão para conectar/desconectar
connect_button = ctk.CTkButton(frame_config, font=new_fonte, text="Conectar", command=conectar_serial, width=120)
connect_button.pack(side=tk.LEFT)

# Frame para o ListView
frame_listview = ttk.Frame(root, padding="10")
frame_listview.grid(row=1, column=0, sticky="nsew", padx=10, pady=0) # Usando grid
root.columnconfigure(0, weight=1) # Faz a coluna se expandir para ocupar todo o espaço
root.rowconfigure(1, weight=1)    # Faz a linha se expandir para ocupar todo o espaço

# Treeview (ListView)
tree = ttk.Treeview(frame_listview, columns=("index", "debugger", "value", "time"), show="headings")
tree.heading("index", text="Index")
tree.heading("debugger", text="Debugger")
tree.heading("value", text="Valor")
tree.heading("time", text="Time")
tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

#Configurando o tamanho das colunas (opcional)
tree.column("index", width=50, anchor=tk.CENTER, stretch=tk.NO)
tree.column("debugger", width=150, anchor=tk.W, stretch=tk.YES)
tree.column("value", width=50, anchor=tk.CENTER, stretch=tk.NO)
tree.column("time", width=50, anchor=tk.CENTER, stretch=tk.NO)

# Frame para adicionar debugger
frame_add_debugger = ctk.CTkFrame(root)
frame_add_debugger.grid(row=2, column=0, sticky="ew", padx=0, pady=10) # Usando grid

# Textbox para editar o debugger
debugger_entry = ctk.CTkEntry(frame_add_debugger, width=220)
debugger_entry.pack(side=tk.LEFT, padx=10)

# Botão para editar debugger
edit_button = ctk.CTkButton(frame_add_debugger, font=new_fonte, text="Editar", command=edit_debugger_name, width=120)
edit_button.pack(side=tk.LEFT, padx=0)

# Botão para clear de break point
break_button = ctk.CTkButton(frame_add_debugger, font=new_fonte, text="", command=clear_break_point, width=120, fg_color="green")
break_button.pack(side=tk.LEFT, padx=10)

# Frame para sinalizar conexão serial
style = ttk.Style()
style.configure("TLabel", background="red") # Definindo o estilo para Desconectado 
frame_conexao = ttk.Frame(root, width=500, height=10, style="TLabel")
frame_conexao.grid(row=3, column=0, sticky="ew") # Usando grid aqui também

root.mainloop()

# Fechar a porta serial ao encerrar o programa
if ser and ser.is_open:
    ser.close()
