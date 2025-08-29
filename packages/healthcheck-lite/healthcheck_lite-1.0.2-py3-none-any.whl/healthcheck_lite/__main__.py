#!/usr/bin/env python3
import argparse
import psutil
import socket
import os
import re
import subprocess
import sys
from configparser import RawConfigParser
from collections import defaultdict

GREEN = "[92m"
RED = "[91m"
WHITE = "[1;37m"
RESET = "[0m"
DEFAULT_COLORS = {"GREEN": GREEN, "RED": RED, "RESET": RESET}

results = []
exit_code = 0
global_severity_threshold = 7
strict_mode = False

def print_status(check_type, name, status, extra="", severity=5):
    color = GREEN if status else RED
    ok = f"{WHITE}OK{GREEN}"
    print(f"{color}[{check_type.capitalize():<10}] {name:<40} {ok if status else 'FAIL'} {extra}{RESET}")
    results.append({
        'type': check_type.capitalize(),
        'name': name,
        'status': 'OK' if status else 'FAIL',
        'details': extra,
        'severity': severity
    })
    if not status and (strict_mode or severity <= global_severity_threshold):
        global exit_code
        exit_code = 1

def check_service(name, service_name, severity):
    try:
        result_active = subprocess.run(['systemctl', 'is-active', '--quiet', service_name], stderr=subprocess.DEVNULL)
        result_enabled = subprocess.run(['systemctl', 'is-enabled', '--quiet', service_name], stderr=subprocess.DEVNULL)
        status_active = result_active.returncode == 0
        status_enabled = result_enabled.returncode == 0

        if status_active and status_enabled:
            print_status('service', name, True, "active + enabled", severity)
        elif status_active:
            print_status('service', name, False, "active but not enabled", severity)
        elif status_enabled:
            print_status('service', name, False, "enabled but not active", severity)
        else:
            print_status('service', name, False, "inactive and disabled", severity)
    except Exception as e:
        print_status('service', name, False, f"Error: {e}", severity)

def check_process(name, regex, countmin, severity):
    count = 0
    for proc in psutil.process_iter(['cmdline']):
        try:
            cmd = ' '.join(proc.info['cmdline'])
            if re.search(regex, cmd):
                count += 1
        except Exception:
            continue
    status = count >= countmin
    print_status('process', name, status, f"found={count}, required={countmin}", severity)

def check_port(name, host, port, severity):
    try:
        with socket.create_connection((host, int(port)), timeout=2):
            print_status('port', name, True, f"{host}:{port}", severity)
    except Exception:
        print_status('port', name, False, f"{host}:{port}", severity)

def check_filesystem(name, path, used_threshold, severity):
    try:
        usage = psutil.disk_usage(path)
        used = usage.percent
        print_status('filesystem', name, used <= used_threshold, f"{used:.1f}% used", severity)
    except Exception as e:
        print_status('filesystem', name, False, f"Error: {e}", severity)

def check_memory(name, used_threshold, severity):
    mem = psutil.virtual_memory()
    used_percent = (mem.used / mem.total) * 100

    print_status(
        'memory',
        name,
        used_percent <= used_threshold,
        f"{used_percent:.1f}% used (real processes)",
        severity
    )

def check_file(name, filepath, regex, severity):
    try:
        with open(filepath, 'r') as f:
            for line in f:
                if re.search(regex, line):
                    print_status('file', name, False, "Match found", severity)
                    return
        print_status('file', name, True, "", severity)
    except Exception as e:
        print_status('file', name, False, f"Error: {e}", severity)

def check_establish(name, dest, used_threshold, severity):
    try:
        out = subprocess.check_output(f"netstat -an | grep '{dest}' | grep ESTABLISHED | wc -l", shell=True)
        count = int(out.decode().strip())
        print_status('establish', name, count <= used_threshold, f"{count} connections", severity)
    except Exception as e:
        print_status('establish', name, False, f"Error: {e}", severity)

def check_command(name, command, expect_regex, severity):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print_status('command', name, False, f"Exit code {result.returncode}", severity)
            return
        if expect_regex:
            if not re.search(expect_regex, result.stdout.strip()):
                print_status('command', name, False, "Regex not matched", severity)
            else:
                print_status('command', name, True, "Regex matched", severity)
            return
        print_status('command', name, True, result.stdout.splitlines()[0]+" ...", severity)
    except Exception as e:
        print_status('command', name, False, f"Error: {e}", severity)

