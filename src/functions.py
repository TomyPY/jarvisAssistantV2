import smtplib
from config import SENDER_EMAIL
from config import PASSWORD

# def send_email(email, text):

#     with smtplib.SMTP('blizzard.mxrouting.net') as smtp:
#         smtp.ehlo()
#         smtp.starttls()
#         smtp.ehlo()
#         smtp.login(SENDER_EMAIL, PASSWORD)

#         backslash='\n'
#         body=f'''Hello There Gamer\n\nYou Raised a buy for the following product:\n\n{game}\n\n{'Here you have the credentials:'+backslash+(game_key if game_key!='empty' else "Email: "+account_email+backslash+"Password"+account_password)}Contact / Chat with Streamstop.co for support.\n\nLet The Game Begin\n\nTeam Streamstop.'''
#         msg=f"""From: {SENDER_EMAIL}\nTo: {email}\nSubject: Buy\n\n{body}."""
#         smtp.sendmail(from_addr=SENDER_EMAIL, to_addrs=email, msg=msg)
#         smtp.close()

#     return f"Email sended to {email}"