import socket
from urllib.parse import urlparse
import time
import requests
import csv
from datetime import datetime

def get_domain(host: str)-> str:      
    #get hostname when user passes a full url-  https:www.google..  hostname= www.google..
    parsed = urlparse(host)         
    if parsed.hostname:
        return parsed.hostname
    return host

def get_ip_addr(host: str) -> str:      #taskes the string host and returns string-error message/ip
    domain = get_domain(host)
    try:                                # take domain and resolve it to an i[]
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return "couldnt resolve domain"


def measure_latency(host: str) -> float:
    domain = get_domain(host)
    url = f"https://{domain}"

    try: 
        start = time.time()        #record start time
        response = requests.get(url, timeout=5)    #send request
        end = time.time()           #record end time

        latency_ms = (end - start) * 1000    #seconds to ms
        return round(latency_ms, 2)
    except requests.exceptions.RequestException:
        return -1       # website unreachable


#get HTTP status codes and classify- catch timeouts, dns and connection errors
def get_status_code(host: str)-> tuple[int, str]:       #[status code, classification]
    domain = get_domain(host)
    url = f"https://{domain}"

    try:
        response = requests.get(url, timeout=5)
        code = response.status_code
        #classification
        if 200 <= code < 300:
            status = "UP(success)"
        elif 300 <= code < 400:
            status = "REDIRECT"
        elif 400 <= code < 500:
            status = "CLIENT ERROR"
        elif 500 <= code < 600:
            status = "SEVER ERROR"
        elif 400 <= code < 500:
            status = "UNKNOWN STATUS"

        return code, status
    
    except requests.exceptions.RequestException:
        return -1, "UNREACHABLE"


def log_result(domain:str, ip: str, latency: float, code:int, status: str):
    filename = "monitor_log.csv"
    #create headder if file doesnt exist- create header once
    try:
        with open(filename, "x", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["timestamp", "domain", "ip", "latency_ms", "status_code", "classification"])
    except FileExistsError:
        pass
    #add new row
    with open(filename, "a", newline="") as file:
        writer = csv.writer(file)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")        #get current date and time
        writer.writerow([timestamp, domain, ip, latency, code, status])


# automatic monitoring loop
def monitor_site(host: str, interval: int = 30):        #check monitord website every 30 seconds as the default
    domain = get_domain(host)
    print(f"\nStarting monitor for {domain}, checks every {interval} seconds \n")
    print("press CTRL+c to stop\n")
    try:
        while True:
            ip = get_ip_addr(domain)
            latency = measure_latency(domain)
            code, status = get_status_code(domain)
            # print results
            print(f"--- {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ---")
            print(f"IP: {ip}")
            print(f"Latency: {latency} ms" if latency != -1 else "Latency: UNREACHABLE")
            print(f"Status code: {code}")
            print(f"Classification: {status}\n")

            log_result(domain, ip, latency, code, status)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n Monitoring stopped")




if __name__ == "__main__":
    user_inp = input("Enter website to monitor: ")
    interval = int(input("check interval in seconds: "))
    monitor_site(user_inp, interval)

    ip = get_ip_addr(user_inp)
    print(f"IP adress: {ip}")

    latency = measure_latency(user_inp)
    if latency == -1:
        print("Latency: Website unreachable or has times out")
    else:
        print(f"Latency: {latency} ms")

    code, status = get_status_code(user_inp)
    print(f"HTTP Status Code: {code}")
    print(f"Status Classification: {status}")

    #log the results
    domain = get_domain(user_inp)
    log_result(domain, ip, latency, code, status)
    print("Results logged")