def check_filecheck(name, path, must_exist, mode, owner, group, severity):
    try:
        if not os.path.exists(path):
            if must_exist:
                print_status('filecheck', name, False, "File not found", severity)
            else:
                print_status('filecheck', name, True, "Optional file not found", severity)
            return
        st = os.stat(path)
        mode_ok = (not mode) or (oct(st.st_mode)[-3:] == mode)
        owner_ok = (not owner) or (owner == get_username(st.st_uid))
        group_ok = (not group) or (group == get_groupname(st.st_gid))
        if mode_ok and owner_ok and group_ok:
            print_status('filecheck', name, True, "", severity)
        else:
            print_status('filecheck', name, False, "Permissions or ownership mismatch", severity)
    except Exception as e:
        print_status('filecheck', name, False, f"Error: {e}", severity)

def get_username(uid):
    try:
        import pwd
        return pwd.getpwuid(uid).pw_name
    except:
        return str(uid)

def get_groupname(gid):
    try:
        import grp
        return grp.getgrgid(gid).gr_name
    except:
        return str(gid)

def check_ping(name, host, count, severity):
    try:
        result = subprocess.run(['ping', '-c', str(count), host], stdout=subprocess.DEVNULL)
        print_status('ping', name, result.returncode == 0, "", severity)
    except Exception as e:
        print_status('ping', name, False, f"Error: {e}", severity)

def check_load(name, load1_threshold, severity):
    try:
        load1, _, _ = os.getloadavg()
        print_status('load', name, load1 <= load1_threshold, f"load1={load1:.2f}", severity)
    except Exception as e:
        print_status('load', name, False, f"Error: {e}", severity)

def check_sslcheck_old(name, host, port, days_warn, severity):
    try:
        import ssl, datetime
        context = ssl.create_default_context()
        with socket.create_connection((host, int(port)), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                expires = datetime.datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
                remaining = (expires - datetime.datetime.utcnow()).days
                print_status('sslcheck', name, remaining >= days_warn, f"{remaining} days left", severity)
    except Exception as e:
        print_status('sslcheck', name, False, f"Error: {e}", severity)

def check_sslcheck(name, host, port, days_warn, severity):
    """
    Vérification SSL complète avec détection de chaîne de certificats
    """
    try:
        import ssl, datetime, socket

        # Étape 1: Test avec vérification complète
        chain_status = "incomplete"
        verification_method = "unverified"
        cert_info = None
        remaining = 0

        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, int(port)), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert_info = ssock.getpeercert()
                    if cert_info and 'notAfter' in cert_info:
                        chain_status = "complete"
                        verification_method = "verified"
        except ssl.SSLError as e:
            # Échec de vérification - probablement chaîne incomplète
            if "certificate verify failed" in str(e).lower():
                chain_status = "incomplete"

        # Étape 2: Si échec, récupérer les infos sans vérification
        if not cert_info or 'notAfter' not in cert_info:
            try:
                # Essai avec cryptography si disponible
                try:
                    from cryptography import x509
                    from cryptography.hazmat.backends import default_backend

                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                    with socket.create_connection((host, int(port)), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=host) as ssock:
                            cert_der = ssock.getpeercert(True)
                            if cert_der:
                                cert = x509.load_der_x509_certificate(cert_der, default_backend())
                                expires = cert.not_valid_after

                                # Créer un dict simple pour le traitement
                                cert_info = {
                                    'notAfter': expires.strftime("%b %d %H:%M:%S %Y GMT")
                                }
                                verification_method = "unverified"

                except ImportError:
                    # Fallback sans cryptography
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                    with socket.create_connection((host, int(port)), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=host) as ssock:
                            cert_info = ssock.getpeercert()
                            verification_method = "unverified"

            except Exception as inner_e:
                print_status('sslcheck', name, False, f"Error retrieving certificate: {inner_e}", severity)
                return

        # Étape 3: Analyse des résultats
        if not cert_info or 'notAfter' not in cert_info:
            print_status('sslcheck', name, False, "Error: Cannot retrieve certificate", severity)
            return

        # Calcul des jours restants
        expires = datetime.datetime.strptime(cert_info['notAfter'], "%b %d %H:%M:%S %Y %Z")
        remaining = (expires - datetime.datetime.utcnow()).days

        if chain_status == "complete":
            chain_msg = "(complete chain)"
        else:
            chain_msg = "(incomplete chain)"

        message = f"{remaining} days left, {chain_msg}"

        # CORRECTION: Le certificat est OK si il reste assez de jours
        # Peu importe l'état de la chaîne pour le statut principal
        is_valid_time = remaining >= days_warn

        print_status('sslcheck', name, is_valid_time, message, severity)

        # Avertissement supplémentaire pour chaîne incomplète
        if chain_status == "incomplete":
            print_status('sslcheck', f"{name} (chain)", False,
                        "Certificate chain incomplete - may cause browser warnings", 1)

    except Exception as e:
        print_status('sslcheck', name, False, f"Error: {e}", severity)

