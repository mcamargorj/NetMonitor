import os
import psutil
import socket
import time
import sys
from rich.console import Console
from rich.table import Table
from rich import box
from colorama import init, Fore, Style
from rich.progress import Progress, SpinnerColumn, TextColumn

# Developed By MSCHelp 

init(autoreset=True)

console = Console()

def efeito(texto, cor=Fore.WHITE, delay=0.02):
    sys.stdout.write("\033[2J\033[H")  
    
    for char in texto:
        sys.stdout.write(cor + char + Style.RESET_ALL) 
        sys.stdout.flush()
        time.sleep(delay)
    
    print()

def obter_tipo_protocolo(protocolo):
    if protocolo == socket.SOCK_STREAM:
        return "TCP"
    elif protocolo == socket.SOCK_DGRAM:
        return "UDP"
    else:
        return f"Desconhecido ({protocolo})"

def obter_conexoes(porta_local_filtro=None, porta_remota_filtro=None, apenas_established=False, progress=None, task=None):
    conexoes = []

    try:
        todas_conexoes = psutil.net_connections(kind='inet')
        #total_conexoes = len(todas_conexoes)

        for i, conn in enumerate(todas_conexoes):
            protocolo = conn.type
            ip_local = conn.laddr.ip
            porta_local = conn.laddr.port
            ip_remoto = conn.raddr.ip if conn.raddr else "0.0.0.0"
            porta_remota = conn.raddr.port if conn.raddr else 0
            estado = conn.status
            pid = conn.pid
            
            if apenas_established and estado != "ESTABLISHED":
                continue

            if porta_local_filtro and porta_local != porta_local_filtro:
                continue

            if porta_remota_filtro and porta_remota != porta_remota_filtro:
                continue
            conexoes.append((protocolo, ip_local, porta_local, ip_remoto, porta_remota, estado, pid))
            
            if progress and task:
                progress.update(task, advance=1)  

    except Exception as e:
        print(f"Erro ao obter conexões: {e}")

    return conexoes

def mostrar_conexoes(porta_local_filtro=None, porta_remota_filtro=None, apenas_established=False):
    os.system('cls' if os.name == 'nt' else 'clear')
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=False,  
    ) as progress:
        
        todas_conexoes = psutil.net_connections(kind='inet')
        total_conexoes = len(todas_conexoes)

        task = progress.add_task("[cyan]Carregando conexões...", total=total_conexoes) 
        
        conexoes = obter_conexoes(porta_local_filtro, porta_remota_filtro, apenas_established, progress, task)

    if not conexoes:
        console.print("[bold yellow]Nenhuma conexão encontrada.[/bold yellow]")
        return
    
    table = Table(title="[bold green]Conexões de Rede[/bold green]", box=box.ROUNDED)
    table.add_column("PID", justify="right", style="cyan")
    table.add_column("Processo", justify="left", style="magenta")
    table.add_column("IP Local", justify="left", style="green")
    table.add_column("Porta Local", justify="right", style="yellow")
    table.add_column("IP Remoto", justify="left", style="red")
    table.add_column("Porta Remota", justify="right", style="blue")
    table.add_column("Hostname", justify="left", style="cyan")
    table.add_column("Estado", justify="left", style="magenta")
    table.add_column("Protocolo", justify="left", style="green")
    
    for protocolo, ip_local, porta_local, ip_remoto, porta_remota, estado, pid in conexoes:
        nome_processo = obter_processo(pid)
        hostname = resolver_hostname(ip_remoto) if ip_remoto != "0.0.0.0" else "N/A"
        porta_local_str = str(porta_local) if porta_local is not None else "N/A"
        porta_remota_str = str(porta_remota) if porta_remota is not None else "N/A"

        table.add_row(
            str(pid), nome_processo, ip_local, porta_local_str, ip_remoto, porta_remota_str, hostname, estado, obter_tipo_protocolo(protocolo)
        )
    console.print(table)
    rodape()

def obter_processo(pid):
    try:
        processo = psutil.Process(int(pid))
        return processo.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Desconhecido"

def resolver_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "Não Resolvido"

def encerrar_processo(pid):
    try:
        os.system(f"taskkill /PID {pid} /F")
        console.print(f"[bold green]Processo {pid} encerrado com sucesso.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Erro ao encerrar processo {pid}: {e}[/bold red]")

def mensagem_inicial():
    efeito("Iniciando varredura de rede...", Fore.GREEN)
    time.sleep(1)
    efeito("Analisando portas e protocolos...", Fore.YELLOW)
    time.sleep(2)
    efeito("Análise concluída...", Fore.RED)
    time.sleep(2)

def rodape():
    largura_tela = os.get_terminal_size().columns
    texto_rodape = "Developed By @MSCHelp"
    texto_centralizado = texto_rodape.center(largura_tela)
    console.print(f"\n\n[bold green]{texto_centralizado}[/bold green]")


ascii_art= """
 _   _      _   __  __             _ _             
| \\ | | ___| |_|  \\/  | ___  _ __ (_) |_ ___  _ __ 
|  \\| |/ _ \\ __| |\\/| |/ _ \\| '_ \\| | __/ _ \\| '__|
| |\\  |  __/ |_| |  | | (_) | | | | | || (_) | |   
|_| \\_|\\___|\\__|_|  |_|\\___/|_| |_|_|\\__\\___/|_|   
"""

if __name__ == "__main__":
    
    console.print(f"[bold green]{ascii_art}[/bold green]")
    
    opcao_established = input("Deseja listar apenas conexões ESTABLISHED? (s/n): ").strip().lower() == "s"

    porta_local = input("Filtrar por porta local (ou pressione Enter para todas): ").strip()
    porta_local = int(porta_local) if porta_local.isdigit() else None

    porta_remota = input("Filtrar por porta remota (ou pressione Enter para todas): ").strip()
    porta_remota = int(porta_remota) if porta_remota.isdigit() else None
    
    mensagem_inicial()   
    ultima_atualizacao = time.time()
    mostrar_conexoes(porta_local, porta_remota, opcao_established)

    while True:
        
        console.print("\n[bold]Digite o PID do processo que deseja encerrar (ou pressione Enter para atualizar, ou 'q' para sair):[/bold]", end=" ")
        pid_input = input().strip()

        if pid_input:
            if pid_input == 'q':
                console.print("[bold yellow]Saindo do programa...[/bold yellow]")
                break
            elif pid_input.isdigit():
                encerrar_processo(pid_input)
         
        else:            
            mostrar_conexoes(porta_local, porta_remota, opcao_established)
            ultima_atualizacao = time.time()
        
        if time.time() - ultima_atualizacao >= 60:
            mostrar_conexoes(porta_local, porta_remota, opcao_established)
            ultima_atualizacao = time.time()