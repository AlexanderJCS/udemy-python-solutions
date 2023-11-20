import smtplib
import imaplib
import email


class EmailSender:
    def __init__(self, sender_email, password):
        print("Connecting to mail server...")
        self.smtp = smtplib.SMTP("smtp.gmail.com", 587)
        self.smtp.ehlo()
        self.smtp.starttls()

        print("Authenticating...")
        try:
            self.smtp.login(sender_email, password)
        except smtplib.SMTPAuthenticationError as e:
            print("Could not authenticate to the SMTP server. Check your sender_email and password.")
            raise e

        print("Logged in!")

        self.sender_email = sender_email

    def send_mail(self, to_email, subject, body):
        msg = f"Subject: {subject}\n{body}"
        self.smtp.sendmail(self.sender_email, to_email, msg)

    def __del__(self):
        self.smtp.quit()


class EmailReceiver:
    def __init__(self, sender_email, password):
        print("Connecting to mail server...")
        self.imap = imaplib.IMAP4_SSL("imap.gmail.com")
        print("Authenticating...")
        self.imap.login(sender_email, password)
        print("Logged in!")

        self.sender_email = sender_email

    def get_last_inbox_item(self, num_items):
        self.imap.select("inbox")
        typ, data = self.imap.search(None, f"TO {self.sender_email}")

        last_email_id = data[0][-1]

        print(last_email_id)

        result, email_data = self.imap.fetch(str(last_email_id), "(RFC822)")
        raw_email = email_data[0][1]
        raw_email_string = raw_email.decode("utf-8")

        email_message = email.message_from_string(raw_email_string)
        for part in email_message.walk():
            if part.get_content_type() not in ("text/plain", "text/html"):
                continue

            body = part.get_payload(decode=True)
            print("Last message:")
            print(body)

            break


def get_credentials():
    sender_email = input("Enter your sender_email: ")
    password = input("Enter your password: ")

    return sender_email, password


def main():
    sender_email, password = get_credentials()

    while True:
        while True:
            send_or_receive = input("Do you want to send or receive emails? (s/r/exit): ").lower()
            if send_or_receive in ("s", "r"):
                break

            print("Please enter either \"s\", \"r\", or \"exit\".")

        print()

        if send_or_receive == "exit":
            break

        if send_or_receive == "s":
            email_sender = EmailSender(sender_email, password)

            to_email = input("Send sender_email to: ")
            subject = input("Subject: ")
            body = input("Email body: ")

            email_sender.send_mail(to_email, subject, body)

        if send_or_receive == "r":
            email_receiver = EmailReceiver(sender_email, password)
            email_receiver.get_last_inbox_item(10)


if __name__ == "__main__":
    main()