def check_zombies(name, max_zombies, severity):
    try:
        count = sum(1 for p in psutil.process_iter(['status']) if p.info['status'] == psutil.STATUS_ZOMBIE)
        print_status('zombies', name, count <= max_zombies, f"{count} zombies", severity)
    except Exception as e:
        print_status('zombies', name, False, f"Error: {e}", severity)

def parse_config_multisection(path):
    with open(path) as f:
        raw_lines = f.readlines()

    config_blocks = []
    current_block = []
    for line in raw_lines:
        if line.strip().startswith("[") and current_block:
            config_blocks.append(current_block)
            current_block = [line]
        else:
            current_block.append(line)
    if current_block:
        config_blocks.append(current_block)

    parsed = defaultdict(list)
    for block in config_blocks:
        cp = RawConfigParser()
        cp.read_string("".join(block))
        section = cp.sections()[0]
        parsed[section].append(dict(cp[section]))

    return parsed

def run_checks(config_file, exec_types=None, specific_name=None):
    global global_severity_threshold
    config_data = parse_config_multisection(config_file)
    if 'global' in config_data and 'severity' in config_data['global'][0]:
        global_severity_threshold = int(config_data['global'][0]['severity'])
    
    if 'global' in config_data:
        global_conf = config_data['global'][0]
        for color_name in ("green", "red", "white", "reset"):
            if color_name in global_conf:
                globals()[color_name.upper()] = global_conf[color_name].encode('utf-8').decode('unicode_escape')

    sections = config_data

    for section_type, entries in sections.items():
        if exec_types and section_type not in exec_types:
            continue
        for options in entries:
            name = options.get('name', section_type)
            if specific_name and name != specific_name:
                continue
            severity = int(options.get('severity', 5))
            if section_type == 'service':
                check_service(name, options['service'], severity)
            elif section_type == 'process':
                check_process(name, options['regex'], int(options['countmin']), severity)
            elif section_type == 'port':
                check_port(name, options['host'], int(options['port']), severity)
            elif section_type == 'filesystem':
                check_filesystem(name, options['filesystem'], int(options['used']), severity)
            elif section_type == 'memory':
                check_memory(name, int(options['used']), severity)
            elif section_type == 'file':
                check_file(name, options['file'], options['regex'], severity)
            elif section_type == 'establish':
                check_establish(name, options['dest'], int(options['used']), severity)
            elif section_type == 'command':
                check_command(name, options['command'], options.get('expect_regex', ''), severity)
            elif section_type == 'filecheck':
                check_filecheck(name, options['path'], options.get('must_exist', 'true') == 'true',
                                options.get('mode'), options.get('owner'), options.get('group'), severity)
            elif section_type == 'ping':
                check_ping(name, options['host'], int(options.get('count', 3)), severity)
            elif section_type == 'load':
                check_load(name, float(options['load1']), severity)
            elif section_type == 'sslcheck':
                check_sslcheck(name, options['host'], options.get('port', 443), int(options['days_warn']), severity)
            elif section_type == 'zombies':
                check_zombies(name, int(options['max']), severity)

