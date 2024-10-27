# Snort3_Enhancement
This project enhances the Snort3 IDS/IPS tool to automatically block suspicious IP addresses after multiple failed login attempts, specifically focusing on brute-force attacks targeting an SMTP server. The scripts provided help in monitoring Snort3 logs and simulating brute-force attacks for testing purposes.

## Prerequisites

Before running the scripts, ensure the following:
1. **Snort3**: Make sure Snort3 is installed, configured, and running properly on your system. You can install it on a Linux system using the following command:

   ```bash
   sudo apt install snort3
 For a detailed guide on how to install and configure Snort3, you can refer to this [documentation](https://www.zenarmor.com/docs/linux-tutorials/how-to-install-and-configure-snort-on-ubuntu-linux).
 
Also, ensure that alerts are being logged correctly in the `alert_fast.txt` file located at `/var/log/snort/alert_fast.txt`. You can verify this by checking the Snort configuration file (`/usr/local/etc/snort/snort.lua`) and making sure that the alerts are set to be written in this file.
 
2. **iptables**: Ensure that iptables is installed and configured correctly. It will be used to block IP addresses based on the results of the Snort3 alerts.
3. **Python3**: The scripts are written in Python 3. Make sure Python 3 is installed:
    ```bash
   sudo apt install python3
    

## Files Included
1. **snort3_auto_block.py**: This script monitors the Snort3 alert log for failed login attempts on an SMTP server. After detecting a number of failed attempts from the same IP, it automatically blocks that IP address using **iptables**.
2. **brute_force.py**: This script simulates a brute-force attack on an SMTP server by attempting to login with multiple passwords from a provided file.




## How to Run the Project
### 1. Run the Blocking Script:
1. **Setup Logging**: The script will create and maintain a log file (`/var/log/snort/Failed_Login.txt`) to store blocking activities. Ensure that you have the necessary permissions for creating and writing to this file.
2. **Run the blocking script**:
   ```bash
   sudo python3 snort3_auto_block.py
 This script will start monitoring Snort3 logs for failed login attempts. It will block any IP that exceeds a threshold number of failed login attempts.
3. **Verify the Blocking**: To check if the script has blocked an IP, you can view the current rules in iptables by running:
    ```bash
    sudo iptables -L

### 2. Run the Brute Force Simulation Script:
This script simulates a brute-force attack to test the blocking functionality.
1. **Set up the SMTP server**: You need an SMTP server running on your network. The `brute_force.py` script will attempt to login to this server using the usernames and passwords provided in text files.
2. **Prepare password and username files**:
   * Create a `usernames.txt` file containing the usernames to be tested.
   * Create a `passwords.txt` file containing a list of passwords to attempt.
3. **Run the brute-force simulation**:
     ```bash
     python3 brute_force.py
The script will attempt to log in to the SMTP server using the provided usernames and passwords. If successful, it will print the correct password. If failed, it will continue trying.



## Integration Steps
1. **Navigate to the systemd directory**: First, go to the following directory to create a new service file:
   ```bash
   cd /etc/systemd/system
2. **Create a new service file**: Create a new service file with a name that reflects the functionality of your service. For example, if you want to use the name "FailedLoginAttempt", you can create the file as follows:
   ```bash
   sudo nano your_file_name.service
3. **Add the following content to your service file**:
    ```bash
    [Unit]
    Description=Failed Login Attempt Monitoring Service
    After=snort3.service
    Requires=snort3.service

    [Service]
    Type=simple
    ExecStart=/usr/bin/env python3 /path/to/your_script.py
    ExecStop=/bin/kill -TERM $MAINPID

    [Install]
    WantedBy=multi-user.target
    
Note: Replace `/path/to/your_script.py` with the actual path to your `snort3_auto_block.py` script.
4. **Reload the systemd daemon**: After saving the service file, reload the `systemd` daemon to recognize the new service:
    ```bash
    sudo systemctl daemon-reload
    
5. **Enable the service**: To ensure the service starts automatically on boot, enable it using the following command:
     ```bash
     sudo systemctl enable your_file_name.service
     
6. **Start the service**: Finally, start the service:
   ```bash
   sudo systemctl start your_file_name.service

7. **Verify that the service is running**: To check the status of your service and ensure it is running correctly, use the following command:
   ```bash
   sudo systemctl status your_file_name.service

 By following these steps, your snort3_auto_block.py script will be running as a systemd service, and it will automatically monitor for failed login attempts and block suspicious IP addresses as defined in your code.


 ## Testing the Integration
 1. **Simulate brute force**: Run the `brute_force.py` script to simulate brute force attempts on your SMTP server. This will attempt multiple logins using different passwords from the `passwords.txt` file you prepared.
 2. **Monitor the blocking script**: The `snort3_auto_block.py` script should detect the failed login attempts and block the suspicious IP after a number of attempts.
 3. **Verify the block**: Use the following command to check if the IP is blocked:
    ```bash
    sudo iptables -L


## Technologies Used
* **Snort3**: Network Intrusion Detection System (NIDS) to detect suspicious activity.
* **Python**: Scripts are written in Python 3 for automation.
* **iptables**: Used to block suspicious IP addresses based on failed login attempts.
* **SMTP Server**: The target for brute-force attack simulations in this project.



















    



















      


    


















  





   






