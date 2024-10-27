#!/usr/bin/env python3

import logging
import subprocess
import time
import os
from datetime import datetime
import threading

# Define a dictionary to store failed login attempts with timestamps for each IP address
failed_logins = {}
# Dictionary to store expiration times for blocked IPs
blocked_ips = {}

# Define the threshold for blocking repeated failed login attempts (e.g., 6 attempts within 60 seconds)
MAX_FAILED_ATTEMPTS = 6
FAILED_ATTEMPT_DURATION_THRESHOLD = 60  # seconds
BLOCK_DURATION = 60  # seconds (for example)
UNBLOCK_CHECK_INTERVAL = 10  # seconds

ALERT_LOG_FILE = "/var/log/snort/alert_fast.txt"
LOG_FILE = '/var/log/snort/Failed_Login.txt'

def setup_log_file():
    # Ensure the log file is only accessible by root
    subprocess.run(['sudo', 'touch', LOG_FILE], check=True)
    subprocess.run(['sudo', 'chown', 'root:root', LOG_FILE], check=True)
    subprocess.run(['sudo', 'chmod', '600', LOG_FILE], check=True)

def block_ip(ip_address):
    logging.info(f"Blocking {ip_address} for {BLOCK_DURATION} seconds.")
    # Execute iptables commands to block the IP address
    subprocess.run(['sudo', 'iptables', '-A', 'INPUT', '-s', ip_address, '-j', 'DROP'])
    
    # Store the expiration time for the blocked IP
    blocked_ips[ip_address] = time.time() + BLOCK_DURATION
    print_blocked_ips()
    # Remove the IP address from failed_logins
    if ip_address in failed_logins:
        del failed_logins[ip_address]

def is_blocked(ip_address):
    # Check if the IP address is currently blocked
    return ip_address in blocked_ips

def handle_login_attempt(ip_address):
    # Check if the IP address is already blocked
    if is_blocked(ip_address):
        logging.info(f"Login attempt from {ip_address} blocked.")
        return

    # Record the failed login attempt with the current timestamp
    current_time = datetime.now()
    if ip_address in failed_logins:
        failed_logins[ip_address].append(current_time)
    else:
        failed_logins[ip_address] = [current_time]

    # Remove attempts older than the threshold duration
    failed_logins[ip_address] = [timestamp for timestamp in failed_logins[ip_address]
                                 if (current_time - timestamp).total_seconds() <= FAILED_ATTEMPT_DURATION_THRESHOLD]

    # Check if the number of failed attempts exceeds the threshold within the specified duration
    if len(failed_logins[ip_address]) >= MAX_FAILED_ATTEMPTS:
        block_ip(ip_address)
        return

    logging.info(f"Failed login attempt from {ip_address}.")

def unblock_expired_ips():
    while True:
        current_time = time.time()
        for ip_address in list(blocked_ips.keys()):
            if current_time >= blocked_ips[ip_address]:
                try:
                    # Remove the block from iptables
                    subprocess.run(['sudo', 'iptables', '-D', 'INPUT', '-s', ip_address, '-j', 'DROP'], check=True)
                    logging.info(f"Unblocked {ip_address}")
                    # Remove from the blocked_ips dictionary
                    del blocked_ips[ip_address]
                    print_blocked_ips()
                except subprocess.CalledProcessError as e:
                    logging.error(f"Error unblocking IP {ip_address}: {e}")

        time.sleep(UNBLOCK_CHECK_INTERVAL)

# Function to parse SNORT3 alert log file and extract IP addresses from failed login attempts
def parse_alert_log(file_path):
    # Get the initial size of the file
    initial_position = os.path.getsize(file_path)

    while True:
        # Check if the file exists (e.g., in case SNORT3 rotates logs)
        if not os.path.exists(file_path):
            time.sleep(5)
            continue

        # Get current file size
        current_position = os.path.getsize(file_path)

        # Read new lines since last read
        with open(file_path, 'r') as file:
            # Adjust starting point based on initial file size
            start_position = initial_position if current_position - initial_position != 0 else 0
            if start_position == 0:
                continue
            else:
                file.seek(start_position)
                for line in file.readlines():
                    if "(smtp) unknown command" in line:
                        parts = line.strip().split(' [**] ')
                        if len(parts) >= 3:
                            timestamp = parts[0]
                            IPs = parts[2].split('{TCP}')[1]
                            srcIP = IPs.split(' -> ')[0]
                            source_ip = srcIP.split(':')[0]
                            handle_login_attempt(source_ip)

        # Update initial_position to current_position after first full read
        initial_position = current_position

        time.sleep(5)  # Wait before reading the log file again

def print_blocked_ips():
    formatted_ips = {ip: datetime.fromtimestamp(expiry_time).strftime('%m/%d-%H:%M:%S.%f') for ip, expiry_time in blocked_ips.items()}
    logging.info("Blocking IPs: %s", formatted_ips)

if __name__ == "__main__":
    setup_log_file()
    
    # Configure logging after setting up the log file
    logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

    print_blocked_ips()
    current_time_microseconds = '%06d' % int((time.time() % 1) * 1000000)
    current_time = time.strftime('%m/%d-%H:%M:%S', time.localtime()) + '.' + current_time_microseconds
    logging.info("Time: %s", current_time)
    # Start the threads
    log_thread = threading.Thread(target=parse_alert_log, args=(ALERT_LOG_FILE,))
    unblock_thread = threading.Thread(target=unblock_expired_ips)

    log_thread.start()
    unblock_thread.start()

    log_thread.join()
    unblock_thread.join()