def main():
    parser = argparse.ArgumentParser(
    description="System Health Check",
    formatter_class=argparse.RawTextHelpFormatter,
    epilog="""Types de sections disponibles dans le fichier INI :

  [service]     → Vérifie si un service systemd est actif et activé
  [process]     → Vérifie la présence d'un processus par regex (ex: gunicorn, formatter_class=argparse.RawTextHelpFormatter)
  [port]        → Vérifie si un port est joignable en TCP
  [filesystem]  → Vérifie l'utilisation disque sur un point de montage
  [memory]      → Vérifie l'utilisation mémoire
  [file]        → Vérifie si un fichier contient une ligne correspondant à un regex
  [establish]   → Vérifie les connexions ESTABLISHED vers un hôte:port
  [command]     → Exécute une commande shell et vérifie le retour ou la sortie
  [filecheck]   → Vérifie existence/fichier/propriétaire/groupe/mode
  [ping]        → Envoie un ping vers une IP ou un nom d'hôte
  [load]        → Vérifie la charge système (loadavg)
  [sslcheck]    → Vérifie la validité du certificat SSL d’un hôte
  [zombies]     → Vérifie le nombre de processus zombies
"""
)
  # parser.description += "\n\nTypes de sections disponibles dans le fichier INI:\n" + """\
  #[service]     → Vérifie si un service systemd est actif et activé
  #[process]     → Vérifie la présence d'un processus par regex (ex: gunicorn)
  #[port]        → Vérifie si un port est joignable en TCP
  #[filesystem]  → Vérifie l'utilisation disque sur un point de montage
  #[memory]      → Vérifie l'utilisation mémoire
  #[file]        → Vérifie si un fichier contient une ligne correspondant à un regex
  #[establish]   → Vérifie les connexions ESTABLISHED vers un hôte:port
  #[command]     → Exécute une commande shell et vérifie le retour ou la sortie
  #[filecheck]   → Vérifie existence/fichier/propriétaire/groupe/mode
  #[ping]        → Envoie un ping vers une IP ou un nom d'hôte
  #[load]        → Vérifie la charge système (loadavg)
  #[sslcheck]    → Vérifie la validité du certificat SSL d’un hôte
  #[zombies]     → Vérifie le nombre de processus zombies\n"""

    parser.add_argument('--config', default='healthcheck.ini', help='Path to config file')
    parser.add_argument('--exec', help='Comma-separated list of check types (e.g., memory,file)')
    parser.add_argument('--name', help='Run check for specific name only')
    parser.add_argument('--output', help='Optional output file (JSON or HTML)')
    parser.add_argument('--strict', action='store_true', help='Fail on any error regardless of severity')
    parser.add_argument('--test', action='store_true', help='Valide le fichier INI sans exécuter les vérifications')
    parser.add_argument('--watch', type=int, help='Répète les vérifications toutes les N minutes')
    args = parser.parse_args()

    exec_types = args.exec.split(',') if args.exec else None
    strict_mode = args.strict

    # Test mode uniquement
    if args.test:
        try:
            _ = parse_config_multisection(args.config)
            print(f"✅ The file '{args.config}' is valid.")
            sys.exit(0)
        except Exception as e:
            print(f"❌ INI file validation error : {e}")
            sys.exit(1)

    def run_once():
        global results, exit_code
        results = []
        exit_code = 0
        run_checks(args.config, exec_types=exec_types, specific_name=args.name)

        ok_count = sum(1 for r in results if r['status'] == 'OK')
        fail_count = sum(1 for r in results if r['status'] != 'OK')
        total = len(results)
        print(f"Summary : {ok_count} OK / {fail_count} FAIL / {total} total")

        if args.output:
            import json
            sorted_results = sorted(results, key=lambda r: (r['type'], r['severity']))
            if args.output.endswith('.json'):
                with open(args.output, 'w') as f:
                    json.dump(sorted_results, f, indent=2)
            elif args.output.endswith('.html'):
                with open(args.output, 'w') as f:
                    f.write("<html><body><h1>Healthcheck Report</h1><table border='1'>")
                    f.write("<tr><th>Type</th><th>Name</th><th>Status</th><th>Details</th></tr>")
                    for r in sorted_results:
                        color = '#cfc' if r['status'] == 'OK' else '#fcc'
                        f.write(f"<tr style='background-color:{color}'><td>{r['type']}</td><td>{r['name']}</td><td>{r['status']}</td><td>{r['details']}</td></tr>")
                    f.write("</table></body></html>")

        return exit_code

    if args.watch:
        import time
        print(f"🔁 Watch mode enabled : check every {args.watch} minute(s)")
        try:
            while True:
                print(f"\n🕒 Running at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                run_once()
                time.sleep(args.watch * 60)
        except KeyboardInterrupt:
            print("⛔ Stopped by user request.")
            sys.exit(0)
    else:
        sys.exit(run_once())

if __name__ == "__main__":
    main()
